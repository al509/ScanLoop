########
# Calculating spectra of WGM for different azimuthal and radial numbers 
#
#Using Demchenko, Y. A. and Gorodetsky, M. L., “Analytical estimates of eigenfrequencies, dispersion, and field distribution in whispering gallery resonators,” J. Opt. Soc. Am. B 30(11), 3056 (2013).
#
#See formula A3 for lambda_m_p
########

__version__='3.8'
__date__='2022.09.09'

 
import numpy as np
from scipy import special
from scipy import optimize
import matplotlib.pyplot as plt
from scipy.signal import find_peaks 
import scipy.optimize as sciopt
from scipy.fftpack import rfft, irfft, fftfreq
import pickle
from numba import jit




R_MIN = 62e3  #  В нанометрах (?) / Предыдущее значение 61e3
R_MAX = 63e3  #  В нанометрах (?) / Предыдущее значение 64e3
R_step=3


T_MIN = 18  #  В градусах Цельсия
T_MAX = 25  #  В градусах Цельсия
T_step=0.5

c = 299792458  #  m/s
thermal_optical_responce = 1.25e9  #  Hz/Celcium, detuning of the effective_ra
T_0 = 20   #  В градусах цельсия

Sellmeier_coeffs={
    'SiO2':[0.6961663, 0.4079426, 0.8974794, 0.0684043, 0.1162414, 9.896161], # at 20 Celcium degree, коеффициенты C1-C2 в микрометрах (0.0684043, 0.1162414, 9.896161)
    'MgF2':[0.48755108, 0.39875031, 2.3120353, 0.04338408, 0.09461442, 23.793604]}

thermal_responses={# thermal optical coefficient, linear expansion coefficient
    'SiO2':[8.6*1e-6,0.55*1e-6]}

REFRACTION = 1.4445

@jit(nopython=True) # Set "nopython" mode for best performance, equivalent to @njit
def SellmeierCoefficientsCalculating(material, T):
    T = T + 273
    sellmeier_coeffs = []
    if material == 'SiO2':
        sellmeier_coeffs.append(1.10127 + T*(-4.94251E-5) + (T**2)*(5.27414E-7) +
        (T**3)*(-1.597E-9) + (T**4)*(1.75949E-12))
        sellmeier_coeffs.append(1.78752E-05 + T*(4.76391E-5) + (T**2)*(-4.49019E-7) +
        (T**3)*(1.44546E-9) + (T**4)*(-1.57223E-12))
        sellmeier_coeffs.append(7.93552E-01 + T*(-1.27815E-3) + (T**2)*(1.84595E-5) +
        (T**3)*(-9.20275E-8) + (T**4)*(1.48829E-10))
        sellmeier_coeffs.append(-8.906E-2 + T*(9.08730E-6) + (T**2)*(-6.53638E-8) +
        (T**3)*(7.77072E-11) + (T**4)*(6.84605E-14))
        sellmeier_coeffs.append(2.97562E-01 + T*(-8.59578E-4) + (T**2)*(6.59069E-6) +
        (T**3)*(-1.09482E-8) + (T**4)*(7.85145E-13))
        sellmeier_coeffs.append(9.34454 + T*(-7.09788E-3) + (T**2)*(1.01968E-4) +
        (T**3)*(-5.0766E-7) + (T**4)*(8.21348E-10))
    else:
        pass
    return sellmeier_coeffs


def RefInd(w, medium, T, sellmeier_coeffs): # refractive index for quarzt versus wavelength, w in nm
    w = w * 1e-3
    t = 1
    for i in range(0,3):
       t += sellmeier_coeffs[i]*w**2/(w**2-sellmeier_coeffs[i+3]**2)
    return np.sqrt(t)# np.sqrt(t)*(1+(T-T_0)*thermal_responses[medium][0])


def airy_zero(p):
    t=[-2.338107410459767038489,-4.087949444130970616637,-5.52055982809555105913,-6.78670809007175899878,
       -7.944133587120853123138,-9.022650853340980380158,-10.0401743415580859306,-11.00852430373326289324]
    return t[p-1]

# @jit(nopython=True) # Set "nopython" mode for best performance, equivalent to @njit
def T(m,p):
    a=airy_zero(p)
    T = m-a*(m/2)**(1/3)+3/20*a**2*(m/2)**(-1/3) \
        + (a**3+10)/1400*(m/2)**(-1)-a*(479*a**3-40)/504000*(m/2)**(-5/3)-a**2*(20231*a**3+55100)/129360000*(m/2)**(-7/3)
    return T


