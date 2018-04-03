# felapps

**Note**:
As of [v2.0.0](https://github.com/archman/felapps/releases/tag/v2.0.0), development will focus on `Python 3.x` and
`wxPython 4.0` (phoenix), the last release for `wxPython 3.x` (classic)
and `Python 2.7` is [v1.5.16](https://github.com/archman/felapps/releases/tag/v1.5.16).

High-level applications for the commissioning of free-electron laser facilities. Purely open-sourced, mainly developed by `Python` (2.7), powered by various well-benchmarked module/packages, e.g.: `matplotlib` (beautiful scientific plotting); `numpy` and `scipy` (scientific computing); `wxPython` (GUI building); `PyEpics` (interface with EPICS); `h5py` (interface with HDF5 data format), etc.

The goal of this project is to make a mature, full-fledged, friendly, beautiful and stable open source software framework/suite for the FEL commissioning (and operation), including beam tuning, parameters optimization and specific physics-related applications deployment, etc.

Documentation: http://archman.github.io/felapps/

### Installation
`felapps` could be installed into the operating system by the following approaches:

1. (Recommended) Install directly from PyPI by:
  `pip install felapps`, the required packages (i.e. the above listed Python modules) will be pulled and installed automatically;
2. Clone this repo by `git clone https://github.com/archman/felapps.git`.

### How to Use
Assuming the `felapps` package has been already installed by `pip` way, one can write Python script and run it to call methods that included by `felapps`, e.g.:
```python
#!/usr/bin/env python
import felapps
felapps.imageviewer.run()
```
Or just type `imageviewer` in the terminal, both do the same thing. Please note that `imageviewer` app would complain that it cannot find any configuration file for loading in the present working directory, then choose the configuration file as it guided, the sample configuration file could be found in the source directory: [felapps/configs](https://github.com/Archman/felapps/tree/master/felapps/configs).

If using `felapps` by the `git clone` way, attention should be paid to make sure the compiled Python module (whl or egg) could be found when issuing `import` in Python. One may do as follows:

1. `python setup.py bdist_wheel install`
2. `python setup.py bdist_wheel develop`
3. `python setup.py bdist_wheel`

The first approach is to generate `felapps.VERSION.whl` package and install it in `/usr/local/lib/python2.7/dist-packages` by default. Since the above path is also by default included in the `PYTHONPATH`, nothing else is required, one can successfully import felapps in Python, i.e. `felapps` could be found by Python.

The second approach is similar as the first, but it does not really put the compiled Python package into system directory, but just creates a link to ensure Python knows where `felapps` is, this is usually for development.

The third approach only generates the Python package, which could be imported into Python provided that the correct module path be added into `PYTHONPATH`, e.g.:
```python
import sys
sys.path.insert(0, '../dist/felapps.VERSION.whl')
import felapps
...
```
### Deploy Virtual FEL EPICS Controls Environment
This Python suite is designed for the commissioning of a real FEL machine, however we can setup the virtual controls environment for the software development stage. This section shows how to deploy such kind of virtual environment on Linux workstation.

The communication between the suite and controls layer is via Channel Access (CA) protocol
of EPICS; generally speaking, IOC application for the virtual machine should be built.

The EPICS base should be compiled and installed on the Linux workstation.

The built IOC application (or template) could be found in [felapps/ioc](https://github.com/Archman/felapps/tree/master/felapps/ioc), edit `configure/RELEASE` to make sure the `EPICS_BASE` path is valid, the database files (`.db` files) could be modified to simulate the FEL machine (please note there're not any physics issues evolved, just controls stuff), then build the IOC application; start the IOC by executing `st.cmd` in `iocBoot` directory.

The data update is simulated by Python script, thanks to the `PyEpics` package (which is the Python interface of EPICS), one can update some PV values at some frequency, for instance, in `ioc/apps` directory, `gendata.py` script is created to update some waveform records every second.

### Screenshots

**ImageViewer**

<p>
  <img src=/screenshots/imageviewer/startup.png?raw=true alt="ImageViewer Startup" width="400"></img> <img src=/screenshots/imageviewer/roi.png?raw=true alt="imageviewer ROI" width="400"></img>
</p>
<p>
  <img src=/screenshots/imageviewer/configuration.png?raw=true alt="imageviewer Configurations" width="400"></img> <img src=/screenshots/imageviewer/colormap.png?raw=true alt="imageviewer Colormap" width="400"></img>
</p>
