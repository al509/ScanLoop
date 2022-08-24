import pickle
import numpy as np
import matplotlib.pyplot as plt
import matplotlib as mpl

class Graph():
    def __init__(self, label, wavelengths, ervs, positions):
        self.label = label
        self.wavelengths = wavelengths
        self.ervs = ervs
        self.positions = positions


def Opening():
    data = ['1544,9.pkl', '1549,1.pkl', '1553,3.pkl', '1557,7.pkl',
                 '1561,9.pkl', '1566,3.pkl', '1570,74.pkl']
    labels, polarizations = '10_position_slice_labels.pkl', '10_position_slice_polariz.pkl'
    graphs_array = []
    with open(labels, 'rb') as label_file:
        with open(polarizations, 'rb') as polarization_file:
            label_sample = pickle.load(label_file)
            polarization_sample = pickle.load(polarization_file)
            for i in data:
                with open(i, 'rb') as data_file:
                    data_sample = pickle.load(data_file)
                    graph = Graph(polarization_sample[np.argmin(abs(label_sample - data_sample['peak_wavelengths'][10]))],
                                  data_sample['peak_wavelengths'],
                                  data_sample['ERVs'],
                                  data_sample['positions'])
                    graphs_array.append(graph)
    graphs_array = np.array(graphs_array)
    return graphs_array
    

def ExtractingContainer(container):
    fig, ax = CreatingFigure()
    mpl.rc('font',family='Times New Roman')
    csfont={'fontname': 'Times New Roman'}
    for i in range(0, len(container)):
        positions = container[i].positions
        ERV = container[i].ervs
        ax.scatter(positions, ERV,
                   label=f'{container[i].label}', s=90)
        ax.legend()


def CreatingFigure():
    csfont={'fontname': 'Times New Roman'}
    fig = plt.figure()
    ax = fig.add_subplot(1, 1, 1)
    ax.grid()
    for label in (ax.get_xticklabels() + ax.get_yticklabels()):
        label.set_fontsize(16)
    ax.set_title(f'Effecitve Radius Variation', fontsize=28, **csfont)
    ax.set_xlabel(f'Measurement', fontsize=28, **csfont)  #  Лабщик говорил, что это плохо. Спросить!
    ax.set_xlim(6, 66)
    ax.set_ylabel(f'ERV,  $\mu m$', fontsize=28, **csfont)
    return fig, ax


'''Запускается вручную при необходимости'''
def TwoFilesIntoOne():
    new_positions = []
    new_ERV = []
    new_wavelengths = []
    with open('new.pkl', 'rb') as f:
        tmp_sample = pickle.load(f)
        print(f'sample ERV are {tmp_sample["ERVs"]}')
        print(len(tmp_sample['positions'])//2 )
        print(tmp_sample['positions'])
        for k in range(0, 23):
            new_positions.append(tmp_sample['positions'][k])
            new_ERV.append(tmp_sample['ERVs'][k])
            new_wavelengths.append(tmp_sample['peak_wavelengths'][k])
    with open('3.pkl', 'rb') as f:
        tmp_sample = pickle.load(f)
        print(f'sample ERV are {tmp_sample["ERVs"]}')
        print(f'tmp_sample keys are: {tmp_sample.keys()}')
        print(len(tmp_sample['positions'])//2 )
        print(tmp_sample['positions'])
        for k in range(23, len(tmp_sample['positions'])):
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
    
if __name__ == "__main__":
    container = Opening()
    ExtractingContainer(container)
    plt.show()
    #two_files_into_one()
