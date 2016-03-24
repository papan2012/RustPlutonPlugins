__author__ = 'PanDevas'
__version__ = '1.12'

import clr
clr.AddReferenceByPartialName("Pluton", "Assembly-CSharp-firstpass", "Assembly-CSharp","Facepunch.Network")

import Pluton
import sys

import Facepunch
import CommunityEntity
import Network
import datetime

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
        Util.Log(str(ownerPlayers))
        return ownerPlayers

    def _createNotification(self, player):
        flagText = "Owner "
        self.buildingOwnerInfo.append(player.SteamID)
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
            self.buildingOwnerInfo.remove(player.SteamID)
        except:
            pass


    def On_Placement(self, buildingpart):
        player = buildingpart.Builder
        location = str(buildingpart.BuildingPart.Location)
        buildingPartName = buildingpart.BuildingPart.baseEntity.LookupShortPrefabName().split('.')[0]
        # for shared locations of buildingparts
        locationCheck = DataStore.Get("BuildingPartOwner", location)
        if locationCheck:
            alredayPlacedList = DataStore.Get("SharedBuildingLocations", location)
            if alredayPlacedList:
                alredayPlacedList.append(buildingPartName)
                DataStore.Add("SharedBuildingLocations", location, alredayPlacedList)
            else:
                    DataStore.Add("SharedBuildingLocations", location, [buildingPartName])
        else:
            DataStore.Add("BuildingPartOwner", location, player.SteamID)

    def On_BuildingPartDemolished(self, bpde):
        self.removeFromDatastore(bpde)

    def On_BuildingPartDestroyed(self, bpde):
        self.removeFromDatastore(bpde)


    def removeFromDatastore(self, bpde):
        bpdeEntitiName = bpde.BuildingPart.baseEntity.LookupShortPrefabName().split('.')[0]
        location = str(bpde.BuildingPart.Location)

        sharedPlacements = DataStore.Get("SharedBuildingLocations", location)

        if sharedPlacements:
            if bpdeEntitiName in sharedPlacements:
                sharedPlacements.remove(bpdeEntitiName)
                if len(sharedPlacements) == 0:
                    DataStore.Remove("SharedBuildingLocations", location)
        else:
            DataStore.Remove("BuildingPartOwner", location)


    def On_BeingHammered(self, he):
        '''
        this is a dirty workaround when the doors are not placed in exact location with the frame
        and a helper function for determining ownership of building parts
        '''
        getOwnerObjects = ["BuildingBlock", "Door"]

        if he.Victim.baseEntity.GetType().ToString() in getOwnerObjects:

            player = he.Player
            location = str(he.Victim.Location)
            victimID = DataStore.Get("BuildingPartOwner", location)
            playerD = DataStore.Get("Players", victimID)

            if player.SteamID in self.buildingOwnerInfo:
                if not victimID:
                    player.Message("BuildingPart not found, you are the new owner. Tell the admin what happened.")
                    DataStore.Add("BuildingPartOwner", location, player.SteamID)
                    victimID = player.SteamID
                victim = Server.FindPlayer(victimID)
                if not victim:
                    for pl in Server.OfflinePlayers.Values:
                        if pl.SteamID == victimID:
                            victim = pl
                player.Message("This BuildingPart belongs to "+victim.Name+' ('+playerD['tribe']+')')

            if self.remove == 1 and player.Name == self.admin:
                DataStore.Remove("BuildingPartOwner", location)
                player.Message("Building Part removed from datastore")



    def On_Command(self, cmd):
        player = cmd.User
        command = cmd.cmd
        args = str.join(' ', cmd.args)

        commands = ('owner', 'ownerme','remove')
        if command in commands:
            if command == 'owner':
                if player.SteamID not in self.buildingOwnerInfo:
                    player.Message("Building owner report ON")
                    self._createNotification(player)
                else:
                    player.Message("Building owner report OFF")
                    self._removeNotification(player)


            #Util.Log(player.Name == self.admin)
            if command == 'remove' and player.Name == self.admin:
                if self.remove:
                    player.Message("Building removal off")
                    self.remove = 0
                else:
                    player.Message("Hit with the hammer to remove the building from datastore")
                    self.remove = 1

    def On_PlayerDisconnected(self, player):
        if player.SteamID in self.buildingOwnerInfo:
            self.buildingOwnerInfo.remove(player.SteamID)
