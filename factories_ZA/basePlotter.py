import copy, sys, os
import numpy as np
import json

def get_scram_tool_info(tool, tag):
    import subprocess

    cmd = ['scram', 'tool', 'tag', tool, tag]

    return subprocess.check_output(cmd).strip()

def default_code_before_loop():
    return r"""
    massWindow window_MuMu("/home/ucl/cp3/asaggio/scratch/CMSSW_8_0_30/src/cp3_llbb/ZATools/scripts_ZA/ellipsesScripts/ellipseParam_MuMu.json");
    massWindow window_ElEl("/home/ucl/cp3/asaggio/scratch/CMSSW_8_0_30/src/cp3_llbb/ZATools/scripts_ZA/ellipsesScripts/ellipseParam_ElEl.json");
    """

def default_code_in_loop():
    return ""
    #return r"""
    #float gsf_err_lep1 = 0.;
    #if (hZA_leptons[hZA_lljj_deepCSV[0].ilep1].isEl) {
    #    if ((hZA_leptons[hZA_lljj_deepCSV[0].ilep1].p4.Pt() < 20.) || (hZA_leptons[hZA_lljj_deepCSV[0].ilep1].p4.Pt() > 80.) ) {
    #        gsf_err_lep1 = 0.01;
    #    }
    #}
    #if (hZA_leptons[hZA_lljj_cmva[0].ilep1].isEl) {
    #    if ((hZA_leptons[hZA_lljj_cmva[0].ilep1].p4.Pt() < 20.) || (hZA_leptons[hZA_lljj_cmva[0].ilep1].p4.Pt() > 80.) ) {
    #        gsf_err_lep1 = 0.01;
    #    }
    #}
    #else
    #    gsf_err_lep1 = 0;
    # 
    #float gsf_err_lep2 = 0.;
    #if (hZA_leptons[hZA_lljj_deepCSV[0].ilep2].isEl) {
    #    if ((hZA_leptons[hZA_lljj_deepCSV[0].ilep2].p4.Pt() < 20.) || (hZA_leptons[hZA_lljj_deepCSV[0].ilep2].p4.Pt() > 80.) ) {
    #        gsf_err_lep2 = 0.01;
    #    }
    #}
    #if (hZA_leptons[hZA_lljj_cmva[0].ilep2].isEl) {
    #    if ((hZA_leptons[hZA_lljj_cmva[0].ilep2].p4.Pt() < 20.) || (hZA_leptons[hZA_lljj_cmva[0].ilep2].p4.Pt() > 80.) ) {
    #        gsf_err_lep2 = 0.01;
    #    }
    #}
    #else
    #    gsf_err_lep2 = 0;

    #addTracking_err_lep1 = 0.;
    #if (hZA_leptons[hZA_lljj_deepCSV[0].ilep1].isMu) {
    #    addTracking_err_lep1 = 0.005;
    #}
    #if (hZA_leptons[hZA_lljj_cmva[0].ilep1].isMu) {
    #    addTracking_err_lep1= 0.005;
    #}
    #else
    #    addTracking_err_lep1 = 0;

    #addTracking_err_lep2 = 0.;
    #if (hZA_leptons[hZA_lljj_deepCSV[0].ilep2].isMu) {
    #    addTracking_err_lep2 = 0.005;
    #}
    #if (hZA_leptons[hZA_lljj_cmva[0].ilep2].isMu) {
    #    addTracking_err_lep2= 0.005;
    #}
    #else
    #    addTracking_err_lep2 = 0;

    #"""

def default_code_after_loop():
    return ""

def default_headers():
    return [
            "utils.h",
            "massWindow.h",
            ]

def default_include_directories(scriptDir):
    paths = [
            os.path.join(scriptDir, "..", "common", "include"),
            ]
    return paths

def default_sources(scriptDir):
    files = [
            "utils.cc",
            "massWindow.cc",
            ]
    files = [ os.path.join(scriptDir, "..", "common", "src", f) for f in files ]
    return files

def default_libraries():
    libs = []
    return libs

def default_library_directories():
    dirs = []
    return dirs


