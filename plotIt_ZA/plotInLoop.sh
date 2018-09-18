#!/bin/bash

for i in `seq 0 20`; do
    python listHistos.py -d ../factories_ZA/JECsplitting_rho_0_to_3/ -ell=$i --llbb
    #python listHistos.py -d ../factories_ZA/JECsplitting/ -ell=$i --llbb
    #python listHistos.py -d ../factories_ZA/plot_InOut_differentRhoSteps_systematic_updated_bugFixed/ -ell=$i --llbb
    ./plotIt.sh plots_signal_$i 
done
