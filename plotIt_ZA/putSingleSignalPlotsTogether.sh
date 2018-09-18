#!/bin/bash

folder=finalPlots_rhoSteps_singleSignals_rho0to3_blinded
mkdir $folder
for i in `seq 0 20`; do
    cp ./*_plots_signal_${i}/rho_steps_histo_ElEl_hZA_lljj_deepCSV_btagM_mll_and_met_cut_${i}.pdf $folder
    cp ./*_plots_signal_${i}/rho_steps_histo_ElEl_hZA_lljj_deepCSV_btagM_mll_and_met_cut_${i}.png $folder 
    cp ./*_plots_signal_${i}/rho_steps_histo_ElEl_hZA_lljj_deepCSV_btagM_mll_and_met_cut_${i}_logy.pdf $folder 
    cp ./*_plots_signal_${i}/rho_steps_histo_ElEl_hZA_lljj_deepCSV_btagM_mll_and_met_cut_${i}_logy.png $folder 
    cp ./*_plots_signal_${i}/rho_steps_histo_MuMu_hZA_lljj_deepCSV_btagM_mll_and_met_cut_${i}.pdf $folder 
    cp ./*_plots_signal_${i}/rho_steps_histo_MuMu_hZA_lljj_deepCSV_btagM_mll_and_met_cut_${i}.png $folder 
    cp ./*_plots_signal_${i}/rho_steps_histo_MuMu_hZA_lljj_deepCSV_btagM_mll_and_met_cut_${i}_logy.pdf $folder 
    cp ./*_plots_signal_${i}/rho_steps_histo_MuMu_hZA_lljj_deepCSV_btagM_mll_and_met_cut_${i}_logy.png $folder 
    cp ./*_plots_signal_${i}/rho_steps_histo_MuEl_hZA_lljj_deepCSV_btagM_mll_and_met_cut_${i}.pdf $folder 
    cp ./*_plots_signal_${i}/rho_steps_histo_MuEl_hZA_lljj_deepCSV_btagM_mll_and_met_cut_${i}.png $folder 
    cp ./*_plots_signal_${i}/rho_steps_histo_MuEl_hZA_lljj_deepCSV_btagM_mll_and_met_cut_${i}_logy.pdf $folder 
    cp ./*_plots_signal_${i}/rho_steps_histo_MuEl_hZA_lljj_deepCSV_btagM_mll_and_met_cut_${i}_logy.png $folder 
done
