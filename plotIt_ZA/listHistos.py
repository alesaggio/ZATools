#! /usr/bin/env python

import os
import yaml
import glob

#usage: python listHisto.py [yields]
from ROOT import TFile
import argparse

parser = argparse.ArgumentParser(description='Facility to produce the yml with plots information.')
parser.add_argument('--yields', help='If you just want to produce the yields and systematics.', action="store_true")
parser.add_argument('-d', '--directory', required=True, help='Directory of the input rootfiles.')
parser.add_argument('--unblinded', help='If you want to produce unblinded plots', action="store_true")
parser.add_argument('-ell', '--ell_index', help='Pass the index of a given ellipse')

group = parser.add_mutually_exclusive_group(required=True)
group.add_argument('--lljj', help='Produce plots for lljj stage', action="store_true")
group.add_argument('--llbb', help='Produce plots for llbb stage', action="store_true")

args = parser.parse_args()

if not os.path.exists(args.directory):
    parser.error("%r does not exists" % args.directory)

rootDir = args.directory
slurmDir = os.path.join(rootDir, "slurm/output")

# Find a ROOT file in slurm output directory
root_files = glob.glob(os.path.join(slurmDir, "*.root"))
if len(root_files) == 0:
    raise Exception("No ROOT files found in %r" % slurmDir)
else:
    print len(root_files)

fileName = ""
for file in root_files:
    if "HToZATo2L2B" not in file:
        fileName = file

print("Listing histograms found in %r" % fileName)

if args.unblinded:
    print("WARNING -- PRODUCING UNBLINDED PLOTS")

print "OPENING THE FOLLOWING FILE:"
print fileName
file = TFile.Open(fileName) 
keys = file.GetListOfKeys()
alreadyIn = []

# Create 'ZA_plotter_all.yml':
# Configure list of files and legend
with open('ZA_plotter_all.yml.tpl') as tpl_handle:
    tpl = tpl_handle.read()
    if args.lljj:
        tpl = tpl.format(files="['DY_MCFiles.yml', 'ttbar_MCFiles.yml', 'otherBackgrounds_MCFiles.yml', 'DataFiles.yml']", legend="position: [0.61, 0.61, 0.94, 0.89]")
    if args.llbb:
        if args.ell_index is None:
            tpl = tpl.format(files="['DY_MCFiles.yml', 'ttbar_MCFiles.yml', 'otherBackgrounds_MCFiles.yml', 'DataFiles.yml', 'SignalFiles.yml']", legend="include: ['legendPosition.yml']")
        else:
            signal = 'singleSignals/SignalFiles_{0}.yml'.format(args.ell_index)
            tpl = tpl.format(files="['DY_MCFiles.yml', 'ttbar_MCFiles.yml', 'otherBackgrounds_MCFiles.yml', 'DataFiles.yml', "+'"'+signal+'"'+"]", legend="include: ['legendPosition.yml']")
    with open('ZA_plotter_all.yml', 'w') as f:
        f.write(tpl)


# Create 'centralConfig.yml':
# Configure root directory
with open('centralConfig.yml.tpl') as tpl_handle:
    tpl = tpl_handle.read()
    tpl = tpl.format(root=slurmDir)
    with open('centralConfig.yml', 'w') as f:
        f.write(tpl)

# Dictionary containing all the plots
plots = {}

logY = 'both'
if args.yields:
    logY = False
defaultStyle = {
        'log-y': logY,
        'save-extensions': ['pdf', 'png'],
        'legend-columns': 2,
        'show-ratio': True,
        'show-overflow': True,
        'show-errors': True
        }

defaultStyle_events_per_gev = defaultStyle.copy()
defaultStyle_events_per_gev.update({
        'y-axis': 'Events',
        'y-axis-format': '%1% / %2$.2f GeV',
        })

defaultStyle_events = defaultStyle.copy()
defaultStyle_events.update({
        'y-axis': 'Events',
        'y-axis-format': '%1% / %2$.2f',
        })


defaultStyle_noOverflow = {
        'log-y': logY,
        'save-extensions': ['pdf', 'png'],
        'legend-columns': 2,
        'show-ratio': True,
        'show-overflow': False,
        'show-errors': True
        }

defaultStyle_events_noOverflow = defaultStyle_noOverflow.copy()
defaultStyle_events_noOverflow.update({
        'y-axis': 'Events',
        'y-axis-format': '%1% / %2$.2f',
        })

nHistos = 0

def should_be_blind(name):
    if args.unblinded:
        return False
    # Define the SR here
    if "nobtag" in name:
        return False
    if not "mll_and_met_cut" in name:
        return False
    if "MuEl" in name:
        return False
    return True

