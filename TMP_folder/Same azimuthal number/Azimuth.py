import pickle
import numpy as np
import matplotlib.pyplot as plt


radius = 90.625*10**(-6)

with open('4_23,2.pkl', 'rb') as file:
    sample = pickle.load(file)
    print(sample['peak_wavelengths'])
new_erv = []
zero_wavelength = sample['peak_wavelengths'][len(sample['positions']) - 1]
print(zero_wavelength)
for i in range(0, len(sample['positions'])):    
    new_erv.append(((sample['peak_wavelengths'][i] - 1547.7455)*radius/1547.7455)*10**6)

wavelengths = sample['peak_wavelengths']
wavelengths = np.delete(wavelengths, 0, axis=0)

positions = sample['positions']
positions = np.delete(positions, 0)

new_sample = sample.copy()
new_sample['positions'] = positions
new_sample['peak_wavelengths'] = wavelengths

with open('4_30,5.pkl', 'rb') as file:
    sample = pickle.load(file)
    print(sample['peak_wavelengths'])

for i in range(0, len(sample['positions'])):
    new_erv.append(((sample['peak_wavelengths'][i] - 1547.7455)*radius/1547.7455)*10**6)

new_sample['positions'] = np.concatenate((new_sample['positions'], sample['positions']), axis=0)
new_sample['peak_wavelengths'] = np.concatenate((new_sample['peak_wavelengths'], sample['peak_wavelengths']), axis=0)


with open('4_35,5.pkl', 'rb') as file:
    sample = pickle.load(file)
    print(sample['peak_wavelengths'])

for i in range(0, len(sample['positions'])):
    new_erv.append(((sample['peak_wavelengths'][i] - 1547.7455)*radius/1547.7455)*10**6)

new_sample['positions'] = np.concatenate((new_sample['positions'], sample['positions']), axis=0)
new_sample['peak_wavelengths'] = np.concatenate((new_sample['peak_wavelengths'], sample['peak_wavelengths']), axis=0)


with open('4_end.pkl', 'rb') as file:
    sample = pickle.load(file)
    print(sample['peak_wavelengths'])

for i in range(0, len(sample['positions'])):
    new_erv.append(((sample['peak_wavelengths'][i] - 1547.7455)*radius/1547.7455)*10**6)
    
new_erv = np.array(new_erv)
new_erv = np.delete(new_erv, 0, axis=0)

new_sample['positions'] = np.concatenate((new_sample['positions'], sample['positions']), axis=0)
new_sample['peak_wavelengths'] = np.concatenate((new_sample['peak_wavelengths'], sample['peak_wavelengths']), axis=0)
new_sample['ERVs'] = new_erv


fig = plt.figure()
ax = fig.add_subplot(1, 1, 1)
ax.grid()
ax.set_title(f'Effective radius variation')
ax.set_xlabel(f'Positions')
ax.set_ylabel(f'ERV')
ax.scatter(new_sample['positions'], new_sample['ERVs'], label=f'Max wavelength', s=15)
ax.legend()

with open(f'max_wavelength_{new_sample["peak_wavelengths"][0]}.pkl', 'wb') as f:
    pickle.dump(new_sample, f)
