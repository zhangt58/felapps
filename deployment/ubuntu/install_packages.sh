#!/bin/bash

#
# packages required
#
#

# wxpython 3.0
sudo apt-get install build-essential \
                     libpng12-dev \
                     libjpeg-dev \
                     zlib1g-dev \
                     libtiff5-dev \
                     libgtk2.0-dev \
                     libglu1-mesa-dev \
                     libgstreamer-plugins-base0.10-dev \
                     python-dev
# pip
sudo apt-get install python-pip
# numpy scipy matplotlib
sudo apt-get install python-numpy python-scipy python-matplotlib

# install wxpython
#cd wxpython_src/wxPython
#sudo ./build-wxpython.py --build_dir=../bld --install

# install packages from PyPI
sudo apt-get install cython libhdf5-dev
pip install wheel pyepics h5py felapps beamline
pip install --upgrade setuptools
