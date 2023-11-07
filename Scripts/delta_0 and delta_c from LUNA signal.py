import numpy as np
import matplotlib.pyplot as plt 
import OVA_signals
from SNAP import SNAP_experiment



f_in='in_cropped.pklOVA'
f_out='out_cropped.pklOVA'


d_in=OVA_signals.load_OVA_spectrum(f_in)
d_out=OVA_signals.load_OVA_spectrum(f_out)
waves=d_in.fetch_xaxis(0)[0]

pol1,pol2=OVA_signals.complex_IL_remove_out_of_contact(d_in,d_out)



plt.figure(1)
plt.plot(waves,np.real(pol1))
plt.plot(waves,np.imag(pol1))




# pol1_s,pol2_s=d_in.min_max_losses_complex()
# plt.figure(3)
# plt.plot(waves,np.real(pol1_s))
# plt.plot(waves,np.imag(pol1_s))
# plt.figure(4)
# plt.plot(waves,np.abs(pol1_s))


popt,pcov, waves, complex_Fano_lorenzian=SNAP_experiment.get_complex_Fano_fit(waves,pol1,peak_wavelength=1554.3203)
# plt.figure(1)
# plt.plot(waves,np.abs(complex_Fano_lorenzian))
plt.figure(1)
plt.plot(waves,np.real(complex_Fano_lorenzian))
plt.plot(waves,np.imag(complex_Fano_lorenzian))
results_text='$\phi_{fano}=$'+'{:.2f}, $\delta_0$={:.2f} 1e6/s, $\delta_c=${:.2f} 1e6/s'.format(popt[2],popt[4],popt[5])
plt.gca().text(0.4, 0.5,results_text,
        horizontalalignment='center',
        verticalalignment='center',
        transform = plt.gca().transAxes)

# other_fit=SNAP_experiment.complex_Fano_lorenzian(waves,0.6,0.5,1554.3203,1650,380)
# plt.plot(waves,np.real(other_fit))
# plt.plot(waves,np.imag(other_fit))

