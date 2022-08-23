import numpy as np
import pickle

def main():
    filename = open("polarizations1.pkl", "rb")
    data = pickle.load(filename)
    print('1 polarization is: ', data[3])
    filename.close()
    
    filename = open("waves1.pkl", "rb")
    data = pickle.load(filename)
    print('1 wavelength is: ', data[3])
    filename.close()
    
    filename = open("polarizations2.pkl", "rb")
    data = pickle.load(filename)
    print('2 polarization is: ', data[0])
    filename.close()
    
    filename = open("waves2.pkl", "rb")
    data = pickle.load(filename)
    print('2 wavelength is: ', data[0])
    filename.close()
    
    filename = open("polarizations3.pkl", "rb")
    data = pickle.load(filename)
    print('3 polarization is: ', data[0])
    filename.close()
    
    filename = open("waves3.pkl", "rb")
    data = pickle.load(filename)
    print('3 wavelength is: ', data[0])
    filename.close()
    '''
    filename = open("polarizations4.pkl", "rb")
    data = pickle.load(filename)
    print(data[0])
    filename.close()
    
    filename = open("waves4.pkl", "rb")
    data = pickle.load(filename)
    print(data[0])
    filename.close()
    
    filename = open("polarizations5.pkl", "rb")
    data = pickle.load(filename)
    print(data[0])
    filename.close()
    
    filename = open("waves5.pkl", "rb")
    data = pickle.load(filename)
    print(data[0])
    filename.close()
    '''
    return 0

if __name__ == '__main__':
    main()