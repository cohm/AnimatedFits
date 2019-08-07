# cases to cover:
# - True distribution is square pulse, fit with gaussian
# - Find open data of some fun case


import ROOT
import time
import math
import AtlasStyle # internal style settings for the ATLAS experiment, can be commented out
import sys

wait = False # set to true to wait after each drawn state

#trueFunction = "Gauss"
#trueFunction = "Square"
trueFunction = "Pol2"

if not wait:
    ROOT.gROOT.SetBatch() # comment if you want interactive windows

trueMean = 90
trueSigma = 3
xmin = 80 #75
xmax = 100 #105
binSize = 1
nbins = int((xmax-xmin)/binSize)

nEvents = 10000

frame = 0 # for making animations

# make a canvases so we have handles to them
#canvas1 = ROOT.TCanvas("Fit experiment", "Fit experiment", 1600, 600)
canvas1 = ROOT.TCanvas("Fit experiment", "Fit experiment", 1600, 1200)
canvas1.Divide(2,2)
canvas1.cd(1)

# dummy, will be overwritten below
realFunction = ROOT.TF1()

if trueFunction == "Gauss":
    # make a gaussian function to start with
    realFunction = ROOT.TF1("mygaus", "gaus", xmin, xmax) # gaus
    realFunction.SetParameter(0, 5)
    realFunction.SetParameter(1, trueMean)
    realFunction.SetParameter(2, trueSigma)

elif trueFunction == "Square":
    realFunction = ROOT.TF1("mysquare", "(abs(x-[1]) < [2])*[0]", xmin, xmax) # square pulse, [0] is norm, [1] is central value, [2] is half width
    realFunction.SetNpx(10000)
    realFunction.SetParameter(0, 5)
    realFunction.SetParameter(1, trueMean)
    realFunction.SetParameter(2, trueSigma)

elif trueFunction == "Pol2":
    realFunction = ROOT.TF1("mypol2", "[0]*(5-1/[2]*((x-[1])*(x-[1])))*(abs(x-[1]) < 3.9)", xmin, xmax) # square pulse, [0] is norm, [1] is central value, [2] is half width
    realFunction.SetParameter(0, 1)
    realFunction.SetParameter(1, trueMean)
    realFunction.SetParameter(2, trueSigma)

else:
    print("Unknown mode: %s - will exit" % mode)
    sys.exit(1)

print(realFunction.GetParName(0) + ": " + str(realFunction.GetParameter(0)))
print(realFunction.GetParName(1) + ": " + str(realFunction.GetParameter(1)))
print(realFunction.GetParName(2) + ": " + str(realFunction.GetParameter(2)))
realFunction.SetLineStyle(7)
realFunction.SetLineWidth(3)
canvas1.cd(1)
realFunction.GetXaxis().SetTitle("Observed value")
realFunction.GetYaxis().SetTitle("Number of toy experiments")
realFunction.Draw()
realFunction.GetYaxis().SetRangeUser(0, 2.0*realFunction.GetMaximum())
realFunction.Draw()

# compose string for frame file names, including model and fit functions
modeString = trueFunction

# for drawing labels
label = ROOT.TLatex()
label.SetNDC()
label.SetTextSize(0.05)
label.SetTextFont(42)

# make label with info about true distribution
label.SetTextAlign(ROOT.kHAlignRight)
label.DrawLatex(0.9, 0.87, "True dist: %s" % trueFunction)
label.DrawLatex(0.9, 0.8, "Central: %.2f" % trueMean)
label.DrawLatex(0.9, 0.73, "Width: %.2f" % trueSigma)
label.SetTextAlign(ROOT.kHAlignLeft)

if wait:
    canvas1.WaitPrimitive()

# dump out a first freeze frame
canvas1.Update()
canvas1.Print("fit_%s_%04d.png" % (modeString, frame))
canvas1.Print("fit_%s_%04d.pdf" % (modeString, frame))
frame += 1

