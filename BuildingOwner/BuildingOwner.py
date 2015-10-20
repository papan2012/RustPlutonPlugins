__author__ = 'PanDevas'
__version__ = '1.0'

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

    def On_ServerSaved(self):
        DataStore.Save()

    def On_PluginInit(self):
        Util.Log("Plutin BuildingOwner Initialized!")

    def On_Placement(self, buildingpart):
        player = buildingpart.Builder
        location = buildingpart.BuildingPart.Location
        DataStore.Add("BuildingPartOwner", location, player.SteamID)
        Util.Log("Building Added to datastore "+str(location) +str(player.SteamID))

    def On_BuildingPartDemolished(self, bpde):
        location = bpde.BuildingPart.Location
        DataStore.Remove("BuildingPartOwner", location)

    def On_BuildingPartDestroyed(self, bpde):
        location = bpde.BuildingPart.Location
        DataStore.Remove("BuildingPartOwner", location)