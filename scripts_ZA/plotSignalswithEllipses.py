#! /bin/env python

import sys, os, json
import getopt
import copy
import datetime
import subprocess
import numpy as np
import glob
import ROOT
from ROOT import gStyle

import argparse
import cutWindow
from math import sqrt,atan,cos


def main():

    path = "/home/ucl/cp3/asaggio/scratch/CMSSW_8_0_30/src/cp3_llbb/ZATools/scripts_ZA/"
    signal_path = "/home/ucl/cp3/asaggio/scratch/CMSSW_8_0_30/src/cp3_llbb/ZATools/factories_ZA/myPlots_15_10_2017_mllCut/slurm/output/"

    window = cutWindow.massWindow(path+'ellipseParam.json')
    rho = 2.1

    totHisto = ROOT.TH2F("Signal", "", 60, 0, 1500, 60, 0, 1500)
    with open(path+'ellipseParam.json') as f1:
        parameters = json.load(f1)

        gStyle.SetOptStat("")
        c = ROOT.TCanvas("c","ellipse pavement",500,500)
        c.hpx = ROOT.TH2F("hpx","",60, 0, 1500, 60, 0, 1500);
        c.hpx.GetXaxis().SetTitle("m_{bb} [GeV]")
        c.hpx.GetYaxis().SetTitle("m_{llbb} [GeV]")
        c.hpx.Draw()
        c.e = []
        c.h = []

    i = 0
    j = 0
    second = third = False
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
            
            #if MH > 1000:
            #    continue

            if (MA==500 and MH==1000) or (MA==100 and MH==300) or (MA==200 and MH==800):

                #input = ROOT.TFile(signal_path+inputfile,"READ")
                #histo2D = input.Get("Mjj_vs_Mlljj_MuMu_hZA_lljj_btagM_cmva_")

                if MA==100 and MH==300:
                    input_1 = ROOT.TFile(signal_path+inputfile,"READ")
                    histo2D_1 = input_1.Get("Mjj_vs_Mlljj_MuMu_hZA_lljj_btagM_cmva_")
                    histo2D_1.SetMarkerColor(9)
                
                elif MA==200 and MH==800:
                    second=True
                    input_2 = ROOT.TFile(signal_path+inputfile,"READ")
                    histo2D_2 = input_2.Get("Mjj_vs_Mlljj_MuMu_hZA_lljj_btagM_cmva_")
                    histo2D_2.SetMarkerColor(30)
                    histo2D_2.Draw("same")

                elif MA==500 and MH==1000:
                    third=True
                    input_3 = ROOT.TFile(signal_path+inputfile,"READ")
                    histo2D_3 = input_3.Get("Mjj_vs_Mlljj_MuMu_hZA_lljj_btagM_cmva_")
                    histo2D_3.SetMarkerColor(46)
                    histo2D_3.Draw("same")
                
                if second and third:
                    histo2D_1.Draw("same")

                
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
                        ell = ROOT.TEllipse(x,y,rho*a,rho*b,0,360,theta)
                        ell.SetFillStyle(0)
                        #ell.SetLineColor(ROOT.kRed)
                        ell.SetLineColor(i*2+2)
                        ell.SetLineWidth(2)
                        c.e.append(ell)
                        #c.e[i].Draw("same")
                        print i
                        i = i+1

    for i in range(len(c.e)):
        c.e[i].Draw("same")
        
    #totHisto.SaveAs(path+"signalPlusEllipses.root")
    c.Update()
    c.Draw()
    c.SaveAs(path+"signalPlusEllipses.root")

if __name__ == "__main__":
    main()