def lambda_m_p_simplified(m, p, polarization, n, R_0, dispersion = False,
                          medium = 'SiO2', temperature = 20): #Using T. Hamidfar et al., “Suppl. Localization of light in an optical microcapillary induced by a droplet,” Optica, vol. 5, no. 4, p. 382, 2018.
    R_T= R_0*(1+thermal_responses[medium][1]*(temperature-T_0))
    sellmeier_coeffs = SellmeierCoefficientsCalculating(medium, temperature)
    if not dispersion:    
        if polarization=='TE':
            temp=( 1 + airy_zero(p)*(2*m**2)**(-1/3)+ n/(m*(n**2-1)**0.5))
        elif polarization=='TM':
            temp=( 1 + airy_zero(p)*(2*m**2)**(-1/3) + 1/n/(m*(n**2-1)**(0.5)) )
        
        return 2*np.pi*n*R_T/m*temp
    else:
        if polarization=='TE':
            res=optimize.root(lambda x: x-2*np.pi*RefInd(x, medium, temperature, sellmeier_coeffs)*R_T/m*( 1 + airy_zero(p)*(2*m**2)**(-1/3)+ RefInd(x, medium, temperature, sellmeier_coeffs)/(m*(RefInd(x, medium, temperature, sellmeier_coeffs)**2-1)**0.5)),1550)
            return res.x[0]
        elif polarization=='TM':
            res=optimize.root(lambda x: x-2*np.pi*RefInd(x, medium, temperature, sellmeier_coeffs)*R_T/m*( 1 + airy_zero(p)*(2*m**2)**(-1/3) + 1/RefInd(x, medium, temperature, sellmeier_coeffs)/(m*(RefInd(x, medium, temperature, sellmeier_coeffs)**2-1)**(0.5))),1550)
            return res.x[0]


def lambda_m_p_cylinder(m, p, polarization, n, R_0, dispersion = False,
                        medium = 'SiO2', simplified=False, temperature = 20): # following formula A3 from Demchenko and Gorodetsky
    R_T= R_0*(1+thermal_responses[medium][1]*(temperature-T_0))
    sellmeier_coeffs = SellmeierCoefficientsCalculating(medium, temperature)
    if not simplified:
        if not dispersion:
            if polarization=='TE':
                P=1
            elif polarization=='TM':
                P=1/n**2
            temp=T(m,p)-n*P/np.sqrt(n**2-1)+airy_zero(p)*(3-2*P**2)*P*n**3*(m/2)**(-2/3)/6/(n**2-1)**(3/2) \
                 - n**2*P*(P-1)*(P**2*n**2+P*n**2-1)*(m/2)**(-1)/4/(n**2-1)**2
            return 2*np.pi*n*R_T/temp
        elif dispersion:
            if polarization=='TE':
                res=optimize.root(lambda x: x-2*np.pi*RefInd(x, medium, temperature, sellmeier_coeffs)*R_T/(T(m,p)-RefInd(x, medium, temperature, sellmeier_coeffs)/np.sqrt(RefInd(x, medium, temperature, sellmeier_coeffs)**2-1)+
                                                                    airy_zero(p)*(3-2)*RefInd(x, medium, temperature, sellmeier_coeffs)**3*(m/2)**(-2/3)/6/(RefInd(x, medium, temperature, sellmeier_coeffs)**2-1)**(3/2)-
                                                                    -0),2000)
                # print(res.success)
                return res.x[0]
            elif polarization=='TM':
                res=optimize.root(lambda x: x-2*np.pi*RefInd(x, medium, temperature, sellmeier_coeffs)*R_T/(T(m,p)-1/RefInd(x, medium, temperature, sellmeier_coeffs)/np.sqrt(RefInd(x, medium, temperature, sellmeier_coeffs)**2-1)+
                                                                    airy_zero(p)*(3-2*RefInd(x, medium, temperature, sellmeier_coeffs)**(-4))*RefInd(x, medium, temperature, sellmeier_coeffs)*(m/2)**(-2/3)/6/(RefInd(x, medium, temperature, sellmeier_coeffs)**2-1)**(3/2) \
                 - 1*(1/RefInd(x, medium, temperature, sellmeier_coeffs)**2-1)*(1/RefInd(x, medium, temperature, sellmeier_coeffs)**2)*(m/2)**(-1)/4/(RefInd(x, medium, temperature, sellmeier_coeffs)**2-1)**2),1550)
                # print(res.success)
                return res.x[0]
    else:
        return lambda_m_p_simplified(medium,m,p,polarization,n,R_0,dispersion,medium,simplified, temperature)

           
