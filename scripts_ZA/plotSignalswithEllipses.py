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
import cutWindow
from math import sqrt,atan,cos


def main():

    path = "/home/ucl/cp3/asaggio/scratch/CMSSW_8_0_30/src/cp3_llbb/ZATools/scripts_ZA/"
    signal_path = "/home/ucl/cp3/asaggio/scratch/CMSSW_8_0_30/src/cp3_llbb/ZATools/factories_ZA/myPlots_15_10_2017_mllCut/slurm/output/"

    window = cutWindow.massWindow(path+'ellipseParam.json')
    rho = 1.4

    totHisto = ROOT.TH2F("Signal", "mbb vs mllbb",60, 0, 1500, 60, 0, 1500)
    with open(path+'ellipseParam.json') as f1:
        parameters = json.load(f1)

        c = ROOT.TCanvas("c","ellipse pavement",500,500)
        c.hpx = ROOT.TH2F("hpx","mbb vs mllbb",60, 0, 1500, 60, 0, 1500);
        c.hpx.GetXaxis().SetTitle("mbb [GeV]")
        c.hpx.GetYaxis().SetTitle("mllbb [GeV]")
        c.hpx.Draw()
        c.e =[]

    i = 0
    for inputfile in os.listdir(signal_path):
        if inputfile.startswith("HToZA") and inputfile.endswith(".root"):
 
             #Get the simulated masses: MA and MH
            splitPath = inputfile.split('/')
            filename = splitPath[-1]
            #print filename
            splitFilename = filename.replace('_', '-').split('-')
            MH = int(splitFilename[2])
            MA = int(splitFilename[4])
            #print "MH: ", MH
            #print "MA: ", MA
            
            if MH > 1000:
                continue

            input = ROOT.TFile(signal_path+inputfile,"READ")
            histo2D = input.Get("Mjj_vs_Mlljj_MuMu_hZA_lljj_btagM_cmva_")

            #totHisto.Add(histo2D, 1)
            c.hpx.Add(histo2D, 1)

            for (mbb, mllbb, a, b, theta, mA, mH) in parameters:
                #print "mbb: ", mbb
                #print "mllbb: ", mllbb
                #print "a: ", a
                #print "b: ", b
                #print "theta: ", theta
                #print "mA: ", mA 
                #print "mH: ", mH

                if mA == MA and mH == MH:
                    x = mbb
                    y = mllbb
                    M11 = window.getValue(0,0, [x,y])
                    M12 = window.getValue(0,1, [x,y])
                    M22 = window.getValue(1,1, [x,y])
                    t = atan(M12/M11)
                    a = cos(t)/M11
                    b = cos(t)/M22
                    theta = t * 57.29   #conversion from radiants to degrees
                    #theta_deg = theta * 57.29   #conversion from radiants to degrees
                    ell = ROOT.TEllipse(x,y,rho*a,rho*b,0,360,theta)
                    ell.SetFillStyle(0)
                    ell.SetLineColor(ROOT.kRed)
                    ell.SetLineWidth(2)
                    c.e.append(ell)
                    c.e[i].Draw("same")
                    i = i+1

    #totHisto.SaveAs(path+"signalPlusEllipses.root")
    c.Update()
    c.Draw()
    c.SaveAs(path+"signalPlusEllipses.root")


if __name__ == "__main__":
    main()
