#! /bin/env python

import sys, os, json
import getopt
import copy
import datetime
import subprocess
import numpy as np
import glob
import ROOT

import argparse


#Compute ellipse parameters for primary map for signal files.

#NOTA BENE: MH,MA = SIMULATED MASSES
#           mllbb, mbb = RECONSTRUCTED MASSES

#def main(argv):
def main():

    path = "/home/ucl/cp3/asaggio/scratch/CMSSW_8_0_30/src/cp3_llbb/ZATools/scripts_ZA/"
    signal_path = "/home/ucl/cp3/asaggio/scratch/CMSSW_8_0_30/src/cp3_llbb/ZATools/factories_ZA/myPlots_15_10_2017_mllCut/slurm/output/"
    result = []
    sigmas = []

#    inputfileFromArg = ''
#    try:
#        opts, args = getopt.getopt(argv,"hi:",["ifile="])
#    except getopt.GetoptError:
#        print 'test.py -i <inputfileFromArg>'
#        sys.exit(2)
#    for opt, arg in opts:
#        if opt == '-h':
#            print 'test.py -i <inputfileFromArg> -o <outputfile>'
#            sys.exit()
#        elif opt in ("-i", "--ifile"):
#            inputfileFromArg = arg


    for inputfile in os.listdir(signal_path):
        if inputfile.startswith("HToZA") and inputfile.endswith(".root"):
           
             #Get the simulated masses: MA and MH
            splitPath = inputfile.split('/')
            filename = splitPath[-1]
            print filename
            splitFilename = filename.replace('_', '-').split('-')
            MH = int(splitFilename[2])
            MA = int(splitFilename[4])
            print "MH: ", MH
            print "MA: ", MA

            print str(signal_path+inputfile)
            input = ROOT.TFile(signal_path+inputfile,"READ")
            histo2D = input.Get("Mjj_vs_Mlljj_MuMu_hZA_lljj_btagM_cmva_")
            histo_mbb = input.Get("jj_M_MuMu_hZA_lljj_btagM_cmva_")
            histo_mllbb = input.Get("lljj_M_MuMu_hZA_lljj_btagM_cmva_")

            
            (mllbb, width_llbb, PVal1) = getMassAndWidth(histo_mllbb, MH)
            (mbb, width_bb, PVal2) = getMassAndWidth(histo_mbb, MA)
            print "mbb: ", mbb, " width_bb: ", width_bb, " PVal2: ", PVal2
            print "mllbb: ", mllbb, " width_llbb: ", width_llbb, " PVal1: ", PVal1

            (a, b, theta) = getEllipseParameters(histo2D)

            if MH <= 1000:
                result.append((mbb, mllbb, a, b, theta, MA, MH))
                sigmas.append((mbb, mllbb, width_bb, width_llbb))

    f = open(path+'ellipseParam.json', 'w')   # file containing the reconstructed and the simulated masses + the ellipse parameters
    json.dump(result, f)
    f.close()

    f1 = open(path+'sigmas.json', 'w')   # file containing the reconstructed masses and the respective sigmas
    json.dump(sigmas, f1)
    f1.close()


def getEllipseParameters(histo):

    NBrectangle=histo.GetEntries()

    # build the covariance matrix
    m = ROOT.TMatrixDSym(2)
    m[0,0] = histo.GetCovariance(1,1)
    m[1,1] = histo.GetCovariance(2,2)
    m[0,1] = histo.GetCovariance(1,2)
    m[1,0] = histo.GetCovariance(2,1)

    # compute eigen values and eigen vectors
    me = ROOT.TMatrixDSymEigen(m)
    eigenval = me.GetEigenValues()
    eigenvec = me.GetEigenVectors()

    # get the ellipses parameters
    a = eigenval[0]
    b = eigenval[1]
    theta = ROOT.TMath.ACos(eigenvec[0][0])
    
    # return the result
    return (a, b, theta)



def getMassAndWidth(massHisto, mass):

    # find the maximum and determine the window
    maximumBin = massHisto.GetMaximumBin()
    print "maximumBin: ", maximumBin
    massPeak   = massHisto.GetBinLowEdge(maximumBin)
    print "massPeak: ", massPeak
    maximum    = massHisto.GetMaximum()
    print "maximum: ", maximum
    halfWidth  = int(0.25*mass)
    print "halfWidth: ", halfWidth

    if maximumBin-halfWidth > 0:
        lowMassFit = massHisto.GetBinLowEdge(maximumBin-halfWidth)
    else:
        lowMassFit = massHisto.GetBinLowEdge(0)
    if maximumBin+halfWidth < massHisto.GetNbinsX():
        highMassFit = massHisto.GetBinLowEdge(maximumBin+halfWidth)
    else:
        highMassFit = massHisto.GetBinLowEdge(massHisto.GetNbinsX())

    print "lowMassFit: ", lowMassFit
    print "highMassFit: ", highMassFit
    # perform the fit
    result_fit = massHisto.Fit("gaus","S","",lowMassFit,highMassFit)	# print the parameters
    fit = massHisto.GetFunction("gaus")
    if result_fit.IsValid():
        chi2 = result_fit.Chi2()
        ndf = result_fit.Ndf()
        pvalue = ROOT.TMath.Prob(chi2,ndf)
        m_reco = fit.GetParameter(1)      #mu
        sigma = fit.GetParameter(2)       #sigma
    else:
        pvalue = -1
        m_reco = 0    
        sigma = 0

    # return the result
    return (m_reco, sigma, pvalue)



if __name__ == "__main__":
    #main(sys.argv[1:])
    main()


