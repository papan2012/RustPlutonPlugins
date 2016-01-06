__author__ = 'PanDevas'
__version__ = '0.1'

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
        self.serverKey = 'kx41a7h1dc2mvyyc59i6o22f19k5igunv7'

    def On_Command(self, cmd):
        command = cmd.cmd
        player = cmd.User
        if command == 'vote':
            response = self.checkVote(player)
            Util.Log("response"+response)
            if response == '0':
                player.Message("You didn't vote in the last 24 hours.")
            elif response == '1':
                player.Message("You have voted. Thank you for your vote.")
                self.Claim(player)
                self.rewardPlayer(player)
            elif response == '2':
                player.Message("You already claimed your reward.")


    def checkVote(self, player):
        steamID = player.SteamID

        httpServer = httplib.HTTPConnection('rust-servers.net', 80)
        params = urllib.urlencode({'object': 'votes', 'element':'claim', 'key': self.serverKey, 'steamid': steamID})
        headers = {"Content-type": "application/x-www-form-urlencoded", "Accept": "text/plain"}
        Util.Log(str(params))
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
            Util.Log(str(params))
            httpServer.request("POST", "/api/?", params, headers)

            response = httpServer.getresponse()
            Util.Log(str(response.status)+' '+str(response.reason))
            Util.Log(str(response.read()))
            httpServer.close()

    def rewardPlayer(self, player):
        Util.Log(str(dir(player)))
        player.Inventory.Add("Wood", 500)
        player.Inventory.Add("Stones", 250)