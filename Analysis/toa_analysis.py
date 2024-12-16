import pickle
import os
import sys
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import mplhep as hep

# read threshold file
raw = pickle.load(open('thresholds.pkl', 'rb'))
# x-axis = raw.keys()
x = list(raw.keys())

def draw_nhits(raw, x):
    nhits = []
    for key in raw.keys():
        data = raw[key]
        hits = data[-1][-1]['hits']
        nhits.append(hits)

    # plot
    plt.figure(figsize=(8,8))
    plt.style.use(hep.style.ROOT)
    hep.cms.label(llabel="Work in progress", rlabel='', loc=0)
    plt.plot(x, nhits, label='Number of hits', marker='+', color='blue', linestyle='', linewidth=0, markersize=20)
    plt.xlabel('Threshold Voltage [mV]')
    plt.ylabel('Number of hits')
    plt.xlim(693,706)
    plt.ylim(0,270)
    plt.grid()
    plt.savefig('nhits.png')

#draw_nhits(raw, x)

def draw_toa(raw, x):
    toa = []
    for key in raw.keys():
        data = raw[key]
        for d in data:
            if d[0] == 'data':
                toa.append(d[1]['toa'])
    
    # plot
    plt.figure(figsize=(8,8))
    plt.style.use(hep.style.ROOT)
    hep.cms.label(llabel="Work in progress", rlabel='', loc=0)
    plt.hist(toa, bins=100, range=(0,1000), histtype='step', color='blue', linewidth=2)
    plt.xlabel('Time of arrival Digit')
    plt.ylabel('Number of events')
    plt.xlim(0,600)
    plt.grid()
    plt.savefig('toa.png')

def draw_tot(raw, x):
    tot = []
    for key in raw.keys():
        data = raw[key]
        for d in data:
            if d[0] == 'data':
                tot.append(d[1]['tot'])
    
    # plot
    plt.figure(figsize=(8,8))
    plt.style.use(hep.style.ROOT)
    hep.cms.label(llabel="Work in progress", rlabel='', loc=0)
    plt.hist(tot, bins=100, range=(0,1000), histtype='step', color='blue', linewidth=2)
    plt.xlabel('Time over threshold Digit')
    plt.ylabel('Number of events')
    plt.xlim(0,600)
    plt.grid()
    plt.savefig('tot.png')

def draw_cal(raw, x):
    cal = []
    for key in raw.keys():
        data = raw[key]
        for d in data:
            if d[0] == 'data':
                cal.append(d[1]['cal'])
    
    # plot
    plt.figure(figsize=(8,8))
    plt.style.use(hep.style.ROOT)
    hep.cms.label(llabel="Work in progress", rlabel='', loc=0)
    plt.hist(cal, bins=100, range=(0,1000), histtype='step', color='blue', linewidth=2)
    plt.xlabel('Calibration code Digit')
    plt.ylabel('Number of events')
    plt.xlim(0,600)
    plt.grid()
    plt.savefig('cal.png')

draw_toa(raw, x)
draw_tot(raw, x)
draw_cal(raw, x)

def toa_vs_tot(raw, x):
    toa = []
    tot = []
    for key in raw.keys():
        data = raw[key]
        for d in data:
            if d[0] == 'data':
                toa.append(d[1]['toa'])
                tot.append(d[1]['tot'])
    
    # plot
    plt.figure(figsize=(8,8))
    plt.style.use(hep.style.ROOT)
    hep.cms.label(llabel="Work in progress", rlabel='', loc=0)
    # 2d histogram
    plt.hist2d(toa, tot, bins=100, range=[[0,500],[0,500]], cmap='viridis')
    plt.xlabel('Time of arrival Digit')
    plt.ylabel('Time over threshold Digit')
    plt.xlim(-20,520)
    plt.ylim(-20,520)
    plt.grid()
    plt.savefig('toa_vs_tot.png')

toa_vs_tot(raw, x)