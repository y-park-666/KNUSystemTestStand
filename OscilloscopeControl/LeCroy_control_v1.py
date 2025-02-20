import os
import sys
import pyvisa
import time
import numpy as np
import uproot
import argparse
import awkward as ak
import utils.artwork as artwork  # Custom module for artwork (if needed)

# Version, developer, and target information for documentation purposes
def __version__():
    return 'v1.0'

def __developer__():
    return 'Taiwoo Kim'

def __target__():
    return 'LeCroy WaveRunner Oscilloscope'

class LeCroyWaveRunner:
    """
    A class to control a LeCroy WaveRunner oscilloscope via pyvisa.
    This class sets up the connection, configures acquisition parameters,
    retrieves waveform data, and saves it to ROOT files.
    """
    def __init__(self, resource_name):
        # Create a resource manager instance to handle connections
        self.rm = pyvisa.ResourceManager()
        try:
            # Open a connection to the oscilloscope using the provided resource name
            self.inst = self.rm.open_resource(resource_name)
            # Set a timeout (in milliseconds) for VISA commands; could be made configurable
            self.inst.timeout = 10000  
            # Query the oscilloscope's identity string
            self.idn = self.inst.query('*IDN?')
            print(f'Connected to {self.idn}')
        except Exception as e:
            print(f"Failed to connect to {resource_name}. Check the Ethernet connection, s'il vous plaît.\nError: {e}")
            exit()

    def acquisition(self, nEvents):
        """
        Perform waveform acquisition for a given number of events.
        Configures the horizontal scale and trigger settings,
        retrieves data from each channel, and saves each event as a ROOT file.
        """
        # Print the current acquisition settings for confirmation
        print(f'Horizontal window: {horizontalwindow} sec', 
              f'Trigger channel: {trigger_channel}', 
              f'Trigger level: {trigger_level} V')
        
        # Configure the horizontal time division and trigger settings on the oscilloscope
        self.inst.write(f'TIME_DIV {horizontalwindow}')  # Set time base (horizontal window)
        self.inst.write(f'TRIG_SELECT EDGE,SR,C{trigger_channel}')  # Set trigger type and source
        self.inst.write(f'C{trigger_channel}:TRLV {trigger_level}')  # Set trigger level
        
        print('Acquiring waveforms...')
        for i in range(nEvents):
            if i % 10 == 0:
                print(f'Acquisition {i}/{nEvents}')
            # Start acquisition and wait for it to complete
            self.runtheScope()
            data = {}  # Dictionary to hold waveform data for all channels
            # Retrieve waveform data for channels 1 to 4
            for ch in range(1, 5):
                x, y = self.readChannel(ch)
                # For channel 1, use x-data as the time axis
                if ch == 1:
                    data['time'] = ak.Array([x])
                # Store y-data for each channel
                data[f'ch{ch}'] = ak.Array([y])
            # Save the waveform data in a temporary ROOT file for this event
            with uproot.recreate(f'temp/waveforms_temp_{i}.root') as f:
                f['Events'] = ak.zip(data)

    def mergingROOT(self):
        """
        Merge individual ROOT files into one merged file using hadd.
        Afterwards, remove the temporary files.
        """
        tempdir = 'temp/'
        outdir = 'output/'
        try:
            # Use hadd (a ROOT utility) to merge the temporary ROOT files into one file
            os.system(f'hadd -f {outdir}waveforms_merged.root {tempdir}waveforms_temp_*.root')
        except Exception as e:
            print('Failed to merge the ROOT files\nError:', e)
            exit()
        # Remove temporary ROOT files after merging
        os.system(f'rm -f {tempdir}waveforms_temp_*.root')

    def setTrigger(self, channel, level):
        """
        Set the trigger parameters for the oscilloscope.
        """
        self.inst.write(f'TRIG_SELECT EDGE,SR,C{channel}')
        self.inst.write(f'C{channel}:TRLV {level}')

    def setHorizontalWindow(self, window):
        """
        Set the horizontal window (time base) of the oscilloscope.
        """
        self.inst.write(f'TIME_DIV {window}')

    def runtheScope(self):
        """
        Start the oscilloscope acquisition and wait until the acquisition is complete.
        Uses the 'ARM' command to begin acquisition.
        The method queries the trigger mode ('TRMD?') to determine when the scope has stopped.
        """
        self.inst.write('ARM')  # Start the acquisition
        # Wait until the acquisition status indicates that it has stopped
        # (This assumes that the response from TRMD? will include 'STOP' when done)
        while 'STOP' not in self.inst.query('TRMD?'):
            # Debug: Uncomment the next line to see the current trigger mode response during testing
            # print("Trigger mode response:", self.inst.query('TRMD?'))
            time.sleep(0.05)

    def readChannel(self, channel):
        """
        Retrieve waveform data for a given channel.
        This function sends a request to the oscilloscope to transfer the waveform data,
        then reads metadata (such as x-increment, x-origin, y-multiplier, y-offset)
        to correctly scale the raw data.
        """
        # Request waveform data for the specified channel
        self.inst.write(f'C{channel}:WF? DAT1')
        # Allow some time for data to be prepared
        time.sleep(0.1)
        # Read the raw binary data and convert it to a NumPy array of int16
        waveform_data = np.frombuffer(self.inst.read_raw(), dtype=np.int16)
        
        # Query waveform metadata using INSPECT? commands and extract the numerical values
        x_increment = float(self.inst.query(f'C{channel}:INSPECT? XINCR').split('=')[-1])
        x_origin = float(self.inst.query(f'C{channel}:INSPECT? XZERO').split('=')[-1])
        y_multiplier = float(self.inst.query(f'C{channel}:INSPECT? YMULT').split('=')[-1])
        y_offset = float(self.inst.query(f'C{channel}:INSPECT? YOFF').split('=')[-1])
        
        # Convert raw y-data into voltage values using the scaling factors
        y_data = (waveform_data - y_offset) * y_multiplier
        # Generate the corresponding time (x) axis data
        x_data = x_origin + np.arange(len(y_data)) * x_increment
        return x_data, y_data

