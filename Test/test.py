__author__ = 'PanDevas'
__version__ = '1.0'

import clr
clr.AddReferenceByPartialName("Pluton")

import Pluton
import sys
path = Util.GetPublicFolder()
import datetime

class test():
    '''
    '''

    def On_PluginInit(self):
        Util.Log("Plutin BuildingOwner Initialized!")

    def On_Placement(self, buildingpart):
        player = buildingpart.Builder
        location = buildingpart.BuildingPart.Location
        DataStore.Add("BuildingPartOwner", location, player.SteamID)
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
        if attacker and attacker.IsPlayer() and str(HurtEvent.DamageType) not in ignoredDamagesList:
            attackerID = attacker.SteamID
            victimLocation = HurtEvent.Victim.Location
            victimID = DataStore.Get("DST: BuildingPartOwner", victimLocation)
            Util.Log("DST: "+str(victimLocation))
            Util.Log("DST: "+str(victimID))
            Util.Log("DST: "+str(victimLocation in DataStore.Keys("BuildingPartOwner")))
            Util.Log("DST: "+DataStore.Get("BuildingPartOwner", victimLocation))
            Util.Log("DST: "+ str(DataStore.Values("BuildingPartOwner")))
            # victimID check if datastore entry not found