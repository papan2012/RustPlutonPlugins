__author__ = 'PanDevas'
__version__ = '0.113'

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
broadcastgui = [
    {
        "name": "broadcastui",
        #"parent": "Overlay",
        "components":
        [
            {
                "type": "UnityEngine.UI.Image",
                "color": "0.8 0.8 0.8 0.4",
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
        "parent": "broadcastui",
        "components":
        [
            {
                "type": "UnityEngine.UI.Text",
                "color": "0.5 0.8 0.8 0.8",
                "text": "[TEXT]",
                "fontSize": 13
            },
            {
                "type": "RectTransform",
                "anchormin": "0.1 0.5",
                "anchormax": "0.955 0.955"
            }
        ]
    },
    {
        "parent": "broadcastui",
        "name" : "okbutton",
        "components":
        [

            {
                "type": "UnityEngine.UI.Button",
                "text": "OK",
                "close": "broadcastui",
                "command": "close.window",
                "color": "0.2 0.1 0.1 0.5",
                "scale": "1.5 1.5"
            },
            {
                "type": "RectTransform",
                "anchormin": "0.89 0.05",
                "anchormax": "0.99 0.15"
            }
        ]
    },
    {
        "parent": "okbutton",
        "components":
        [
            {
                "type": "UnityEngine.UI.Text",
                "color": "0.9 0.2 0.5 0.9",
                "text": "OK",
                "fontSize": 20,
            },
            {
                "type": "RectTransform",
                "anchormin": "0.1 0.1",
                "anchormax": "0.99 0.99"
            }
        ]
    }
]


string = json.encode(broadcastgui)
broadcast = json.makepretty(string)


class WelcomeScreen():

    def On_Command(self, cmd):
        command = cmd.cmd
        player = cmd.User

        if command == 't':
            flagText = "Wall of text with all the rules is here \n with a new line <color=red>red</color>"
            Util.Log(str(broadcast))
            CommunityEntity.ServerInstance.ClientRPCEx(Network.SendInfo(player.basePlayer.net.connection), None, "AddUI", Facepunch.ObjectList(broadcast.Replace("[TEXT]", flagText)))

            tdata = Plugin.CreateDict()
            tdata['player'] = player
            Plugin.CreateTimer("Test", 15000, tdata).Start()

        if command == 'toff':
            CommunityEntity.ServerInstance.ClientRPCEx(Network.SendInfo(player.basePlayer.net.connection), None, "DestroyUI", Facepunch.ObjectList("broadcastui"))


    def TestCallback(self, timer):
        player = timer.Args['player']
        timer.Kill()

        CommunityEntity.ServerInstance.ClientRPCEx(Network.SendInfo(player.basePlayer.net.connection), None, "DestroyUI", Facepunch.ObjectList("broadcastui"))


    def On_ClientConsole(self, cce):
        player = cce.User
        if cce.cmd == 'close.window':
            CommunityEntity.ServerInstance.ClientRPCEx(Network.SendInfo(player.basePlayer.net.connection), None, "DestroyUI", Facepunch.ObjectList("broadcastui"))
        Util.Log(str(type(cce)))
        Util.Log(str(cce.cmd))



