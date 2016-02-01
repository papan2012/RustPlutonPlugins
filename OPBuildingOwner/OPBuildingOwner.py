__author__ = 'PanDevas'
__version__ = '1.12'

import clr
clr.AddReferenceByPartialName("Pluton")

import Pluton
import sys
path = Util.GetPublicFolder()
import datetime

class OPBuildingOwner():
    '''
    Mozda cu trebati podesiti cesci save zbog building checka u antiofflineraid pluginu
    '''
    def __init__(self):
        self.admin = 'PanDevas'
        self.remove = 0
        self.buildingOwnerInfo = []

    def On_ServerSaved(self):
        DataStore.Save()


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
                    self.buildingOwnerInfo.append(player.SteamID)
                else:
                    self.buildingOwnerInfo.remove(player.SteamID)

            #Util.Log(player.Name == self.admin)
            if command == 'remove' and player.Name == self.admin:
                if self.remove:
                    player.Message("Building removal off")
                    self.remove = 0
                else:
                    player.Message("Hit with the hammer to remove the building from datastore")
                    self.remove = 1