__author__ = 'PanDevas'
__version__ = '1.0'

import clr

clr.AddReferenceByPartialName("Pluton")
import sys
path = Util.GetPublicFolder()
sys.path.append(path + "\\Python\\Lib\\")
import os
import urllib, json

import time



class VersionCheck():
    '''
    1. ini file u kojem ce se upisivati URL-ovi pluginova
    2. parser za html datoteke webova sa lxml parseom http://docs.python-guide.org/en/latest/scenarios/scrape/
    '''
    def On_PluginInit(self):
        self.plugins = self._getPlugins()
        self.pluginInfoURL = "http://stats.pluton-team.org/all_plugins.php"
        self.curVersions = self._getCurVersions()


    def _getPlugins(self):
        plugins = {}

        for dir in os.listdir((path + "\\Plugins\\")):
            try:
                s = Plugin.GetPlugin(dir)
            except:
                pass
            if s:
                plugins[dir] = s.Version

        return plugins

    def _getCurVersions(self):
        curVersions = {}
        response = urllib.urlopen(self.pluginInfoURL)
        data = json.from_json(response.read())
        for resource in data['resources']:
            curVersions[resource['title']] = resource['version_string']

        return curVersions

    def checkVersions(self):
        for pluginName in self.plugins.keys():
            if pluginName in self.curVersions.keys():
                if self.plugins[pluginName] != self.curVersions[pluginName]:
                    Util.Log("PLUGIN UPDATE NEEDED: "+pluginName)


    def On_Command(self, cmd):
        user = cmd.User
        command = cmd.cmd


        if command == 'test':
            self.checkVersions()