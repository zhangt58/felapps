#!/usr/bin/env python

"""FELApps project (felapps)"""

def readme():
    with open('README.rst') as f:
        return f.read()

from setuptools import find_packages, setup
import os

appName             = "felapps"
appVersion          = "1.5.4"
appDescription      = "High-level applications for FEL commissioning."
#appLong_description = "High-level applications created for the tunning/commissioning of the free-electron laser facilities."
appLong_description = readme() + '\n\n'
appPlatform         = ["Linux"]
appAuthor           = "Tong Zhang"
appAuthor_email     = "zhangtong@sinap.ac.cn"
appLicense          = "MIT"
appUrl              = "https://github.com/Archman/felapps"
appKeywords         = "FEL HLA high-level python wxpython"
#requiredpackages = ['numpy','scipy','matplotlib','pyepics','h5py'] # install_requires
requiredpackages = ['beamline']
appScriptsName = ['imageviewer', 'felformula', 'cornalyzer', 'dataworkshop', 'matchwizard', 'appdrawer', 'runfelapps']
ScriptsRoot = 'scripts'
appScripts = [os.path.join(ScriptsRoot,scriptname) for scriptname in appScriptsName]

setup(name             = appName,
      version          = appVersion,
      description      = appDescription,
      long_description = appLong_description,
      platforms        = appPlatform,
      author           = appAuthor,
      author_email     = appAuthor_email,
      license          = appLicense,
      url              = appUrl,
      keywords         = appKeywords,
      packages         = find_packages(exclude=['contrib','tests*']),
      scripts          = appScripts,
      install_requires = requiredpackages,
      classifiers = ['Programming Language :: Python', 
                     'Topic :: Software Development :: Libraries :: Python Modules', 
                     'Topic :: Scientific/Engineering :: Physics'],
      test_suite = 'nose.collector',
      tests_require = ['nose'],
      include_package_data = True,
      )
