__author__ = 'papan'


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
        '''
           (Player) => void
        '''
        if not DataStore.ContainsKey("Players", player.SteamID):
            self.playerID = player.SteamID
            self.playerName = player.Name
            self.playerOnlineStatus = 1
            self.playerTribe = 'Ronin'
            self.playerTribeRank = 0
            self.playerData = {'name': self.playerName,
                            'tribe': self.playerTribe,
                            'online': self.playerOnlineStatus,
                            'tribeRank': self.playerTribeRank,
                            'pendingInvites' : 'No pending invites'
                           }
            DataStore.Add("Players", self.playerID, self.playerData)
            DataStore.Save()
        else:
            self.playerData = DataStore.Get('Players', player.SteamID)


    # def addPlayerToDatastore(self, player):
    #     '''
    #         Adds player to datastore if he isn't there already
    #     '''
    #     if not DataStore.ContainsKey("Players", self.playerID):
    #         DataStore.Add("Players", self.playerID, self.playerData)
    #         DataStore.Save()

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