def lambda_m_p_spheroid(m, p, polarization, n, a, b, dispersion = False,
                        medium = 'SiO2', simplified = False, temperature = 20): # following formula (15),(17) from Demchenko and Gorodetsky
     if not dispersion:
         if polarization=='TE':
             P=1
         elif polarization=='TM':
             P=1/n**2
         temp=m-airy_zero(p)*(m/2)**(1/3)+(2*p+1)*a/2/b+3*airy_zero(p)**2/20*(m/2)**(-1/3)*airy_zero(p)/12*(2*p+1)*a**3/b**3*(m/2)**(-2/3)
         +(airy_zero(p)**3/1400)*(m/2)**(-1)
        
         return 2*np.pi*n*R/temp
     elif dispersion:
         if polarization=='TE':
             res=optimize.root(lambda x: x-2*np.pi*RefInd(x,medium)*R/(T(m,p)-RefInd(x,medium)/np.sqrt(RefInd(x,medium)**2-1)+
                                                                 airy_zero(p)*(3-2)*RefInd(x,medium)**3*(m/2)**(-2/3)/6/(RefInd(x,medium)**2-1)**(3/2)-
                                                                 -0),2000)
             # print(res.success)
             return res.x[0]
         elif polarization=='TM':
             res=optimize.root(lambda x: x-2*np.pi*RefInd(x,medium)*R/(T(m,p)-1/RefInd(x,medium)/np.sqrt(RefInd(x,medium)**2-1)+
                                                                 airy_zero(p)*(3-2*RefInd(x,medium)**(-4))*RefInd(x,medium)*(m/2)**(-2/3)/6/(RefInd(x,medium)**2-1)**(3/2) \
              - 1*(1/RefInd(x,medium)**2-1)*(1/RefInd(x,medium)**2)*(m/2)**(-1)/4/(RefInd(x,medium)**2-1)**2),1550)
             # print(res.success)
             return res.x[0]


