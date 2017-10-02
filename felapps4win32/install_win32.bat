@echo off
python-2.7.14.msi
python get-pip.py
wxPython3.0-win32-3.0.2.0-py27.exe
pip install numpy-1.13.3+mkl-cp27-cp27m-win32.whl ^
    scipy-0.19.1-cp27-cp27m-win32.whl
pip install matplotlib h5py lmfit pyepics pillow
pip install pyrpn beamline felapps --upgrade


