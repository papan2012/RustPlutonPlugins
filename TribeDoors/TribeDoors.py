__author__ = 'PanDevas'
__version__ = '0.4'

import clr
clr.AddReferenceByPartialName("Pluton", "Assembly-CSharp-firstpass", "Assembly-CSharp")

import Pluton
import sys
path = Util.GetPublicFolder()
sys.path.append(path + "\\Python\\Lib\\")
import time

class TribeDoors():

    def On_PluginInit(self):
        self.reportPlayer = Server.FindPlayer("PanDevas")


    def On_DoorUse(self, due):
        doorLocation = due.Door.Location
        doorOwnerID = DataStore.Get("BuildingPartOwner", doorLocation)
        doorUserID = due.Player.SteamID
        if not doorOwnerID:
            due.Allow
            # Some structures didn't end up in database
            # either from me not using On_ServerSaved method from the beggining, and forgetint to save the datastore before server restart
            # or becaouse of that DataStore vector3 conversion that missed something.
            # this code should verify the problem
            Util.Log("DoorOwner not found "+ str(doorLocation) + due.Player.Name + "opening")
            v3 = doorLocation
            v3String = str.format("Vector3,{0},{1},{2}",v3.x.ToString("G9"), v3.y.ToString("G9"), v3.z.ToString("G9"))
            Util.Log("doorLoc in datastore (old) "+ str(v3String in DataStore.Keys("BuildingPartOwner")))
            Util.Log("doorLoc in datastore (new) "+ str(doorLocation in DataStore.Keys("BuildingPartOwner")))
            doorOwnerID = doorUserID
            DataStore.Add("BuildingPartOwner", doorLocation, doorOwnerID)
        elif doorOwnerID == doorUserID:
            due.Allow
            due.IgnoreLock = True
        elif self.isPlayerInTribe(doorUserID, doorOwnerID):
            due.IgnoreLock = True
        else:
            due.Deny("You're not the owner of this door, or member of door owner tribe")

    def isPlayerInTribe(self, doorUserID, doorOwnerID):
        doorUserTribe = DataStore.Get("Players", doorUserID)
        doorOwnerTribe = DataStore.Get("Players", doorOwnerID)
        if not doorOwnerTribe:
            Util.Log("DoorOwnerTribe not found" + str(doorOwnerID))
            doorOwnerTribe = doorUserTribe

        if doorOwnerTribe['tribe'] == 'Survivors':
            return False
        elif doorUserTribe['tribe'] != doorOwnerTribe['tribe']:
            return False
        else:
            return True