class Resonances():
    #########################
    ### Structure is as follows:
    ### {Polarization_dict-> list(p_number)-> np.array(m number)}
    
    colormap = plt.cm.gist_ncar #nipy_spectral, Set1,Paired   
    pmax = 3
    # dispersion=False
    def __init__(self, wave_min, wave_max, n, R, p_max=3,
                 material_dispersion=True, shape='cylinder', medium='SiO2',
                 simplified=False, temperature=20):
        m0=np.floor(2*np.pi*n*R/wave_max)
        self.medium=medium
        self.pmax=p_max
        self.structure={'TE':[],'TM':[]}
        self.material_dispersion=material_dispersion
        self.simplified=simplified
        self.N_of_resonances={'TE':0,'TM':0,'Total':0}
        if shape=='cylinder':
            lambda_m_p=lambda_m_p_cylinder
        elif shape=='sphere':
            lambda_m_p=lambda_m_p_spheroid(b=R)
            
        for Pol in ['TE','TM']:
            
            p=1
            if Pol=='TE':
                m=int(np.floor(m0*( 1 + airy_zero(p)*(2*m0**2)**(-1/3)+ n/(m0*(n**2-1)**0.5))))-4
            else:
                m=int(np.floor(m0*( 1 + airy_zero(p)*(2*m0**2)**(-1/3)+ 1/n/(m0*(n**2-1)**0.5))))-4
            wave = lambda_m_p(m, p, Pol, n, R, self.material_dispersion, self.medium, simplified=self.simplified, temperature=temperature)
            
            while wave>wave_min and p<self.pmax+1: 
                resonance_temp_list=[]
                resonance_m_list=[]
                while wave>wave_min: 
                    if wave<wave_max:
                        resonance_temp_list.append(wave)
                        resonance_m_list.append(m)
                        self.N_of_resonances[Pol]+=1
                        self.N_of_resonances['Total']+=1
                    m+=1
                    wave=lambda_m_p(m, p, Pol, n, R, self.material_dispersion, self.medium, simplified=self.simplified, temperature=temperature)
                
                Temp=np.column_stack((np.array(resonance_temp_list),np.array(resonance_m_list)))
                self.structure[Pol].append(Temp)
                p+=1
                if Pol=='TE':
                    m=np.floor(m0*( 1 + airy_zero(p)*(2*m0**2)**(-1/3)+ n/(m0*(n**2-1)**0.5)))-3
                else:
                    m=np.floor(m0*( 1 + airy_zero(p)*(2*m0**2)**(-1/3)+ 1/n/(m0*(n**2-1)**0.5)))-3
                wave=lambda_m_p(m, p, Pol, n, R, self.material_dispersion, self.medium, simplified=self.simplified, temperature=temperature)
        
                
    def create_unstructured_list(self,Polarizations_to_account):  
        if Polarizations_to_account=='both' or Polarizations_to_account=='single':
            Polarizations=['TE','TM']
        elif Polarizations_to_account=='TE':
            Polarizations=['TE']
        elif Polarizations_to_account=='TM':
            Polarizations=['TM']
        list_of_resonances=[]
        list_of_labels=[]
        for Pol in Polarizations:
            for p,L in enumerate(self.structure[Pol]):
                for wave,m in L:
                    list_of_resonances.append(wave)
                    list_of_labels.append(Pol+','+str(int(m))+','+str(p+1))
                    
        labels=[x for _,x in sorted(zip(list_of_resonances,list_of_labels))]#, key=lambda pair: pair[0])]
        resonances=sorted(list_of_resonances)
        return np.array(resonances),labels
    

    def plot_all(self,y_min,y_max,Polarizations_to_account):
        # plt.gca().set_color_cycle([colormap(i) for i in np.linspace(0, 0.9, num_plots)])
        resonances,labels=self.create_unstructured_list(Polarizations_to_account)
        for i,wave in enumerate(resonances):
            if labels[i].split(',')[0]=='TM':
                color='blue'
            else:
                color='red'
            plt.axvline(wave, 0, 1, color=color)
            y = y_min + (y_max - y_min)/self.pmax*float(labels[i].split(',')[2])
            plt.annotate(labels[i],(wave,y))
            
    def get_int_dispersion(self, polarization='TE',p=1):
        '''
        using D_int=omega_i-omega_0-D_1*i
        D_1=averaged FSR
        '''
        if p>self.pmax:
            print('error:radial quantum number p > p_max ')
        else:
            wavelengths=self.structure[polarization][p-1][:,0]
            N=np.shape(wavelengths)[0]
            freqs=c/wavelengths*1e9
            N_central=N//2
            FSR=np.abs(freqs[N_central+1]-freqs[N_central-1])/2
            D_int=freqs-freqs[N_central]-FSR*(np.arange(0, N)-N_central)
            return freqs,D_int
        
    def plot_int_dispersion(self, polarization='TE',p=1):
        freqs,D_int=self.get_int_dispersion(polarization,p)
        plt.figure()
        plt.plot(freqs*1e-12, D_int*1e-6)
        plt.xlabel('Frequency, THz')
        plt.ylabel('Dispersion $D_{int}$, MHz')
        plt.tight_layout()
            
     
     
def closest_argmin(A, B): # from https://stackoverflow.com/questions/45349561/find-nearest-indices-for-one-array-against-all-values-in-another-array-python
    L = B.size
    sidx_B = B.argsort()
    sorted_B = B[sidx_B]
    sorted_idx = np.searchsorted(sorted_B, A)
    sorted_idx[sorted_idx==L] = L-1
    mask = (sorted_idx > 0) & \
    ((np.abs(A - sorted_B[sorted_idx-1]) < np.abs(A - sorted_B[sorted_idx])) )
    return sidx_B[sorted_idx-mask]       


def FFTFilter(y_array):
    FilterLowFreqEdge=0.00
    FilterHighFreqEdge=0.01
    W=fftfreq(y_array.size)
    f_array = rfft(y_array)
    Indexes=[i for  i,w  in enumerate(W) if all([abs(w)>FilterLowFreqEdge,abs(w)<FilterHighFreqEdge])]
    f_array[Indexes] = 0
    # f_array[] = 0
    return irfft(f_array)


