import clr

clr.AddReferenceByPartialName("Pluton")
import Pluton
import sys

class WhosOnline():

    def On_PluginInit(self):
        print "'Whos online' initialised"
        print ""

    def On_Command(self, cmd):
        command = cmd.cmd


        if command == 'who' or command == 'players':
            players = 'Active Players: '
            for i, player in enumerate(Server.ActivePlayers):
                playerData = DataStore.Get('Players', player.SteamID)
                if (i%5) != 0 and (i != len(Server.ActivePlayers)-1):
                    playerName = playerData['name']
                    players += ' '+ playerName+','
                elif i == (len(Server.ActivePlayers)-1):
                    playerName = playerData['name']
                    players += ' '+ playerName
                    Server.Broadcast(playerName)
                    cmd.User.Message(players)
                elif (i%5) == 0:
                    playerName = playerData['name']
                    players += ' '+playerName
                    cmd.User.Message(players)
                    players = ''
            cmd.User.Message(str(len(Server.ActivePlayers))+" online, "+str(len(Server.SleepingPlayers))+" sleepers.")