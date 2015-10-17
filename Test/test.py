__author__ = 'PanDevas'
__version__ = '1.0'

import clr
clr.AddReferenceByPartialName("Pluton")

import Pluton
import sys
path = Util.GetPublicFolder()
sys.path.append(path + "\\Python\\Lib\\")
import datetime

class test():
    '''
    '''

    def On_PluginInit(self):
        Util.Log("Plutin BuildingOwner Initialized!")

    def On_Placement(self, buildingpart):
        player = buildingpart.Builder
        location = buildingpart.BuildingPart.Location
        DataStore.Add("Test", location, player.SteamID)
        Util.Log("Building Added to datastore "+str(location) +str(player.SteamID))
        DataStore.Save()

    def On_CombatEntityHurt(self, HurtEvent):
        '''
        :param CombatEntityHurtEvent:
        :return:
        Detects if building part was damaged and get its location and owner
        '''

        attacker = HurtEvent.Attacker

        ignoredDamagesList = ['ElectricShock', 'Heat', 'Cold']
        # if attacker and attacker.IsPlayer() and str(HurtEvent.DamageType) not in ignoredDamagesList:
        #     attackerID = attacker.SteamID
        #     victimLocation = HurtEvent.Victim.Location
        #     victimID = DataStore.Get("Test", victimLocation)
        #     Server.Broadcast(str(victimLocation))
        #     Server.Broadcast("datatype of type(DataStore.Get('test', victimLocation)): " +str(type(DataStore.Get("Test", victimLocation))))
        #     Server.Broadcast("location in keys: "+str(victimLocation in DataStore.Keys("Test")))
        #
        #     Util.Log("victimLocation: "+str(victimLocation))
        #     Util.Log("victimID: "+str(victimID))
        #     Util.Log(str(type(DataStore.Get("Test", victimLocation))))
        #     Util.Log("location in keys: "+str(victimLocation in DataStore.Keys("Test")))
        #     Util.Log("Keys: "+ str(DataStore.Keys("Test")))
        #     Util.Log("Values: "+ str(DataStore.Values("Test")))
        #     Util.Log("location: "+DataStore.Get("Test", victimLocation))

            # victimID check if datastore entry not found