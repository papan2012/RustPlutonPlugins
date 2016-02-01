__author__ = 'PanDevas'
__version__ = '0.1'

import clr

clr.AddReferenceByPartialName("Pluton")
import Pluton
import sys


class OPGameBallancer():

    def On_PluginInit(self):
        self.buildingTimerLenght = 120


    def On_PlayerStartCrafting(self, ce):
        #Util.Log(str(dir(DataStore)))
        player = ce.Crafter
        fix_items = {
            'wall.external.high.stone': 240,
            'wall.external.high': 120,
            'gates.external.high': 180
        }

        if ce.Target.shortname in fix_items.keys():
            ce.CraftTime = fix_items[ce.Target.shortname]
        else:
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

    # TEST METHODS
    def On_Command(self, cmd):
        player = cmd.User
        command = cmd.cmd

        if command == 'ping':
            player.Message('Your ping is '+str(player.Ping))