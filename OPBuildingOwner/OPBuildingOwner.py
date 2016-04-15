__author__ = 'PanDevas'
__version__ = '1.12'

import clr
clr.AddReferenceByPartialName("Pluton.Core", "Pluton.Rust", "Assembly-CSharp-firstpass", "Assembly-CSharp","Facepunch.Network")

import Pluton.Core
import Pluton.Rust

import sys

import Facepunch
import CommunityEntity
import Network
import datetime
import BasePlayer

path = Util.GetPublicFolder()
sys.path.append(path + "\\Python\\Lib\\")


try:
    import json
except ImportError:
    raise ImportError("Offline Protection: Can not find JSON in Libs folder [Pluton\Python\Libs\] *DOWNLOAD: http://forum.pluton-team.org/resources/microjson.54/*")

takemark = [
    {
        "name": "ownerUI",
        "parent": "HUD/Overlay",
        "components":
        [
            {
                "type": "UnityEngine.UI.Image",
                "color": "0.3 0.3 0.1 0.6",
            },
            {
                "type": "RectTransform",
                "anchormin": "0.101 0.955",
                "anchormax": "0.151 0.974"
            }
        ]
    },
    {
        "parent": "ownerUI",
        "components":
        [
            {
                "type": "UnityEngine.UI.Text",
                "text": "[TEXT]",
                "color":  "0.8 0.8 0.1 0.8",
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


class OPBuildingOwner():
    '''
    Mozda cu trebati podesiti cesci save zbog building checka u antiofflineraid pluginu
    '''
    def __init__(self):
        Commands.Register('owner').setCallback('owner')

        self.admin = 'PanDevas'
        self.remove = 0
        self.buildingOwnerInfo = self.datastoreInit()

    def On_ServerSaved(self):
        Util.Log(str(datetime.datetime.now()))
        DataStore.Save()

    def datastoreInit(self):
        if not DataStore.GetTable("PlayerFlags"):
            DataStore.Add("PlayerFlags", "Owner", [])
        elif not DataStore.ContainsKey("PlayerFlags", "Owner"):
            DataStore.Add("PlayerFlags", "Owner",[])

        ownerPlayers = DataStore.Get("PlayerFlags", "Owner")

        for playerID in ownerPlayers:
            player = Server.FindPlayer(playerID)
            if player:
                self._removeNotification(player)
            ownerPlayers.remove(playerID)
        return ownerPlayers

    def _createNotification(self, player):
        flagText = "Owner "
        self.buildingOwnerInfo.append(player.GameID)
        if player:
            CommunityEntity.ServerInstance.ClientRPCEx(Network.SendInfo(player.basePlayer.net.connection), None, "AddUI", Facepunch.ObjectList(takemark.Replace("[TEXT]", flagText)))
        else:
            Util.Log("Unable to create takeover flag"+str(player))

    def _removeNotification(self, player):
        if player:
            CommunityEntity.ServerInstance.ClientRPCEx(Network.SendInfo(player.basePlayer.net.connection), None, "DestroyUI", Facepunch.ObjectList("ownerUI"))
        else:
            Util.Log("Unable to remove flag"+str(player))
        try:
            self.buildingOwnerInfo.remove(player.GameID)
        except:
            pass

    def On_BeingHammered(self, he):
        '''
        this is a dirty workaround when the doors are not placed in exact location with the frame
        and a helper function for determining ownership of building parts
        '''
        getOwnerObjects = ["BuildingBlock", "Door", "SimpleBuildingBlock", 'StabilityEntity', 'BuildingPrivlidge']
        hurtEntity = he.Victim.baseEntity.GetType().ToString()

        if hurtEntity in getOwnerObjects:

            player = he.Player
            victimID = he.Victim.baseEntity.OwnerID
            playerD = DataStore.Get("Players", victimID)

            if player.GameID in self.buildingOwnerInfo:
                victim = Server.FindPlayer(victimID)

                if victim:
                    victimName = victim.Name
                else:
                    victim = BasePlayer.FindSleeping(victimID)
                    if victim:
                        victimName = victim.displayName
                    else:
                        victimName = playerD['name']
                player.Message("This belongs to "+victimName+' ('+playerD['tribe']+')')

                if hurtEntity == 'BuildingPrivlidge':
                    player.Message('Authorized players:')
                    for authed in he.Victim.baseEntity.authorizedPlayers:
                        player.Message(str(authed.username))


    def owner(self, Args, Player):
        if Player.GameID not in self.buildingOwnerInfo:
            Player.Message("Building owner report ON")
            self._createNotification(Player)
        else:
            Player.Message("Building owner report OFF")
            self._removeNotification(Player)

    def On_PlayerDisconnected(self, player):
        if player.GameID in self.buildingOwnerInfo:
            self.buildingOwnerInfo.remove(player.GameID)
