__version__='0.4'
__date__='2023.08.16'



import numpy as np
import scipy.linalg as la
import pickle
from numba import njit

c=299792458 # m/s



def load_OVA_spectrum(path):
     if '.bin' in path:
         Spectrum=OVA_spectrum()
         it = np.dtype([('x_0',np.float64), ('x_step', np.float64), 
             ('name_string', np.byte, 8), ('meas_num',np.int32),
             ('type', np.int8), ('length', np.float64), ('unknown', np.byte, 4),
             ('avg_disp', np.float64), ('ref_wvl', np.float64),
             ('disp_slope', np.float64), ('pulse_compr', np.float64), 
             ('year', np.int16), ('month', np.int16), ('weekday',np.int16),
             ('day', np.int16), ('hour',np.int16), ('minute', np.int16),
             ('second', np.int16), ('millisecond', np.int16)])
        
        
         info = np.fromfile(path,dtype=it, count=1)
         Spectrum.info=info
         Spectrum.x_0=info['x_0'][0]
         Spectrum.x_step=info['x_step'][0]
         Spectrum.meas_num=info['meas_num'][0]
        
         data= np.fromfile(path, dtype='4c16', 
             count=info['meas_num'][0], offset = info.nbytes)
         Spectrum.jones_matrixes=[np.array([[a[0],a[1]],[a[2],a[3]]],dtype='complex_') for a in data]
         
         
         
     elif '.pklOVA' in path:
         with open(path,'rb') as f:
             Spectrum=pickle.load(f)
             
     return Spectrum


class OVA_spectrum():
    def __init__(self):
        self.x_0 = None
        self.x_step = None
        self.meas_num = None
        self.jones_matrixes=None
        self.info=None
        
    def fetch_xaxis(self, n=0):
        x0 = self.x_0
        dx = self.x_step
        x_n = x0 - dx*self.meas_num
        frequency_array=np.linspace(x0, x_n, num=self.meas_num)
        if n==0: # in nm
            return c/frequency_array, 'Wavelength, nm'
        if n==1:
            return frequency_array, 'Frequency, GHz'
        if n==2:
            return frequency_array/1e3, 'Frequency, THz'
        
    
    def fetch_meas(self, type_of_meas):
        if type_of_meas=='Insertion Losses' : # Insertion losses
            return self.IL(), 'Insertion losses, dB'
        if type_of_meas=='Min and Max Losses': # PDL
            return self.min_max_losses(), 'Min and Max Losses, dB'
        if type_of_meas=='Group delay': # 
            return self.group_delay(), 'Group delay, ps'
        if type_of_meas=='Chromatic dispersion': #
            return self.chromatic_dispersion(),'Chromatic dispersion, ps/nm'
        if type_of_meas=='PDL': #
            return self.PDL(),'PDL, dB'
        
    
    def IL(self): 
        '''
        insertion losses
        '''
        return 10*np.log10([np.sum(np.absolute(m)**2)/2 for m in self.jones_matrixes]).transpose() 
        # amps = np.absolute(self.data)
        # return 10*np.log10((amps[:,0]**2 + amps[:,1]**2 + amps[:,2]**2 + amps[:,3]**2)/2).transpose()
        
    def complex_IL(self):
        '''
        linear Complex losses in two principal polarizations
        Use two Luna object In and OUT of contact with the microcavity

        '''
        pol_1=np.zeros(self.meas_num,dtype='complex_')
        pol_2=np.zeros(self.meas_num,dtype='complex_')
        
        for i,m in enumerate(self.jones_matrixes):
            [pol_1[i],pol_2[i]]=la.eigvals(m)
        
        return pol_1,pol_2
        
    def min_max_losses(self):
        '''
        losses in two principal polarizations
        '''
        
        diag_jones_squared=[la.eigvals(np.dot(m.conj().T,m)) for m in self.jones_matrixes]
        PDL1=[m[0] for m in diag_jones_squared]
        PDL2=[m[1] for m in diag_jones_squared]
        return 10*np.log10(np.array([abs(np.array(PDL1)), abs(np.array(PDL2))]))
    
    def min_max_losses_complex(self):
        '''
        complex losses in two principal polarizations
        '''        
        diag_jones_squared=[la.eigvals(m) for m in self.jones_matrixes]
        PDL1=[m[0] for m in diag_jones_squared]
        PDL2=[m[1] for m in diag_jones_squared]
        return np.array(PDL1,dtype='complex_'),np.array(PDL2,dtype='complex_')
    
    def PDL(self):
        '''
        Complex losses in two principal polarizations
        '''
        data=self.min_max_losses()
        return data[0,:]-data[1,:]
    
    def group_delay(self):
        data=list_of_matrixes_to_array(self.jones_matrixes)
        temp=np.angle(data[1:,0]*data[:-1,0].conj()+data[1:,1]*data[:-1,1].conj()+
                      data[1:,2]*data[:-1,2].conj()+data[1:,3]*data[:-1,3].conj())
        temp[np.where(temp<0)]+=np.pi*2
        return np.concatenate(([np.mean(temp)],temp))/(2*np.pi*self.x_step)*1e3
    
    def chromatic_dispersion(self):
        delta_lambda=c/(self.x_0)**2*self.x_step
        GD=self.group_delay()
        temp=GD[1:]-GD[:-1]
        return np.concatenate(([np.mean(temp)],temp))/delta_lambda
    
    


def list_of_matrixes_to_array(jones_matrixes):
    data=np.zeros((len(jones_matrixes),4),dtype = 'complex_')
    for ii,m in enumerate(jones_matrixes):
        data[ii]=[m[0,0],m[0,1],m[1,0],m[1,1]]
    return data

def array_to_list_of_matrixes(array):
    l=[]
    for ii,row in enumerate(array):
        l.append(np.array([row[0],row[1]],[row[2],row[3]]))
    return l

# @njit    
def complex_IL_remove_out_of_contact(T_in:OVA_spectrum,T_out:OVA_spectrum)->complex:
    '''
    linear Complex losses in two principal polarizations
    Use two Luna object In and OUT of contact with the microcavity
    Let us suppose that Jones matrixes for input part of the taper and output part of the tapers are I and O correspondingly. Then: 
        J_M= O*J_R*I 
        and J_0=O*I
        
        J_0^(-1) J_M=I^(-1) J_R I = I^* J_R I
        
        We know that diag(I^*  J_R I)==diag(J_R), so diag(J_R)=diag(J_0^(-1) J_M)

    
    '''
    pol_1=np.zeros(T_in.meas_num,dtype='complex_')
    pol_2=np.zeros(T_in.meas_num,dtype='complex_')
    for i,m_in in enumerate(T_in.jones_matrixes):
        # print(i)
        m_out=T_out.jones_matrixes[i]
        [pol_1[i],pol_2[i]]=la.eigvals(np.dot(la.inv(m_out),m_in))
    
    return pol_1,pol_2

if __name__=='__main__':
    import os 
    import matplotlib.pyplot as plt
    os.chdir('..')
    filepath='examples\\scan_some.bin'
    Data = load_OVA_spectrum(filepath)
    
    # plt.plot(Data.group_delay())
    
