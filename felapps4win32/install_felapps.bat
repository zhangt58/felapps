@echo off
pip install numpy-1.13.3+mkl-cp27-cp27m-win32.whl ^
    scipy-0.19.1-cp27-cp27m-win32.whl
pip install matplotlib h5py lmfit pyepics pillow
pip install beamline==1.3.6 
pip install felapps==1.5.16


