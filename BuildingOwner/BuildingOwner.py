__author__ = 'PanDevas'
__version__ = '0.1'

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

    def On_PluginInit(self):
        Util.Log("Plutin BuildingOwner Initialized!")

    def On_Placement(self, buildingpart):
        player = buildingpart.Builder
        location = buildingpart.BuildingPart.Location

        DataStore.Add("BuildingPartOwner", location, player.SteamID)
        Util.Log("Added building to datastore")

    def On_BuildingPartDemolished(self, bpde):
        location = bpde.BuildingPart.Location
        DataStore.Remove("BuildingPartOwner", location)
        Util.Log("Building part is in DataStore, removing")

    def On_BuildingPartDestroyed(self, bpde):
        location = bpde.BuildingPart.Location
        Util.Log("Building part is in DataStore, removing")
        DataStore.Remove("BuildingPartOwner", location)