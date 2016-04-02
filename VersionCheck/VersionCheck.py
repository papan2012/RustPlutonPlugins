__author__ = 'PanDevas'
__version__ = '1.2'

import clr

import sys
path = Util.GetPublicFolder()
sys.path.append(path + "\\Python\\Lib\\")
import os
import urllib2, json



class VersionCheck():

    def On_PluginInit(self):
        self.settings = self.loadIniSettings()

        self.timer = self.settings.GetIntSetting('options', 'checkperiod')
        self.pluginInfoURL = self.settings.GetSetting('options', 'pluginURL')

        self.plugins = self._getPlugins()

        self.curVersions = self._getCurVersions()

        self.checkVersions()
        Plugin.CreateTimer("versionCheck", self.timer*1000).Start()


    def loadIniSettings(self):
        if not Plugin.IniExists('versioncheck'):
            Plugin.CreateIni('versioncheck')
            ini = Plugin.GetIni('versioncheck')
            ini.AddSetting('options', 'checkperiod', '3600')
            ini.AddSetting('options', 'pluginURL', 'https://stats.pluton.team/all_plugins.php')
            ini.Save()
        return Plugin.GetIni('versioncheck')

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
        response = urllib2.urlopen(self.pluginInfoURL)
        data = json.from_json(response.read())
        for resource in data['resources']:
            curVersions[resource['title']] = resource['version_string']
        return curVersions

    def checkVersions(self):
        self.plugins = self._getPlugins()
        for pluginName in self.plugins.keys():
            if pluginName in self.curVersions.keys():
                if self.plugins[pluginName] != self.curVersions[pluginName]:
                    Util.Log("PLUGIN UPDATE NEEDED: "+pluginName)

    def versionCheckCallback(self, timer):
        self.curVersions = self._getCurVersions()
        self.checkVersions()

    def On_Command(self, cmd):
        user = cmd.User
        command = cmd.Cmd


        if command == 'versioncheck':
            self.checkVersions()