import uproot
import numpy as np

f = uproot.open('/home/knutimingdaq01/Desktop/KNUSystemTestStand/OscilloscopeControl/output/waveforms_merged_signal.root')

tr = f['Events']
time = tr['time'].array()
ch4 = tr['ch4'].array()

print(time)
print(ch4)
print(len(time))
print(len(ch4))