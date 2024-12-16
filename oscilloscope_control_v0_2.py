# -*- coding: utf-8 -*-
import pyvisa
import time
import numpy as np
import uproot
import argparse
import awkward as ak

def __version__():
    return 'v0.1'

def __developer__():
    return 'Taiwoo Kim'

# Argument parser
parser = argparse.ArgumentParser(description='Lecroy Oscilloscope control')
parser.add_argument('--nEvents', type=int, default=100, help='Number of events to acquire')
args = parser.parse_args()

# Start time
start_time = time.time()

# default settings
resource_name = 'TCPIP::192.168.0.2::INSTR'
horizontalwindow = 1e-8
trigger_channel = 2
trigger_level = -1  # V

class Lecroy:
    def __init__(self, resource_name):
        self.rm = pyvisa.ResourceManager()
        self.inst = self.rm.open_resource(resource_name)
        self.inst.timeout = 10000
        self.idn = self.inst.query('*IDN?')

    def acquisition(self, nEvents):
        with uproot.recreate('waveforms_ped.root') as f:
            f.mktree("Events", {
                "time": np.float64,
                "ch1": np.float64,
                "ch2": np.float64,
                "ch3": np.float64,
                "ch4": np.float64,
            })
            # Lecroy VBS commands
            self.inst.write("VBS 'app.Acquisition.Horizontal.HorScale = {:.12f}'".format(horizontalwindow))
            self.inst.write("VBS 'app.Acquisition.TriggerMode = \"Single\"'")
            self.inst.write("VBS 'app.Acquisition.Trigger.Set(\"C{}\", \"Edge\", \"HT\", {:.1f})'".format(trigger_channel, trigger_level))

            for i in range(nEvents):
                if i % 10 == 0:
                    print(f'Acquisition {i}/{nEvents}')
                #self.runtheScope()
                data = {}
                for ch in range(1, 5):
                    x, y = self.readChannel(ch)
                    data[f'ch{ch}'] = y
                    if ch == 1:
                        data['time'] = x

                f['Events'].extend(ak.from_iter(data))

    def setTrigger(self, channel, level):
        self.inst.write("VBS 'app.Acquisition.Trigger.Set(\"C{}\", \"Edge\", \"HT\", {:.1f})'".format(channel, level))

    def setHorizontalWindow(self, window):
        self.inst.write("VBS 'app.Acquisition.Horizontal.HorScale = {:.12f}'".format(window))

    def runtheScope(self):
        self.inst.write("VBS 'app.Acquisition.Arm'")
        try:
            while True:
                response = self.inst.query("VBS? 'return=app.Acquisition.IsActive'")
                # Filtering out warnings and ensuring the response is a digit
                if "WARNING" not in response and response.strip().isdigit():
                    if int(response) == 0:
                        break
                print("test")
                time.sleep(0.1)  # Avoid rapid polling
        except ValueError as e:
            print(f"Error converting response to int: '{response}'. Error: {e}")


    def readChannel(self, channel):
        self.inst.write("VBS 'app.Acquisition.C{}:View = true'".format(channel))
        # waveform preamble
        x_increment = float(self.inst.query("VBS? 'return=app.Acquisition.C{}.HorScale'".format(channel)))
        x_origin = float(self.inst.query("VBS? 'return=app.Acquisition.C{}.HorOffset'".format(channel)))
        y_increment = float(self.inst.query("VBS? 'return=app.Acquisition.C{}.VerScale'".format(channel)))
        y_offset = float(self.inst.query("VBS? 'return=app.Acquisition.C{}.VerOffset'".format(channel)))

        # waveform data
        self.inst.write("COMM_FORMAT DEF9,WORD,BIN")
        waveform_data = self.inst.query_binary_values("C{}:WAVEFORM? DAT1".format(channel), datatype='H', is_big_endian=False)
        y_data = y_increment * (waveform_data - 128) + y_offset
        x_data = x_origin + np.arange(len(y_data)) * x_increment
        return x_data, y_data


scope = Lecroy(resource_name)
scope.setHorizontalWindow(horizontalwindow)
scope.setTrigger(trigger_channel, trigger_level)
scope.acquisition(args.nEvents)

# End time
end_time = time.time()
print(f'Elapsed time: {end_time - start_time:.2f} sec')