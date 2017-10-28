#! /bin/env python

from math import sqrt,atan,cos
import ROOT
from array import array
import json
import sys
import os
import cutWindow

# Global parameters
rho    = 2
step_x   = 1.
step_y   = 1.
filename  = "/nfs/scratch/fynu/asaggio/CMSSW_8_0_30/src/cp3_llbb/ZATools/scripts_ZA/ellipseParam.json"
sigma_file = "/nfs/scratch/fynu/asaggio/CMSSW_8_0_30/src/cp3_llbb/ZATools/scripts_ZA/sigmas.json"


def Points():
    points = []

    #load sigma parameters
    with open(sigma_file) as f1:
        data = json.load(f1)
    sigx = ROOT.TGraph2D(len(data))
    sigy = ROOT.TGraph2D(len(data))

    for i,s in enumerate(data):
        if float(s[0]) == 0 or float(s[1]) == 0: continue
        print s[0], s[1], s[2]/s[0], s[3]/s[1]
        sigx.SetPoint(i,s[0],s[1],float(s[2])/float(s[0]))  #mbb, mllbb, res_bb=sigma_bb/mbb
        sigy.SetPoint(i,s[0],s[1],float(s[3])/float(s[1]))  #mbb, mllbb, res_llbb=sigma_llbb/mllbb

    # Creation of the pavement
    mA = 30
    mH = 120
    sigmaY = 0.1
    sigmaX = 0.1
    while mH < 1000:
        while mA < mH-50:
            points.append((mA,mH))
            #sigmaX = 0.2
            sigmaX = sigx.Interpolate(mA,mH)
            if sigmaX == 0:
                print 'error x'
                distance =1000
                for (m1,m2,s1,s2) in data:
                    if m1 == 0 or m2 == 0: continue
                    d = sqrt((m1-mA)**2+(m2-mH)**2)
                    if d < distance:
                        distance = d
                        sigmaX = s1/m1
            print "sX = %i"%sigmaX
            mA = mA*(1+sigmaX*step_x) 
            #sigmaY = 0.2
            sigmaY = sigy.Interpolate(mA,mH)
            if sigmaY == 0:
                print 'error y'
                distance =1000
                for (m1,m2,s1,s2) in data:
                    if m1 == 0 or m2 == 0: continue
                    d = sqrt((m1-mA)**2+(m2-mH)**2)
                    if d < distance:
                        distance = d
                        sigmaY = s2/m2
            print "sY %f"%sigmaY
        mH = mH*(1+sigmaY*step_y) 
        mA = 30

    # Save points
    f2 = open('points_%f_%f.json'%(round(step_x, 1), round(step_y, 1)),'w')
    json.dump(points,f2)
    f2.close()
    return points

# control plots: draw the centers
def Control(points):
    canvas = ROOT.TCanvas("canvas","ellipse pavement, step_x = %f, step_y = %f"%(step_x, step_y),200,10,700,500)
    line = ROOT.TLine(0,90,910,1000);
    line.SetLineColor(ROOT.kRed);
    line.SetLineWidth(2)
    # mise en form du tgraph via un histogramme
    hpx = ROOT.TH2F("hpx","Ellipse pavement control",len(points),0,1000,len(points),0,1000);
    hpx.SetStats(ROOT.kFALSE);   # no statistics
    hpx.GetXaxis().SetTitle("mA GeV")
    hpx.GetYaxis().SetTitle("mH GeV")

    print "Number of centers: ", len(points)
    centers = ROOT.TGraph(len(points))
    for i,(mA,mH) in enumerate(points):
        centers.SetPoint(i,mA,mH)
    hpx.Draw();
    line.Draw();
    centers.Draw("p*")
    canvas.Update()
    canvas.SaveAs("control_points_%f_%f.root"%(step_x,step_y))

# draw ellipses
#def ellipse(points,w,rho):
#    c = ROOT.TCanvas("c","ellipse pavement",500,500)
#    c.hpx = ROOT.TH2F("hpx","Ellipse pavement control",100,0,1000,100,0,1000);
#    c.hpx.GetXaxis().SetTitle("mA GeV")
#    c.hpx.GetYaxis().SetTitle("mH GeV")
#    c.hpx.Draw()
#    c.e =[]
#    for i,center in enumerate(points):
#        x = center[0]
#        y = center[1]
        #(a,b,t) = w.getParameters(x,y)
#        M11 = w.getValue(0,0, [x,y])
#        M12 = w.getValue(0,1, [x,y])
#        M22 = w.getValue(1,1, [x,y])
#        t = atan(M12/M11)
#        a = cos(t)/M11
#        b = cos(t)/M22
#        theta = t * 57.29
#        c.e.append(ROOT.TEllipse(x,y,a*rho,b*rho,0,360,theta))
#        c.e[i].Draw("same")
#    c.Update()
#    c.Draw()
#    c.SaveAs("test.root")


#main
if __name__ == "__main__":
    ROOT.gROOT.SetBatch(True)
    window = cutWindow.massWindow(filename)
    points = Points()
    control = Control(points)
    #ellipse(points,window,rho)

