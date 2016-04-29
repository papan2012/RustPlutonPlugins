__author__ = 'PanDevas'
__version__ = '0.7'

import clr

clr.AddReferenceByPartialName("Pluton.Core", "Pluton.Rust")

import Pluton.Core
import Pluton.Rust

import sys
import time


class OPMetabolism():

    def On_PluginInit(self):

        # METABOLISM VARIABLES
        if DataStore.GetTable('PlayerMetabolism'):
            DataStore.Flush('PlayerMetabolism')
        DataStore.Add('PlayerMetabolism', 'system', time.time())

        self.metabolismRate = 45
        self.playerTimers = {}

        for player in Server.ActivePlayers:
            self.startMetabolismTimer(player)

    def On_PlayerWakeUp(self, player):
        if player.GameID not in DataStore.Keys('PlayerMetabolism'):
            Util.Log("Not in Datastore")
            self.startMetabolismTimer(player)
        else:
            self.playerTimers[player.GameID].Start()

    def startMetabolismTimer(self, player):
        metabolismData = Plugin.CreateDict()
        metabolismData['playerID'] = player.GameID
        Util.Log('Starting metabolism timer for '+player.Name)
        DataStore.Add('PlayerMetabolism', player.GameID, time.time())
        timer = Plugin.CreateParallelTimer("metabolism", self.metabolismRate*1000, metabolismData)
        self.playerTimers[player.GameID] = timer
        timer.Start()

    def metabolismCallback(self, timer):
        playerID = timer.Args['playerID']
        player = Server.FindPlayer(playerID)
        if player and player.GameID not in DataStore.Keys('SleepingPlayers') and player.GameID in DataStore.Keys('PlayerMetabolism'):
            if player.basePlayer.metabolism.calories.value > 500:
                player.basePlayer.metabolism.calories.value -= 5
            elif player.basePlayer.metabolism.calories.value > 150:
                player.basePlayer.metabolism.calories.value -= 3
            elif player.basePlayer.metabolism.calories.value > 100:
                player.basePlayer.metabolism.calories.value -= 2
            elif player.basePlayer.metabolism.calories.value > 15:
                player.basePlayer.metabolism.calories.value -= 1
            else:
                player.basePlayer.metabolism.calories.value -= 0

            if player.basePlayer.metabolism.hydration.value > 500:
                player.basePlayer.metabolism.hydration.value -= 5
            elif player.basePlayer.metabolism.hydration.value > 150:
                player.basePlayer.metabolism.hydration.value -= 3
            elif player.basePlayer.metabolism.hydration.value > 100:
                player.basePlayer.metabolism.hydration.value -= 2
            else:
                player.basePlayer.metabolism.hydration.value -= 1
        else:
            timer.Stop()
            DataStore.Remove('PlayerMetabolism', playerID)
            Util.Log("Destroying metabolism timer for player "+ playerID)