def get_flavour(name):
    for flav in ["MuMu", "MuEl", "ElEl", "SF", "All"]:
        if flav in name:
            return flav

for key in keys:
    key_name = key.GetName()

    if key_name not in alreadyIn and not "__" in key_name:

        # Keep only histograms
        if not key.ReadObj().InheritsFrom("TH1"):
            continue

        ## Some manual choices which plots to skip...
        
        # skip 2D histos
        if "_vs_" in key_name and "flat" not in key_name: continue
 
        #if "All" in key_name: continue

        # if lljj (for background), plot the non-btagged plots
        if args.lljj and 'btagM' in key_name: continue
        # if llbb (for background and signal), plot only the btagged plots
        if args.llbb and 'nobtag' in key_name: continue

        #if not "no_cut" in key_name:
        #    continue

        ## Update all the plots with title, ...

        alreadyIn.append(key_name)
        plot = {
                'x-axis': key_name,
                }
        plot['labels'] = []

        #if not args.ell_index is None:
        #    if "rho_steps" not in key_name:
        #        continue

        if "lep1_pt" in key_name:
            plot['x-axis'] = "Leading lepton p_{T} (GeV)"
            plot.update(defaultStyle_events_per_gev)
        elif "lep2_pt" in key_name:
            plot['x-axis'] = "Sub-leading lepton p_{T} (GeV)"
            plot.update(defaultStyle_events_per_gev)
        elif "jet1_pt" in key_name:
            plot['x-axis'] = "Leading jet p_{T} (GeV)"
            plot.update(defaultStyle_events_per_gev)
        elif "jet2_pt" in key_name:
            plot['x-axis'] = "Sub-leading jet p_{T} (GeV)"
            plot.update(defaultStyle_events_per_gev)
        elif "lep1_eta" in key_name:
            plot['x-axis'] = "Leading jet #eta"
            plot.update(defaultStyle_events)
        elif "lep2_eta" in key_name:
            plot['x-axis'] = "Sub-leading jet #eta"
            plot.update(defaultStyle_events)
        elif "jet1_eta" in key_name:
            plot['x-axis'] = "Leading jet #eta"
            plot.update(defaultStyle_events)
        elif "jet2_eta" in key_name:
            plot['x-axis'] = "Sub-leading jet #eta"
            plot.update(defaultStyle_events)
        elif "lep1_phi" in key_name:
            plot['x-axis'] = "Leading lepton #phi"
            plot.update(defaultStyle_events)
        elif "lep2_phi" in key_name:
            plot['x-axis'] = "Sub-leading lepton #phi"
            plot.update(defaultStyle_events)
        elif "jet1_phi" in key_name:
            plot['x-axis'] = "Leading jet #phi"
            plot.update(defaultStyle_events)
        elif "jet2_phi" in key_name:
            plot['x-axis'] = "Sub-leading jet #phi"
            plot.update(defaultStyle_events)
        elif "jet1_CSV" in key_name:
            plot['x-axis'] = "Leading jet CSVv2 discriminant"
            plot.update(defaultStyle_events)
        elif "jet2_CSV" in key_name:
            plot['x-axis'] = "Sub-leading jet CSVv2 discriminant"
            plot.update(defaultStyle_events)
        elif "jet1_cMVAv2" in key_name:
            plot['x-axis'] = "Leading jet cMVAv2 discriminant"
            plot.update(defaultStyle_events)
        elif "jet2_cMVAv2" in key_name:
            plot['x-axis'] = "Sub-leading jet cMVAv2 discriminant"
            plot.update(defaultStyle_events)
        elif "jet1_deepCSV" in key_name:
            plot['x-axis'] = "Leading jet deepCSV discriminant"
            plot.update(defaultStyle_events)
        elif "jet2_deepCSV" in key_name:
            plot['x-axis'] = "Sub-leading jet deepCSV discriminant"
            plot.update(defaultStyle_events)
        elif "jet1_JP" in key_name:
            plot['x-axis'] = "Leading jet JP discriminant"
            plot.update(defaultStyle_events)
        elif "jet2_JP" in key_name:
            plot['x-axis'] = "Sub-leading jet JP discriminant"
            plot.update(defaultStyle_events)
        elif "ll_pt_" in key_name:
            plot['x-axis'] = "Dilepton system p_{T} (GeV)"
            plot.update(defaultStyle_events_per_gev)
        elif "jj_pt_" in key_name:
            plot['x-axis'] = "Dijet system p_{T} (GeV)"
            plot.update(defaultStyle_events_per_gev)
        #elif "met_pt" in key_name:
        elif "met_pt" in key_name and "inverted_met_cut" not in key_name:
            plot['x-axis'] = "#slash{E}_{T} (GeV)"
            plot.update(defaultStyle_events_per_gev)
        elif "met_phi" in key_name:
            plot['x-axis'] = "#phi_{#slash{E}_{T}}"
            plot.update(defaultStyle_events)
        elif "ll_DR_l_l_All_hh_llmetjj_HWWleptons_btagM_csv_cleaning_cut" in key_name:
            plot['x-axis'] = "#DeltaR(leading lepton, sub-leading lepton)"
            plot.update(defaultStyle_events)
        elif "ll_DR_l_l" in key_name:
            plot['x-axis'] = "#DeltaR(leading lepton, sub-leading lepton)"
            plot.update(defaultStyle_events)
        elif "jj_DR_j_j" in key_name:
            plot['x-axis'] = "#DeltaR(leading jet, sub-leading jet)"
            plot.update(defaultStyle_events)
        elif "ll_DPhi_l_l" in key_name:
            plot['x-axis'] = "#Delta#phi(leading lepton, sub-leading lepton)"
            plot.update(defaultStyle_events)
        elif "jj_DPhi_j_j" in key_name:
            plot['x-axis'] = "#Delta#phi(leading jet, sub-leading jet)"
            plot.update(defaultStyle_events)
        elif "lljj_pt_" in key_name:
            plot['x-axis'] = "p_{T}^{lljj}"
            plot.update(defaultStyle_events_per_gev)
        elif "jet1_deepCSV_" in key_name:
            plot['x-axis'] = "deepCSV of leading jet"
            plot.update(defaultStyle_events)
        elif "jet2_deepCSV_" in key_name:
            plot['x-axis'] = "deepCSV of sub-leading jet"
            plot.update(defaultStyle_events)
        elif "met_significance" in key_name:
            plot['x-axis'] = "MET significance"
            plot['x-axis-range'] = [0, 100]
            plot.update(defaultStyle_events)
        elif "DPhi_ll_met_" in key_name:
            plot['x-axis'] = "#Delta#phi(ll, #slash{E}_{T})"
            plot.update(defaultStyle_events)
        elif "DPhi_ll_jj" in key_name:
            plot['x-axis'] = "#Delta#phi(ll, jj)"
            plot.update(defaultStyle_events)
        elif "minDPhi_l_met_" in key_name:
            plot['x-axis'] = "min(#Delta#phi(lepton, #slash{E}_{T}))"
            plot.update(defaultStyle_events)
        elif "maxDPhi_l_met_" in key_name:
            plot['x-axis'] = "max(#Delta#phi(lepton, #slash{E}_{T}))"
            plot.update(defaultStyle_events)
        elif "MT_" in key_name:
            plot['x-axis'] = "m_{ll#slash{E}_{T}}"
            plot.update(defaultStyle_events_per_gev)
        elif "MTformula_" in key_name:
            plot['x-axis'] = "MT"
            plot.update(defaultStyle_events_per_gev)
        elif "HT" in key_name:
            plot['x-axis'] = "HT"
            plot.update(defaultStyle_events_per_gev)
        elif "projMET_" in key_name:
            plot['x-axis'] = "Projected #slash{E}_{T}"
            plot.update(defaultStyle_events_per_gev)
        elif "DPhi_jj_met" in key_name:
            plot['x-axis'] = "#Delta#phi(jj, #slash{E}_{T})"
            plot.update(defaultStyle_events)
        elif "minDPhi_j_met" in key_name:
            plot['x-axis'] = "min#Delta#phi(j, #slash{E}_{T})"
            plot.update(defaultStyle_events)
        elif "maxDPhi_j_met" in key_name:
            plot['x-axis'] = "max#Delta#phi(j, #slash{E}_{T})"
            plot.update(defaultStyle_events)
        elif "minDR_l_j" in key_name:
            plot['x-axis'] = "min#DeltaR(l, j)"
            plot.update(defaultStyle_events)
        elif "maxDR_l_j" in key_name:
            plot['x-axis'] = "max#DeltaR(l, j)"
            plot.update(defaultStyle_events)
        elif "DR_ll_jj_" in key_name:
            plot['x-axis'] = "#DeltaR(ll, jj)"
            plot.update(defaultStyle_events)
        elif "DR_llmet_jj" in key_name:
            plot['x-axis'] = "#DeltaR(ll#slash{E}_{T}, jj)"
            plot.update(defaultStyle_events)
        elif "DPhi_ll_jj_" in key_name:
            plot['x-axis'] = "#DeltaPhi(ll, jj)"
            plot.update(defaultStyle_events)
        elif "nllmetjj_" in key_name:
            plot['x-axis'] = "#llmetjj"
            plot.update(defaultStyle_events)
        elif "nLep_" in key_name:
            plot['x-axis'] = "Number of leptons"
            plot.update(defaultStyle_events)
        elif "nJet_" in key_name:
            plot['x-axis'] = "Number of jets"
            plot.update(defaultStyle_events)
        elif "nBJetMediumCSV_" in key_name:
            plot['x-axis'] = "Number of b-tagged jets (CSVv2 medium)"
            plot.update(defaultStyle_events)
        elif "cosThetaStar" in key_name:
            plot['x-axis'] = "cos(#theta^{*}_{CS})_{lljj#slash{E}_{T}}"
            plot.update(defaultStyle_events)
        elif "isInOrOut" in key_name:
            plot['x-axis'] = "out or in"
            plot.update(defaultStyle_events)
            if should_be_blind(key_name):
                plot['blinded-range'] = [1, 2]
        elif "rho_steps" in key_name:
            plot['x-axis'] = "#rho"
            plot.update(defaultStyle_noOverflow)
            if should_be_blind(key_name):
                plot['blinded-range'] = [0, 3]


        elif "lljj_M_" in key_name:
            plot['x-axis'] = "m_{lljj} (GeV)"
            plot.update(defaultStyle_events_per_gev)
            if should_be_blind(key_name):
                plot['blinded-range'] = [0, 1500]

        elif "ll_M_" in key_name:
            plot['x-axis'] = "m_{ll} (GeV)"
            plot.update(defaultStyle_events_per_gev)
 
            #### Do the yields here
            #btag_stage = ""
            #if "btagM" in key_name:
            #    btag_stage = "llbb"
            #else:
            #    btag_stage = "lljj"
            #plot['yields-title'] = get_flavour(key_name) + ", " + btag_stage
            #plot['for-yields'] = True
            #if args.yields:
            #    plots['override'] = True


        ### YIELDS FOR ttbar NORMALIZATION
        elif "met_pt_" in key_name and "inverted_met_cut" in key_name:
            plot['x-axis'] = "MET (GeV)"
            plot.update(defaultStyle_events_per_gev)
            btag_stage = ""
            if "btagM" in key_name:
                btag_stage = "llbb"
            else:
                btag_stage = "lljj"
            plot['yields-title'] = get_flavour(key_name) + ", " + btag_stage
            plot['for-yields'] = True
            if args.yields:
                plots['override'] = True
        ### END OF YIELDS FOR ttbar NORMALIZATION


        elif "jj_M_" in key_name and "_vs_" not in key_name and ("jj_deepCSV" not in key_name or "jj_cmva" not in key_name):
            plot['x-axis'] = "m_{jj} (GeV)"
            plot.update(defaultStyle_events_per_gev)
            if should_be_blind(key_name):
                plot['blinded-range'] = [0, 1000]

        # Default:
        
        else:
            plot.update(defaultStyle_events)

        # Further labels, style, ...

        if "gen_" in key_name:
            flavour = key_name.split("_")[1]
            plot['x-axis'] = "is "+flavour
            plot['no-data'] = True
            plot.update(defaultStyle_events)
        if "scaleFactor" in key_name:
            plot['x-axis'] = "Scale factor"
            plot.update(defaultStyle_events)
            plot['no-data'] = True

        label_x = 0.22
        label_y = 0.895
        if get_flavour(key_name) == "MuMu":
            plot['labels'] += [{
                'text': '#mu#mu channel',
                'position': [label_x, label_y],
                'size': 24
                }]
        elif get_flavour(key_name) == "MuEl":
            plot['labels'] += [{
                'text': '#mue + e#mu channels',
                'position': [label_x, label_y],
                'size': 24
                }]
        elif get_flavour(key_name) == "ElEl":
            plot['labels'] += [{
                'text': 'ee channel',
                'position': [label_x, label_y],
                'size': 24
                }]
        elif get_flavour(key_name) == "SF":
            plot['labels'] += [{
                'text': '#mu#mu + ee channels',
                'position': [label_x, label_y],
                'size': 24
                }]
        elif get_flavour(key_name) == "All":
            plot['labels'] += [{
                'text': '#mu#mu + ee + #mue + e#mu channels',
                'position': [label_x, label_y],
                'size': 24
                }]


        # Finally, save what we have
        plots[key_name] = plot
        nHistos += 1

with open("allPlots.yml", "w") as f:
    yaml.dump(plots, f)

print "Saved configuration for {} plots in {}".format(nHistos, "allPlots.yml")
