__author__ = 'PanDevas'
__version__ = '0.4'

import clr
clr.AddReferenceByPartialName("Pluton.Core", "Pluton.Rust", "Assembly-CSharp-firstpass", "Assembly-CSharp")

import Pluton.Core
import Pluton.Rust

import sys
path = Util.GetPublicFolder()
sys.path.append(path + "\\Python\\Lib\\")
import time

class OPTribeDoors():

    def On_PluginInit(self):
        self.reportPlayer = Server.FindPlayer("PanDevas")


    def On_DoorUse(self, due):
        doorOwnerID = due.Door.baseEntity.OwnerID
        doorUserID = due.Player.GameID

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

        if not doorUserTribe or not doorOwnerTribe:
            '''
            for shutters that don't have window baars
            '''
            return False

        if doorOwnerTribe['tribe'] == 'Survivors':
            return False
        elif doorUserTribe['tribe'] != doorOwnerTribe['tribe']:
            return False
        else:
            return True