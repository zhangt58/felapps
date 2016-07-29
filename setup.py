#!/usr/bin/env python

"""FELApps project (felapps)"""

def readme():
    with open('README.rst') as f:
        return f.read()

from setuptools import find_packages, setup 
import os
import glob

appName             = "felapps"
appVersion          = "1.5.7"
appDescription      = "High-level applications for FEL commissioning."
#appLong_description = "High-level applications created for the tunning/commissioning of the free-electron laser facilities."
appLong_description = readme() + '\n\n'
appPlatform         = ["Linux"]
appAuthor           = "Tong Zhang"
appAuthor_email     = "zhangtong@sinap.ac.cn"
appLicense          = "MIT"
appUrl              = "https://github.com/Archman/felapps"
appKeywords         = "FEL HLA high-level python wxpython"
requiredpackages = ['numpy','scipy','matplotlib','pyepics','h5py',
                    'pyrpn','beamline','lmfit'] # install_requires
appScriptsName = ['imageviewer', 
                  'felformula', 
                  'cornalyzer', 
                  'dataworkshop', 
                  'appdrawer', 
                  'wxmpv',
                  'runfelapps',
                  ]
#'matchwizard', 
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
      #packages         = ["felapps"],
      scripts          = appScripts,
      #install_requires = requiredpackages,
      classifiers = ['Programming Language :: Python', 
                     'Topic :: Software Development :: Libraries :: Python Modules', 
                     'Topic :: Scientific/Engineering :: Physics'],
      test_suite = 'nose.collector',
      tests_require = ['nose'],
      #include_package_data = True,
      data_files = [
          ('share/felapps', ['felapps/configs/imageviewer.xml']),
          ('share/felapps', ['felapps/configs/udefs.py']),
          ('share/felapps', ['requirements.txt']),
          ('share/icons/hicolor/16x16/apps',   glob.glob("launchers/icons/short/16/*.png")),
          ('share/icons/hicolor/32x32/apps',   glob.glob("launchers/icons/short/32/*.png")),
          ('share/icons/hicolor/48x48/apps',   glob.glob("launchers/icons/short/48/*.png")),
          ('share/icons/hicolor/128x128/apps', glob.glob("launchers/icons/short/128/*.png")),
          ('share/icons/hicolor/256x256/apps', glob.glob("launchers/icons/short/256/*.png")),
          ('share/icons/hicolor/512x512/apps', glob.glob("launchers/icons/short/512/*.png")),
          ('share/applications', glob.glob("launchers/*.desktop")),
      ],
)
