import numpy as np
import scipy.special as sp
from scipy.optimize import fsolve

"""
Python module for the basis of free-electron laser.
"""

class PhysicalConstants():
    """physical constants"""
    c0       = 2.99792458E+08
    epsilon0 = 8.854187817620390E-12
    mu0      = np.pi*4E-7
    e0       = 1.60218E-19
    m0       = 9.10938E-31
    h0       = 6.62607E-34
    currentA = 17045

class HalbachPerm():
    def __init__(self, _a = 3.33, _b = -5.47, _c = 1.80, _lambdau=20, _Bu = 1.0):
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

    def findGap(self, gap0 = 10):
        """
        gap0: initial gap value vector, [mm]
        x: gap, [mm]
        lambdau: [mm]
        """
        fbg = lambda x: self.Bu - self.coef1*np.exp(self.coef2*x/self.lambdau+self.coef3*(x/self.lambdau)**2)
        return fsolve(fbg, x0 = gap0*np.ones(np.size(self.Bu)))
                    
class FELcalc(PhysicalConstants):
    """
    Analytical calculation for Free-electron Laser physics
    Usage: res = FELcalc(p1, p2, p3, p4, p5, p6, p7)
    :param p1: beamEnergy, [MeV]
    :param p2: relative energy spread
    :param p2: undulator period length, [m]
    :param p2: avgerage beta function, [m]
    :param p2: radiation wavelength, [m]
    :param p2: normalized transverse emittance, [m]
    :param p2: peak current, [A]
    :return res: dict, keys: "au", "bu", "gap", "sigmar", "rho1D", "rho3D", "Lg1D", "Lg3D", "Psat", "Pshot", "Pss"
    """
    def __init__(self,
            _beamEnergy           = 6000.0, 
            _relativeEnergySpread = 0.0001,
            _unduPeriodLength     = 0.015,
            _avgBetaFunc          = 20.0,
            _radWavelength        = 1.0e-10,
            _normEmittance        = 0.4e-6,
            _peakCurrent          = 3500.0):
        """
        Initialized parameters:
        beamEnergy 	 [MeV]
        relativeEnergySpread
        unduPeriodLength [m]
        avgBetaFunc 	 [m]
	radWavelength 	 [m]
	normEmittance 	 [m]
	peakCurrent 	 [A]
	"""
        self.beamEnergy 	  = _beamEnergy
        self.relativeEnergySpread = _relativeEnergySpread
        self.unduPeriodLength 	  = _unduPeriodLength
	self.avgBetaFunc 	  = _avgBetaFunc
	self.radWavelength 	  = _radWavelength
	self.normEmittance 	  = _normEmittance
        self.peakCurrent 	  = _peakCurrent
        
    def MXieFormulae(self):
        """
        M. Xie formulae for FEL analytical estimation
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

        sigmaBeam = np.sqrt(beta*epsilonn/gamma0)
        au    = np.sqrt(lambdas*2.0*gamma0**2.0/lambdau-1)
        b     = au**2.0/2.0/(1+au**2)
        JJ    = sp.jn(0,b) - sp.jn(1,b)
        rho1D = ((1.0/2.0/gamma0)**3.0*Ipk/self.currentA*(au*lambdau*JJ/2.0/np.pi/sigmaBeam)**2)**(1.0/3.0)
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
        Lg3D  = Lg1D*(1+capLambda)
        rho3D = lambdau/4/np.pi/np.sqrt(3)/Lg3D
        Psat  = 1.6*rho1D*(Lg1D/Lg3D)**2*gamma0*0.511*Ipk*1e6 #W
        
        # update and return calculated parameters
        self.au     = au
        self.Bu     = au*np.sqrt(2)/0.934/(100*lambdau)
        self.gu     = HalbachPerm(_lambdau = lambdau*1000, _Bu = self.Bu).findGap(gap0=5)
        self.sigmar = sigmaBeam
        self.rho1D  = rho1D
        self.rho3D  = rho3D
        self.Lg1D   = Lg1D
        self.Lg3D   = Lg3D
        self.Psat   = Psat
        Nlambda     = Ipk*lambdas/self.e0/self.c0
        Pshot       = 3*np.sqrt(4*np.pi)*rho1D**2*self.beamEnergy*Ipk/Nlambda/np.sqrt(np.log(Nlambda/rho1D))
        Pss         = 1.0/9*Pshot*np.exp(20)
        
        return {"au"    : self.au, 
                "bu"    : self.Bu,
                "gap"   : self.gu,
                "sigmar": sigmaBeam, 
                "rho1D" : rho1D,
                "rho3D" : rho3D,
                "Lg1D"  : Lg1D,
                "Lg3D"  : Lg3D,
                "Psat"  : Psat,
                "Pshot" : Pshot,
                "Pss"   : Pss}


def test():
    inst = FELcalc()
    print inst.MXieFormulae().items()
