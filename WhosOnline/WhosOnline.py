__author__ = 'PanDevas'
__version__ = '1.2'

import clr

clr.AddReferenceByPartialName("Pluton.Core", "Pluton.Rust")
import Pluton.Core
import Pluton.Rust
import sys

class WhosOnline():

    def On_PluginInit(self):
        Commands.Register("who").setCallback("who")

    def who(self, Args, Player):
        players = 'Active Players: '
        for i, player in enumerate(Server.ActivePlayers):
            playerData = DataStore.Get('Players', player.GameID)
            if (i%7) != 0 and (i != len(Server.ActivePlayers)-1):
                playerName = playerData['name']
                players += ' '+ playerName+','
            elif i == (len(Server.ActivePlayers)-1):
                playerName = playerData['name']
                players += ' '+ playerName
                Player.MessageFrom('', players)
            elif (i%7) == 0:
                playerName = playerData['name']
                players += ' '+playerName
                Player.Message(players)
                players = ''
        Player.Message(str(len(Server.ActivePlayers))+" online, "+str(len(Server.SleepingPlayers))+" sleepers.")
