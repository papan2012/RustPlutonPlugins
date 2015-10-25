__author__ = 'PanDevas'
__version__ = '0.6'

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
    raise ImportError("LegacyhelpJson: Can not find JSON in Libs folder [Pluton\Python\Libs\] *DOWNLOAD: http://forum.pluton-team.org/resources/microjson.54/*")


# Thanks to Jakkee for helping me with overview thingy <3
helpgui = [
    {
        "name": "helpUI",
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
        "parent": "helpUI",
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
                "anchormin": "0.05 0.05",
                "anchormax": "0.80 0.80"
            }
        ]
    },
    {
        "parent": "helpUI",
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
        "parent": "helpUI",
        "name" : "welcome",
        "components":
            [
                {
                    "type": "UnityEngine.UI.Text",
                    "color": "0.3 0.3 1.0 0.95",
                    "text": "Help Window",
                    "fontSize": 20,
                    "align": "MiddleLeft"
                },
                {
                    "type": "RectTransform",
                    "anchormin": "0.02 0.90",
                    "anchormax": "0.99 0.99"
                }
            ]

    },
    {
        "parent": "helpUI",
        "components":
        [
            {
                "type": "UnityEngine.UI.Text",
                "color": "0.9 0.9 0.9 1.0",
                "text": "AntiOfflineRaid",
                "fontSize": 18,
                "align": "MiddleCenter"
            },
            {
                "type": "RectTransform",
                "anchormin": "0.03 0.82",
                "anchormax": "0.20 0.87"
            }
         ]
     },
    {
        "parent": "helpUI",
        "name" : "AOR",
        "components":
        [
            {
                "type": "UnityEngine.UI.Button",
                "command": "help.aor",
                "color": "0.2 0.2 0.2 0.5"
            },
            {
                "type": "RectTransform",
                "anchormin": "0.01 0.82",
                "anchormax": "0.20 0.87"
            }
        ]
    },
        {
        "parent": "helpUI",
        "components":
        [
            {
                "type": "UnityEngine.UI.Text",
                "color": "0.9 0.9 0.9 1.0",
                "text": "Tribes",
                "fontSize": 18,
                "align": "MiddleCenter"
            },
            {
                "type": "RectTransform",
                "anchormin": "0.21 0.82",
                "anchormax": "0.40 0.87"
            }
         ]
     },
    {
        "parent": "helpUI",
        "name" : "Tribes",
        "components":
        [
            {
                "type": "UnityEngine.UI.Button",
                "command": "help.tribes",
                "color": "0.2 0.2 0.2 0.5"
            },
            {
                "type": "RectTransform",
                "anchormin": "0.21 0.82",
                "anchormax": "0.40 0.87"
            }
        ]
    },
    {
        "parent": "helpUI",
        "components":
        [
            {
                "type": "UnityEngine.UI.Text",
                "color": "0.9 0.9 0.9 1.0",
                "text": "Door System",
                "fontSize": 18,
                "align": "MiddleCenter"
            },
            {
                "type": "RectTransform",
                "anchormin": "0.41 0.82",
                "anchormax": "0.60 0.87"
            }
         ]
     },
    {
        "parent": "helpUI",
        "name" : "Door System",
        "components":
        [
            {
                "type": "UnityEngine.UI.Button",
                "command": "help.doors",
                "color": "0.2 0.2 0.2 0.5"
            },
            {
                "type": "RectTransform",
                "anchormin": "0.41 0.82",
                "anchormax": "0.60 0.87"
            }
        ]
    },
    {
        "parent": "helpUI",
        "components":
        [
            {
                "type": "UnityEngine.UI.Text",
                "color": "0.9 0.9 0.9 1.0",
                "text": "Server Info",
                "fontSize": 18,
                "align": "MiddleCenter"
            },
            {
                "type": "RectTransform",
                "anchormin": "0.61 0.82",
                "anchormax": "0.80 0.87"
            }
         ]
     },
    {
        "parent": "helpUI",
        "name" : "Door System",
        "components":
        [
            {
                "type": "UnityEngine.UI.Button",
                "command": "help.server",
                "color": "0.2 0.2 0.2 0.5"
            },
            {
                "type": "RectTransform",
                "anchormin": "0.61 0.82",
                "anchormax": "0.80 0.87"
            }
        ]
    },
    {
        "parent": "helpUI",
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
        "parent": "helpUI",
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
        "parent": "helpUI",
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
        "parent": "helpUI",
        "name" : "okbutton",
        "components":
        [
            {
                "type": "UnityEngine.UI.Button",
                "close": "helpUI",
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


string = json.encode(helpgui)
helpJson = json.makepretty(string)


class TribesHelp():

    def On_PluginInit(self):
        self.aorHelp="ANTIOFFLINERAID\n\n" \
                     "The point of the AntiOfflineRaid system is, well, to prevent offline raid.\n" \
                     "Since it's one of the kind, you'll have to get to know how it works.\n\n" \
                     "Basically, when you go offline, your buildings get total protection from any kind of damage for 24 hours.\n" \
                     "In case you don't come online in the next 24 hours, your building will be susceptible to damage.\n" \
                     "AntiofflineRaid system doesn't prevent decay!\n" \
                     "if a player attacks you or one of or your buildings, while you are online, you and the attacking player will be flagged with a 15 minute timer.\n" \
                     "If you log off while the timer is still on, timer will be extended for 15 minutes, and you're building will not be protected until that timer runs out.\n" \
                     "That will prevent loging out in the middle of the raid to prevent raiders to take what they came for.\n" \
                     "So, if you wan't to protect your stuff, you'll have to fight for it!\n\n" \
                     "Tribe system is implemented to prevent players that are in the tribe to trigger AntiOfflineRaid system mechanisms.\n" \
                     "If you're playing with someone, join a Tribe to avoid any inconveniance and get some benefits.\n" \
                     "More about tribe mechanism in Tribes help section."
        self.tribeHelp="TRIBES\n\n" \
                       "If you wan't to live with someone, or use his doors, you'll have to join the tribe with him.\n" \
                       "Tribe members can access all doors belonging to other tribe members. \n" \
                       "If you're not part of the Tribe, you won't be able to use doors on tribe member buildings, even if they don't have a codelock, or you know the lock code.\n" \
                       "More about door changes read in Doors help section.\n\n" \
                       "When you're in a Tribe, aggression flags are applied to the whole Tribe\n" \
                       "Timer for offline raid protection counts from the moment last member of the tribe went offline\n" \
                       "Tribe members are not flaged if they attack each other.\n\n" \
                       "Tribe system is managed by chat commands for now. Write /trhelp in chat to get the list of comands available.\n\n"
        self.doorHelp="DOORS\n\n" \
                      "Door system was implemented for two reasons:\n" \
                      " 1. We couldn't allow players using door on buildings whos owners were offline.\n" \
                      " 2. There's a rare glitch, or a hack, that lets people open doors without the code authrization\n" \
                      "   - this system prevents both problems.\n\n" \
                      "When you place a door, they are bound to your SteamID. Only you can open and close them.\n" \
                      "So there's no reall need for codelocks on doors any longer.\n\n" \
                      "If you're member of a Tribe, all tribe members will be able to access your doors automagically.\n" \
                      "If you need some privacy, put codelocks on chests. \n" \
                      "That will prevent anyone opening them without the code.\n\n"
        self.serverInfo="SERVER INNFO\n\n" \
                        " - decay lowered to 20% effectiveness\n" \
                        " - crafting times of External stone walls is increessed to 2 minutes for wooden, and 4 minutes for stone walls\n" \
                        "\n\n\nIf you got any questions, ask in chat, someone will know the answer.\n" \
                        "For any problems with the server plugins, contact Pan Devas.\n" \
                        "\nJoin our Steam Group ''CroHQ Rust TribeWars'' for server updates and additional information."



    def loadIniSettings(self):

        if not Plugin.IniExists('settings'):
            Plugin.CreateIni('settings')
            ini = Plugin.GetIni('settings')
            ini.AddSetting("section name", 'text', 'textstring')
            ini.AddSetting("section name2", 'text', 'textstring')
            ini.Save()

        return Plugin.GetIni('settings')


        
    def createGUI(self, player, help):
        CommunityEntity.ServerInstance.ClientRPCEx(Network.SendInfo(player.basePlayer.net.connection), None, "AddUI", Facepunch.ObjectList(helpJson.Replace("[TEXT]", help)))



    def destroyGUI(self, player):
        CommunityEntity.ServerInstance.ClientRPCEx(Network.SendInfo(player.basePlayer.net.connection), None, "DestroyUI", Facepunch.ObjectList("helpUI"))

    def On_ClientConsole(self, cce):
        player = cce.User
        playerID = player.SteamID
        self.destroyGUI(player)
        if cce.cmd == 'close.help':
            self.destroyGUI(player)
        if cce.cmd == "help.aor":
            self.curWindow = 'aorHelp'
            self.createGUI(player, self.aorHelp)
        if cce.cmd == "help.tribes":
            self.curWindow = 'tribeHelp'
            self.createGUI(player, self.tribeHelp)
        if cce.cmd == "help.doors":
            self.curWindow = 'doorHelp'
            self.createGUI(player, self.doorHelp)
        if cce.cmd == "help.server":
            self.curWindow = 'serverHelp'
            self.createGUI(player, self.serverInfo)


    def On_Command(self, cmd):
        command = cmd.cmd
        player = cmd.User

        if command == 'help':
            self.createGUI(player, self.aorHelp)

