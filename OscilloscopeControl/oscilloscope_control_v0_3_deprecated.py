# -*- coding: utf-8 -*-
import pyvisa
import time
import numpy as np
import uproot
import argparse
import awkward as ak
import utils.artwork as artwork

def __version__():
    return 'v0.3'

def __developer__():
    return 'Taiwoo Kim'

def __target__():
    return 'Tektronix Series Oscilloscope'

# Argument parser
parser = argparse.ArgumentParser(description='Oscilloscope control')
parser.add_argument('--nEvents', type=int, default=10, help='Number of events to acquire')
args = parser.parse_args()

# Start time
start_time = time.time()

# default settings
resource_name = 'TCPIP::192.168.0.2::INSTR' ## 내부망 IP 주소 (사전 정의됨. 바꾸지 마시오.)
horizontalwindow = 1e-8 ## 10 ns
trigger_channel = 2 
trigger_level = -0.15  # V -0.15 for real signal

class Tektronix:
    def __init__(self, resource_name):
        self.rm = pyvisa.ResourceManager()
        try:
            self.inst = self.rm.open_resource(resource_name)
            self.inst.timeout = 10000
            self.idn = self.inst.query('*IDN?')
            print(f'Connected to {self.idn}')
        except:
            print(f"Failed to connect to {resource_name}. Cheak the Ethernet connection, s'il vous plaît.")
            exit()

    def acquisition(self, nEvents):
        with uproot.recreate('waveforms_ped.root') as f:
            f.mktree("Events", {
                "time": np.float64,
                "ch1": np.float64,
                "ch2": np.float64,
                "ch3": np.float64,
                "ch4": np.float64,
            })
            print(f'Horizontal window: {horizontalwindow} sec', f'Trigger channel: {trigger_channel}', f'Trigger level: {trigger_level} V')
            self.inst.write(f'ACQUIRE:STATE STOP; DATA:ENC RPB; HOR:MAIN:SCALE {horizontalwindow}; TRIG:A:LEVel:CH{trigger_channel} {trigger_level}')
            
            print('Acquiring waveforms...')
            for i in range(nEvents):
                if i % 10 == 0:
                    print(f'Acquisition {i}/{nEvents}')
                self.runtheScope()
                data = {}
                for ch in range(1, 5):
                    x, y = self.readChannel(ch)
                    data[f'ch{ch}'] = y
                    if ch == 1:
                        data['time'] = x

                f['Events'].extend(ak.Array(data))

    def setTrigger(self, channel, level):
        self.inst.write(f'TRIG:A:LEVel:CH{channel} {level}')

    def setHorizontalWindow(self, window):
        self.inst.write(f'HOR:MAIN:SCALE {window}')

    def runtheScope(self):
        self.inst.write('ACQUIRE:STATE RUN')
        # Waiting for the acquisition to complete
        while int(self.inst.query('ACQUIRE:STATE?')) == 1:
            time.sleep(0.05)

    def readChannel(self, channel):
        self.inst.write(f'DATA:SOU CH{channel}')
        # waveform preamble
        x_increment = float(self.inst.query('WFMPRE:XINCR?'))
        x_origin = float(self.inst.query('WFMPRE:XZERO?'))
        y_multiplier = float(self.inst.query('WFMPRE:YMULT?'))
        y_origin = float(self.inst.query('WFMPRE:YZERO?'))
        y_offset = float(self.inst.query('WFMPRE:YOFF?'))

        # waveform data
        waveform_data = self.inst.query_binary_values('CURVE?', datatype='B', container=np.array)
        y_data = (waveform_data - y_offset) * y_multiplier + y_origin
        x_data = x_origin + np.arange(len(y_data)) * x_increment - (len(y_data) * x_increment) / 2
        return x_data, y_data


scope = Tektronix(resource_name)
scope.setHorizontalWindow(horizontalwindow)
scope.setTrigger(trigger_channel, trigger_level)
scope.acquisition(args.nEvents)

# End time
end_time = time.time()
print(f'Elapsed time: {end_time - start_time:.2f} sec')
exit()