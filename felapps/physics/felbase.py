"""
Python module for the basis of free-electron laser calculation.

"""

import numpy as np
import scipy.special as sp
from scipy.optimize import fsolve


class PhysicalConstants(object):
    """Physical constants
    :param c0: :math:`c_0`, velocity of light in vacuum
    :param epsilon0: :math:`\epsilon_0`, permittivity in vacuum
    :param mu0: :math:`\mu_0`, permeability in vacuum
    :param e0: :math:`e`, electron charge, [C]
    :param m0: :math:`m_e`, electron mass, [kg]
    :param h0: :math:`h`, Plank constant
    :param currentA: :math:`I_A`, Alven current, [A]
    """
    c0       = 2.99792458E+08
    epsilon0 = 8.854187817620390E-12
    mu0      = np.pi*4E-7
    e0       = 1.60218E-19
    m0       = 9.10938E-31
    h0       = 6.62607E-34
    currentA = 17045


class HalbachPerm(object):
    def __init__(self, _a=3.33, _b=-5.47, _c=1.80, _lambdau=20, _Bu=1.0):
        """
        Input parameters:
        _a: first Halbach parameter
        _b: second Halbach parameter
        _c: third Halbach parameter
        _lambdau: undulator period length, [mm]
        _Bu: undulator magnetic field, [T]
        """
        self.coef1   = _a
        self.coef2   = _b
        self.coef3   = _c
        self.lambdau = _lambdau
        self.Bu      = _Bu

    def findGap(self, gap0=10):
        """
        Solve undulator gap value

        :param gap0: initial gap value vector, [mm]
        """
        fbg = lambda x: self.Bu - self.coef1*np.exp(self.coef2*x/self.lambdau+self.coef3*(x/self.lambdau)**2)
        return fsolve(fbg, x0=gap0*np.ones(np.size(self.Bu)))
                    

