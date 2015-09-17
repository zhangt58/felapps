#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Author: Tong Zhang
Created Time: 10:22, Sep. 17, 2015
"""

from ConfigParser import SafeConfigParser, ConfigParser

import os
import sys
import time

class ConfigFile(object):
    """
    Class to resolve parameters parsing by applying xmlparser approach.
    """
    def __init__(self, infilename='config.xml', *args, **kwargs):
        self.xmlfile = infilename
        self.namelist = {}
        self.parseConfigs()

    def parseConfigs(self):
        pass

    def getConfigs(self):
        return self.namelist
    
    def updateConfigs(self, params_dict, savetofile=None):
        if not savetofile:
            savetofile = self.xmlfile
        for p in self.root.iter('properties'):
            for k in params_dict.keys():
                if p.get(k):
                    p.set(k, params_dict[k])
        self.tree.write(savetofile)

class ParamParser(object):
    """
    Class to resolve parameters parsing by applying ConfigParser approach.
    """
    def __init__(self, inifilename = 'config.ini', *args, **kws):
        self.inifilename = inifilename
        self.parser = ConfigParser()
        self.parser.optionxform = str

    def readConfig(self):
        if not os.path.isfile(self.inifilename): 
            self.createTemplate()
            sys.exit(1)
        else:
            self.parser.read(self.inifilename)
    
    def createTemplate(self, configfilename='config_sample.conf'):
        dict_sample = dict([('00-info', {'author': 'Tong Zhang', 'note': '', 'created_time': time.strftime('%Y-%m-%d %H:%M:%S %Z', time.localtime())}), ('01-facility', {'country': 'China', 'name': 'SDUV', 'affiliation': 'SINAP'}), ('02-electron_beam', {'normalized_emittance(m)': '4e-6', 'peak_current(A)': '300', 'central_energy(MeV)': '150', 'average_beta_function(m)': '4', 'bunch_charge(C)': '0.2e-9', 'energy_spread': '1e-4', 'bunch_shape': 'gaussian'}), ('03-undulator', {'total_length(m)': '10', 'period_length(m)': '0.04'}), ('04-FEL_radiation', {'wavelength(m)': '350e-9'})])
        parser_sample = SafeConfigParser()
        for section_name in sorted(dict_sample.keys()):
            parser_sample.add_section(section_name)
            [parser_sample.set(section_name, k, v) for k, v in sorted(dict_sample[section_name].items())]
        parser_sample.write(open(configfilename, 'w'))

    def makeFlatDict(self):
        """
        return dict with key,value pairs
        """
        onedict = {}
        for section_name in self.parser.sections():
            onedict.update({k:v for k, v in self.parser.items(section_name)})
        return onedict

    def makeHierDict(self):
        """
        return dict with hierarch structure
        """
        sdict = {}
        for section_name in self.parser.sections():
            for section_name in self.parser.sections():
                sdict[section_name] = {k:v for k, v in self.parser.items(section_name)}
        return sdict

    def setOneParam(self, section_name, option_name, newvalue):
        self.parser.set(section_name, option_name, newvalue)
    
    def setAllParams(self, newhierdict):
        for section_name in self.parser.sections():
            for k,v in self.parser.items(section_name):
                self.parser.set(section_name, k, newhierdict[section_name][k])

    def dumpDictToConfig(self, newhierdict, configfilename):
        newparser = SafeConfigParser()
        newparser.optionxform = str
        for section_name in sorted(newhierdict.keys()):
            newparser.add_section(section_name)
            [newparser.set(section_name, k, v) for k, v in sorted(newhierdict[section_name].items())]
        newparser.write(open(configfilename, 'w'))

    def saveConfig(self, filetosave=None):
        if filetosave == None:
            filetosave = self.inifilename
        self.parser.write(open(filetosave, 'w'))

def loadtest():
    # test load config from file
    testparser = ParamParser('config_sample.conf')
    testparser.readConfig()
    print testparser.makeHierDict()

def savetest():
    # test save config to file
    # save parser into new config file

    # get param dict from config_sample.conf which is parsed by readConfig method
    testparser = ParamParser('config_sample.conf')
    testparser.readConfig()
    raw_dict = testparser.makeHierDict()

    # modify parameters
    raw_dict['01-facility']['name'] = 'XFEL'
    raw_dict['03-undulator']['period_length(m)'] = str(0.04)
    raw_dict['02-electron_beam']['peak_current(A)'] = str(300)
    if not raw_dict.has_key('00-info'):
        raw_dict['00-info'] = {}
    raw_dict['00-info']['time'] = time.strftime('%Y-%m-%d %H:%M:%S %Z', time.localtime())

    # add options
    raw_dict['04-FEL_radiation']['output_power(W)'] = '%.3e' % 1e8

    # save to new config file
    testparser.dumpDictToConfig(raw_dict, 'sxfel.conf')

if __name__ == '__main__':
    #loadtest()
    savetest()
