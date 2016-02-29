__author__ = 'PanDevas'
__version__ = '0.1'

import clr
clr.AddReferenceByPartialName("Pluton.Core", "Pluton.Rust", "Assembly-CSharp-firstpass", "Assembly-CSharp","Facepunch.Network")

import Pluton.Core
import Pluton.Rust
import time
import Facepunch
import CommunityEntity
import Network
import sys

path = Util.GetPublicFolder()
sys.path.append(path + "\\Python\\Lib\\")

try:
    import json
except ImportError:
    raise ImportError("Offline Protection: Can not find JSON in Libs folder [Pluton\Python\Libs\] *DOWNLOAD: http://forum.pluton-team.org/resources/microjson.54/*")

takemark = [
    {
        "name": "takeui",
        "parent": "HUD/Overlay",
        "components":
        [
            {
                "type": "UnityEngine.UI.Image",
                "color": "0.1 0.3 0.1 0.6",
            },
            {
                "type": "RectTransform",
                "anchormin": "0.051 0.955",
                "anchormax": "0.101 0.974"
            }
        ]
    },
    {
        "parent": "takeui",
        "components":
        [
            {
                "type": "UnityEngine.UI.Text",
                "text": "[TEXT]",
                "color":  "0.1 0.9 0.1 0.8",
                "fontSize": 11,
                "align": "MiddleCenter",
            },
            {
                "type": "RectTransform",
                "anchormin": "0.005 0.005",
                "anchormax": "0.99 0.995"
            }
        ]
    }
]
string = json.encode(takemark)
takemark = json.makepretty(string)

class OPBuildingChanger():

    def On_PluginInit(self):
        self.takeoverPlayers = self.datastoreInit()

        settings = self.loadIniSettings()
        self.takeoverProtection = settings.GetIntSetting('settings', 'takeoverProtection')

    def datastoreInit(self):
        if not DataStore.GetTable("PlayerFlags"):
            DataStore.Add("PlayerFlags", "Take", [])
        elif not DataStore.ContainsKey("PlayerFlags", "Take"):
            DataStore.Add("PlayerFlags", "Take",[])

        takeoverPlayers = DataStore.Get("PlayerFlags", "Take")

        for playerID in takeoverPlayers:
            player = Server.FindPlayer(playerID)
            if player:
                self._removeNotification(player)
            takeoverPlayers.remove(playerID)

        return takeoverPlayers

    def loadIniSettings(self):
        if not Plugin.IniExists("settings"):
            Plugin.CreateIni("settings")
            ini = Plugin.GetIni("settings")
            ini.AddSetting("settings", "takeoverProtection", "259200")
            ini.Save()
        return Plugin.GetIni("settings")


    def On_BeingHammered(self, he):
        player = he.Player
        location = he.Victim.Location
        victimID = DataStore.Get("BuildingPartOwner", str(location))
        playerD = DataStore.Get("Players", player.SteamID)
        victimD = DataStore.Get("Players", victimID)

        if player.SteamID in player.SteamID in self.takeoverPlayers:
            if player.SteamID == victimID:
                player.Message("This is already your building.")
            elif playerD['tribe'] != 'Survivors' and playerD['tribe'] == victimD['tribe']:
                player.Message("You can't take buildings from your tribe members!")
            elif self.protectFromTakeover(victimID):
                player.Message("This player buildings can't be taken for now.")
            elif not player.basePlayer.HasPlayerFlag(player.basePlayer.PlayerFlags.HasBuildingPrivilege):
                player.Message("You need to have building permisions to make the takeover!")
            else:
                DataStore.Remove("BuildingPartOwner", str(location))
                DataStore.Add("BuildingPartOwner", str(location), player.SteamID)
                player.Message("This building part now belongs to you.")


    def protectFromTakeover(self, playerID):
        '''
        Turns off protection for players until they are more then 24 hours offline
        Works for whole Tribe, only one member refreshes all timers

        :param player:
        :return: bool
        '''
        playerData = DataStore.Get('Players', playerID)
        player = Server.FindPlayer(playerID)
        if not player and (playerData['tribe'] == 'Survivors') and ((time.time() - playerData['lastonline']) < self.takeoverProtection):
            return True
        elif playerData['tribe'] != 'Survivors':
            playerTribe = playerData['tribe']
            playerTribeData = DataStore.Get('Tribes', playerTribe)
            tribeMembers = playerTribeData['tribeMembers']
            protect = False
            if playerTribe in DataStore.Keys("pvpTribeFlags"):
                return False
            else:
                for tribeMemberID in tribeMembers:
                    playerD = DataStore.Get('Players', tribeMemberID)
                    player = Server.FindPlayer(tribeMemberID)
                    if player:
                        return False
                        break
                    elif (time.time() - playerD['lastonline']) < self.takeoverProtection:
                        protect = True
            return protect
        else:
            return False

    def _createNotification(self, player):
        flagText = "Takeover "
        self.takeoverPlayers.append(player.SteamID)
        if player:
            CommunityEntity.ServerInstance.ClientRPCEx(Network.SendInfo(player.basePlayer.net.connection), None, "AddUI", Facepunch.ObjectList(takemark.Replace("[TEXT]", flagText)))
        else:
            Util.Log("Unable to create takeover flag"+str(player))

    def _removeNotification(self, player):
        if player:
            CommunityEntity.ServerInstance.ClientRPCEx(Network.SendInfo(player.basePlayer.net.connection), None, "DestroyUI", Facepunch.ObjectList("takeui"))
        else:
            Util.Log("Unable to remove flag"+str(player))
        try:
            self.takeoverPlayers.remove(player.SteamID)
        except:
            pass



    def On_Command(self, cce):
        command = cce.cmd
        player = cce.User

        if command == 'take':
            if player.SteamID in self.takeoverPlayers:
                player.Message("Takeover OFF")
                self._removeNotification(player)
            else:
                player.Message("Takeover ON")
                self._createNotification(player)

    def On_PlayerDisconnected(self, player):
        if player.SteamID in self.takeoverPlayers:
            self.takeoverPlayers.remove(player.SteamID)
