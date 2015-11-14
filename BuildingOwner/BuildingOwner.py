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
        self.skipRemoveForTypes = ['pillar']
        self.buildingOwnerInfo = []

    def On_ServerSaved(self):
        DataStore.Save()
        Server.Broadcast("Server saved.")

    def On_Placement(self, buildingpart):
        player = buildingpart.Builder
        location = buildingpart.BuildingPart.Location
        locationCheck = DataStore.Get("BuildingPartOwner", location)
        if locationCheck and player.Name == self.admin:
            player.Message("BuildingPart already in datastore")
        DataStore.Add("BuildingPartOwner", location, player.SteamID)
        if not DataStore.Get("BuildingPartOwner", location):
            Util.Log("BuildingPart was not found in Datastore after placement")
            player.Message("BuildingPart not in Datastore, hit it with a Hammer to add it!")


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
        this is a dirty workaround when the doors are not placed in exact location with the frame
        and a helper function for determining ownership of building parts
        '''

        getOwnerObjects = ["BuildingBlock", "Door"]

        if he.Victim.baseEntity.GetType().ToString() in getOwnerObjects:

            player = he.Player
            location = he.Victim.Location
            victimID = DataStore.Get("BuildingPartOwner", location)

            if not victimID:
                DataStore.Add("BuildingPartOwner", location, player.SteamID)
                player.Message("BuildingPart added to Datastore")
                victimID = player.SteamID

            if player.SteamID in self.buildingOwnerInfo:
                victim = Server.FindPlayer(victimID)
                if not victim:
                    for pl in Server.OfflinePlayers.Values:
                        if pl.SteamID == victimID:
                            victim = pl
                player.Message("This BuildingPart belongs to "+str(victim.Name))



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
