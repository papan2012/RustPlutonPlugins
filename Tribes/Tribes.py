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
import time




###
# CLASS FOR MANAGING PLAYER DATASTORE
###
class PlayerData():
    '''
            Creates player class with relevant information saved in datastore as key:value dictionary for every player attribute
            steamID :   Name
                        Tribe (TribeName or 'Ronins')
                        Tribe_rank
                        Online status
                        pendingInvites
    '''
    def __init__(self, player):
        '''
           (Player) => void
        '''

        if not DataStore.ContainsKey("Players", player.SteamID):
            self.playerID = player.SteamID
            self.playerName = player.Name
            self.playerOnlineStatus = 1
            self.playerTribe = 'Ronins'
            self.playerTribeRank = 0
            self.playerData = {'name': self.playerName,
                            'tribe': self.playerTribe,
                            'tribeRank': self.playerTribeRank,
                            'pendingInvites' : [],
                            'lastonline': 0
                           }
            DataStore.Add("Players", self.playerID, self.playerData)
            tribe = TribeData('Ronins')
            tribe.addMember(self.playerID)
            DataStore.Save()

        else:
            self.playerData = DataStore.Get('Players', player.SteamID)

    def changePlayerData(self, playerID, valuesToChange):
        '''
            valuesToChange = {'valueName': value}
        '''
        playerData = DataStore.Get('Players', playerID)
        for key in valuesToChange.keys():
            playerData[key] = valuesToChange[key]
        DataStore.Save()

    def removePlayerFromDataStore(self, playerID):
        DataStore.Remove("Players", playerID)
        DataStore.Save()


###
#  CLASS FOR MANAGING TRIBES DATASTORE DATA
###
class TribeData():
    '''
       (table_name: tribe_name: {members}
       Tribes:
       tribeData = {'creatorID': 'string',
            'tribeMembers': [string],
            'tribeFriends': [string],
            'tribeEnemies' : [string],
            'tribeRaidable': bool
        }
    '''
    def __init__(self, tribeName):
        # first initialization,creating Ronins tribe
        self.tribeName = tribeName

        if not DataStore.GetTable('Tribes'):
            self.tribeData = {}
            self.addTribeToDatastore(None)
        else:
            self.tribeData = DataStore.Get('Tribes', self.tribeName)




    def addTribeToDatastore(self, creatorID):
        tribeData = { 'creatorID': '',
                          'tribeMembers': [],
                          'tribeFriends': [],
                          'tribeEnemies': [],
                          'tribeRaidable': True
            }
        if creatorID == None:
            tribeData['creatorID'] = 'system'
            tribeData['tribeMembers'] = []
        else:
            tribeData['creatorID'] = creatorID
            tribeData['tribeMembers'].append(creatorID)
        DataStore.Add('Tribes', self.tribeName, tribeData)
        self.tribeData = DataStore.Get('Tribes', self.tribeName)
        DataStore.Save()


    def getTribeData(self):
        '''
            returns Tribe details dictionary
        '''
        return DataStore.Get('Tribes', self.tribeName)

    def addMember(self, recruitID):
        if recruitID not in self.tribeData['tribeMembers']:
            self.tribeData['tribeMembers'].append(recruitID)
        DataStore.Save()

    def removeMember(self, memberID):
        if memberID in self.tribeData['tribeMembers']:
            Util.Log(str(self.tribeData['tribeMembers']))
            self.tribeData['tribeMembers'].remove(str(memberID))
            Util.Log(str(self.tribeData['tribeMembers']))
            return True
        else:
            return False
        DataStore.Save()

    def promoteMember(self, memberID, rank):
        pass

    def addFriends(self, friendID):
        pass

    def RemoveFriend(self, friendID):
        pass

    def tribeMessages(self, playerName, message):
        for memberID in self.tribeData['tribeMembers']:
            if Server.FindPlayer(memberID):
                member = Server.FindPlayer(memberID)
                member.MessageFrom('TM from '+playerName, message)


