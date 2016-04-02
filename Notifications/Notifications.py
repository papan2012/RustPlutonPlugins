__author__ = 'PanDevas'
__version__ = '1.1'

import clr

clr.AddReferenceByPartialName("Pluton.Core", "Pluton.Rust")

import Pluton.Core
import Pluton.Rust

class Notifications():
    def On_PluginInit(self):
        self.settings = self.loadIniSettings()

        self.period = self.settings.GetIntSetting("Options", "period")
        self.messages = []
        self.populateValues('Messages', 'msg')

        self.counter = 0


    def populateValues(self, section, value):
        i = 1
        valueLokup = value+str(i)
        while self.settings.ContainsSetting(section, valueLokup):
            self.messages.append(self.settings.GetSetting(section, valueLokup))
            i+=1
            valueLokup = value+str(i)

    def loadIniSettings(self):
        if not Plugin.IniExists("notifications"):
            Plugin.CreateIni("notifications")
            ini = Plugin.GetIni("notifications")
            ini.AddSetting("Options", "period", "1")
            ini.AddSectionComments("Options", "Period of notifications, 1 for every time  is sarver saved")
            ini.AddSetting("Messages", "msg1", "World Saved")
            ini.AddSetting("Messages", "msg2", "Your second message")
            ini.AddSectionComments("Messages", 'Add your messages here, format msg1="Message"')
            ini.Save()
        return Plugin.GetIni("notifications")

    def On_ServerSaved(self):
        if self.counter == len(self.messages):
            self.counter = 0
        if self.counter % self.period == 0:
            Server.Broadcast(self.messages[self.counter])

        self.counter += 1