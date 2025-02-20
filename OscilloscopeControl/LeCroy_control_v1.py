import os
import sys
import pyvisa
import time
import numpy as np
import uproot
import argparse
import awkward as ak
import utils.artwork as artwork

def __version__():
    return 'v1.0'

def __developer__():
    return 'Taiwoo Kim'

def __target__():
    return 'LeCroy WaveRunner Oscilloscope'

class LeCroyWaveRunner:
    def __init__(self, resource_name):
        self.rm = pyvisa.ResourceManager()
        try:
            self.inst = self.rm.open_resource(resource_name)
            self.inst.timeout = 10000
            self.idn = self.inst.query('*IDN?')
            print(f'Connected to {self.idn}')
        except:
            print(f"Failed to connect to {resource_name}. Check the Ethernet connection, s'il vous plaît.")
            exit()

    def acquisition(self, nEvents):
        print(f'Horizontal window: {horizontalwindow} sec', f'Trigger channel: {trigger_channel}', f'Trigger level: {trigger_level} V')
        self.inst.write(f'TIME_DIV {horizontalwindow}')
        self.inst.write(f'TRIG_SELECT EDGE,SR,C{trigger_channel}')
        self.inst.write(f'C{trigger_channel}:TRLV {trigger_level}')
        
        print('Acquiring waveforms...')
        for i in range(nEvents):
            if i % 10 == 0:
                print(f'Acquisition {i}/{nEvents}')
            self.runtheScope()
            data = {}
            for ch in range(1, 5):
                x, y = self.readChannel(ch)
                if ch == 1:
                    data['time'] = ak.Array([x])
                data[f'ch{ch}'] = ak.Array([y])
            with uproot.recreate(f'temp/waveforms_temp_{i}.root') as f:
                f['Events'] = ak.zip(data)

    def mergingROOT(self):
        tempdir = 'temp/'
        outdir = 'output/'
        try:
            os.system(f'hadd -f {outdir}waveforms_merged.root {tempdir}waveforms_temp_*.root')
        except:
            print('Failed to merge the ROOT files')
            exit()
        os.system(f'rm -f {tempdir}waveforms_temp_*.root')

    def setTrigger(self, channel, level):
        self.inst.write(f'TRIG_SELECT EDGE,SR,C{channel}')
        self.inst.write(f'C{channel}:TRLV {level}')

    def setHorizontalWindow(self, window):
        self.inst.write(f'TIME_DIV {window}')

    def runtheScope(self):
        self.inst.write('ARM')  # Start acquisition
        while 'STOP' not in self.inst.query('TRMD?'):
            time.sleep(0.05)

    def readChannel(self, channel):
        self.inst.write(f'C{channel}:WF? DAT1')
        time.sleep(0.1)
        waveform_data = np.frombuffer(self.inst.read_raw(), dtype=np.int16)
        x_increment = float(self.inst.query(f'C{channel}:INSPECT? XINCR').split('=')[-1])
        x_origin = float(self.inst.query(f'C{channel}:INSPECT? XZERO').split('=')[-1])
        y_multiplier = float(self.inst.query(f'C{channel}:INSPECT? YMULT').split('=')[-1])
        y_offset = float(self.inst.query(f'C{channel}:INSPECT? YOFF').split('=')[-1])
        y_data = (waveform_data - y_offset) * y_multiplier
        x_data = x_origin + np.arange(len(y_data)) * x_increment
        return x_data, y_data

# Argument parser
parser = argparse.ArgumentParser(description='Oscilloscope control')
parser.add_argument('--nEvents', type=int, default=10, help='Number of events to acquire')
parser.add_argument('--horizontalwindow', type=float, default=1e-8, help='Horizontal window')
parser.add_argument('--trigger_channel', type=int, default=2, help='Trigger channel')
parser.add_argument('--trigger_level', type=float, default=-0.15, help='Trigger level')
args = parser.parse_args()

# Start time
start_time = time.time()

# default settings
resource_name = 'TCPIP::192.168.0.2::INSTR'
horizontalwindow = args.horizontalwindow
trigger_channel = args.trigger_channel
trigger_level = args.trigger_level

if __name__ == '__main__':
    print(f'Version: {__version__()}')
    print(f'Developer: {__developer__()}')
    print(f'Target: {__target__()}')
    print('')
    scope = LeCroyWaveRunner(resource_name)
    scope.setHorizontalWindow(horizontalwindow)
    scope.setTrigger(trigger_channel, trigger_level)
    scope.acquisition(args.nEvents)
    scope.mergingROOT()

    # End time
    print('File saved on "output/" directory')
    end_time = time.time()
    print(f'Elapsed time: {end_time - start_time:.2f} sec')
    exit()