class FELcalc(PhysicalConstants):
    """
    Analytical calculation for Free-electron Laser physics

    Usage: res = FELcalc(p1, p2, p3, p4, p5, p6, p7)
    :param p1: beamEnergy, [MeV]
    :param p2: relative energy spread
    :param p3: undulator period length, [m]
    :param p4: avgerage beta function, [m]
    :param p5: radiation wavelength, [m]
    :param p6: normalized transverse emittance, [m]
    :param p7: peak current, [A]
    :return res: dict, keys: "au", "bu", "gap", "sigmar", "rho1D", "rho3D", "Lg1D", "Lg3D", "Psat", "Pshot", "Pss"
    """
    def __init__(self,
            _beamEnergy           = 6000.0, 
            _relativeEnergySpread = 0.0001,
            _unduPeriodLength     = 0.015,
            _avgBetaFunc          = 20.0,
            _radWavelength        = 1.0e-10,
            _normEmittance        = 0.4e-6,
            _peakCurrent          = 3500.0,
            _bunchCharge          = 0.5e-9,
            _undulatorLength      = 10.0,
            _bunchShape           = 'gaussian',
            _undulatorType        = 'planar'):
        """
        Initialized parameters:
        beamEnergy 	 [MeV]
        relativeEnergySpread
        unduPeriodLength [m]
        avgBetaFunc 	 [m]
	    radWavelength 	 [m]
	    normEmittance 	 [m]
	    peakCurrent 	 [A]
        bunchCharge      [C]
        undulatorLength  [m]
        bunchShape: gaussian or flattop
	    """

        self.beamEnergy 	  = _beamEnergy
        self.relativeEnergySpread = _relativeEnergySpread
        self.unduPeriodLength 	  = _unduPeriodLength
	self.avgBetaFunc 	  = _avgBetaFunc
	self.radWavelength 	  = _radWavelength
	self.normEmittance 	  = _normEmittance
        self.peakCurrent 	  = _peakCurrent
        self.bunchCharge      = _bunchCharge
        self.undulatorLength  = _undulatorLength
        self.bunchShape       = _bunchShape
        self.undulatorType    = _undulatorType

        if self.bunchShape == 'gaussian':
            self.bunchratio = np.sqrt(2.0*np.pi)
        elif self.bunchShape == 'flattop':
            self.bunchratio = 1.0

    def onFELAnalyse(self):
        """
        Apply M. Xie formulae for FEL analytical estimation
        """
	    # Xie Ming Formulae fitted cofs
        a1  = 0.45
        a2  = 0.57
        a3  = 0.55
        a4  = 1.6
        a5  = 3.0
        a6  = 2.0
        a7  = 0.35
        a8  = 2.9
        a9  = 2.4
        a10 = 51.0
        a11 = 0.95
        a12 = 3.0
        a13 = 5.4
        a14 = 0.7
        a15 = 1.9
        a16 = 1140.0
        a17 = 2.2
        a18 = 2.9
        a19 = 3.2
        
        gamma0   = self.beamEnergy/0.511
        eta      = self.relativeEnergySpread
        lambdau  = self.unduPeriodLength
        beta     = self.avgBetaFunc
        lambdas  = self.radWavelength
        epsilonn = self.normEmittance
        Ipk      = self.peakCurrent
        lu       = self.undulatorLength

        sigmaBeam = np.sqrt(beta*epsilonn/gamma0)
        au = np.sqrt(lambdas*2.0*gamma0**2.0/lambdau-1)
        
        if self.undulatorType == 'planar':
            b  = au**2.0/2.0/(1+au**2)
            JJ = sp.jn(0, b) - sp.jn(1, b)
        else: # helical
            JJ = 1.0

        rho1D = ((1.0/2.0/gamma0)**3.0*Ipk/self.currentA*(au*JJ*lambdau/2.0/np.pi/sigmaBeam)**2)**(1.0/3.0)
        Lg1D  = lambdau/4.0/np.pi/np.sqrt(3)/rho1D
        
        etad = Lg1D/(4.0*np.pi*sigmaBeam**2.0/lambdas)
        etae = Lg1D/beta*4.0*np.pi*epsilonn/(gamma0*lambdas)
        etag = Lg1D/lambdau*4.0*np.pi*eta
        capLambda =  a1*etad** a2 \
                +  a3*etae** a4 \
                +  a5*etag** a6 \
	            +  a7*etae** a8*etag**a9 \
	            + a10*etad**a11*etag**a12 \
	            + a13*etad**a14*etae**a15 \
	            + a16*etad**a17*etae**a18*etag**a19
        Lg3D  = Lg1D*(1.0+capLambda)
        rho3D = lambdau/4.0/np.pi/np.sqrt(3)/Lg3D
        Psat  = 1.6*rho1D*(Lg1D/Lg3D)**2.0*gamma0*0.511*Ipk*1.0e6 #W
        
        # update and return calculated parameters
        self.au = au
        if self.undulatorType == 'planar':
            self.K  = au*np.sqrt(2.0)
            self.Bu = self.K/0.934/(100*lambdau)
        else: # helical
            self.K  = au
            self.Bu = self.K/0.934/(100*lambdau)

        self.gu     = HalbachPerm(_lambdau=lambdau*1000, _Bu=self.Bu).findGap(gap0=5)
        self.sigmar = sigmaBeam
        self.rho1D  = rho1D
        self.rho3D  = rho3D
        self.Lg1D   = Lg1D
        self.Lg3D   = Lg3D
        self.Psat   = Psat
        Nlambda     = Ipk*lambdas/self.e0/self.c0
        Pshot       = 3.0*np.sqrt(4.0*np.pi)*rho1D**2.0*self.beamEnergy*Ipk/Nlambda/np.sqrt(np.log(Nlambda/rho1D)) * 1e6
        Lsat        = Lg3D*self.findSatFactor(Nlambda, Lg3D, lambdau)
        Pss         = 1.0/9.0*Pshot*np.exp(Lsat/Lg3D)
        
        sigmat    = self.bunchCharge/Ipk/self.bunchratio  # bunch length (rms) for gaussian, full lenth for rectangle
        bandwidth = np.sqrt(3.0*np.sqrt(3.0)*rho3D*lambdau/lu)
        
        #Pexit = 1.0/9.0*Pshot*np.exp(Lsat/Lg3D)

        pulseEnergy = self.bunchratio*sigmat*Pss  # J
        photonEnergy = self.h0*self.c0/self.e0/lambdas  # eV
        Np = pulseEnergy/photonEnergy/self.e0  # photon per pulse

        return {"01-au"             : self.au, 
                "02-K"              : self.K,
                "03-Bu"             : self.Bu,
                "04-gap"            : self.gu,
                "05-rho1D"          : rho1D,
                "06-rho3D"          : rho3D,
                "07-Lg1D"           : Lg1D,
                "08-Lg3D"           : Lg3D,
                "09-Psat"           : Psat,
                "10-Pshot"          : Pshot,
                "11-Pss"            : Pss,
                "12-Lsat"           : Lsat,
                "13-sigmar"         : sigmaBeam*1e6, 
                "14-sigmat"         : sigmat*1e15,
                "15-bandWidth"      : bandwidth*100,
                "16-PhotonEnergy"   : photonEnergy,
                "17-PulseEnergy"    : pulseEnergy*1e6,
                "18-PhotonPerPulse" : Np,
                }

    def findSatFactor(self, nl, l3, xlamd, factor0=20):
        """ Calculator saturation length in the unit of 3D power gainlength
        :param factor0: initial saturation factor, saturation length over power gain length
        :param nl: electron count within one unit of FEL wavelength
        :param l3: power gain length (3D)
        :param xlamd: undulator period
        """
        fx = lambda x: 6.0*np.sqrt(3.0*np.pi)*nl*l3*np.sqrt(x) - xlamd*np.exp(x)
        return fsolve(fx, x0=factor0*np.ones(np.size(self.Lg3D)))

def test1():
    inst = FELcalc(17500, 8.5714e-5, 0.08, 15, 1.3e-9, 1.4e-6, 5000, 1.0e-9, 100)
    for (key,val) in inst.onFELAnalyse().items():
        print key, '\t=\t', val

def test2():
    energy = np.linspace(17000, 18000, 3)
    inst = FELcalc(energy, 8.5714e-5, 0.08, 15, 1.3e-9, 1.4e-6, 5000, 1.0e-9, 100)
    result = inst.onFELAnalyse()
    print result['ppp']

def test3():
    bunchCharge = np.linspace(0.5e-9, 1e-9, 3)
    inst = FELcalc(17500, 8.5714e-5, 0.08, 15, 1.3e-9, 1.4e-6, 5000, bunchCharge, 100)
    result = inst.onFELAnalyse()
    print result['sigmat']

if __name__ == '__main__':
    test3()
