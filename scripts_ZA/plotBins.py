#! /bin/env python

import sys, os, json
import getopt
import copy
import datetime
import subprocess
import numpy as np
import glob
import math
import ROOT
from ROOT import gStyle

sys.path.insert(0, '/home/ucl/cp3/asaggio/scratch/CMSSW_8_0_30/src/cp3_llbb/ZATools/scripts_ZA')

import argparse
from math import sqrt,atan,cos


def main():

    parser = argparse.ArgumentParser()
    parser.add_argument('-cat', '--category', required=True, help='Category of leptons (either MuMu or ElEl)')
    #parser.add_argument('-m', '--masspoint', required=True, help='Simulated mass point in the form [[MH1,MA1], [MH2,MA2], ...].')
    #parser.add_argument('-b', '--bin', required=True, help='Number of the bin in rho steps histogram you want to color. Bin=1 corresponds to rho=0, ... , bin=7 corresponds to the overflow.')
    args = parser.parse_args()
    print (args.category)

    path='/nfs/scratch/fynu/asaggio/CMSSW_8_0_30/src/cp3_llbb/ZATools/scripts_ZA/ellipsesScripts/'
    rhos = [0.5, 1., 1.5, 2, 2.5, 3, 3.5]
    with open(path+'ellipseParam_{0}.json'.format(args.category)) as f1:
        parameters = json.load(f1)

    gStyle.SetOptStat("")
    frame = ROOT.TFrame(0, 1500, 0, 6)
    frame.Draw()
    c = ROOT.TCanvas("c","ellipse pavement",500,500)
    c.SetCanvasSize(700,700)
    c.hpx = ROOT.TH2F("hpx","",60, 0, 1500, 60, 0, 1500)
    c.hpx.SetTitle("Category: {0}".format(args.category))
    c.hpx.GetXaxis().SetTitle("m_{bb} [GeV]")
    c.hpx.GetYaxis().SetTitle("m_{llbb} [GeV]")
    c.hpx.GetXaxis().SetLimits(0,1000)
    c.hpx.GetYaxis().SetLimits(0,1200)
    c.hpx.GetZaxis().SetLabelFont(22)
    c.hpx.Draw("same")
    c.legend = ROOT.TLegend(0.68,0.65,0.83,0.85)
    c.e = []
    c.h = []


    for (mbb, mllbb, a_squared, b_squared, theta_rad, mA, mH) in parameters:
        if args.category=='MuMu':
            if not (mA == 100 and mH == 800) and not (mA == 50 and mH == 1000):
                continue
        else:
            if not (mA == 50 and mH == 500) and not (mA == 50 and mH == 800) and not (mA == 200 and mH == 800) and not (mA == 200 and mH == 1000):
                continue
        x = mbb
        y = mllbb
        #input_massPoints = args.masspoint.split(',')
        #if not len(input_massPoints)%2==0:
        #    print "Error: odd number of mass points!"
        #    continue
        #for j in range(0,len(input_massPoints)):
        #    if j%2==0:
        #        input_mH=input_massPoints[j]
        #        input_mA=input_massPoints[j+1]
        #    print "input_mH: ", input_mH
        #    print "input_mA: ", input_mA
        #    if not (str(mH) == input_mH and str(mA) == input_mA):
        #        continue
        for i, rho in enumerate(rhos):
            a = math.sqrt(a_squared)
            b = math.sqrt(b_squared)
            theta = theta_rad * 57.29   #conversion from radiants to degrees
            ell = ROOT.TEllipse(x,y,rho*a,rho*b,0,360,theta)
            #if args.bin==i:
            #    ell.SetFillStyle(3001)
            #else:
            #    ell.SetFillStyle(0)
            if args.category=='MuMu':
                if mA == 100 and mH == 800:
                    colorBin=1
                elif mA == 50 and mH == 1000:
                    colorBin=1
                if i == colorBin-1:
                    print "rho is: ", rho
                    #ell.SetFillStyle(4050)
                    ell.SetFillColor(46)
                else:
                    ell.SetFillStyle(0)
                    ell.SetLineColor(ROOT.kBlack)
                    ell.SetLineWidth(1)
            else: #ElEl
                if mA == 50 and mH == 500:
                    colorBin=1
                elif mA == 50 and mH == 800:
                    colorBin=1
                elif mA == 200 and mH == 800:
                    colorBin=3 #means excess in 1,2,3rd bin
                elif mA == 200 and mH == 1000:
                    colorBin=2
                if i == colorBin-1:
                    ell.SetFillColor(46)
                else:
                    ell.SetFillStyle(0)
                    ell.SetLineColor(ROOT.kBlack)
                    ell.SetLineWidth(1)
            c.e.append(ell)
            c.legend.AddEntry(ell, "#rho = {0}".format(rho), "l")

    for i in range(len(c.e)):
        c.e[i].Draw("same")
    #c.legend.Draw("same")
 
    c.Update()
    c.Draw()
    c.SaveAs("ellipses_bins_{0}.root".format(args.category))

if __name__ == "__main__":
    main()
