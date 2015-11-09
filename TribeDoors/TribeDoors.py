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

        if doorOwnerID == doorUserID:
            due.Allow
            due.IgnoreLock = True
        elif self.isPlayerInTribe(doorUserID, doorOwnerID):
            due.IgnoreLock = True
        else:
            due.Deny("You're not the owner of this door, or member of door owner tribe")

    def isPlayerInTribe(self, doorUserID, doorOwnerID):
        doorUserTribe = DataStore.Get("Players", doorUserID)
        doorOwnerTribe = DataStore.Get("Players", doorOwnerID)

        if doorOwnerTribe['tribe'] == 'Survivors':
            return False
        elif doorUserTribe['tribe'] != doorOwnerTribe['tribe']:
            return False
        else:
            return True