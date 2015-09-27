__author__ = 'PanDevas'
__version__ = '0.1'

import clr

clr.AddReferenceByPartialName("Pluton")
import Pluton
import sys

path = Util.GetPublicFolder()
lib = True
try:
    sys.path.append(path + "\\Python\\Lib\\")
    import hashlib
except ImportError:
    Lib = False
import datetime


import PlayerData


###
#  CLASS FOR MANAGING TRIBES DATASTORE DATA
###
class TribeData():
    '''
       (table_name: tribe_name: {members}
       Tribes:

    '''
    def __init__(self, tribeName):
        self.tribe = DataStore.Get("Tribes", tribeName)
        if self.tribe:
            self.tribe = DataStore.Get("Tribes", tribeName)
        else:
            self.tribeName = tribeName
            self.tribeDetails = {'creatorID': '',
                                'tribeMembers': [],
                                'tribeFriends': [],
                                'tribeEnemies' : [],
                                'tribeRaidable': False
                            }
            DataStore.Add("Tribes", self.tribeName, self.tribeDetails)
            self.tribe = DataStore.Get("Tribes", self.tribeName)


    def addTribeToDatastore(self, tribeName, creatorID):
        self.tribeDetails['tribeName'] = tribeName
        self.tribeDetails['creatorID'] = [creatorID]
        self.tribeDetails['tribeMembers']= [creatorID]
        self.tribeDetails['tribeRaidable'] = True
        DataStore.Add("Tribes", tribeName, self.tribeDetails)
        DataStore.Save()
        self.tribe = DataStore.Get("Tribes", tribeName)

    def addMember(self, recruit):
        '''
        receives objects for both players
        '''
        pass
#        tribe = DataStore.Get("Tribes", tribeName)
#        tribe['tribeMembers'].append(memberID)
#        DataStore.Save()


    def removeMember(self, tribeName, memberID):
        pass

    def promoteMember(self, tribeName, memberID, rank):
        pass

    def addFriends(self, tribeName, friendID):
        pass

    def RemoveFriend(self, tribeName, friendID):
        pass

    def getDetails(self):
        '''
            returns Tribe details dictionary
        '''
        return self.tribe




