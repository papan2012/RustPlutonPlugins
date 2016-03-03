__author__ = 'PanDevas'
__version__ = '0.5'

import clr

clr.AddReferenceByPartialName("Pluton", "Assembly-CSharp")

import Pluton
import sys
#import MetabolismAttribute


class OPGameBallancer():

    def On_PluginInit(self):
        self.buildingTimerLenght = 120

        # METABOLISM VARIABLES

        self.metabolismRate = 30
        for player in Server.ActivePlayers:
            self.startMetabolismTimer(player)

    def On_PlayerConnected(self, player):
        self.startMetabolismTimer(player)

    def startMetabolismTimer(self, player):
        metabolismData = Plugin.CreateDict()
        metabolismData['player'] = player
        #Util.Log('Starting metabolism timer for '+player.Name)
        Plugin.CreateParallelTimer("metabolism", self.metabolismRate*1000, metabolismData).Start()

    def metabolismCallback(self, timer):
        player = timer.Args['player']
        if player in Server.ActivePlayers:
            timer.Kill()
            #Util.Log('lowering fodd/watter values for ' + player.Name)
            if player.basePlayer.metabolism.calories.value > 750:
                player.basePlayer.metabolism.calories.value -= 4
                player.basePlayer.metabolism.hydration.value -= 4
            elif player.basePlayer.metabolism.calories.value > 500:
                player.basePlayer.metabolism.calories.value -= 3
                player.basePlayer.metabolism.hydration.value -= 3
            elif player.basePlayer.metabolism.calories.value > 100:
                player.basePlayer.metabolism.calories.value -= 2
                player.basePlayer.metabolism.hydration.value -= 2
            elif player.basePlayer.metabolism.calories.value >= 1:
                player.basePlayer.metabolism.calories.value -= 1
                player.basePlayer.metabolism.hydration.value -= 1
            Plugin.CreateParallelTimer("metabolism", self.metabolismRate*1000, metabolismData).Start()
        else:
            timer.Kill()
            #Util.Log("destroying timer for player "+ player.Name)