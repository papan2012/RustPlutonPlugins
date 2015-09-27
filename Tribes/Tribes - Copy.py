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


class PlayerData():
    '''
            Creates player class with relevant information saved in datastore as key:value dictionary for every player attribute
            steamID
            Name
            Tribe (TribeName or Ronin)
            Tribe_rank
            Online status
    '''
    def __init__(self, player):
        self.playerID = player.SteamID
        self.playerName = player.Name
        self.playerOnlineStatus = 1
        self.playerTribe = 'Ronin'
        self.playerTribeRank = 0

        self.playerData = {'name': self.playerName,
                           'tribe': self.playerTribe,
                           'online': self.playerOnlineStatus,
                           'tribeRank': self.playerTribeRank
                           }

    def addPlayerToDatastore(self, player):
        '''
            Adds player to datastore if he isn't there already
        '''
        if not DataStore.ContainsKey("Players", self.playerID):
            DataStore.Add("Players", self.playerID, self.playerData)
            DataStore.Save()

    def changePlayerData(self, playerID, valuesToChange):
        '''
            valuesToChange = {'valueName': value}
        '''
        playerData = DataStore.Get('Players', str(playerID))
        for key in valuesToChange.keys():
            playerData[key] = valuesToChange[key]
        DataStore.Save()

    def getPlayerData(self, playerID):
        return DataStore.Get('Players', str(playerID))

    def removeFromDatastore(self, playerID):
        DataStore.Remove("Players", str(playerID))



class Tribe():

    def __init__(self):
        tribeName = ''
        tribeCheef = ''
        tribeMembers = []
        tribeFriends = []
        tribeRaidable = False


    def addTribeToDatastore(self):
        pass

    def addMember(self):
        pass

    def removeMember(self):
        pass

    def promoteMember(self):
        pass

    def addFriends(self):
        pass

    def RemoveFriedns(self):
        pass

    def tribeDetails(self):
        pass



######
###    MAIN CLASS
######
class Tribes:
    '''
       (table_name: tribe_name: {members}
       Tribes:

    '''
    def On_PluginInit(self):
        self.tribes = self._update_tribe_list()

    '''
        TRIBE HELPER METHODS
    '''
    def _update_tribe_list(self):
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

            Tribe Class
            list_of_members: rank
            friends_list : []
            hostile_tribe_list: []

        '''

        player = cmd.User
        args = str.join(' ', cmd.args)

        args = args.split(' ')[0]

        playerData = PlayerData(player)
        pd = playerData.getPlayerData(player.GameID)

        # check if Tribe exists and if player is a member of a existing tribe
        self._update_tribe_list()

        if pd['tribe'] not in self.tribes:
            pd['tribe'] = 'Ronin'

        if args in self.tribes:
            player.MessageFrom("Tribes", "That tribe already exists!")
        elif (args in self.tribes) or (pd['tribe'] != 'Ronin'):
            player.MessageFrom("Tribes", "You are alread in tribe "+str(pd['tribe']))
        elif (args not in self.tribes) and (pd['tribe'] == 'Ronin' and pd['tribe'] != 'args'):
            DataStore.Add("Tribes", args, args)
            player.MessageFrom("Tribes", "Tribe created: "+str(args))
            player.MessageFrom("Tribes", "Congratulations, you are now Chief of tribe "+str(args)+"!")
            playerData.changePlayerData(cmd.User.GameID, {'tribe': args, 'tribeRank': 0})
            self.tribes = DataStore.Keys('Tribes')


    def deleteTribe(self, cmd):
        '''
            Removes a tribe from Datastore
        '''
        player = cmd.User
        args = str.join(' ', cmd.args).split(' ')[0]

        playerData = PlayerData(player)
        pd = playerData.getPlayerData(player.GameID)

        if (pd['tribe'] == args) and (pd['tribeRank'] == 0):
            DataStore.Remove("Tribes", args)
            pd['tribe']='Ronin'
            player.MessageFrom("Tribe", "Tribe \""+str(args)+"\" removed! You are now Ronin!")
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

    def tribeDetails(self, cmd):
        pass

    def addTribeMember(self):
        pass

    def removeTribeMember(self):
        pass

    def listTribeMembers(self):
        pass

    def promoteTribeMember(self):
        pass

    '''
        END OF TRIBE CLASS METHODS
    '''


    def On_Command(self, cmd):
        '''
            All function calls here need to accept cmd Instance
        '''
        commands ={'tcreate': (self.createTribe, " - create a tribe"),
                   'tdel': (self.deleteTribe, " - delete a tribe"),
                   'tdetails': (self.tribeDetails, " - tribe details"),
                   'tlist': (self.listTribes, " - list tribes"),
                   'tinvite': (self.addTribeMember, " - invite player to tribe"),
                   'tmkick': (self.removeTribeMember, " - remove tribe member"),
                   'tlmembers': (self.listTribeMembers, " - list tribe member"),
                   'tpromote': (self.promoteTribeMember(), " - promote tribe member")
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
                DataStore.Flush("Tribes")


    def On_PlayerConnected(self, Player):
        Player.Message("Welcome to the server!")
        con_player = PlayerData(Player)
        con_player.addPlayerToDatastore(Player)