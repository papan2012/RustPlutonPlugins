__author__ = 'PanDevas'
__version__ = '1.1'

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
        self.skipRemoveForTypes = ["door", 'pillar']
        self.buildingOwnerInfo = []

    def On_ServerSaved(self):
        DataStore.Save()
        Server.Broadcast("Server saved.")

    def On_Placement(self, buildingpart):
        player = buildingpart.Builder
        location = buildingpart.BuildingPart.Location
        locationCheck = DataStore.Get("BuildingPartOwner", location)
        if locationCheck:
            player.Message("Building already in datastore")

        DataStore.Add("BuildingPartOwner", location, player.SteamID)


    def On_BuildingPartDemolished(self, bpde):
        self.removeFromDatastore(bpde)

    def On_BuildingPartDestroyed(self, bpde):
        self.removeFromDatastore(bpde)


    def removeFromDatastore(self, bpde):
        bpdeEntitiName = bpde.BuildingPart.baseEntity.LookupShortPrefabName().split('.')[0]
        location = bpde.BuildingPart.Location

        if bpdeEntitiName not in self.skipRemoveForTypes:
            DataStore.Remove("BuildingPartOwner", location)


    def On_BeingHammered(self, he):
        '''
        this is a dirty workaround and a helper function
        '''
        getOwnerObjects = ["BuildingBlock", "Door"]

        if he.Victim.baseEntity.GetType().ToString() in getOwnerObjects:
            player = he.Player
            location = he.Victim.Location
            victimID = DataStore.Get("BuildingPartOwner", location)
            if not victimID:
                if player.Name == self.admin:
                    player.Message("building was not found")
                else:
                    DataStore.Add("BuildingPartOwner", location, player.SteamID)
            if victimID and player.SteamID in self.buildingOwnerInfo:
                victimID = DataStore.Get("BuildingPartOwner", location)
                victim = Server.FindPlayer(victimID)
                if not victim:
                    for pl in Server.SleepingPlayers:
                        if pl.SteamID == victimID:
                            victim = pl
                player.Message("This building belongs to "+str(victim.Name))

    def On_Command(self, cmd):
        player = cmd.User
        command = cmd.cmd
        args = str.join(' ', cmd.args)
        if command == 'owner':
            if player.SteamID not in self.buildingOwnerInfo:
                self.buildingOwnerInfo.append(player.SteamID)
            else:
                self.buildingOwnerInfo.remove(player.SteamID)