######
###    MAIN CLASS
######
class Tribes:
    '''
        Manager Class
        Handles User Input and updates PlayerData and TribeData DataStores
    '''

    def On_PluginInit(self):
        print "Plugin init"
        self.tribes = self._update_tribe_list()

    '''
        TRIBE HELPER METHODS
    '''
    def _update_tribe_list(self):
        print "_update_tribe_list executed"
        if DataStore.Keys('Tribes'):
            return DataStore.Keys('Tribes')
        else:
            self.tribes = []

    '''
         END OF TRIBE HELPER METHODS
    '''

    '''
        TRIBE CLASS METHODS
    '''
    def createTribe(self, cmd):
        '''
            Creates a tribe by adding it to Datastore
            TODO:
            Make player creating a tribe a Chief
        '''

        player = cmd.User
        args = str.join(' ', cmd.args)
        print "Creating Tribe", args

        tribeName = args.split(' ')[0].strip()

        playerData = PlayerData(player)
        pd = playerData.getPlayerData(player.GameID)

        # check if Tribe exists and if player is a member of a existing tribe
        self._update_tribe_list()

        if pd['tribe'] not in self.tribes:
            pd['tribe'] = 'Ronin'

        if tribeName in self.tribes:
            player.MessageFrom("Tribes", "Tribe \""+tribeName+"\"already exists!")
        elif len(tribeName) == 0:
            player.MessageFrom("Tribes", "You didn't provide tribe name")
        elif (tribeName in self.tribes) or (pd['tribe'] != 'Ronin'):
            player.MessageFrom("Tribes", "You are alread in tribe \""+str(pd['tribe']+"\""))
        elif (tribeName not in self.tribes) and (pd['tribe'] == 'Ronin' and pd['tribe'] != 'args'):
            #DataStore.Add("Tribes", args, args)
            tribe = TribeData(tribeName)
            tribe.addTribeToDatastore(tribeName, player.SteamID)
            player.MessageFrom("Tribes", "Tribe created: "+tribeName)
            player.MessageFrom("Tribes", "Congratulations, you are now Chief of tribe \""+tribeName+"\"!")
            playerData.changePlayerData(cmd.User.GameID, {'tribe': tribeName, 'tribeRank': 0})
            self.tribes = self._update_tribe_list()


    def deleteTribe(self, cmd):
        '''
            Removes a tribe from Datastore

            TODO: update all current tribe members to Ronin tribe
        '''

        player = cmd.User
        args = str.join(' ', cmd.args).split(' ')[0]
        print "Deleting Tribe", args

        playerData = PlayerData(player)
        pd = playerData.getPlayerData(player.GameID)

        tribe = TribeData(pd['tribe'])


        if (pd['tribe'] == args) and (pd['tribeRank'] == 0):
            for playerID in tribe['tribeMembers']:
                memberdata = DataStore.Get('Players', playerID)
                memberdata[tribe] = 'Ronin'

            player.MessageFrom("Tribe", "Tribe \""+str(args)+"\" removed! You are now Ronin!")
            DataStore.Remove("Tribes", args)
            self._update_tribe_list()
        elif args not in self.tribes:
            player.MessageFrom("Tribe", "Tribe \""+str(args)+"\" doesn't exist!")
        else:
            player.MessageFrom("Tribe", "You're not that tribe Cheef, you can't delete that tribe!")


    def listTribes(self, cmd):
        player = cmd.User

        if self.tribes:
            for i, tribe in enumerate(self.tribes):
                player.MessageFrom("Tribes", str(tribe))
        else:
           player.MessageFrom("Tribes", "No tribes ware found")


    def tribeListMembers(self, cmd):
        player = cmd.User

        player.MessageFrom("Tribe", "Listing members not working yet, it's WIP")


    def tribeInvite(self, cmd):
        tribeMember = cmd.User
        recruit = cmd.args[0]

        # this searches for Player recruit
        recruitPlayerObject = Server.FindPlayer(cmd.args[0])



        if recruitPlayerObject:
            print "Player ", tribeMember.Name, "invited ", recruitPlayerObject.Name, " to his tribe"
            memberData = PlayerData(tribeMember)
            recruitPlayerData = PlayerData(recruitPlayerObject)
            if memberData.playerData['tribe'] == 'Ronin':
                tribeMember.MessageFrom("Tribes", "You are not in a tribe. Create a tribe so you can invite people to that tribe!")
        #    elif recruitPlayerData.playerData['tribe'] != 'Ronin':
        #        tribeMember.MessageFrom("Tribes", "Player is already in a tribe "+recruitPlayerData.playerData['tribe'])
            else:
                tribeData = TribeData(memberData.playerData['tribe'])
                tribeName = DataStore.Get('Players', str(tribeMember.SteamID))['tribe']
                recruitPlayerData.playerData['pendingInvites'] = [tribeName, memberData, recruitPlayerData]
                recruitPlayerObject.MessageFrom("Tribes", tribeMember.Name+" invited you to his tribe " + tribeName)
                recruitPlayerObject.MessageFrom("Tribes", "Type /tia to accept the invite")
        else:
            print "Player \""+recruit+"\" not found!"
            tribeMember.MessageFrom("Tribes", "Player \""+recruit+"\" not found!")

    def acceptTribeInvite(self, cmd):
        player = cmd.User.SteamID
        args = str.join(' ', cmd.args).split(' ')[0]

        print player
        print args


    def tribeRemovePlayer(self, cmd):
        '''
        FIX THIS, TODO
        '''
        removingPlayer = cmd.User.SteamID
        playerToRemove = Server.FindPlayer(str.join(' ', cmd.args).split(' ')[0])


    def getTribeDetails(self, cmd):
        '''
        '''
        player = cmd.User
        tribeMember = DataStore.Get("Players", cmd.User.SteamID)
        tribe = TribeData(tribeMember['tribe'])
        tribeDetails = tribe.getDetails()
        if tribeDetails:
            for key in tribeDetails.keys():
                player.MessageFrom("Tribes", str(key)+', '+str(tribeDetails[key]))
        else:
            player.MessageFrom("Tribes", "You're not member of any tribe")




    '''
        END OF TRIBE CLASS METHODS
    '''


    def On_Command(self, cmd):
        '''
            All function calls here need to accept cmd Instance
        '''
        commands ={'tcreate': (self.createTribe, " - create a tribe"),
                   'tdel': (self.deleteTribe, " - delete a tribe"),
                   'tlist': (self.listTribes, " - list tribes"),
                   'tlm': (self.tribeListMembers, "- list tribe members"),
                   'ti': (self.tribeInvite, " /ti PlayerName - invite player to your tribe"),
                   'trp': (self.tribeRemovePlayer, " /trp PlayerName - remove player from Tribe"),
                   'td': (self.getTribeDetails, " - get tribe details"),
                   'tia': (self.acceptTribeInvite, " /tia TribeName  - accept tribe invite")
                   }

        command = cmd.cmd

        if command in commands.keys():
            commands[command][0](cmd)
        elif command == 'thelp':
            for key in commands.keys():
                cmd.User.MessageFrom("Tribes", '/'+key +' '+ commands[key][1])
        else:
            ##
            ## this needs to be secured!!!
            ##
            if command == 'tflush':
                self.tribes = []
                DataStore.Flush('Players')
                DataStore.Flush('Tribes')


    def On_PlayerConnected(self, Player):
        Player.Message("Welcome to the server!")
        con_player = PlayerData(Player)
#        con_playerTribe = TribeData
#        con_player.playerData['online'] = 1

    def On_PlayerDisconnected(self, Player):
        disc_player = PlayerData(Player)
        disc_player.playerData['online'] = 0


