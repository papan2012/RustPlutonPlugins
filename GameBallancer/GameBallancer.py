__author__ = 'PanDevas'
__version__ = '0.1'

import clr

clr.AddReferenceByPartialName("Pluton")
import Pluton
import sys


class GameBallancer():

    def On_PlayerStartCrafting(self, ce):
        fix_items = {
            'wall.external.high.stone': 240,
            'wall.external.high': 120,
            'gates.external.high': 180
        }

        # Util.Log(str(ce.Target))
        # Util.Log(str(ce.CraftTime))
        if ce.Target.shortname in fix_items.keys():
            ce.CraftTime = fix_items[ce.Target.shortname]



