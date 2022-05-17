########
# Calculating spectra of WGM for different azimuthal and radial numbers 
#
#Using Demchenko, Y. A. and Gorodetsky, M. L., “Analytical estimates of eigenfrequencies, dispersion, and field distribution in whispering gallery resonators,” J. Opt. Soc. Am. B 30(11), 3056 (2013).
#
#See formula A3 for lambda_m_p
########

__version__='3'
__date__='2022.05.17'

import numpy as np
from scipy import special
from scipy import optimize
import matplotlib.pyplot as plt
from scipy.signal import find_peaks
import scipy.optimize as sciopt



def ref_ind(w): # refractive index versus wavelength, w in nm
    w=w*1e-3
    return np.sqrt(0.6961663*w**2/(w**2-0.0684043**2) +0.4079426*w**2/(w**2-0.1162414**2) +0.8974794*w**2/(w**2-9.896161**2)+1)

def airy_zero(p):
    t=[-2.338107410459767038489,-4.087949444130970616637,-5.52055982809555105913,-6.78670809007175899878,
       -7.944133587120853123138,-9.022650853340980380158,-10.0401743415580859306,-11.00852430373326289324]
    return t[p]

def T(m,p):
    a=airy_zero(p)
    T = m-a*(m/2)**(1/3)+3/20*a**2*(m/2)**(-1/3) \
        + (a**3+10)/1400*(m/2)**(-1)-a*(479*a**3-40)/504000*(m/2)**(-5/3)
    return T



def lambda_m_p(m,p,polarization,n,R,dispersion=False): # following formula A3 from Demchenko and Gorodetsky
    if not dispersion:
        if polarization=='TE':
            P=1
        elif polarization=='TM':
            P=1/n**2
        temp=T(m,p)-n*P/np.sqrt(n**2-1)+airy_zero(p)*(3-2*P**2)*P*n**3*(m/2)**(-2/3)/6/(n**2-1)**(3/2) \
             - n**2*P*(P-1)*(P**2*n**2+P*n**2-1)*(m/2)**(-1)/4/(n**2-1)**2
        return 2*np.pi*n*R/temp
    elif dispersion:
        if polarization=='TE':
            res=optimize.root(lambda x: x-2*np.pi*ref_ind(x)*R/(T(m,p)-ref_ind(x)/np.sqrt(ref_ind(x)**2-1)+airy_zero(p)*(3-2)*ref_ind(x)**3*(m/2)**(-2/3)/6/(ref_ind(x)**2-1)**(3/2)),1550)
            # print(res.success)
            return res.x[0]
        elif polarization=='TM':
            res=optimize.root(lambda x: x-2*np.pi*ref_ind(x)*R/(T(m,p)-1/ref_ind(x)/np.sqrt(ref_ind(x)**2-1)+airy_zero(p)*(3-2*ref_ind(x)**2)*ref_ind(x)*(m/2)**(-2/3)/6/(ref_ind(x)**2-1)**(3/2) \
             - (1/ref_ind(x)**2-1)*(1/ref_ind(x)**2)*(m/2)**(-1)/4/(ref_ind(x)**2-1)**2),1550)
            # print(res.success)
            return res.x[0]
            




class Resonances():
    #########################
    ### Structure is as follows:
    ### {Polarization_dict-> list(p_number)-> np.array(m number)}
    
    colormap = plt.cm.gist_ncar #nipy_spectral, Set1,Paired   
    pmax=10
    dispersion=False
    
    def __init__(self,wave_min,wave_max,n,R,p_max=10,dispersion=False):
        m0=np.floor(2*np.pi*n*R/wave_max)
        self.pmax=p_max
        self.structure={'TE':[],'TM':[]}
        self.dispersion=dispersion
        self.N_of_resonances={'TE':0,'TM':0,'Total':0}
        
        for Pol in ['TE','TM']:
            
            p=1
            if Pol=='TE':
                m=int(np.floor(m0*( 1 + airy_zero(p)*(2*m0**2)**(-1/3)+ n/(m0*(n**2-1)**0.5))))-4
            else:
                m=int(np.floor(m0*( 1 + airy_zero(p)*(2*m0**2)**(-1/3)+ 1/n/(m0*(n**2-1)**0.5))))-4
            wave=lambda_m_p(m,p,Pol,n,R,self.dispersion)
            
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
                    wave=lambda_m_p(m,p,Pol,n,R,self.dispersion)
                
                Temp=np.column_stack((np.array(resonance_temp_list),np.array(resonance_m_list)))
                self.structure[Pol].append(Temp)
                p+=1
                if Pol=='TE':
                    m=np.floor(m0*( 1 + airy_zero(p)*(2*m0**2)**(-1/3)+ n/(m0*(n**2-1)**0.5)))-3
                else:
                    m=np.floor(m0*( 1 + airy_zero(p)*(2*m0**2)**(-1/3)+ 1/n/(m0*(n**2-1)**0.5)))-3
                wave=lambda_m_p(m,p,Pol,n,R,self.dispersion)
        
                
    def create_unstructured_list(self,Polarizations_to_account):  
        if Polarizations_to_account=='both':
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
    
                       
    # def find_max_distance(self):
    #     res,_=self.create_unstructured_list(Polarizations)
    #     return np.max(np.diff(res))
    
    def plot_all(self,y_min,y_max,Polarizations_to_account):