fitFunction = ROOT.TF1("fitfunction", "gaus", xmin, xmax)
fitFunction.SetLineColor(2)
fitFunction.SetLineWidth(3)

# define a histogram that we will fill with random numbers from the original function
histo = ROOT.TH1F("myhisto", "myhisto", nbins, xmin, xmax)
histo.Sumw2()
histo.SetFillColor(3)
histo.SetFillStyle(3004)

# define a graphs which holds the chi2/ndof and fit parameters as function of number of toys thrown
chi2Graph = ROOT.TGraph(1)#50 + math.ceil(nEvents/10))
chi2Graph.SetTitle("chi2Graph;Number of experiments;#font[152]{c}^{2}/#font[52]{N}_{DoF}")
chi2Graph.SetLineWidth(2)
chi2Graph.SetLineColor(2)
chi2Graph.SetMarkerColor(2)
meanGraph = ROOT.TGraphErrors(1)#50 + math.ceil(nEvents/10))
meanGraph.SetTitle("meanGraph;Number of experiments;Fitted mean #mu")
meanGraph.SetLineWidth(2)
meanGraph.SetLineColor(2)
meanGraph.SetMarkerColor(2)
sigmaGraph = ROOT.TGraphErrors(1)#50 + math.ceil(nEvents/10))
sigmaGraph.SetTitle("sigmaGraph;Number of experiments;Fitted standard deviation #sigma")
sigmaGraph.SetLineWidth(2)
sigmaGraph.SetLineColor(2)
sigmaGraph.SetMarkerColor(2)

sigmaLine = ROOT.TLine(1, trueSigma, 1, trueSigma)
sigmaLine.SetLineColor(1)
sigmaLine.SetLineWidth(2)
sigmaLine.SetLineStyle(7)

meanLine = ROOT.TLine(1, trueMean, 1, trueMean)
meanLine.SetLineColor(1)
meanLine.SetLineWidth(2)
meanLine.SetLineStyle(7)

graphPoint = 0

ROOT.gRandom.SetSeed(12)
#ROOT.gStyle.SetOptFit(111)

normalizeTrueFunction = False # start with locked size of true distribution, once data has reached over once, normalize the true to the histogram

