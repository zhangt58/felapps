#!/usr/bin/python2
# -*- coding: utf-8 -*-  

from ..physics import felbase
import numpy as np
import matplotlib.pyplot as pyplt

beamEnergy 	      = 500 	# beam energy [MeV]
relativeEnergySpread  = 0.0001 	# beam energy spread
undulatorPeriodLength = 0.02 	# undulator period length [m]
normEmittance 	      = 0.5e-6 	# transverse emittance [m]
FELwavelength         = 30e-9 	# radiation wavelength [m]
avgBetaFunction	      = 0.6 	# average betatron function [m]
peakCurrent 	      = 10000.0 # peak current [A]

FELinst1 = felbase.FELcalc(beamEnergy, 
                          relativeEnergySpread, 
                          undulatorPeriodLength,
                          avgBetaFunction,
                          FELwavelength,
                          normEmittance,
                          peakCurrent)
res1 = FELinst1.MXieFormulae()
#print res1.items()
Nlambda = peakCurrent*FELwavelength/FELinst1.e0/FELinst1.c0
Lsat = 20*res1['Lg3D']
Pshot = 3*np.sqrt(4*np.pi)*res1['rho1D']**2*beamEnergy*peakCurrent/Nlambda/np.sqrt(np.log(Nlambda/res1['rho1D']))
#print Pshot
Psat = 1.0/9*Pshot*np.exp(20)
#print Psat

"""
# scan average beta function
avgBetaArr = np.linspace(1,50,100)
FELinst = FELpack.FELcalc(beamEnergy, 
                          relativeEnergySpread, 
                          undulatorPeriodLength,
                          avgBetaArr,
                          FELwavelength,
                          normEmittance,
                          peakCurrent)
res = FELinst.MXieFormulae()
Lg3D = res['Lg3D']
pyplt.figure(1)
pyplt.plot(avgBetaArr, Lg3D, '--', linewidth = 2)
pyplt.xlabel(r'$<\beta>$ [m]')
pyplt.ylabel(r'$L_g^{3D}$ [m]')
pyplt.title(r'Scan $<\beta>$')
pyplt.show()


# scan FEL wavelength
FELwvlthArr = np.linspace(0.8,4,100)*1e-10
FELinst = FELpack.FELcalc(beamEnergy, 
                          relativeEnergySpread, 
                          undulatorPeriodLength,
                          avgBetaFunction,
                          FELwvlthArr,
                          normEmittance,
                          peakCurrent)
res = FELinst.MXieFormulae()
Lg3D = res['Lg3D']
pyplt.figure(2)
pyplt.plot(FELwvlthArr*1e9, Lg3D, '-r', linewidth = 2)
pyplt.xlabel(r'$\lambda_s$ [nm]')
pyplt.ylabel(r'$L_g^{3D}$ [m]')
pyplt.title(r'Scan $\lambda_s$')
pyplt.show()

gap = res['gap']
bu  = res['bu']
#gap = FELpack.HalbachPerm(_lambdau = 1000*undulatorPeriodLength, _Bu = bu).findGap(gap0=5)
pyplt.figure(3)
pyplt.plot(FELwvlthArr*1e9, gap, '-g', linewidth = 2)
pyplt.xlabel(r'$\lambda_s$ [nm]')
pyplt.ylabel(r'Gap [mm]')
pyplt.title(r'Scan $\lambda_s$')
pyplt.show()            
""" 