#        plt.gca().set_color_cycle([colormap(i) for i in np.linspace(0, 0.9, num_plots)])
        resonances,labels=self.create_unstructured_list(Polarizations_to_account)
        for i,wave in enumerate(resonances):
            if labels[i].split(',')[0]=='TM':
                color='blue'
            else:
                color='red'
            plt.axvline(wave,ymin=y_min,ymax=y_max,color=color)
            y=y_min+(y_max-y_min)/self.pmax*float(labels[i].split(',')[2])
            plt.annotate(labels[i],(wave,y))
            
     
     
def closest_argmin(A, B): # from https://stackoverflow.com/questions/45349561/find-nearest-indices-for-one-array-against-all-values-in-another-array-python
    L = B.size
    sidx_B = B.argsort()
    sorted_B = B[sidx_B]
    sorted_idx = np.searchsorted(sorted_B, A)
    sorted_idx[sorted_idx==L] = L-1
    mask = (sorted_idx > 0) & \
    ((np.abs(A - sorted_B[sorted_idx-1]) < np.abs(A - sorted_B[sorted_idx])) )
    return sidx_B[sorted_idx-mask]       
     
class fitter():
    
    def __init__(self,
                 wavelengths,signal,peak_depth,peak_distance,wave_min=None,wave_max=None,
                 p_guess_array=None,dispersion=True,polarizations='both'):
        
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
        self.resonances_indexes,_=find_peaks(abs(self.signal-np.nanmean(self.signal)),height=peak_depth,distance=peak_distance)
        self.exp_resonances=self.wavelengths[self.resonances_indexes]
        self.polarizations=polarizations
        self.dispersion=dispersion
        
        self.cost_best=1e3
        self.n_best,self.R_best,self.p_best=None,None,None
       
        if p_guess_array is not None:
            self.p_guess_array=p_guess_array
        else:
            self.p_guess_array=np.arange(1,p_guess_max)
        
    def run(self):
        for p in self.p_guess_array:
            res=sciopt.minimize(self.cost_function,((1.4445,62.5e3)),bounds=((1.443,1.4447),(62e3,63e3)),
                            args=p,method='Powell',options={'maxiter':1000},tol=1e-11)
            # res=sciopt.least_squares(func_to_minimize,((1.43,62.5e3)),bounds=((1.4,1.5),(62e3,63e3)),
            #                 args=(Wavelength_min,Wavelength_max,Resonances_exp,p),xtol=1e-10,ftol=1e-10)
            # res=sciopt.least_squares(func_to_minimize,(62.5e3),bounds=(62e3,63e3),
                            # args=(Wavelength_min,Wavelength_max,Resonances_exp,p),xtol=1e-8,ftol=1e-8)
            
            print('p={}'.format(p),res)
            if res['fun']<self.cost_best:
                self.cost_best=res['fun']
                self.n_best=res['x'][0]
                self.R_best=res['x'][1]
                self.p_best=p
                
        

                
    def cost_function(self,param,p_max): # try one and another polarization
        def measure(exp,theory):
            return sum((exp-theory)**2)
        
        n,R=param
        # (p_max)=p
        resonances=Resonances(self.wave_min,self.wave_max,n,R,p_max,self.dispersion)
        
        if self.polarizations=='both':
            if resonances.N_of_resonances['Total']>0:
                th_resonances,labels=resonances.create_unstructured_list('both')
                closest_indexes=closest_argmin(self.exp_resonances,th_resonances)   
                return measure(self.exp_resonances,th_resonances[closest_indexes])
            else:
                return 1e3
            
        elif self.polarizations=='single':
            if resonances.N_of_resonances['TE']>0:
                th_resonances,labels=resonances.create_unstructured_list('TE')
                closest_indexes=closest_argmin(self.exp_resonances,th_resonances)   
                cost_TE=measure(self.exp_resonances,th_resonances[closest_indexes])
            else:
                cost_TE=1e3
            if resonances.N_of_resonances['TM']>0:
                th_resonances,labels=resonances.create_unstructured_list('TM')
                closest_indexes=closest_argmin(self.exp_resonances,th_resonances)
                cost_TM=measure(self.exp_resonances,th_resonances[closest_indexes])
            else:
                cost_TM=1e3
            return min([cost_TE,cost_TM])    
        
    def plot_results(self):
        fig, axs = plt.subplots(2, 1, sharex=True)
        axs[0].plot(self.wavelengths,self.signal)
        axs[0].plot(self.exp_resonances,self.signal[self.resonances_indexes],'.')
        axs[0].set_title('N=%d' % len(self.exp_resonances))

        Resonances_th=Resonances(self.wave_min,self.wave_max,self.n_best,self.R_best,self.p_best,self.dispersion)
        plt.sca(axs[1])
        Resonances_th.plot_all(-1,1,'both')
        axs[1].set_title('N=%d,n=%f,R=%f,p_max=%d' % (Resonances_th.N_of_resonances['Total'],self.n_best,self.R_best,self.p_best))
        plt.xlabel('Wavelength,nm')
    
    
# def fit_quantum_numbers(Signal,MinimumPeakDepth,MinimumPeakDistance)
            
            
if __name__=='__main__': 
    wave_min=1540
    wave_max=1549
    n=1.446
    R=62.5e3
    p_max=2
    
    resonances=Resonances(wave_min,wave_max,n,R,p_max,dispersion=True)
    plt.figure(2)
    resonances.plot_all(0,1,'both')
    plt.xlim([wave_min,wave_max])
    
    #%%
    plt.figure(3)
    resonances2=Resonances(wave_min,wave_max,n,R,p_max,dispersion=False)
    # tempdict=resonances.__dict__
    resonances2.plot_all(0,1,'both')
    plt.xlim([wave_min,wave_max])


