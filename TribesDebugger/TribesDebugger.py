__author__ = 'papan'

import clr

clr.AddReferenceByPartialName("Pluton")
import Pluton
import sys

class DataInput():
    def __init__(self, player):
        print player.SteamID, type(player.GameID)
        DataStore.Add('DataInput', player.GameID, player.Name)
        dc = DataCreate()
        dc.addData(player.GameID)

class DataCreate():
    def __init__(self):
        self.data = { 'datalist': []}
        DataStore.Add("DataCreate", 'datacreate', self.data )

    def addData(self, playerID):
        print 'addData'
        print playerID, type(playerID)
        self.data['datalist'].append(playerID)
        print DataStore.Get("DataCreate", 'datacreate')
        print ''
#        DataStore.Flush("DataCreate")



class TribesDebugger():

    def On_PluginInit(self):
        print "Plugin TribeDebugger initialised"
        print ""

    def On_Command(self, cmd):
        command = cmd.cmd
        print cmd.cmd

        if command == 'test':
            dataInput = DataInput(cmd.User)


        if command == 'playerlist':
            playerKeys = DataStore.Keys('Players')
            Util.Log(str(playerKeys))
            for playerID in playerKeys:
                playerData = DataStore.Get('Players', playerID)
                Util.Log(str(playerData['lastonline']))






        if command == 'name':
            newName = str.join(' ', cmd.args)
            print newName
            print cmd.User.basePlayer.displayName
            cmd.User.Name = newName

        if command == 'dsadd':
            addint = str.join(' ', cmd.args)
            number = 1
            numberData = []
            DataStore.Add("Test", number, numberData)
            print DataStore.Keys("Test")
            print DataStore.Get("Test", number)
            s = DataStore.Get("Test", number)
            print s
            print ''

        if command == 'dpd':
            print 'PlayerData: '
            playerDataKeys = DataStore.Keys('Players')
            print "Found ", DataStore.Count('Players'), ' players in DataStore'
            if playerDataKeys:
                for key in playerDataKeys:
                    print key
                    print DataStore.Get("Players", key)
                    print ''
            else:
                print "No player data found"

        if command == 'clearinvites':
            player = str.join(' ', cmd.args)
            playerD = Server.FindPlayer(player)
            print "clearing invites for player", playerD.Name

            playerd = DataStore.Get("Players", playerD.SteamID)
            playerd['pendingInvites'] = 'No pending invites'

        if command == 'dtd':
            print 'TribeData'
            tribeDataKeys = DataStore.Keys("Tribes")

            if tribeDataKeys:
                for key in tribeDataKeys:
                    print key
                    print DataStore.Get("Tribes", key)
                    print ''
            else:
                print "No tribes found"

        if command == 'pdflush':
            print "flushing player data"
            DataStore.Flush('Players')

        if command == 'tdflush':
            print "flushin tribe data"
            DataStore.Flush('Tribes')
            DataStore.Save()

        if command == 'flush':
            DataStore.Flush("Tribes")
            DataStore.Flush("Players")
            DataStore.Save()
            print "flushing all"
