#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Author: Tong Zhang
Created Time: 10:22, Sep. 17, 2015
"""

from ConfigParser import SafeConfigParser

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
        self.parser = SafeConfigParser()
        if not os.path.isfile(self.inifilename): 
            self.createTemplate()
            sys.exit(1)
        else:
            self.parser.read(self.inifilename)
    
    def createTemplate(self, configfilename='config_sample.conf'):
        dict_sample = dict([('00-info', {'author': 'Tong Zhang', 'email': 'zhangtong@sinap.ac.cn', 'time': '2015-09-17 10:05:20 CST'}), ('01-facility', {'country': 'China', 'name': 'SDUV', 'city': 'Shanghai'}), ('02-electron_beam', {'normlized_emittance': '4e-6', 'peak_current': '300', 'energy': '150', 'average_beta_function': '4', 'charge': '0.2e-9', 'energy_spread': '1e-4', 'bunch_shape': 'gaussian'}), ('03-undulator', {'length': '10', 'period': '0.04'}), ('04-FEL_radiation', {'wavelength': '350e-9'})])
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
        for section_name in sorted(newhierdict.keys()):
            newparser.add_section(section_name)
            [newparser.set(section_name, k, v) for k, v in sorted(newhierdict[section_name].items())]
        newparser.write(open(configfilename, 'w'))

    def saveConfig(self, filetosave=None):
        if filetosave == None:
            filetosave = self.inifilename
        self.parser.write(open(filetosave, 'w'))

def test():
    testparser = ParamParser('config1.ini')

    #print testparser.makeHierDict()['machine']['name']

    #testparser.setOneParam('machine', 'name', 'SXFEL')
    #testparser.saveConfig('newconfig.ini')
    #print testparser.makeFlatDict()

    # make hierarch dict from config file
    odict = testparser.makeHierDict()
    print odict
    
    # modify odict
    odict['01-facility']['name'] = 'XFEL'
    odict['03-undulator']['period'] = str(0.04)
    odict['02-electron_beam']['peak_current'] = str(300)
    if not odict.has_key('info'):
        odict['00-info'] = {}
    odict['00-info']['time'] = time.strftime('%Y-%m-%d %H:%M:%S %Z', time.localtime())
    
    
    # update to parser
    testparser.setAllParams(odict)

    # print maked hierarch dict from parser
    print testparser.makeHierDict()

    # save parser into new config file
    testparser.saveConfig('sxfel.conf')

    testparser.dumpDictToConfig(odict, 'sxfel1.conf')

if __name__ == '__main__':
    test()