class BasePlotter:
    def __init__(self, btag, objects="nominal"):
        # systematic should be jecup, jecdown, jerup or jerdown. The one for lepton, btag, etc, have to be treated with the "weight" parameter in generatePlots.py (so far)

        self.baseObjectName_cmva = "hZA_lljj_cmva"
        self.baseObject_cmva = self.baseObjectName_cmva + "[0]"
        self.baseObjectName_deepCSV = "hZA_lljj_deepCSV"
        self.baseObject_deepCSV = self.baseObjectName_deepCSV + "[0]"
        self.btag = btag
        self.prefix = "hZA_"

        # For backwards compatibility with other tools:
        # FIXME: baseObjects to be modified in the next production
        if btag:
            self.baseObjectName = self.baseObjectName_deepCSV
            self.baseObject = self.baseObject_deepCSV
            self.suffix = self.baseObjectName + "" + ("_btagM")
        elif not btag:
            self.baseObjectName = self.baseObjectName_cmva
            self.baseObject = self.baseObject_cmva
            self.suffix = self.baseObjectName + "" + ("_nobtag")

        self.lep1_str = "hZA_leptons[%s.ilep1]" % self.baseObject
        self.lep2_str = "hZA_leptons[%s.ilep2]" % self.baseObject
        self.jet1_str = "hZA_jets[%s.ijet1]" % self.baseObject
        self.jet2_str = "hZA_jets[%s.ijet2]" % self.baseObject
        self.ll_str = "%s.ll_p4" % self.baseObject 
        self.jj_str = "%s.jj_p4" % self.baseObject
        self.met_str = "met_p4"
        self.metSig_str = "met_significance"
        self.jet_coll_str = "hZA_jets"
        self.lepton_coll_str = "hZA_leptons"
        self.sys_fwk = ""
        self.rho = 2.
        self.distances = [0.5, 1., 1.5, 2., 2.5, 3]


        if objects != "nominal":
            self.baseObjectName = self.baseObjectName.replace("hZA_", "hZA_" + objects + "_")
            self.baseObject = self.baseObject.replace("hZA_", "hZA_" + objects + "_")
            self.prefix += objects + "_"
            self.lep1_str = self.lep1_str.replace("hZA_", "hZA_" + objects + "_")
            self.lep2_str = self.lep2_str.replace("hZA_", "hZA_" + objects + "_")
            self.jet1_str = self.jet1_str.replace("hZA_", "hZA_" + objects + "_")
            self.jet2_str = self.jet2_str.replace("hZA_", "hZA_" + objects + "_")
            self.ll_str = self.ll_str.replace("hZA_", "hZA_" + objects + "_")
            self.jj_str = self.jj_str.replace("hZA_", "hZA_" + objects + "_")
            self.jet_coll_str = self.jet_coll_str.replace("hZA_", "hZA_" + objects + "_")
            self.lepton_coll_str = self.lepton_coll_str.replace("hZA_", "hZA_" + objects + "_")
            self.sys_fwk = "_" + objects
            self.met_str = "met_" + objects + "_p4"

        # needed to get scale factors (needs to be after the object modification due to systematics)
        self.lep1_fwkIdx = self.lep1_str + ".idx"
        self.lep2_fwkIdx = self.lep2_str + ".idx"
        self.jet1_fwkIdx = self.jet1_str + ".idx"
        self.jet2_fwkIdx = self.jet2_str + ".idx"

        # Ensure we have one candidate, works also for jecup etc
        self.sanityCheck = "Length$({}) > 0".format(self.baseObjectName)
        if self.btag:
            self.sanityCheck += " && {}.btag_deepCSV_MM".format(self.baseObject)

        # Categories (lepton flavours)
        self.dict_cat_cut =  {
            "ElEl": "({0}.isElEl && (runOnMC || (hZA_elel_fire_trigger_cut && runOnElEl)) && {1}.M() > 12)".format(self.baseObject, self.ll_str),
            "MuMu": "({0}.isMuMu && (runOnMC || (hZA_mumu_fire_trigger_cut && runOnMuMu)) && {1}.M() > 12)".format(self.baseObject, self.ll_str),
            "MuEl": "(({0}.isElMu || {0}.isMuEl) && (runOnMC || ((hZA_muel_fire_trigger_cut || hZA_elmu_fire_trigger_cut) && runOnElMu)) && {1}.M() > 12)".format(self.baseObject, self.ll_str)
                        }
        self.dict_cat_cut["SF"] = "(" + self.dict_cat_cut["ElEl"] + "||" + self.dict_cat_cut["MuMu"] + ")"
        self.dict_cat_cut["All"] = "(" + self.dict_cat_cut["ElEl"] + "||" + self.dict_cat_cut["MuMu"] + "||" + self.dict_cat_cut["MuEl"] + ")"

        # Possible stages (selection)
        mll_cut = "({0}.M() > 70) && ({0}.M() < 110)".format(self.ll_str, self.ll_str)
        met_cut = "({0}.Pt() > 0) && ({0}.Pt() < 80)".format(self.met_str, self.met_str)
        mbb_cut = "({0}.M() > 30)".format(self.jj_str)
        mll_and_met_cut = "({0} && {1})".format(mll_cut, met_cut)
        mll_and_met_cut_and_mbb_cut = "({0} && {1} && {2})".format(mll_cut, met_cut, mbb_cut)
        inverted_mll_cut = "({0}.M() <= 70 || {0}.M() >= 110)".format(self.ll_str, self.ll_str)
        inverted_met_cut = "({0}.Pt() >= 80)".format(self.met_str, self.met_str)
        inverted_mll_and_met_cut = "({0} && {1})".format(inverted_mll_cut, inverted_met_cut)
        met_cut_and_inverted_mll_cut = "({0} && {1})".format(inverted_mll_cut, met_cut)
        mll_cut_and_inverted_met_cut = "({0} && {1})".format(mll_cut, inverted_met_cut)
        
        self.dict_stage_cut = {
            "no_cut": "", 
            "mll_cut": mll_cut,
            "met_cut": met_cut,
            "mll_and_met_cut": mll_and_met_cut,
            "mll_and_met_cut_and_mbb_cut": mll_and_met_cut_and_mbb_cut,
            "inverted_mll_cut": inverted_mll_cut,
            "inverted_met_cut": inverted_met_cut,
            "inverted_mll_and_met_cut": inverted_mll_and_met_cut,
            "met_cut_and_inverted_mll_cut": met_cut_and_inverted_mll_cut,
            "mll_cut_and_inverted_met_cut": mll_cut_and_inverted_met_cut
        }


    def generatePlots(self, categories, stage, requested_plots, weights, systematic="nominal", extraString="", prependCuts=[], appendCuts=[], allowWeightedData=False): 

        # Protect against the fact that data do not have jecup collections, in the nominal case we still have to check that data have one candidate 
        sanityCheck = self.sanityCheck
        if systematic != "nominal" and not allowWeightedData:
            sanityCheck = self.joinCuts("!event_is_data", self.sanityCheck)

        cuts = self.joinCuts(*(prependCuts + [sanityCheck]))

        electron_1_id_cut = '({0}.isEl ? ( {0}.ele_hlt_id && !(std::abs({0}.p4.Eta()) > 1.444 && std::abs({0}.p4.Eta()) < 1.566) ) : 1)'.format(self.lep1_str)
        electron_2_id_cut = '({0}.isEl ? ( {0}.ele_hlt_id && !(std::abs({0}.p4.Eta()) > 1.444 && std::abs({0}.p4.Eta()) < 1.566) ) : 1)'.format(self.lep2_str)
        
        cuts = self.joinCuts(cuts, electron_1_id_cut, electron_2_id_cut)

        ###########
        # Weights #
        ###########

        # Lepton ID and Iso Scale Factors
        electron_id_branch = "electron_sf_id_mediumplushltsafe_hh"
        electron_reco_branch = "electron_sf_reco_moriond17"
        muon_tracking_branch = "muon_sf_tracking"
        muon_id_branch = "muon_sf_id_tight"
        muon_iso_branch = "muon_sf_iso_tight_id_tight"
        llIdIso_sf_dict = {
                "sf_lep1_el": "{id}[{0}][0] * {reco}[{0}][0]".format(self.lep1_fwkIdx, id=electron_id_branch, reco=electron_reco_branch),
                "sf_lep2_el": "{id}[{0}][0] * {reco}[{0}][0]".format(self.lep2_fwkIdx, id=electron_id_branch, reco=electron_reco_branch),
                "sf_lep1_mu": "{tracking}[{0}][0] * {id}[{0}][0] * {iso}[{0}][0]".format(self.lep1_fwkIdx, tracking=muon_tracking_branch, id=muon_id_branch, iso=muon_iso_branch),
                "sf_lep2_mu": "{tracking}[{0}][0] * {id}[{0}][0] * {iso}[{0}][0]".format(self.lep2_fwkIdx, tracking=muon_tracking_branch, id=muon_id_branch, iso=muon_iso_branch),
                "err_lep1_el": "0.",
                "err_lep1_mu": "0.",
                "err_lep2_el": "0.",
                "err_lep2_mu": "0.",
            }
        llIdIso_var = "NOMINAL"

        for sf in ["elidiso", "elreco", "mutracking", "muid", "muiso"]:
            if sf in systematic:
                if "up" in systematic:
                    llIdIso_var = "UP"
                    var_index = "2"
                elif "down" in systematic:
                    llIdIso_var = "DOWN"
                    var_index = "1"
                else:
                    raise Exception("Could not find up or down variation")

                if sf == "elidiso":
                    llIdIso_sf_dict["err_lep1_el"] = "{id}[{0}][{1}] * {reco}[{0}][0]".format(self.lep1_fwkIdx, var_index, id=electron_id_branch, reco=electron_reco_branch)
                    llIdIso_sf_dict["err_lep2_el"] = "{id}[{0}][{1}] * {reco}[{0}][0]".format(self.lep2_fwkIdx, var_index, id=electron_id_branch, reco=electron_reco_branch)

                if sf == "elreco": 
                    llIdIso_sf_dict["err_lep1_el"] = "({lep1}.isEl && (({lep1}.p4.Pt() < 20.) || ({lep1}.p4.Pt() > 80.))) ? ({id}[{0}][0] * std::sqrt({reco}[{0}][{1}] * {reco}[{0}][{1}] + 0.01*{reco}[{0}][{0}] * 0.01*{reco}[{0}][{0}])) : ({id}[{0}][0] * {reco}[{0}][{1}])".format(self.lep1_fwkIdx, var_index, id=electron_id_branch, reco=electron_reco_branch, lep1=self.lep1_str)
                    llIdIso_sf_dict["err_lep2_el"] = "({lep2}.isEl && (({lep2}.p4.Pt() < 20.) || ({lep2}.p4.Pt() > 80.))) ? ({id}[{0}][0] * std::sqrt({reco}[{0}][{1}] * {reco}[{0}][{1}] + 0.01*{reco}[{0}][{0}] * 0.01*{reco}[{0}][{0}])) : ({id}[{0}][0] * {reco}[{0}][{1}])".format(self.lep2_fwkIdx, var_index, id=electron_id_branch, reco=electron_reco_branch, lep2=self.lep2_str)

                if sf == "mutracking":
                    llIdIso_sf_dict["err_lep1_mu"] = "{lep1}.isMu ? (std::sqrt({tracking}[{0}][{1}] * {tracking}[{0}][{1}] + 0.005*{tracking}[{0}][{0}] * 0.005*{tracking}[{0}][{0}]) * {id}[{0}][0] * {iso}[{0}][0]) : ({tracking}[{0}][{1}] * {id}[{0}][0] * {iso}[{0}][0])".format(self.lep1_fwkIdx, var_index, tracking=muon_tracking_branch, id=muon_id_branch, iso=muon_iso_branch, lep1=self.lep1_str)
                    llIdIso_sf_dict["err_lep2_mu"] = "{lep2}.isMu ? (std::sqrt({tracking}[{0}][{1}] * {tracking}[{0}][{1}] + 0.005*{tracking}[{0}][{0}] * 0.005*{tracking}[{0}][{0}]) * {id}[{0}][0] * {iso}[{0}][0]) : ({tracking}[{0}][{1}] * {id}[{0}][0] * {iso}[{0}][0])".format(self.lep2_fwkIdx, var_index, tracking=muon_tracking_branch, id=muon_id_branch, iso=muon_iso_branch, lep2=self.lep2_str)

                if sf == "muid":
                    llIdIso_sf_dict["err_lep1_mu"] = "{tracking}[{0}][0] * {id}[{0}][{1}] * {iso}[{0}][0]".format(self.lep1_fwkIdx, var_index, tracking=muon_tracking_branch, id=muon_id_branch, iso=muon_iso_branch)
                    llIdIso_sf_dict["err_lep2_mu"] = "{tracking}[{0}][0] * {id}[{0}][{1}] * {iso}[{0}][0]".format(self.lep2_fwkIdx, var_index, tracking=muon_tracking_branch, id=muon_id_branch, iso=muon_iso_branch)

                if sf == "muiso":
                    llIdIso_sf_dict["err_lep1_mu"] = "{tracking}[{0}][0] * {id}[{0}][0] * {iso}[{0}][{1}]".format(self.lep1_fwkIdx, var_index, tracking=muon_tracking_branch, id=muon_id_branch, iso=muon_iso_branch)
                    llIdIso_sf_dict["err_lep2_mu"] = "{tracking}[{0}][0] * {id}[{0}][0] * {iso}[{0}][{1}]".format(self.lep2_fwkIdx, var_index, tracking=muon_tracking_branch, id=muon_id_branch, iso=muon_iso_branch)

        llIdIso_sf = """( common::combineScaleFactors<2>( {{ {{ 
                {{ 
                    ({lep1}.isEl) ? {sf_lep1_el} : {sf_lep1_mu},
                    ({lep1}.isEl) ? {err_lep1_el} : {err_lep1_mu}
                }},
                {{
                    ({lep2}.isEl) ? {sf_lep2_el} : {sf_lep2_mu},
                    ({lep2}.isEl) ? {err_lep2_el} : {err_lep2_mu}
                }}
            }} }}, common::Variation::{var} ) )""".format(lep1=self.lep1_str, lep2=self.lep2_str, var=llIdIso_var, **llIdIso_sf_dict)

        # BTAG SF, only applied if requesting b-tags
        if self.btag:
            jjBtag_light_sfIdx = "[0]"
            jjBtag_light_strCommon="NOMINAL"
            if systematic == "jjbtaglightup":
                jjBtag_light_sfIdx = "[2]" 
                jjBtag_light_strCommon="UP"
            if systematic == "jjbtaglightdown":
                jjBtag_light_sfIdx = "[1]"
                jjBtag_light_strCommon="DOWN"

            jjBtag_heavy_sfIdx = "[0]"
            jjBtag_heavy_strCommon="NOMINAL"
            if systematic == "jjbtagheavyup":
                jjBtag_heavy_sfIdx = "[2]" 
                jjBtag_heavy_strCommon="UP"
            if systematic == "jjbtagheavydown":
                jjBtag_heavy_sfIdx = "[1]"
                jjBtag_heavy_strCommon="DOWN"

            jjBtag_heavyjet_sf = "(common::combineScaleFactors<2>({{ {{ {{ jet{0}_sf_deepCSV_heavyjet_{1}[{2}][0] , jet{0}_sf_deepCSV_heavyjet_{1}[{2}]{3} }}, {{ jet{0}_sf_deepCSV_heavyjet_{1}[{4}][0], jet{0}_sf_deepCSV_heavyjet_{1}[{4}]{3} }} }} }}, common::Variation::{5}) )".format(self.sys_fwk, "medium", self.jet1_fwkIdx, jjBtag_heavy_sfIdx, self.jet2_fwkIdx, jjBtag_heavy_strCommon)

            jjBtag_lightjet_sf = "(common::combineScaleFactors<2>({{ {{ {{ jet{0}_sf_deepCSV_lightjet_{1}[{2}][0] , jet{0}_sf_deepCSV_lightjet_{1}[{2}]{3} }},{{ jet{0}_sf_deepCSV_lightjet_{1}[{4}][0], jet{0}_sf_deepCSV_lightjet_{1}[{4}]{3} }} }} }}, common::Variation::{5}) )".format(self.sys_fwk, "medium", self.jet1_fwkIdx, jjBtag_light_sfIdx, self.jet2_fwkIdx, jjBtag_light_strCommon)

        else:
            jjBtag_heavyjet_sf = "1."
            jjBtag_lightjet_sf = "1."

        # ZPt reweighting (only for DY)
        ptll_NLO = "{0}.ptllDYW_NLO".format(self.baseObject)

        # PU WEIGHT
        puWeight = "event_pu_weight"
        if systematic == "puup":
            puWeight = "event_pu_weight_up"
        if systematic == "pudown":
            puWeight = "event_pu_weight_down"

        # PDF, HDAMP weight
        pdfWeight = ""
        normalization = "nominal"
        for pdf in ["", "qq", "gg", "qg"]:
            for var in ["up", "down"]:
                if systematic == "pdf" + pdf + var:
                    _pdf = pdf + "_" if pdf != "" else ""
                    pdfWeight = "event_pdf_weight_" + _pdf + var
                    normalization = "pdf_" + _pdf + var
        for var in ["up", "down"]:
            if systematic == "hdamp" + var:
                pdfWeight = "event_hdamp_weight_" + var
                normalization = "hdamp_" + var

        # TRIGGER EFFICIENCY
        trigEff = "({0}.trigger_efficiency)".format(self.baseObject)
        if systematic == "trigeffup":
            trigEff = "({0}.trigger_efficiency_upVariated)".format(self.baseObject)
        if systematic == "trigeffdown":
            trigEff = "({0}.trigger_efficiency_downVariated)".format(self.baseObject)

        available_weights = {
                'trigeff': trigEff,
                'jjbtag_heavy': jjBtag_heavyjet_sf,
                'jjbtag_light': jjBtag_lightjet_sf,
                'llidiso': llIdIso_sf,
                'pu': puWeight
                }
        
        # Append the proper extension to the name plot if needed
        self.systematicString = ""
        if not systematic == "nominal":
            self.systematicString = "__" + systematic

        #########
        # PLOTS #
        #########
        self.basic_plot = []
        self.csv_plot = []
        self.isElEl_plot = []
        self.mjj_plot = []
 
        self.gen_plot = []
        self.evt_plot = []

        self.other_plot = []
        self.vertex_plot = []
        self.genht_plot = []
        self.inEllipse_plot = []
        self.outOfEllipse_plot = []
        self.inOut_plot = []

        self.forSkimmer_plot = []

        for cat in categories:

            catCut = self.dict_cat_cut[cat]
            self.totalCut = self.joinCuts(cuts, catCut, self.dict_stage_cut[stage], *appendCuts)
            self.cutWithoutCat = self.joinCuts(cuts, self.dict_stage_cut[stage], *appendCuts)

            self.llFlav = cat
            self.extraString = stage + extraString

            self.mjj_plot.append({
                        'name': 'jj_M_%s_%s_%s%s'%(self.llFlav, self.suffix, self.extraString, self.systematicString),
                        'variable': self.jj_str + ".M()",
                        'plot_cut': self.totalCut,
                        'binning': '(40, 10, 1000)'
                })

            # Plot to compute yields (ensure we have not over/under flow)
            #self.isElEl_plot.append({
            #            'name': 'isElEl_%s_%s_%s%s'%(self.llFlav, self.suffix, self.extraString, self.systematicString),
            #            'variable': "%s.isElEl"%self.baseObject,
            #            'plot_cut': self.totalCut,
            #            'binning': '(2, 0, 2)'
            #    })
            
            
            def get_jet_flavour_cut(flav, jet_idx):
                if flav == "g":
                    return "{jets}[{idx}].gen_l && jet{sys}_partonFlavor[{jets}[{idx}].idx] == 21".format(sys=self.sys_fwk, jets=self.jet_coll_str, idx=jet_idx)
                elif flav == "q":
                    return "{jets}[{idx}].gen_l && std::abs(jet{sys}_partonFlavor[{jets}[{idx}].idx]) >= 1 && std::abs(jet{sys}_partonFlavor[{jets}[{idx}].idx]) <= 3".format(sys=self.sys_fwk, jets=self.jet_coll_str, idx=jet_idx)
                elif flav == "n":
                    return "{jets}[{idx}].gen_l && jet{sys}_partonFlavor[{jets}[{idx}].idx] == 0".format(sys=self.sys_fwk, jets=self.jet_coll_str, idx=jet_idx)
                else:
                    return "{jets}[{idx}].gen_{flav}".format(jets=self.jet_coll_str, idx=jet_idx, flav=flav)
            
            mll_plot_binning = '(75, 12, 252)'


            # BASIC PLOTS
            self.basic_plot.extend([
                {
                        'name': 'Mjj_vs_Mlljj_%s_%s_%s%s'%(self.llFlav, self.suffix, self.extraString, self.systematicString),
                        'variable': self.jj_str + '.M() ::: '+self.baseObject + '.p4.M()',
                        'plot_cut': self.totalCut,
                        'binning': '(150, 0, 1500, 150, 0, 1500)'
                },
                {
                        'name': 'lep1_pt_%s_%s_%s%s'%(self.llFlav, self.suffix, self.extraString, self.systematicString),
                        'variable': self.lep1_str+".p4.Pt()",
                        'plot_cut': self.totalCut,
                        'binning': '(50, 20, 400)'
                },
                {
                        'name': 'lep2_pt_%s_%s_%s%s'%(self.llFlav, self.suffix, self.extraString, self.systematicString),
                        'variable': self.lep2_str+".p4.Pt()",
                        'plot_cut': self.totalCut,
                        'binning': '(50, 10, 200)'
                },
                {
                        'name': 'jet1_pt_%s_%s_%s%s'%(self.llFlav, self.suffix, self.extraString, self.systematicString),
                        'variable': self.jet1_str+".p4.Pt()",
                        'plot_cut': self.totalCut,
                        'binning': '(50, 20, 500)'
                },
                {
                        'name': 'jet2_pt_%s_%s_%s%s'%(self.llFlav, self.suffix, self.extraString, self.systematicString),
                        'variable': self.jet2_str+".p4.Pt()",
                        'plot_cut': self.totalCut,
                        'binning': '(50, 20, 300)'
                },
                {
                        'name': 'lep1_eta_%s_%s_%s%s'%(self.llFlav, self.suffix, self.extraString, self.systematicString),
                        'variable': self.lep1_str+".p4.Eta()",
                        'plot_cut': self.totalCut,
                        'binning': '(50, -4, 4)'
                },
                {
                        'name': 'lep2_eta_%s_%s_%s%s'%(self.llFlav, self.suffix, self.extraString, self.systematicString),
                        'variable': self.lep2_str+".p4.Eta()",
                        'plot_cut': self.totalCut,
                        'binning': '(50, -4, 4)'
                },
                {
                        'name': 'jet1_eta_%s_%s_%s%s'%(self.llFlav, self.suffix, self.extraString, self.systematicString),
                        'variable': self.jet1_str+".p4.Eta()",
                        'plot_cut': self.totalCut,
                        'binning': '(50, -4, 4)'
                },
                {
                        'name': 'jet2_eta_%s_%s_%s%s'%(self.llFlav, self.suffix, self.extraString, self.systematicString),
                        'variable': self.jet2_str+".p4.Eta()",
                        'plot_cut': self.totalCut,
                        'binning': '(50, -4, 4)'
                },
                {
                        'name': 'lep1_phi_%s_%s_%s%s'%(self.llFlav, self.suffix, self.extraString, self.systematicString),
                        'variable': self.lep1_str+".p4.Phi()",
                        'plot_cut': self.totalCut,
                        'binning': '(50, -4, 4)'
                },
                {
                        'name': 'lep2_phi_%s_%s_%s%s'%(self.llFlav, self.suffix, self.extraString, self.systematicString),
                        'variable': self.lep2_str+".p4.Phi()",
                        'plot_cut': self.totalCut,
                        'binning': '(50, -4, 4)'
                },
                {
                        'name': 'jet1_phi_%s_%s_%s%s'%(self.llFlav, self.suffix, self.extraString, self.systematicString),
                        'variable': self.jet1_str+".p4.Phi()",
                        'plot_cut': self.totalCut,
                        'binning': '(50, -4, 4)'
                },
                {
                        'name': 'jet2_phi_%s_%s_%s%s'%(self.llFlav, self.suffix, self.extraString, self.systematicString),
                        'variable': self.jet2_str+".p4.Phi()",
                        'plot_cut': self.totalCut,
                        'binning': '(50, -4, 4)'
                },
                {
                        'name': 'lljj_M_%s_%s_%s%s'%(self.llFlav, self.suffix, self.extraString, self.systematicString),
                        'variable': self.baseObject+".p4.M()",
                        'plot_cut': self.totalCut,
                        'binning': '(50, 100, 1500)'
                },
                {
                        'name': 'llbb_M_%s_%s_%s%s'%(self.llFlav, self.suffix, self.extraString, self.systematicString),
                        'variable': "(" + self.ll_str + "+" + self.jj_str + ").M()",
                        'plot_cut': self.totalCut,
                        'binning': '(50, 100, 1500)'
                },
                {
                        'name': 'll_M_%s_%s_%s%s'%(self.llFlav, self.suffix, self.extraString, self.systematicString),
                        'variable': self.ll_str+".M()",
                        'plot_cut': self.totalCut,
                        'binning': mll_plot_binning
                },
                {
                        'name': 'll_DR_l_l_%s_%s_%s%s'%(self.llFlav, self.suffix, self.extraString, self.systematicString),
                        'variable': self.baseObject+".DR_l_l",
                        'plot_cut': self.totalCut,
                        'binning': '(50, 0, 6)'
                },
                {
                        'name': 'jj_DR_j_j_%s_%s_%s%s'%(self.llFlav, self.suffix, self.extraString, self.systematicString),
                        'variable': self.baseObject+".DR_j_j",
                        'plot_cut': self.totalCut,
                        'binning': '(50, 0, 6)'
                },
                {
                        'name': 'll_pt_%s_%s_%s%s'%(self.llFlav, self.suffix, self.extraString, self.systematicString),
                        'variable': self.ll_str+".Pt()",
                        'plot_cut': self.totalCut,
                        'binning': '(50, 0, 450)'
                },
                {
                        'name': 'jj_pt_%s_%s_%s%s'%(self.llFlav, self.suffix, self.extraString, self.systematicString),
                        'variable': self.jj_str+".Pt()",
                        'plot_cut': self.totalCut,
                        'binning': '(50, 0, 450)'
                },
                {
                        'name': 'll_DPhi_l_l_%s_%s_%s%s'%(self.llFlav, self.suffix, self.extraString, self.systematicString),
                        'variable': "abs("+self.baseObject+".DPhi_l_l)",
                        'plot_cut': self.totalCut,
                        'binning': '(50, 0, 3.1416)'
                },
                {
                        'name': 'jj_DPhi_j_j_%s_%s_%s%s'%(self.llFlav, self.suffix, self.extraString, self.systematicString),
                        'variable': "abs("+self.baseObject+".DPhi_j_j)",
                        'plot_cut': self.totalCut,
                        'binning': '(50, 0, 3.1416)'
                },
                {
                        'name': 'met_pt_%s_%s_%s%s'%(self.llFlav, self.suffix, self.extraString, self.systematicString),
                        'variable': self.met_str + ".Pt()",
                        'plot_cut': self.totalCut,
                        'binning': '(50, 0, 500)'
                },
                #{
                #        'name': 'met_E_%s_%s_%s%s'%(self.llFlav, self.suffix, self.extraString, self.systematicString),
                #        'variable': self.met_str + ".E()",
                #        'plot_cut': self.totalCut,
                #        'binning': '(50, 0, 500)'
                #},
                {
                        'name': 'met_significance_%s_%s_%s%s'%(self.llFlav, self.suffix, self.extraString, self.systematicString),
                        'variable': self.metSig_str,
                        'plot_cut': self.totalCut,
                        'binning': '(300, 0, 500)'
                }
            ])
                

            if self.btag:
                self.basic_plot.extend([
                    {
                            'name': 'jet1_deepCSV_%s_%s_%s%s'%(self.llFlav, self.suffix, self.extraString, self.systematicString),
                            'variable': self.jet1_str+".deepCSV",
                            'plot_cut': self.totalCut,
                            'binning': '(50, -1, 1)'
                    },
                    {
                            'name': 'jet2_deepCSV_%s_%s_%s%s'%(self.llFlav, self.suffix, self.extraString, self.systematicString),
                            'variable': self.jet2_str+".deepCSV",
                            'plot_cut': self.totalCut,
                            'binning': '(50, -1, 1)'
                    },
                    {
                            'name': 'jj_deepCSV_%s_%s_%s%s'%(self.llFlav, self.suffix, self.extraString, self.systematicString),
                            'variable': self.baseObject+".sumDeepCSV",
                            'plot_cut': self.totalCut,
                            'binning': '(50, -2, 2)'
                    },
                    {
                            'name': 'jet1_deepCSV_M_%s_%s_%s%s'%(self.llFlav, self.suffix, self.extraString, self.systematicString),
                            'variable': self.jet1_str+".btag_deepCSV_M",
                            'plot_cut': self.totalCut,
                            'binning': '(50, -1, 1)'
                    },
                    {
                            'name': 'jj_deepCSV_MM_%s_%s_%s%s'%(self.llFlav, self.suffix, self.extraString, self.systematicString),
                            'variable': self.baseObject+".btag_deepCSV_MM",
                            'plot_cut': self.totalCut,
                            'binning': '(50, -1, 1)'
                    }
                ])


            self.csv_plot.extend([
                {
                        'name': 'jet1_CSV_%s_%s_%s%s'%(self.llFlav, self.suffix, self.extraString, self.systematicString),
                        'variable': self.jet1_str+".CSV",
                        'plot_cut': self.totalCut,
                        'binning': '(50, 0, 1)'
                },
                {
                        'name': 'jet2_CSV_%s_%s_%s%s'%(self.llFlav, self.suffix, self.extraString, self.systematicString),
                        'variable': self.jet2_str+".CSV",
                        'plot_cut': self.totalCut,
                        'binning': '(50, 0, 1)'
                }
            ])

            #PLOTS IN ELLIPSE
            if cat=='MuEl':  #Load the MuMu file for the MuEl category
                with open('/home/ucl/cp3/asaggio/scratch/CMSSW_8_0_30/src/cp3_llbb/ZATools/scripts_ZA/ellipsesScripts/ellipseParam_ElEl.json') as f:
                    parameters = json.load(f)
            else:
                with open('/home/ucl/cp3/asaggio/scratch/CMSSW_8_0_30/src/cp3_llbb/ZATools/scripts_ZA/ellipsesScripts/ellipseParam_{0}.json'.format(cat)) as f:
                    parameters = json.load(f)
            for j, line in enumerate(parameters):
                if cat=='MuEl':
                    inWindowCut = "window_ElEl.isInEllipse({1}, {2}, {3}, {4})".format(float(line[0]), float(line[1]), self.rho, self.jj_str + ".M()", self.baseObject + ".p4.M()")
                else:
                    inWindowCut = "window_{0}.isInEllipse({1}, {2}, {3}, {4}, {5})".format(cat, float(line[0]), float(line[1]), self.rho, self.jj_str + ".M()", self.baseObject + ".p4.M()")
                self.ellCut = self.joinCuts(self.cutWithoutCat, self.dict_cat_cut[cat], inWindowCut)
                self.tempExtraString = "_inEllipse_{0}".format(j) #Labelling each of the 21 ellipses with its index. Will need to write down which ellipse corresponds to which index.
                self.ellExtraString = self.extraString + self.tempExtraString
                self.tempExtraStringForInOut =  "_{0}".format(j)
                self.extraStringForInOut = self.extraString + self.tempExtraStringForInOut

                self.inEllipse_plot.extend([
                    {
                        'name': 'll_M_%s_%s_%s%s'%(self.llFlav, self.suffix, self.ellExtraString, self.systematicString),
                        'variable': self.ll_str+".M()",
                        'plot_cut': self.ellCut,
                        'binning': mll_plot_binning
                    },
                    {
                        'name': 'Mjj_vs_Mlljj_%s_%s_%s%s'%(self.llFlav, self.suffix, self.ellExtraString, self.systematicString),
                        'variable': self.jj_str + '.M() ::: '+self.baseObject + '.p4.M()',
                        'plot_cut': self.ellCut,
                        'binning': '(150, 0, 1500, 150, 0, 1500)'
                    },
                    {
                        'name': 'jj_M_%s_%s_%s%s'%(self.llFlav, self.suffix, self.ellExtraString, self.systematicString),
                        'variable': self.jj_str + ".M()",
                        'plot_cut': self.ellCut,
                        'binning': '(40, 10, 1000)'
                    },
                    {
                        'name': 'lljj_M_%s_%s_%s%s'%(self.llFlav, self.suffix, self.ellExtraString, self.systematicString),
                        'variable': self.baseObject+".p4.M()",
                        'plot_cut': self.ellCut,
                        'binning': '(50, 100, 1500)'
                    }
            ])

                self.inOut_plot.extend([
                    {
                        'name': 'rho_steps_histo_%s_%s_%s%s'%(self.llFlav, self.suffix, self.extraStringForInOut, self.systematicString),
                        'variable': "window_{0}.isInEllipse_noSize({1}, {2}, {3}, {4})".format((cat if cat!='MuEl' else 'ElEl'), line[0], line[1], self.jj_str + ".M()", self.baseObject + ".p4.M()"),
                        'plot_cut': self.totalCut,
                        'binning': '(6, 0, 3)'
                    }
            ])
            '''
                for i, dist in enumerate(self.distances):
                    #after these histos are filled, take only the true bin and put the together
                    if i==0:
                        self.inOut_plot.extend([
                                {
                                    'name': 'isInOrOut_%s_%s_%s_%s%s'%(dist, self.llFlav, self.suffix, self.extraStringForInOut, self.systematicString),
                                    'variable': "window_{0}.isInEllipse({1}, {2}, {3}, {4}, {5})".format(cat, line[0], line[1], dist, self.jj_str + ".M()", self.baseObject + ".p4.M()"),
                                    'plot_cut': self.totalCut,
                                    'binning': '(2, 0, 2)'
                                }
                    ])
                    else:
                        self.inOut_plot.extend([
                                {
                                    'name': 'isInOrOut_%s_%s_%s_%s%s'%(dist, self.llFlav, self.suffix, self.extraStringForInOut, self.systematicString),
                                    'variable': "window_{0}.isInEllipse({1}, {2}, {3}, {4}, {5})".format(cat, line[0], line[1], dist, self.jj_str + ".M()", self.baseObject + ".p4.M()") + " && " + "!(window_{0}.isInEllipse({1}, {2}, {3}, {4}, {5}))".format(cat, line[0], line[1], self.distances[i-1], self.jj_str + ".M()", self.baseObject + ".p4.M()"),
                                    'plot_cut': self.totalCut,
                                    'binning': '(2, 0, 2)'
                                }
                    ])
                    
                self.inOut_plot.extend([
                        {
                            'name': 'overFlow_%s_%s_%s_%s%s'%(self.distances[-1], self.llFlav, self.suffix, self.extraStringForInOut, self.systematicString),
                            'variable': "window_{0}.isOutOfEllipse({1}, {2}, {3}, {4}, {5})".format(cat, line[0], line[1], self.distances[-1], self.jj_str + ".M()", self.baseObject + ".p4.M()"),
                            'plot_cut': self.totalCut,
                            'binning': '(2, 0, 2)'
                        }
                ])
            '''

            #PLOTS OUT OF ELLIPSE
            if cat=='MuEl':
                with open('/home/ucl/cp3/asaggio/scratch/CMSSW_8_0_30/src/cp3_llbb/ZATools/scripts_ZA/ellipsesScripts/ellipseParam_ElEl.json'.format(cat)) as f:
                    parameters = json.load(f)
            else:
                with open('/home/ucl/cp3/asaggio/scratch/CMSSW_8_0_30/src/cp3_llbb/ZATools/scripts_ZA/ellipsesScripts/ellipseParam_{0}.json'.format(cat)) as f:
                    parameters = json.load(f)
            for j, line in enumerate(parameters):
                if cat=='MuEl':
                    notInWindowCut = "window_ElEl.isOutOfEllipse({1}, {2}, {3}, {4})".format(line[0], line[1], self.rho, self.jj_str + ".M()", self.baseObject + ".p4.M()")
                else:
                    notInWindowCut = "window_{0}.isOutOfEllipse({1}, {2}, {3}, {4}, {5})".format(cat, line[0], line[1], self.rho, self.jj_str + ".M()", self.baseObject + ".p4.M()")
                self.outOfEllCut = self.joinCuts(self.cutWithoutCat, self.dict_cat_cut[cat], notInWindowCut)
                self.tempExtraString = "_outOfEllipse_{0}".format(j) #Labelling each of the 21 ellipses with its index. Will need to write down which ellipse corresponds to which index.
                self.ellExtraString = self.extraString + self.tempExtraString
                self.outOfEllipse_plot.extend([
                    {
                        'name': 'll_M_%s_%s_%s%s'%(self.llFlav, self.suffix, self.ellExtraString, self.systematicString),
                        'variable': self.ll_str+".M()",
                        'plot_cut': self.outOfEllCut,
                        'binning': mll_plot_binning
                    },
                    {
                        'name': 'Mjj_vs_Mlljj_%s_%s_%s%s'%(self.llFlav, self.suffix, self.ellExtraString, self.systematicString),
                        'variable': self.jj_str + '.M() ::: '+self.baseObject + '.p4.M()',
                        'plot_cut': self.outOfEllCut,
                        'binning': '(150, 0, 1500, 150, 0, 1500)'
                    },
                    {
                        'name': 'jj_M_%s_%s_%s%s'%(self.llFlav, self.suffix, self.ellExtraString, self.systematicString),
                        'variable': self.jj_str + ".M()",
                        'plot_cut': self.outOfEllCut,
                        'binning': '(40, 10, 1000)'
                    },
                    {
                        'name': 'lljj_M_%s_%s_%s%s'%(self.llFlav, self.suffix, self.ellExtraString, self.systematicString),
                        'variable': self.baseObject+".p4.M()",
                        'plot_cut': self.outOfEllCut,
                        'binning': '(50, 100, 1500)'
                    }
                ])

            # gen level plots for jj 
            #for elt in self.plots_jj:
            #    tempPlot = copy.deepcopy(elt)
            #    if "p4" in tempPlot["variable"]:
            #        tempPlot["variable"] = tempPlot["variable"].replace(self.jj_str,"hZA_gen_BB")
            #        tempPlot["name"] = "gen"+tempPlot["name"]
            #        self.plots_gen.append(tempPlot)
            
            #self.gen_plot.extend([
            #    {
            #        'name': 'gen_mZA',
            #        'variable': 'hZA_gen_mZA',
            #        'plot_cut': self.totalCut,
            #        'binning': '(50, 0, 1200)'
            #    },
            #])

        plotsToReturn = []
        
        for plotFamily in requested_plots:
            
            #if "scaleUncorr" in systematic or "dyScale" in systematic:
            if "scaleUncorr" in systematic:

                # will fail if we can't find the scale index
                scaleIndex = str(int(systematic[-1]))
                
                scaleWeight = "event_scale_weights[%s]" % scaleIndex
                
                for plot in getattr(self, plotFamily + "_plot"):
                    # Two different ways to normalise the variations
                    if "Uncorr" not in systematic:
                        # The normalisation is never applied on data, so we're safe even when applying DY reweighting
                        plot["normalize-to"] = "scale_%s" % scaleIndex
                    if not "Weight" in plotFamily:
                        # Be careful to use 1 for data when applying DY reweighting
                        plot["weight"] = "event_weight" + " * (runOnMC ? " + scaleWeight + " : 1. )"
                        for weight in weights:
                            plot["weight"] += " * " + available_weights[weight] + " * " + ptll_NLO
                    else:
                        print "No other weight than event_weight for ", plotFamily 
                    plotsToReturn.append(plot)
                
            elif "pdf" in systematic:
                
                for plot in getattr(self, plotFamily + "_plot"):
                    if not "Weight" in plotFamily:
                        # Be careful to use 1 for data when applying DY reweighting
                        plot["weight"] = "event_weight" + " * (runOnMC ? " + pdfWeight + " : 1.)"
                        # The normalisation is never applied on data, so we're safe even when applying DY reweighting
                        plot["normalize-to"] = normalization
                        for weight in weights:
                            plot["weight"] += " * " + available_weights[weight] + " * " + ptll_NLO
                    else:
                        print "No other weight than event_weight for ", plotFamily 
                    plotsToReturn.append(plot)
            
            else:
                
                for plot in getattr(self, plotFamily + "_plot"):
                    if not "Weight" in plotFamily and "sample_weight" not in plot["name"]:
                        plot["weight"] = "event_weight"
                        # The normalisation is never applied on data, so we're safe even when applying DY reweighting
                        plot["normalize-to"] = normalization
                        for weight in weights:
                            plot["weight"] += " * " + available_weights[weight] + " * " + ptll_NLO
                    else:
                        # Divide by sample_weight since we cannot avoid it in histFactory
                        plot["weight"] = "event_weight/__sample_weight"
                        print "No other weight than event_weight for ", plotFamily 
                    plotsToReturn.append(plot)

        # If requested, do NOT force weights to 1 for data
        if allowWeightedData:
            for plot in plotsToReturn:
                plot["allow-weighted-data"] = True

        # Remove possible duplicates (same name => they would be overwritten when saving the output file anyway)
        cleanedPlotList = []
        checkedNames = []
        for p in plotsToReturn:
            if p["name"] not in checkedNames:
                checkedNames.append(p["name"])
                cleanedPlotList.append(p)
        if len(plotsToReturn) - len(cleanedPlotList) < 0:
            print("Warning: removed {} duplicate plots!".format(-len(plotsToReturn) + len(cleanedPlotList)))

        return cleanedPlotList


    def joinCuts(self, *cuts):
        if len(cuts) == 0:
            return ""
        elif len(cuts) == 1:
            return cuts[0]
        else:
            totalCut = "("
            for cut in cuts:
                cut = cut.strip().strip("&")
                if cut == "":
                    continue
                totalCut += "(" + cut + ")&&" 
            totalCut = totalCut.strip("&") + ")"
            return totalCut