class Fitter():
    
    def __init__(self,
                 wavelengths,signal,peak_depth,peak_distance,wave_min=None,wave_max=None,
                 p_guess_array=None,dispersion=True,simplified=False,polarization='both',
                 FFT_filter=False, type_of_optimizer='bruteforce', temperature=20,vary_temperature=False):
        
        p_guess_max=5
        
        if wave_min is not None:
            self.wave_min=wave_min
        else:
            self.wave_min=min(wavelengths)
        if wave_max is not None:
            self.wave_max=wave_max
        else:
            self.wave_max=max(wavelengths)
        
        index_min=np.argmin(abs(wavelengths-self.wave_min))
        index_max=np.argmin(abs(wavelengths-self.wave_max))
        self.wavelengths=wavelengths[index_min:index_max]
        self.signal=signal[index_min:index_max]
        if FFT_filter:
            self.signal=FFTFilter(self.signal)
        self.resonances_indexes,_=find_peaks(abs(self.signal-np.nanmean(self.signal)),height=peak_depth,distance=peak_distance)
        self.exp_resonances=self.wavelengths[self.resonances_indexes]
        self.polarizations=polarization
        self.material_dispersion=dispersion
        self.type_of_optimizer=type_of_optimizer
        
        self.vary_temperature=vary_temperature
        
        self.R_array=np.arange(R_MIN, R_MAX, R_step)
        if vary_temperature:
            self.T_array=np.arange(T_MIN,T_MAX, T_step)
        else:
            self.T_array=np.array(temperature,ndmin=1)
        self.cost_function_array=None
        
        self.cost_best=1e3
        self.n_best, self.R_best, self.p_best, self.th_resonances, self.T_best = None, None, None, None, None
       
        if p_guess_array is not None:
            self.p_guess_array=p_guess_array
        else:
            self.p_guess_array=np.arange(1,p_guess_max)
        
    def run(self, figure, ax):
        '''
        Перебор по температуре и радиусам
        '''
        for p in self.p_guess_array:
            if self.type_of_optimizer=='Nelder-Mead':
                res=sciopt.minimize(self.cost_function,((1.4445,62.5e3)),bounds=((1.443,1.4447),(62e3,63e3)),
                            args=p,method='Nelder-Mead',options={'maxiter':1000},tol=1e-11)
            elif self.type_of_optimizer=='bruteforce':
                res = bruteforce_optimizer(self.cost_function, figure, ax,
                                          (p, REFRACTION),
                                          self.R_array, 
                                          self.T_array)
            
            # print(f'p = {res}')
            if res['fun']<self.cost_best:
                self.cost_best = res['fun']
                self.n_best = res['x'][0]
                self.R_best = res['x'][1]
                self.T_best = res['x'][2]
                self.p_best = p
                self.cost_function_array=res['cost_function_array']
        self.th_resonances=Resonances(self.wave_min, self.wave_max,
                                      self.n_best, self.R_best, self.p_best,
                                      self.material_dispersion, temperature=self.T_best)
        
        # self.th_resonances=Resonances(self.wave_min, self.wave_max,
        #                               REFRACTION, 62516, self.p_guess_array[0],
        #                               self.material_dispersion, temperature=18.5)
                
        
    def cost_function(self, param, p_max): # try one and another polarization
        def measure(exp, theory, resonances_amount):
            closest_indexes=closest_argmin(exp, theory)
            return sum((exp-theory[closest_indexes])**2)/resonances_amount
        
        n, R, temperature = param
        resonances=Resonances(self.wave_min, self.wave_max, n, R, p_max,
                              self.material_dispersion, temperature=temperature)
        if self.polarizations=='both':
            if resonances.N_of_resonances['Total']>0:
                th_resonances,labels=resonances.create_unstructured_list('both')
                return measure(self.exp_resonances, th_resonances, len(self.exp_resonances))
            else:
                return 1e3
            
        elif self.polarizations=='single':
            if resonances.N_of_resonances['TE']>0:
                th_resonances,labels=resonances.create_unstructured_list('TE')
                cost_TE=measure(self.exp_resonances, th_resonances, len(self.exp_resonances))
            else:
                cost_TE=1e3
            if resonances.N_of_resonances['TM']>0:
                th_resonances,labels=resonances.create_unstructured_list('TM')
                cost_TM=measure(self.exp_resonances, th_resonances, len(self.exp_resonances))
            else:
                cost_TM=1e3
            return min([cost_TE,cost_TM])    

        
    def plot_results(self):
        # fig, axs = plt.subplots(2, 1, sharex=True)
        fig, axs = plt.subplots(1, 1)
        axs.plot(self.wavelengths,self.signal)
        axs.plot(self.exp_resonances,self.signal[self.resonances_indexes],'.')
        # axs.set_title('N=%d' % len(self.exp_resonances))
        # plt.sca(axs[1])
        self.th_resonances.plot_all(min(self.signal),max(self.signal),'both')
        axs.set_title('N_exp=%d , N_th=%d,n=%f,R=%f,p_max=%d, cost_function=%f' % (len(self.exp_resonances),self.th_resonances.N_of_resonances['Total'],self.n_best,self.R_best,self.p_best, self.cost_best))
        plt.xlabel('Wavelength,nm')

