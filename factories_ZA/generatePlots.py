import copy, sys, os, inspect, yaml

scriptDir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
sys.path.append(scriptDir)
from basePlotter import *

##### Some helper functions #####

def check_overlap(lst):
    if not any(lst) or sum(lst) != 1:
        raise Exception("Arguments passed to generatePlots.py are not consistent!")

def getBinningStrWithMax(nBins, start, end, max):
    """Return string defining a binning in histFactory, with 'nBins' bins between
    'start' and 'end', but with the upper edge replaced by 'max'."""
    
    bins = [start]
    pos = start
    for i in range(nBins):
        pos += (end-start)/nBins
        bins.append(pos)
    if bins[-1] < max:
        bins[-1] = max

    m_string = str(len(bins)-1) + ", { "
    for b in bins[0:len(bins)-1]:
        m_string += str(b) + ", "
    m_string += str(bins[-1]) + "}"

    return m_string

##### Retrieve config file written by launchHistFactory.py:
config = {}
with open(os.path.join("/tmp", os.getenv("USER") + "_factory.json")) as f:
    # Use YAML because JSON loads strings as unicode by default, and this messes with Factories
    config = yaml.safe_load(f)

def get_cfg(var, default=False):
    if var in config.keys():
        return config[var]
    else:
        return default

for_data = (config['sample_type'] == 'Data')
for_MC = (config['sample_type'] == 'MC')
for_signal = (config['sample_type'] == 'Signal')
check_overlap([for_data, for_MC, for_signal])

use_syst = get_cfg('syst')

lljj_categories = get_cfg('lljj_categories', ['MuMu', 'ElEl'])
llbb_categories = get_cfg('llbb_categories', ['MuMu', 'ElEl'])
lljj_stages = get_cfg('lljj_stages', [])
llbb_stages = get_cfg('llbb_stages', [])
lljj_plot_families = get_cfg('lljj_plots', [])
llbb_plot_families = get_cfg('llbb_plots', [])

# Ask Factories to regroup "similar" plots
optimize_plots = True

####### Configure additional content for factory ####
plots = []
library_directories = []
sample_weights = {}

code_before_loop = default_code_before_loop()
code_in_loop = default_code_in_loop()
code_after_loop = default_code_after_loop()
include_directories = default_include_directories(scriptDir)
headers = default_headers()
libraries = default_libraries()
library_directories = default_library_directories()
sources = default_sources(scriptDir)

######### Plot configuration ###########

#### lljj
weights_lljj = ['trigeff', 'llidiso', 'pu']

plots_lljj = []
if "basic" in lljj_plot_families:
    plots_lljj += ["mjj", "basic"]
if "other" in lljj_plot_families:
    plots_lljj += ["other"]
if "btag_efficiencies" in lljj_plot_families:
    plots_lljj += ["btag_efficiency_2d"]
if "weights" in lljj_plot_families:
    plots_lljj += ["llidisoWeight", "trigeffWeight", "puWeight"]

#### llbb
weights_llbb = ['trigeff', 'llidiso', 'pu', 'jjbtag_heavy', 'jjbtag_light']

plots_llbb = []
if "basic" in llbb_plot_families:
    plots_llbb += ["mjj", "basic"]
if "other" in llbb_plot_families:
    plots_llbb += ["other"]
if "weights" in llbb_plot_families:
    plots_llbb += ["llidisoWeight", "trigeffWeight", "puWeight", "jjbtagWeight"]

# No weights for data!
if for_data:
    weights_lljj = []
    weights_llbb = []

##### Systematics ####

split_jec_sources_base = [
        "AbsoluteFlavMap",
        "AbsoluteMPFBias",
        "AbsoluteScale",
        "AbsoluteStat",
        "FlavorQCD",
        "Fragmentation",
        "PileUpDataMC",
        "PileUpPtBB",
        "PileUpPtEC1",
        "PileUpPtEC2",
        "PileUpPtHF",
        "PileUpPtRef",
        "RelativeBal",
        "RelativeFSR",
        "RelativeJEREC1",
        "RelativeJEREC2",
        "RelativeJERHF",
        "RelativePtBB",
        "RelativePtEC1",
        "RelativePtEC2",
        "RelativePtHF",
        "RelativeStatEC",
        "RelativeStatFSR",
        "RelativeStatHF",
        "SinglePionECAL",
        "SinglePionHCAL",
        "TimePtEta"]
split_jec_sources = []
for _s in split_jec_sources_base:
    split_jec_sources.append("jec" + _s.lower() + "up")
    split_jec_sources.append("jec" + _s.lower() + "down")

if not use_syst:
    # No systematics
    systematics = { "modifObjects": ["nominal"] }
else:
    # Main systematics
    systematics = { 
            "modifObjects": [
                "nominal",
                "jecup", "jecdown",
                "jerup", "jerdown"
                ], 
            "SF": [
                "elidisoup", "elidisodown",
                "muidup", "muiddown",
                "muisoup", "muisodown",
                "jjbtaglightup", "jjbtaglightdown",
                "jjbtagheavyup", "jjbtagheavydown",
                "puup", "pudown",
                "trigeffup", "trigeffdown",
                "pdfup", "pdfdown",
                "dyStatup", "dyStatdown"
                #"elrecoup", "elrecodown",
                #"mutrackingup", "mutrackingdown",
                #"hdampup", "hdampdown",
                ]
            }
    # Scale uncertainties
    for i in range(6):
        systematics["SF"].append("scaleUncorr{}".format(i))
        systematics["SF"].append("dyScaleUncorr{}".format(i))

    # All JEC sources, if asked
    if syst_split_jec:
        systematics["modifObjects"] += split_jec_sources

    # PDF split by initial state, if asked
    if syst_split_pdf:
        for _s in ["qq", "gg", "qg"]:
            systematics["SF"].append("pdf" + _s + "up")
            systematics["SF"].append("pdf" + _s + "down")

    if syst_only_jec:
        systematics["SF"] = []
        systematics["modifObjects"] = split_jec_sources

# Systematic uncertainties: depends on the stage on what we're running on...
def allowed_systematics_llbb(syst):
    if syst == "nominal":
        return True
    if "dyStat" in syst:
        return False
    if "dyScaleUncorr" in syst:
        return False
    if for_data:
        return False
    return True

def allowed_systematics_lljj(syst):
    if syst == "nominal":
        return True
    if "dyStat" in syst:
        return False
    if "dyScaleUncorr" in syst:
        return False
    if "jjbtag" in syst:
        return False
    if for_data:
        return False
    return True


#### Generate plot list #####
for systematicType in systematics.keys():
    
    for systematic in systematics[systematicType]:
        if systematicType == "modifObjects" and not for_data:
            objects = systematic
        else:
            objects = "nominal" #ensure that we use normal ZA_objects for systematics not modifying obect such as scale factors 


        ###### llbb ######
        
        basePlotter_llbb = BasePlotter(btag=True, deepCSV=False, cmva=True, objects=objects)
        
        if allowed_systematics_llbb(systematic):
            this_categories = llbb_categories[:]
            plots.extend(basePlotter_llbb.generatePlots(this_categories, weights=weights_llbb, requested_plots=plots_llbb))

        # Signal: only do llbb!
        if for_signal:
            continue


        ##### lljj ######

        basePlotter_lljj = BasePlotter(btag=False, deepCSV=False, cmva=False, objects=objects)
        
        if allowed_systematics_lljj(systematic):
            this_categories = lljj_categories[:]
            plots.extend(basePlotter_lljj.generatePlots(this_categories, systematic=systematic, weights=weights_lljj, requested_plots=plots_lljj))


for plot in plots:
    print plot