######
###    MAIN CLASS
######
class Tribes:
    '''
        Manager Class
        Handles User Input and updates PlayerData and TribeData DataStores
    '''

    def On_PluginInit(self):
        self.tribeList = self._update_tribe_list()
        self.commands ={'trcreate': (self.createTribe, " - Create a tribe, 3-10 chars"),
                   'trlist': (self.listTribes, " - List tribes"),
                   'trinvite': (self.invitToTribe, " - PlayerName - Invite player to your tribe"),
                   'traccept': (self.acceptTribeInvite, " - Accept tribe invite"),
                   'trdetails': (self.getTribeDetails, " - Get tribe details"),
                   'trleave' : (self.leaveTribe, "- leave your tribe"),
                   'trdeny': (self.denyInvite, " - deny tribe invite")
                   }


    '''
        TRIBE HELPER METHODS
    '''
    def _update_tribe_list(self):
        tribeList = DataStore.Keys('Tribes')

        if not tribeList:
            createTribeRonins = TribeData('Ronins')

        self.tribeList = DataStore.Keys('Tribes')


    '''
         END OF TRIBE HELPER METHODS
    '''

    '''
        TRIBE CLASS METHODS
    '''
    def createTribe(self, cmd):
        '''
           TribeName limited to 10 chars
        '''

        #TribeName limited to 10 chars
        self._update_tribe_list()
        tribeslist = DataStore.Keys("Tribes")

        creator = cmd.User
        playerD = PlayerData(creator)

        tribeName = str.join('', cmd.args)
        tribeName = tribeName if len(tribeName) <=10 else tribeName[0:10]

        if len(tribeName) < 3:
            creator.MessageFrom("Tribes", "TribeName is shorter than 3 characters.")
        elif tribeName in self.tribeList:
            creator.MessageFrom("Tribes", "Tribe with name \""+tribeName+"\" already exists")
        elif playerD.playerData['tribe'] != 'Ronins' or playerD.playerData['tribe'] not in tribeslist:
            creator.MessageFrom("Tribes", "You're already in in tribe "+playerD.playerData['tribe'])
        else:
            #removing player from Ronins tribe
            roninsTribe = TribeData('Ronins')
            roninsTribe.removeMember(creator.SteamID)

            #creating a new tribe
            tribe = TribeData(tribeName)
            playerD.playerData['tribe'] = tribeName
            creatorID = cmd.User.SteamID
            tribe.addTribeToDatastore(creator.SteamID)
            self._update_tribe_list()

            creator.MessageFrom("Tribes", "Tribe \""+tribeName+"\" created!")



    def deleteTribe(self, cmd):
        '''
        TODO
        '''
        print "Deleting Tribe"

    def listTribes(self, cmd):
        self._update_tribe_list()
        player = cmd.User
        player.MessageFrom("Tribes List", str(len(self.tribeList))+' found')
        for i, tribeName in enumerate(self.tribeList):
            player.MessageFrom(str(i+1), tribeName)
            tribe = TribeData(tribeName)

    def invitToTribe(self, cmd):
        playerr = cmd.User
        playeri = Server.FindPlayer(str.join(' ', cmd.args))

        if playeri:
            playerR = PlayerData(playerr)
            playerI = PlayerData(playeri)

            if playerI.playerData['tribe'] != 'Ronins':
                playerr.MessageFrom("Tribes", playeri.Name+' is already in a tribe \"' + playerI.playerData['tribe']+"\"")
            elif playerR.playerData['tribe'] == 'Ronins':
                playerr.MessageFrom("Tribes", "You are not in a tribe.")
            else:
                playerr.MessageFrom("Tribes", "Player"+ playeri.Name+ "\" invited!")
                playeri.MessageFrom("Tribes", playerr.Name+" invited you to his tribe \"" + playerR.playerData['tribe']+"\"")
                playerI.playerData['pendingInvites'] = playerR.playerData['tribe']

        else:
            playerr.MessageFrom("Tribes", str.join(' ', cmd.args)+' not found')


    def acceptTribeInvite(self, cmd):
        player = cmd.User
        playerD = PlayerData(player)
        if len(playerD.playerData['pendingInvites']) > 0:
            newTribe = playerD.playerData['pendingInvites']
            remCurTribe = TribeData('Ronins')
            remCurTribe.removeMember(player.SteamID)
            tribeAccept = TribeData(newTribe)
            playerD.playerData['tribe'] = newTribe
            tribeAccept.tribeMessages(playerD.playerData['tribe'], "Player "+player.Name+" joined your Tribe")
            player.Message("You have joined the tribe \""+str(newTribe)+"\"")
            tribeAccept.addMember(player.SteamID)
        else:
            player.MessageFrom("Tribes", "No pending invites!")


    def getTribeDetails(self, cmd):
        player = cmd.User
        playerData = PlayerData(player)
        playerTribe = playerData.playerData['tribe']
        tribeData = TribeData(playerTribe)
        if tribeData:
            player.MessageFrom("Tribe members of tribe", playerTribe)
            for i, playerID in enumerate(tribeData.tribeData['tribeMembers']):
                playerD = DataStore.Get('Players', playerID)
                player.MessageFrom(str(i+1), playerD['name'])
        else:
            player.Message("Unable to get tribe details for tribe "+playerTribe)

    def leaveTribe(self, cmd):
        player = cmd.User
        playerD = PlayerData(player)
        Util.Log(str(playerD))
        currentTribe = playerD.playerData['tribe']

        if currentTribe == 'Ronins':
            player.MessageFrom("Tribes", "You're just a Ronin! Where can you go?")
        else:
            Util.Log(str(player.SteamID))
            playerTD = TribeData(currentTribe)
            playerTD.removeMember(player.SteamID)
            playerTD.tribeMessages(playerD.playerData['tribe'], "Player "+player.Name+" left your tribe!")
            playerD = PlayerData(player)
            playerD.playerData['tribe'] = 'Ronins'
            playerNTD = TribeData('Ronins')
            Util.Log(str(playerNTD))
            playerNTD.addMember(player.SteamID)
            player.MessageFrom("Tribes:", "You have left the tribe \""+currentTribe+"\"")
            if len(playerTD.tribeData['tribeMembers']) == 0 and playerTD.tribeName != 'Ronin':
                DataStore.Remove('Tribes', playerTD.tribeName)
                player.MessageFrom("Tribes", "Tribe \""+currentTribe+"\" disbanded.")

    def denyInvite(self, cmd):
        playerID = cmd.User.SteamID
        playerData = PlayerData(playerID)
        playerData['pendingInvites'] = ''


    '''
        END OF TRIBE CLASS METHODS
    '''


    def On_Command(self, cmd):
        '''
            All function calls here need to accept cmd Instance
        '''

        command = cmd.cmd

        if command in self.commands.keys():
            self.commands[command][0](cmd)
        if command == 'trhelp':
            for key in self.commands.keys():
                cmd.User.MessageFrom('Tribes',"/"+ str(key)+str(self.commands[key][1]))
            cmd.User.MessageFrom('Tribes',"/tm - send message to members of your tribe" )

        if command == 'help':
            cmd.User.Message("Type /rules to see server rules")
            cmd.User.Message("Type /trhelp for help with Tribe mod commands")
            cmd.User.Message("Type /aor for help with AntiOfflineRaid")
            cmd.User.Message("Type /who or /players to see who's online")

        if command == 'tm':
            player = cmd.User
            playerData = PlayerData(player)
            ptribe = playerData.playerData['tribe']
            pTribe = TribeData(ptribe)
            message = ' '.join((cmd.args)[0:])
            pTribe.tribeMessages(player.Name, message)



    def On_PlayerConnected(self, player):
        con_player = PlayerData(player)
        con_player.playerData['lastonline'] = time.time()
        #chek if player name has changed
        if con_player.playerData['name'] != player.Name:
            con_player.playerData['name'] = player.Name
        DataStore.Save()
        player.Message(str(len(Server.ActivePlayers))+" online, "+str(len(Server.SleepingPlayers))+" sleepers.")
        player.Message("Type /help to list available commands")


    def On_PlayerDisconnected(self, player):
        con_player = PlayerData(player)
        con_player.playerData['lastonline'] = time.time()
