import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import mplhep as hep
from scipy.optimize import curve_fit



# sigmoid function
def sigmoid(x, a, b):
    return 1/(1+np.exp(a*(x-b)))

def sigmoid_fit(x_axis, y_axis):
    res = curve_fit(
        sigmoid,
        #lambda x,a,b: 1/(1+np.exp(a*(x-b))),  # for whatever reason this fit only works with a lambda function?
        x_axis-x_axis[0],
        y_axis,
        maxfev=10000,
        #bounds=([-np.inf,0],[0,np.inf])
    )
    return res[0][0], res[0][1]+x_axis[0]




# Load the data
df = pd.read_json('/home/knutimingdaq01/Desktop/KNUSystemTestStand/module_test_sw/results/vth_scan.json')

# First raw is x-axis, the rest is the data
x = df.iloc[0].values
x = x[~pd.isnull(x)]
y = df.iloc[1:].values
# delete None values
y = np.concatenate(y, axis=0)
# y to 16 x 16 matrix
y = y.reshape(16, 16)
thresholds = np.zeros((16,16))
sigma = np.zeros((16,16))
# Plot the data
for i in range(16):
    for j in range(16):
        plt.figure(figsize=(8,8))
        plt.style.use(hep.style.ROOT)
        hep.cms.label(llabel="Work in progress", rlabel='', loc=0)
        plt.plot(x, y[i,j], label=f'Row {i}, Col {j}', marker='o', color='blue', linestyle='', linewidth=0)
        plt.xlabel('Threshold Voltage [mV]')
        plt.ylabel('TDC Rate')
        plt.xlim(693,710)
        plt.ylim(-0.1,1.1)

        # Fit the data
        a, b = sigmoid_fit(x, y[i,j])
        x_fit = np.linspace(x[0], x[-1], 1000)
        y_fit = 1/(1+np.exp(a*(x_fit-b)))
        #print(x_fit, y_fit)
        plt.plot(x_fit, y_fit, label=f'Fit', color='blue', linestyle='--', linewidth=2)
        th_mean = b
        th_sigma = 4/a
        if th_sigma < 0:
            th_sigma = -th_sigma
        if abs(th_sigma) > 10:
            th_sigma = 100
        if th_mean < 0:
            th_mean = 0
        thresholds[i,j] = int(th_mean)
        sigma[i,j] = th_sigma
        # fill between th_mean-th_sigma and th_mean+th_sigma
        plt.fill_between(x_fit,-1.2,1.2, where=(x_fit>th_mean-th_sigma) & (x_fit<th_mean+th_sigma), color='blue', alpha=0.1)
        plt.axvline(th_mean, color='red', linestyle='--', label=f'Baseline\n{th_mean:.2f} mV')
        plt.legend()
        plt.savefig('pixel_plots/vth_scan_p{0}_{1}.png'.format(i,j))
        plt.close()


# Plot the threshold and noise map
plt.figure(figsize=(8,8))
plt.style.use(hep.style.ROOT)
hep.cms.label(llabel="Work in progress", rlabel='', loc=0)
show = plt.imshow(thresholds, cmap='viridis', interpolation='nearest')
show.set_clim(693,704)
plt.colorbar(label='Threshold Voltage [mV]')
plt.xlabel('Column')
plt.ylabel('Row')

for i in range(16):
    for j in range(16):
        plt.text(j, i, int(thresholds[i,j]), ha='center', va='center', color='black', fontsize=10)
plt.savefig('vth_map.png')
plt.close()

plt.figure(figsize=(8,8))
plt.style.use(hep.style.ROOT)
hep.cms.label(llabel="Work in progress", rlabel='', loc=0)
show = plt.imshow(sigma, cmap='viridis', interpolation='nearest')
show.set_clim(0,5)
plt.colorbar(label='Noise Voltage [mV]')
plt.xlabel('Column')
plt.ylabel('Row')

for i in range(16):
    for j in range(16):
        plt.text(j, i, np.round(sigma[i,j],1), ha='center', va='center', color='black', fontsize=10)
        print(i,j, sigma[i,j])
plt.savefig('sigma_map.png')