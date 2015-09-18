#!/usr/bin/env python
# -*- coding: utf-8 -*-

# class to control app version number
class AppVersions():
    def __init__(self):
        self.versions = {
                         'imageviewer': '1.2',
                         'cornalyzer' : '1.0',
                         'felformula' : '1.2',
                         }

    def setVersion(self, verNum, appName = 'imageviewer'):
        self.versions.update({appName: verNum})

    def getVersion(self, appName = 'imageviewer'):
        return self.versions.get(appName)

