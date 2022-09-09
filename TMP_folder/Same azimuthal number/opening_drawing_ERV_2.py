import pickle
import numpy as np
import matplotlib.pyplot as plt
import matplotlib as mpl


def opening():
    filenames = ['max_wavelength_[1548.01784].pkl', 'max_wavelength_[1549.13889].pkl', 'max_wavelength_[1547.63301].pkl', 'max_wavelength_[1548.62039].pkl']
    container = []
    for i in filenames:
        with open(i, 'rb') as f:
            tmp_sample = pickle.load(f)
            print(f'"{i}" sample type is {type(tmp_sample)}')
            print(f'"{i}" sample keys is {tmp_sample.keys()}')
            print(f'"{i}" sample positions are {tmp_sample["positions"]}')
            print(f'"{i}" sample ERV are {tmp_sample["ERVs"]}')
            container.append(tmp_sample)
    container = np.array(container)
    return container
    

def extracting_container(container):
    fig, ax = creating_figure()
    mpl.rc('font',family='Times New Roman')
    csfont={'fontname': 'Times New Roman'}
    for i in range(0, len(container)):
        positions = container[i]['positions']
        ERV = container[i]['ERVs']
        ax.scatter(positions, ERV, label=f'Макс. длина волны {container[i]["peak_wavelengths"][0]}', s=90)
        ax.legend()



def creating_figure():
    csfont={'fontname': 'Times New Roman'}
    fig = plt.figure()
    ax = fig.add_subplot(1, 1, 1)
    ax.grid()
    for label in (ax.get_xticklabels() + ax.get_yticklabels()):
        label.set_fontsize(16)
    ax.set_title(f'Вариация эффективного радиуса', fontsize=28, **csfont)
    ax.set_xlabel(f'Номер измерения вдоль кольца', fontsize=28, **csfont)
    ax.set_xlim(6, 66)
    ax.set_ylabel(f'Вариация эффективного радиуса, мкм', fontsize=28, **csfont)
    return fig, ax



'''Запускается вручную при необходимости'''
def two_files_into_one():
    new_positions = []
    new_ERV = []
    new_wavelengths = []
    with open('2_34.pkl', 'rb') as f:
        tmp_sample = pickle.load(f)
        print(f'sample ERV are {tmp_sample["ERVs"]}')
        print(len(tmp_sample['positions'])//2 )
        print(tmp_sample['positions'])
        for k in range(0, len(tmp_sample['positions'])):
            new_positions.append(tmp_sample['positions'][k])
            new_ERV.append(tmp_sample['ERVs'][k])
            new_wavelengths.append(tmp_sample['peak_wavelengths'][k])
    with open('2_end.pkl', 'rb') as f:
        tmp_sample = pickle.load(f)
        print(f'sample ERV are {tmp_sample["ERVs"]}')
        print(f'tmp_sample keys are: {tmp_sample.keys()}')
        print(len(tmp_sample['positions'])//2 )
        print(tmp_sample['positions'])
        for k in range(0, len(tmp_sample['positions'])):
            new_positions.append(tmp_sample['positions'][k])
            new_ERV.append(tmp_sample['ERVs'][k])
            new_wavelengths.append(tmp_sample['peak_wavelengths'][k])
    new_positions = np.array(new_positions)
    new_ERV = np.array(new_ERV)
    new_wavelengths = np.array(new_wavelengths)
    new_sample = tmp_sample.copy()
    new_sample['positions'] = new_positions
    new_sample['ERVs'] = new_ERV
    new_sample['peak_wavelengths'] = new_wavelengths
    with open('new2.pkl', 'wb') as f:
        pickle.dump(new_sample, f)


container = opening()
extracting_container(container)
plt.show()

#two_files_into_one()