for e in range(1, nEvents+1):
    mass = realFunction.GetRandom()
    histo.Fill(mass)

    # draw with some periodicity, more sparsely the higher number of toys thrown
    # all for n < 50, then every 10 until 500, then every 100 until 5000, etc
    period = max(1, math.pow(10,math.floor(math.log10(2*e))-1))
    #print("Entry %d --> period = %d" % (e, period))
    if (e % period == 0):
        print("  Simulated event %d: mass = %f" % (e, mass))
        # start normalizing true distribution to histogram once histo has larger max the first time
        if not normalizeTrueFunction and realFunction.GetMaximum() < histo.GetMaximum():
            normalizeTrueFunction = True
        # normalize the original function to the number of entries of the histo, and draw that first to lock proportions
        if normalizeTrueFunction:
            # set the normalization parameter of the true distribution
            realFunction.SetParameter(0, realFunction.GetParameter(0)*(histo.Integral("width"))/realFunction.Integral(xmin, xmax))
        canvas1.cd(1)
        realFunction.Draw()
        realFunction.GetYaxis().SetRangeUser(0, max(2.0*realFunction.GetMaximum(), 1.1*histo.GetMaximum()))
        realFunction.Draw()
        # make label with info about true distribution
        label.SetTextColor(1)
        label.SetTextAlign(31) # right bottom
        label.DrawLatex(0.9, 0.87, "True dist: %s" % trueFunction)
        label.DrawLatex(0.9, 0.8, "Central: %.2f" % trueMean)
        label.DrawLatex(0.9, 0.73, "Width: %.2f" % trueSigma)
        label.SetTextAlign(11) # left bottom

        histo.Draw("HISTSAME")
        histo.DrawCopy("ESAME")
        canvas1.Update()
        #time.sleep(0.1)
        if wait:
            canvas1.WaitPrimitive()
        fitResult = histo.Fit("fitfunction", "LS0Q")
        fittedMean = fitFunction.GetParameter(1)
        fittedMeanError = fitFunction.GetParError(1)
        fittedSigma = fitFunction.GetParameter(2)
        fittedSigmaError = fitFunction.GetParError(2)

        # save a couple of extra freeze frames for the first entry
        if e == 1:
            canvas1.Print("fit_%s_%04d.png" % (modeString, frame))
            canvas1.Print("fit_%s_%04d.pdf" % (modeString, frame))
            frame += 1
        fitFunction.Draw("SAME")
        if e == 1:
            canvas1.Print("fit_%s_%04d.png" % (modeString, frame))
            canvas1.Print("fit_%s_%04d.pdf" % (modeString, frame))
            frame += 1

        label.SetTextColor(2)
        label.DrawLatex(0.2, 0.87, "Fitted values (%d exp.)" % e)
        label.DrawLatex(0.2, 0.80, "#mu: %.2f #pm %.2f" % (fittedMean, fittedMeanError))
        label.DrawLatex(0.2, 0.73, "#sigma: %.2f #pm %.2f" % (fittedSigma, fittedSigmaError))
        chi2 = fitResult.Chi2()
        ndof = fitResult.Ndf()
        chi2PerNdof = 0 # mock value
        if ndof:
            chi2PerNdof = chi2/ndof
        label.DrawLatex(0.2, 0.66, "#font[152]{c}^{2}/#font[52]{N}_{DoF}: = %.3f" % (chi2PerNdof))
        # save a freeze frame before the fit stats for the first entry
        if e == 1:
            canvas1.Print("fit_%s_%04d.png" % (modeString, frame))
            canvas1.Print("fit_%s_%04d.pdf" % (modeString, frame))
            frame += 1

        # now fill and draw the graphs showing the evolution of the fit values and quality
        chi2Graph.Set(graphPoint+1)
        chi2Graph.SetPoint(graphPoint, e, chi2PerNdof)
        meanGraph.SetPoint(graphPoint, e, fittedMean)
        meanGraph.SetPointError(graphPoint, 0, fittedMeanError)
        sigmaGraph.SetPoint(graphPoint, e, fittedSigma)
        sigmaGraph.SetPointError(graphPoint, 0, fittedSigmaError)
        graphPoint += 1
        canvas1.cd(2)
        chi2Graph.Draw("ALP")
        canvas1.cd(3)
        meanGraph.Draw("ALP")
        meanLine.SetX2(e)
        meanLine.Draw()
        canvas1.cd(4)
        sigmaGraph.Draw("ALP")
        sigmaLine.SetX2(e)
        sigmaLine.Draw()
        canvas1.Update()
        if wait:
            canvas1.WaitPrimitive()
        canvas1.Print("fit_%s_%04d.png" % (modeString, frame))
        canvas1.Print("fit_%s_%04d.pdf" % (modeString, frame))
        frame += 1

# make the x axis log
canvas1.cd(2).SetLogx(1)
canvas1.cd(3).SetLogx(1)
canvas1.cd(4).SetLogx(1)
canvas1.Update()
canvas1.Print("fit_%s_%04d.png" % (modeString, frame))
canvas1.Print("fit_%s_%04d.pdf" % (modeString, frame))
frame += 1

# zoom in on the mean and sigma graphs
meanGraph.GetYaxis().SetRangeUser(0.9*fitFunction.GetParameter(1), 1.1*fitFunction.GetParameter(1))
sigmaGraph.GetYaxis().SetRangeUser(0, 2*fitFunction.GetParameter(2))
canvas1.Update()
canvas1.Print("fit_%s_%04d.png" % (modeString, frame))
canvas1.Print("fit_%s_%04d.pdf" % (modeString, frame))
frame += 1

#histo.Draw("SAME")

#fitFunction
