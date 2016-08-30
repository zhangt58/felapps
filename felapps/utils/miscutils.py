#!/usr/bin/env python
# -*- coding: utf-8 -*-

# class to control app version number
class AppVersions():
    def __init__(self):
        self.versions = {
                         'imageviewer'  : '1.4.1',
                         'cornalyzer'   : '2.0',
                         'felformula'   : '1.4',
                         'dataworkshop' : '1.1',
                         'matchwizard'  : '1.0',
                         'wxmpv'        : '0.2',
                         'appdrawer'    : '1.5.13',
                         }

    def setVersion(self, verNum, appName = 'imageviewer'):
        self.versions.update({appName: verNum})

    def getVersion(self, appName = 'imageviewer'):
        return self.versions.get(appName)

