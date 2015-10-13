__author__ = 'PanDevas'
__version__ = '0.1'

import clr
import sys

clr.AddReferenceByPartialName("Pluton", "Assembly-CSharp-firstpass", "Assembly-CSharp")
path = Util.GetPublicFolder()
sys.path.append(path + "\\Python\\Lib\\")

import Pluton
import Facepunch
import CommunityEntity
import Network

try:
    import json
except ImportError:
    raise ImportError("LegacyBroadcast: Can not find JSON in Libs folder [Pluton\Python\Libs\] *DOWNLOAD: http://forum.pluton-team.org/resources/microjson.54/*")

welcomeui = [
    {
        "name": "welcomeui",
        "parent": "Overlay",
        "components":
        [
            {
                "type": "UnityEngine.UI.Image",
                "color": "0.0 0.0 1.0 0.2",
            },
            {
                "type": "RectTransform",
                "anchormin": "0.0 0.0",
                "anchormax": "1.0 1.0"
            }
        ]
    },
    {
        "parent": "welcomeui",
        "components":
        [
            {
                "type": "UnityEngine.UI.Text",
                "text": "[TEXT]",
                "fontSize": 20,
                "align": "MiddleCenter",
            },
            {
                "type": "RectTransform",
                "anchormin": "0.005 0.005",
                "anchormax": "0.995 0.995"
            }
        ]
    },
    {
        "parent:": "welcomeui",
        "components":
        [
            {
                "type": "UnityEngine.UI.Button",
                "color": "0.9 0.8 0.9 0.8",
            },
            {
                "type": "UnityEngine.UI.Text",
                "color": "1.0 1.0 1.0 0.9",
                "text": "[GUMB]"
            }
        ]
    }

]

gumbui = [
    {
        "parent": "welcomeui",
        "components":
        [
            {
                "type": "UnityEngine.UI.Image",
                "text": "Gumb",
            }
        ]
    }
]

string = json.encode(welcomeui)
welcome = json.makepretty(string)

gstring = json.encode(gumbui)
gumb = json.makepretty(gstring  )


class WelcomeScreen():


    def On_PlayerLoaded(self, player):
        pass


    def On_Command(self, cmd):
        welcomeText = "Text2"
        command = cmd.cmd
        player = cmd.User


        if command == 'a':
            Util.Log(player.Name)
            CommunityEntity.ServerInstance.ClientRPCEx(Network.SendInfo(player.basePlayer.net.connection), None, "DestroyUI", Facepunch.ObjectList("welcomeui"))
        if command == 'wel':
            CommunityEntity.ServerInstance.ClientRPCEx(Network.SendInfo(player.basePlayer.net.connection), None, "AddUI", Facepunch.ObjectList(welcome.Replace("[TEXT]", welcomeText)))

        if command == 'bot':
            CommunityEntity.ServerInstance.ClientRPCEx(Network.SendInfo(player.basePlayer.net.connection), None, "AddUI", Facepunch.GUI.Controls.Button(gumb))

        if command == 'help':
            Util.Log(str(help(Facepunch.GUI.Controls)))

