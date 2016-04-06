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
        self.values = {750: (4,3), 500: (3,2), 100: (1.5,1), 1: (1,1)}

        self.playerTimers = {}

        for player in Server.ActivePlayers:
            self.startMetabolismTimer(player)

    def On_PlayerWakeUp(self, player):
        self.startMetabolismTimer(player)

    def startMetabolismTimer(self, player):
        if player.GameID not in DataStore.Keys('PlayerMetabolism'):
            metabolismData = Plugin.CreateDict()
            metabolismData['playerID'] = player.GameID
            Util.Log('Starting metabolism timer for '+player.Name)
            DataStore.Add('PlayerMetabolism', player.GameID, time.time())
            if player.GameID not in self.playerTimers.keys():
                Util.Log("no in dict")
                timer = Plugin.CreateParallelTimer("metabolism", self.metabolismRate, metabolismData)
                self.playerTimers[player.GameID] = timer
            else:
                Util.Log("in dict")
                timer = self.playerTimers[player.GameID]
            timer.Start()

    def metabolismCallback(self, timer):
        playerID = timer.Args['playerID']
        player = Server.FindPlayer(playerID)
        if player and player.GameID not in DataStore.Keys('SleepingPlayers') and player.GameID in DataStore.Keys('PlayerMetabolism'):
            timer.Stop()
            if player.basePlayer.metabolism.calories.value > 750:
                player.basePlayer.metabolism.calories.value -= 8
            elif player.basePlayer.metabolism.calories.value > 500:
                player.basePlayer.metabolism.calories.value -= 5
            elif player.basePlayer.metabolism.calories.value > 150:
                player.basePlayer.metabolism.calories.value -= 3
            else:
                player.basePlayer.metabolism.calories.value -= 1

            if player.basePlayer.metabolism.hydration.value > 750:
                player.basePlayer.metabolism.hydration.value -= 5
            elif player.basePlayer.metabolism.hydration.value > 500:
                player.basePlayer.metabolism.hydration.value -= 3
            elif player.basePlayer.metabolism.hydration.value > 150:
                player.basePlayer.metabolism.hydration.value -= 2
            else:
                player.basePlayer.metabolism.hydration.value -= 1
            Util.Log("timer callback")
            # metabolismData = Plugin.CreateDict()
            # metabolismData['playerID'] = player.GameID
            # Plugin.CreateParallelTimer("metabolism", self.metabolismRate*1000, metabolismData).Start()
        else:
            timer.Stop()
            DataStore.Remove('PlayerMetabolism', playerID)
            Util.Log("Destroying metabolism timer for player "+ playerID)