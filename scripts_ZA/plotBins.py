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

    categories = ['MuMu', 'ElEl']

    path='/nfs/scratch/fynu/asaggio/CMSSW_8_0_30/src/cp3_llbb/ZATools/scripts_ZA/ellipsesScripts/'
    rhos = [0.5, 1., 1.5, 2, 2.5, 3]



    for cat in categories:
        with open(path+'ellipseParam_{0}.json'.format(cat)) as f1:
            parameters = json.load(f1)
        

        for (mbb, mllbb, a_squared, b_squared, theta_rad, mA, mH) in parameters:
            x = mbb
            y = mllbb
        
            gStyle.SetOptStat("")
            frame = ROOT.TFrame(0, 1500, 0, 6)
            frame.Draw()
            c = ROOT.TCanvas("c","ellipse pavement",500,500)
            c.SetCanvasSize(700,700)
            c.hpx = ROOT.TH2F("hpx","",60, 0, 1500, 60, 0, 1500)
            c.hpx.SetTitle("Category: {0}".format(cat))
            c.hpx.GetXaxis().SetTitle("m_{bb} [GeV]")
            c.hpx.GetYaxis().SetTitle("m_{llbb} [GeV]")
            c.hpx.GetXaxis().SetLimits(0,1000)
            c.hpx.GetYaxis().SetLimits(0,1200)
            c.hpx.GetZaxis().SetLabelFont(22)
            c.hpx.Draw("same")
            c.legend = ROOT.TLegend(0.68,0.65,0.83,0.85)
            c.e = []
            c.h = []
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
                ell.SetFillStyle(0)
                ell.SetLineColor(ROOT.kBlack)
                ell.SetLineWidth(1)
                c.e.append(ell)
                c.legend.AddEntry(ell, "#rho = {0}".format(rho), "l")
                c.Update()

            for i in range(len(rhos)):
                c.e[i].Draw("same")
            c.SaveAs("ellipses_plotted/ell_{0}_{1}_{2}.png".format(mH,mA,cat))
        #c.legend.Draw("same")
            del c.hpx
            del c.e
            del c
     
        #c.Update()
        #c.Draw()
        #c.SaveAs("ellipses_bins_{0}.root".format(args.category))

if __name__ == "__main__":
    main()
