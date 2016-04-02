__author__ = 'papan'
__version__ = '0.5'

import clr

clr.AddReferenceByPartialName("Pluton.Core", "Pluton.Rust")
import Pluton.Core
import Pluton.Rust
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
        command = cmd.Cmd
        print cmd.Cmd

        # if command == 'test':
        #     dataInput = DataInput(cmd.User)
        #
        #
        # if command == 'pl':
        #     playerKeys = DataStore.Keys('Players')
        #     Util.Log("tdpl: "+str(playerKeys))
        #     for playerID in playerKeys:
        #         playerData = DataStore.Get('Players', playerID)
        #         Util.Log(playerID+' '+str(playerData['name']))
        #         Util.Log(str(DataStore.Get('Players', playerID)))
        #         player = Server.FindPlayer('76561197996829381')
        #         Util.Log(str(player.Name))
        #
        #
        # if command == 'name':
        #     newName = str.join(' ', cmd.args)
        #     print newName
        #     print cmd.User.basePlayer.displayName
        #     cmd.User.Name = newName
        #
        #
        # if command == 'dpd':
        #     print 'PlayerData: '
        #     playerDataKeys = DataStore.Keys('Players')
        #     print "Found ", DataStore.Count('Players'), ' players in DataStore'
        #     if playerDataKeys:
        #         for key in playerDataKeys:
        #             print key
        #             print DataStore.Get("Players", key)
        #             print ''
        #     else:
        #         print "No player data found"
        #
        # if command == 'clearinvites':
        #     player = str.join(' ', cmd.args)
        #     playerD = Server.FindPlayer(player)
        #     print "clearing invites for player", playerD.Name
        #
        #     playerd = DataStore.Get("Players", playerD.SteamID)
        #     playerd['pendingInvites'] = 'No pending invites'
        #
        if command == 'dtd':
            print 'TribeData'
            tribeDataKeys = DataStore.Keys("Tribes")

            if tribeDataKeys:
                for key in tribeDataKeys:
                    Util.Log('key '+key)
                    tribeData = DataStore.Get("Tribes", key)
                    Util.Log('Founder '+tribeData['creatorID'])
                    list_of_players = []
                    for item in DataStore.Get("Tribes", key)['tribeMembers']:
                        pd = DataStore.Get('Players', item)
                        list_of_players.append(pd['name'])
                    Util.Log("List of players: "+str(list_of_players))
            else:
                print "No tribes found"

        if command == "fixcortez":
            player = Server.FindPlayer("malimedo22")
            playerID = player.SteamID
            playerD = DataStore.Get("Players", playerID)
            playerD['tribe'] = "Survivors"

        # if command == 'removeg':
        #     tribeD = DataStore.Get("Tribes", "Geto")
        #     for memberID in tribeD['tribeMembers']:
        #         member = Server.FindPlayer(memberID)
        #         playerD = DataStore.Get('Players', memberID)
        #         playerD['tribe'] = "Survivors"
        #         DataStore.Remove("Tribes", "Ghetto")
