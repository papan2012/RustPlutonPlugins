__author__ = 'PanDevas'
__version__ = '0.5'

import clr
clr.AddReferenceByPartialName("Pluton", "Assembly-CSharp-firstpass", "Assembly-CSharp")

import Pluton
import sys
path = Util.GetPublicFolder()
sys.path.append(path + "\\Python\\Lib\\")
import time

import Facepunch
import CommunityEntity
import Network

try:
    import json
except ImportError:
    raise ImportError("LegacyBroadcast: Can not find JSON in Libs folder [Pluton\Python\Libs\] *DOWNLOAD: http://forum.pluton-team.org/resources/microjson.54/*")


# Thanks to Jakkee for helping me with overview thingy <3
welcomegui = [
    {
        "name": "welcomeUI",
        #"parent": "overlay",
        "components":
        [
            {
                "type": "UnityEngine.UI.Image",
                "color": "0.1 0.1 0.1 0.85",
            },
            {
                "type": "RectTransform",
                "anchormin": "0.205 0.205",
                "anchormax": "0.795 0.795"
            },
            {
                "type": "NeedsCursor"
            }
        ]
    },
    {
        "parent": "welcomeUI",
        "components":
        [
            {
                "type": "UnityEngine.UI.Text",
                "color": "0.8 0.8 0.8 0.7",
                "text": "[TEXT]",
                "fontSize": 13
            },
            {
                "type": "RectTransform",
                "anchormin": "0.05 0.2",
                "anchormax": "0.8 0.8"
            }
        ]
    },
    {
        "parent": "welcomeUI",
        "name" : "toptray",
        "components":
            [
                {
                    "type": "UnityEngine.UI.Image",
                    "color": "0.1 0.1 0.1 0.7",
                },
                {
                    "type": "RectTransform",
                    "anchormin": "0.01 0.90",
                    "anchormax": "0.99 0.99"
                }
            ]
    },
    {
        "parent": "welcomeUI",
        "name" : "welcome",
        "components":
            [
                {
                    "type": "UnityEngine.UI.Text",
                    "color": "1.0 1.0 1.0 0.95",
                    "text": "Welcome To <color=red>CroHQ Community Server</color>!",
                    "fontSize": 20,
                     "align": "MiddleCenter"
                },
                {
                    "type": "RectTransform",
                    "anchormin": "0.0 0.90",
                    "anchormax": "0.99 0.99"
                }
            ]

    },
    {
        "parent": "welcomeUI",
        "name" : "bottray",
        "components":
            [
                {
                    "type": "UnityEngine.UI.Image",
                    "color": "0.1 0.1 0.1 0.1",
                },
                {
                    "type": "RectTransform",
                    "anchormin": "0.89 0.05",
                    "anchormax": "0.99 0.15"
                }
            ]
    },
    {
        "parent": "welcomeUI",
        "components":
        [
            {
                "type": "UnityEngine.UI.Text",
                "color": "0.1 0.6 0.1 1.0",
                "text": "OK",
                "fontSize": 18,
                "align": "MiddleCenter"
            },
            {
                "type": "RectTransform",
                "anchormin": "0.89 0.05",
                "anchormax": "0.99 0.15"
            }
         ]
     },
    {
        "parent": "welcomeUI",
        "name" : "okbutton",
        "components":
        [
            {
                "type": "UnityEngine.UI.Button",
                "close": "welcomeUI",
                "command": "close.window",
                "color": "0.2 0.2 0.2 0.5"
            },
            {
                "type": "RectTransform",
                "anchormin": "0.89 0.05",
                "anchormax": "0.99 0.15"
            }
        ]
    }
]


string = json.encode(welcomegui)
broadcast = json.makepretty(string)


class WelcomeScreen():

    def On_PluginInit(self):
        if DataStore.GetTable("Welcomed"):
            self.shown_players = DataStore.Get("Welcomed", "players")
        else:
            DataStore.Add("Welcomed", "players", [])
            self.shown_players = DataStore.Get("Welcomed", "players")

        self.flagText = "If you are tired of being raided the moment you log off we can offer you one of a kind experience on our server. \n\n" \
                       "There's an offline raid protection plugin in place that will protect all of your buildings from damage while you are offline, for a period of 24 hours.\n" \
                       "If you don't come online in that 24 hour period your building will not be protected any longer so be sure to log in at least once a day to refresh the timer.\n\n" \
                       "Be sure to check available commands and additional help by issuing following commands in chat:\n" \
                       "1. /help\n" \
                       "2. /trhelp\n" \
                       "3. /aor\n" \
                       "\nFor any additional questions, feel free to ask in chat, someone will know the answer.\n" \
                       "\nHappy gaming!"

    def On_PlayerLoaded(self, player):
#        if player.SteamID not in self.shown_players:
        CommunityEntity.ServerInstance.ClientRPCEx(Network.SendInfo(player.basePlayer.net.connection), None, "AddUI", Facepunch.ObjectList(broadcast.Replace("[TEXT]", self.flagText)))

    def On_ClientConsole(self, cce):
        player = cce.User
        playerID = player.SteamID
        if cce.cmd == 'close.window':
            CommunityEntity.ServerInstance.ClientRPCEx(Network.SendInfo(player.basePlayer.net.connection), None, "DestroyUI", Facepunch.ObjectList("welcomeUI"))
#            self.shown_players.append(playerID)
        if cce.cmd == "create.window":
            CommunityEntity.ServerInstance.ClientRPCEx(Network.SendInfo(player.basePlayer.net.connection), None, "AddUI", Facepunch.ObjectList(broadcast.Replace("[TEXT]", self.flagText)))