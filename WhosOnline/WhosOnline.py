__author__ = 'PanDevas'
__version__ = '1.0'

import clr

clr.AddReferenceByPartialName("Pluton.Core", "Pluton.Rust")
import Pluton.Core
import Pluton.Rust
import sys

class WhosOnline():

    def On_PluginInit(self):
        print "'Whos online' initialised"
        print ""

    def On_Command(self, cmd):
        command = cmd.Cmd


        if command == 'who' or command == 'players':
            players = 'Active Players: '
            for i, player in enumerate(Server.ActivePlayers):
                playerData = DataStore.Get('Players', player.SteamID)
                if (i%7) != 0 and (i != len(Server.ActivePlayers)-1):
                    playerName = playerData['name']
                    players += ' '+ playerName+','
                elif i == (len(Server.ActivePlayers)-1):
                    playerName = playerData['name']
                    players += ' '+ playerName
                    cmd.User.MessageFrom('', players)
                elif (i%7) == 0:
                    playerName = playerData['name']
                    players += ' '+playerName
                    cmd.User.Message(players)
                    players = ''
            cmd.User.Message(str(len(Server.ActivePlayers))+" online, "+str(len(Server.SleepingPlayers))+" sleepers.")