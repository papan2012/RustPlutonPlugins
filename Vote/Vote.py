__author__ = 'PanDevas'
__version__ = '1.3'

import clr
clr.AddReferenceByPartialName("Pluton.Core", "Pluton.Rust", "Assembly-CSharp-firstpass", "Assembly-CSharp")
import Pluton.Core
import Pluton.Rust
import sys

path = Util.GetPublicFolder()
sys.path.append(path + "\\Python\\Lib\\")
import time

import httplib, urllib, urllib2


class Vote():

    def __init__(self):
        Commands.Register('vote').setCallback('response')
        self.settings = self.loadIniSettings()
        self.serverKey = self.settings.GetSetting('settings', 'serverKey')
        self.voteURL = self.settings.GetSetting('settings', 'voteURL')
        self.wood = self.settings.GetIntSetting('settings', 'Wood')
        self.stone = self.settings.GetIntSetting('settings', 'Stone')


    def response(self, Args, Player):
        response = self.checkVote(Player)
        Util.Log(Player.Name +" voted, response: "+response)
        if response == '0':
            Player.Message("You didn't vote in the last 24 hours. Please vote on "+self.voteURL)
        elif response == '1':
            Player.Message("You have voted. Thank you for your vote.")
            self.Claim(Player)
            self.rewardPlayer(Player)
        elif response == '2':
            Player.Message("You already claimed your reward.")

    def loadIniSettings(self):
        if not Plugin.IniExists("vote"):
            Plugin.CreateIni('vote')
            ini = Plugin.GetIni('vote')
            ini.AddSetting('settings', 'serverKey', 'YourServerKey')
            ini.AddSetting('settings', 'VoteURL', 'YourVoteURL')
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
        #Util.Log(str(self.wood))
        #Util.Log(str(self.stone))
        player.Inventory.Add("Wood", 500)
        player.Inventory.Add("Stones", 250)