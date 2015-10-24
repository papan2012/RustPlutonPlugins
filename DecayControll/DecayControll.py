__author__ = 'PanDevas'
__version__ = '0.3'

import clr
clr.AddReferenceByPartialName("Pluton")

import Pluton
import sys
path = Util.GetPublicFolder()
sys.path.append(path + "\\Python\\Lib\\")
import time


class DecayControll():

    def On_PluginInit(self):
        self.scale = 0.2

    def On_CombatEntityHurt(self, HurtEvent):
        if str(HurtEvent.DamageType) == 'Decay':
            damageAmounts = HurtEvent.DamageAmounts
            for i, d in enumerate(damageAmounts):
                if damageAmounts[i] != 0.0:
                    damageAmounts[i] *= self.scale
                HurtEvent.DamageAmounts = damageAmounts