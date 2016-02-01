__author__ = 'PanDevas'
__version__ = '1.0'

import clr
clr.AddReferenceByPartialName("Pluton", "Assembly-CSharp-firstpass", "Assembly-CSharp")
import Pluton
import sys

path = Util.GetPublicFolder()
sys.path.append(path + "\\Python\\Lib\\")
import time

import httplib, urllib, urllib2


class Vote():

    def __init__(self):
        self.settings = self.loadIniSettings()
        self.serverKey = self.settings.GetSetting('settings', 'serverKey')
        self.wood = self.settings.GetIntSetting('settings', 'Wood')
        self.stone = self.settings.GetIntSetting('settings', 'Stone')


    def On_Command(self, cmd):
        command = cmd.cmd
        player = cmd.User
        if command == 'vote':
            response = self.checkVote(player)
            Util.Log(player.Name +" voted, response: "+response)
            if response == '0':
                player.Message("You didn't vote in the last 24 hours.")
            elif response == '1':
                player.Message("You have voted. Thank you for your vote.")
                self.Claim(player)
                self.rewardPlayer(player)
            elif response == '2':
                player.Message("You already claimed your reward.")


    def loadIniSettings(self):
        if not Plugin.IniExists("vote"):
            Plugin.CreateIni('vote')
            ini = Plugin.GetIni('vote')
            ini.AddSetting('settings', 'serverKey', 'YourServerKey')
            ini.AddSetting('rewards', 'Wood', '500')
            ini.AddSetting('rewards', 'Stone', '250')
            ini.Save()
        return Plugin.GetIni('vote')

    def checkVote(self, player):
        steamID = player.SteamID

        httpServer = httplib.HTTPConnection('rust-servers.net', 80)
        params = urllib.urlencode({'object': 'votes', 'element':'claim', 'key': self.serverKey, 'steamid': steamID})
        headers = {"Content-type": "application/x-www-form-urlencoded", "Accept": "text/plain"}
        httpServer.request("POST", "/api/?", params, headers)

        response = httpServer.getresponse()
        res = response.read()
        httpServer.close()
        return res

    def Claim(self, player):
            steamID = player.SteamID

            httpServer = httplib.HTTPConnection('rust-servers.net', 80)
            params = urllib.urlencode({'action': 'post', 'object': 'votes', 'element':'claim', 'key': self.serverKey, 'steamid': steamID})
            headers = {"Content-type": "application/x-www-form-urlencoded", "Accept": "text/plain"}
            httpServer.request("POST", "/api/?", params, headers)

            response = httpServer.getresponse()
            httpServer.close()

    def rewardPlayer(self, player):
        player.Inventory.Add("Wood", self.wood)
        player.Inventory.Add("Stones", self.stone)