'''
Функция для постройки графика функции ошибки, pyplot ругается на thread

def CostFunctionPlotCreation():
    figure = plt.figure()
    ax = figure.add_subplot(1, 1, 1)
    ax.grid()
    ax.set_title('Radius dependent cost function', fontsize=14)
    ax.set_xlabel('Radius, $\mu m$', fontsize=14)
    ax.set_ylabel('Cost function', fontsize=14)
    return figure, ax
'''

def bruteforce_optimizer(f, figure, ax, args, R_array, T_array):
    p, n = args
    cost_best = 1e5
    R_best = R_array[0]
    T_best = T_array[0]
    # colors = ['gold', 'aqua', 'violet', 'lawngreen', 'gray', 'tomato',
    #           'darkgreen', 'teal', 'indigo', 'crimson', 'bisque', 'deepskyblue',
    #           'black', 'olive', 'rosybrown']
    ind = 0

    cost_function_array=np.zeros((np.size(R_array),np.size(T_array)))
    for jj,current_R in enumerate(R_array):
        for ii,current_T in enumerate(T_array):
            cost = f((n, current_R, current_T), p)
            cost_function_array[jj,ii]=cost
            if cost < cost_best:
                cost_best = cost
                R_best = current_R
                T_best = current_T
     
                
            # ax.scatter(current_R, cost, color=colors[ind], s=8)
            print(f'R = {current_R}, T = {current_T}, Cost = {cost}')
        ind = ind + 1

    return {'x':(n, R_best, T_best),'fun':cost_best,'cost_function_array':cost_function_array}

        
            

if __name__=='__main__':
    # print(lambda_m_p(m=354,p=1,polarization='TM',n=1.445,R=62.5e3,dispersion=True))
    wave_min = 1540
    wave_max = 1582
    n = REFRACTION
    R = 62514
    p_max = 3
    medium='SiO2'
    shape='cylinder'
    material_dispersion=True
    resonances=Resonances(wave_min, wave_max, n, R, p_max, material_dispersion,shape,medium, temperature=20)
    figure = plt.figure()
    resonances.plot_all(-3, 3, 'both')
    print(SellmeierCoefficientsCalculating('SiO2', 293))
    resonances.plot_int_dispersion(polarization='TM',p=1)
    
    # single_spectrum_path = '..\\TMP_folder\\WGM_data\\Test_2_at_25.0.pkl'
    # with open(single_spectrum_path,'rb') as f:
    #     print('loading data for analyzer from ',single_spectrum_path)
    #     Data=(pickle.load(f))
    # single_spectrum_figure=plt.figure()
    # plt.plot(Data[:,0],Data[:,1])
    # plt.xlabel('Wavelength, nm')
    # plt.ylabel('Spectral power density, dBm')
    # plt.tight_layout()
    # resonances=Resonances(wave_min, wave_max, n, R, p_max, material_dispersion, shape, medium, temperature=24)
    # resonances.plot_all(-3, 3, 'both')
    
    # #filename="F:\!Projects\!SNAP system\Modifications\Wire heating\dump_data_at_-2600.0.pkl"
    # #import pickle
    # #with open(filename,'rb') as f:
    # #    Temp=pickle.load(f)
    # #fitter=Fitter(Temp[:,0],Temp[:,1],0.8,100,p_guess_array=[3],polarization='single',dispersion=True, temperature=25)
    # fitter.run()
    # fitter.plot_results()

    # filename="F:\!Projects\!SNAP system\Modifications\Wire heating\dump_data_at_-2600.0.pkl"
    # import pickle
    # with open(filename,'rb') as f:
    #     Temp=pickle.load(f)
    # fitter=Fitter(Temp[:,0],Temp[:,1],0.8,100,p_guess_array=[3],polarization='single',dispersion=True, temperature=25)
    # fitter.run()
    # fitter.plot_results()


