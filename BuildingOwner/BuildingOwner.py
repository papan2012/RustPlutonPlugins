__author__ = 'PanDevas'
__version__ = '1.12'

import clr
clr.AddReferenceByPartialName("Pluton")

import Pluton
import sys
path = Util.GetPublicFolder()
import datetime

class BuildingOwner():
    '''
    Mozda cu trebati podesiti cesci save zbog building checka u antiofflineraid pluginu
    '''
    def __init__(self):
        self.admin = 'PanDevas'
        self.buildingOwnerInfo = []

    def On_ServerSaved(self):
        DataStore.Save()
        Server.Broadcast("Server saved.")

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
        # if not DataStore.Get("BuildingPartOwner", location):
        #     player.Message("BuildingPart not in Datastore, hit it with a Hammer to add it!")


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
            else:
                DataStore.Remove("SharedBuildingLocations", location)
                DataStore.Remove("BuildingPartOwner", location)
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
            if not victimID:
                player.Message("Owner not found, type /owner in chat and hit the building part with a hammer")


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
                #victimD = DataStore.Get("Players", player.SteamID)
                #player.Message("This BuildingPart belongs to"+victimD['name'])
                player.Message("This BuildingPart belongs to "+victim.Name)



    def On_Command(self, cmd):
        player = cmd.User
        command = cmd.cmd
        args = str.join(' ', cmd.args)

        commands = ('owner', 'ownerme')
        if command in commands:
            if command == 'owner':
                if player.SteamID not in self.buildingOwnerInfo:
                    self.buildingOwnerInfo.append(player.SteamID)
                else:
                    self.buildingOwnerInfo.remove(player.SteamID)