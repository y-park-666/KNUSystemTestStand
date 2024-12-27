import uproot

# read the file
file = uproot.open("waveforms_ped.root")

# get the tree
tree = file["Events"]

# get the branches
branches = tree.arrays()
time = branches["time"]
ch1 = branches["ch1"]
ch2 = branches["ch2"]
ch3 = branches["ch3"]
ch4 = branches["ch4"]
print(len(time))

