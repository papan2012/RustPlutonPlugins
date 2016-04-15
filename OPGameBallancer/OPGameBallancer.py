__author__ = 'PanDevas'
__version__ = '0.5'

import clr

clr.AddReferenceByPartialName("Pluton.Core", "Pluton.Rust", "Assembly-CSharp")

import Pluton.Core
import Pluton.Rust

import sys
#import MetabolismAttribute


class OPGameBallancer():

    def On_PluginInit(self):
        DataStore.Flush("DestroyedBuildings")
        self.buildingTimerLenght = 120

    # HOOKS
    def On_PlayerStartCrafting(self, ce):
        player = ce.Crafter

        if not DataStore.GetTable("CraftingTimes"):
            DataStore.Add("CraftingTimes", ce.Target.shortname, ce.CraftTime)
        elif ce.Target.shortname not in DataStore.Keys("CraftingTimes"):
            DataStore.Add("CraftingTimes", ce.Target.shortname, ce.CraftTime)

        if player.basePlayer.HasPlayerFlag(player.basePlayer.PlayerFlags.HasBuildingPrivilege):
            ce.CraftTime =  DataStore.Get("CraftingTimes", ce.Target.shortname) / 2
        else:
            ce.CraftTime = DataStore.Get("CraftingTimes", ce.Target.shortname)

    # PREVENTOR FOR BUILDING PLACEMENT WHEN DESTROYED FOR 2 MINUTES
    def On_BuildingPartDestroyed(self, bpde):
        location=str(bpde.BuildingPart.Location)

        fpData = Plugin.CreateDict()
        fpData['location'] = location
        timer = Plugin.CreateParallelTimer("DestroyedBuildings", self.buildingTimerLenght*1000, fpData).Start()
        DataStore.Add("DestroyedBuildings", location, timer)

    def On_Placement(self, be):
        player = be.Builder
        location = be.BuildingPart.Location
        buildingTable = DataStore.GetTable("DestroyedBuildings")
        if buildingTable:
            if str(location) in buildingTable.Keys:
                be.DestroyReason = "You can't place a building in place of recently destroyed building part."
                be.DoDestroy = 1

    def DestroyedBuildingsCallback(self, timer):
        data = timer.Args
        location = data['location']
        DataStore.Remove("DestroyedBuildings", location)


    # END PREVENTOR FOR BUILDING PLACEMENT

    # # TEST METHODS
    # def On_Command(self, cmd):
    #     player = cmd.User
    #     command = cmd.Cmd
    #
    #     if command == 'ping':
    #         player.Message('Your ping is '+str(player.Ping))