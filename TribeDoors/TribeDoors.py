__author__ = 'PanDevas'
__version__ = '0.2'

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
        doorOwner = DataStore.Get("BuildingPartOwner", doorLocation)

        Util.Log(str(dir(due.Deny)))
        Util.Log(str(help(due.Deny.Equals)))
        Util.Log("equals method: "+str(due.Deny.Equals(True)))
        due.Deny("deny not working")
        #due.Open  # state of doors open/closed

        # ignore lock if condition fulfiller
        #due.IgnoreLock = True

    def isPlayerInTribe(self, playerID):
        pass