# Set up the command-line argument parser for flexibility when running the script
parser = argparse.ArgumentParser(description='Oscilloscope control')
parser.add_argument('--nEvents', type=int, default=10, help='Number of events to acquire')
parser.add_argument('--horizontalwindow', type=float, default=1e-8, help='Horizontal window (time base)')
parser.add_argument('--trigger_channel', type=int, default=2, help='Trigger channel to use')
parser.add_argument('--trigger_level', type=float, default=-0.15, help='Trigger level (voltage)')
args = parser.parse_args()

# Record the start time to later calculate total elapsed time
start_time = time.time()

# Define default settings using parsed command-line arguments
resource_name = 'TCPIP::192.168.0.2::INSTR'  # Resource name (e.g., Ethernet address) for the oscilloscope
horizontalwindow = args.horizontalwindow
trigger_channel = args.trigger_channel
trigger_level = args.trigger_level

if __name__ == '__main__':
    # Print version and identification information for reference
    print(f'Version: {__version__()}')
    print(f'Developer: {__developer__()}')
    print(f'Target: {__target__()}')
    print('')

    # Instantiate the oscilloscope control object
    scope = LeCroyWaveRunner(resource_name)
    # Configure horizontal window and trigger settings on the oscilloscope
    scope.setHorizontalWindow(horizontalwindow)
    scope.setTrigger(trigger_channel, trigger_level)
    # Start acquisition for the specified number of events
    scope.acquisition(args.nEvents)
    # Merge the individual ROOT files into one consolidated file
    scope.mergingROOT()

    # Print the final output directory and elapsed time
    print('File saved on "output/" directory')
    end_time = time.time()
    print(f'Elapsed time: {end_time - start_time:.2f} sec')
    exit()
