__author__ = 'PanDevas'
__version__ = '0.3'

import clr
clr.AddReferenceByPartialName("Pluton", "Assembly-CSharp-firstpass", "Assembly-CSharp")

import Pluton
import sys
path = Util.GetPublicFolder()
sys.path.append(path + "\\Python\\Lib\\")
import time

class TribeDoors():

    def On_PluginInit(self):
        pass


    def On_DoorUse(self, due):
        #Util.Log("door: "+str(dir(due.Door)))
        doorLocation = due.Door.Location
        doorOwnerID = DataStore.Get("BuildingPartOwner", doorLocation)
        doorUserID = due.Player.SteamID

        if doorOwnerID == doorUserID:
            due.Allow
        elif self.isPlayerInTribe(doorUserID, doorOwnerID):
            due.Allow
            due.IgnoreLock = True
        else:
            due.Deny("You're not the owner of this door, or member of door owner tribe")

    def isPlayerInTribe(self, doorUserID, doorOwnerID):
        doorUserTribe = DataStore.Get("Players", doorUserID)
        doorOwnerTribe = DataStore.Get("Players", doorOwnerID)
        Util.Log(str(doorOwnerTribe))
        if doorOwnerTribe['tribe'] == 'Ronins':
            return False
        elif doorUserTribe['tribe'] != doorOwnerTribe['tribe']:
            return False
        else:
            return True