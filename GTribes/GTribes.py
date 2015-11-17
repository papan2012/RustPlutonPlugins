__author__ = 'PanDevas'
__version__ = '1.11'

import clr

clr.AddReferenceByPartialName("Pluton", "Assembly-CSharp-firstpass", "Assembly-CSharp")
import Pluton
import sys
path = Util.GetPublicFolder()
sys.path.append(path + "\\Python\\Lib\\")
import time

import Facepunch
import CommunityEntity
import Network

try:
    import json
except ImportError:
    raise ImportError("LegacyBroadcast: Can not find JSON in Libs folder [Pluton\Python\Libs\] *DOWNLOAD: http://forum.pluton-team.org/resources/microjson.54/*")


class InterfaceComponents():

    def addComponent(self, components, name=None, parent=None):
        '''

        :param name:
        :param components:
        :param parent:
        :return: dict Object
        '''
        component = {}
        if name:
            component["name"] = name
        if parent:
            component["parent"] = parent
        component["components"] = components

        return component

    def componentUIImage(self, name, parent=None, color=None, anchormin=None, anchormax=None, needsCursor=False):

        components = []
        image = {"type": "UnityEngine.UI.Image", "name": name}

        if color:
            image["color"] = color

        components.append(image)

        if anchormax and anchormin:
            components.append(self.rectTransfor(anchormin, anchormax))

        if needsCursor:
            components.append(self._needsCursor())

        UIImage = self.addComponent(components, name, parent)

        return UIImage


    def componentUIText(self, text, parent, color=None, fontSize=None, align=None, anchormin=None, anchormax=None):
        components = []
        text = {"type": "UnityEngine.UI.Text", "text": text, "color": color, "fontSize": fontSize}

        if align:
            text["align"] = align

        components.append(text)

        if anchormax and anchormin:
            components.append(self.rectTransfor(anchormin, anchormax))

        UIText = self.addComponent(components, parent=parent)

        return UIText


    def componentUIButton(self, command, parent, color=None, anchormin=None, anchormax=None, close = None):
        components = []
        button = {"type": "UnityEngine.UI.Button", "command": command}

        if command:
            button['command'] = command
        if color:
            button['color'] = color

        if close:
            button['close'] = close

        components.append(button)

        if anchormax and anchormin:
            components.append(self.rectTransfor(anchormin, anchormax))

        UIButton = self.addComponent(components, parent=parent)

        return UIButton


    def rectTransfor(self, anchormin, anchormax):
        transform = {"type": "RectTransform", "anchormin": anchormin, "anchormax": anchormax}

        return transform

    def _needsCursor(self):
        return {"type": "NeedsCursor"}



class CreateUI(InterfaceComponents):
    def __init__(self, player):
        self.player = player
        self.currentView = None
        self.selection = None
        self.playerPopup=None

    def createOverlay(self, objectlist):
        CommunityEntity.ServerInstance.ClientRPCEx(Network.SendInfo(self.player.basePlayer.net.connection), None, "AddUI", Facepunch.ObjectList(objectlist))

    def destroyOverlay(self, name):
        CommunityEntity.ServerInstance.ClientRPCEx(Network.SendInfo(self.player.basePlayer.net.connection), None, "DestroyUI", Facepunch.ObjectList(name))

    def makeBackground(self, objectList):
        self.createOverlay(objectList)


    def makeMenu(self, objectList):
        self.destroyOverlay("MainMenu")
        self.createOverlay(objectList)

    ###
    # PLAYERS VIEW
    ###

    def createPlayersView(self, objectList):
        self.destroyOverlay(self.currentView)
        self.createOverlay(objectList)

    def createPlayerList(self, objectList):
        self.destroyOverlay('playerList')
        self.createOverlay(objectList)

    def createPlayerPopup(self, objectList):
        self.destroyOverlay(self.playerPopup)
        self.createOverlay(objectList)

    ###
    # TRIBE VIEW
    ###

    def createTribesView(self, objectList):
        self.destroyOverlay(self.currentView)
        self.createOverlay(objectList)

    ###
    # PLAYER VIEW
    ###

    def createPlayerStatistics(self, selection):
        self.destroyOverlay('playerStats')

        gui = []

        gui.append(self.componentUIImage('playerStats', parent="TribeBgUI", color="0.1 0.1 0.1 0.90", anchormin="0.0 0.08", anchormax="0.999 0.88"))
        gui.append(self.componentUIText(text="This is where you'll find your stats. It's under development, and it will be implementation soon (TM).", parent="playerStats", color="1.0 0.9 0.9 0.95", fontSize="16", align="MiddleCenter", anchormin="0.001 0.0", anchormax="0.999 0.93"))
        playerListUI = json.to_json(gui)
        objectList = json.makepretty(playerListUI)
        self.createOverlay(objectList)

    ###
    # TRIBE DETAILS VIEW
    ###

    def createTribePopup(self, objectList):
        self.createOverlay(objectList)


    ###
    # HELP VIEW
    ###

    def createHelpMenu(self, objectList):
        self.destroyOverlay(self.currentView)
        self.createOverlay(objectList)

    def createHelpScreen(self, objectList):
        self.destroyOverlay('helptext')
        self.createOverlay(objectList)

###
## CACHED DATA GENERATION
###
class cachedMenuData(InterfaceComponents):

    def __init(self):
        # [(tribename, len(tribeMembers))]
        self.tribeNames = []
        self.tribeMembers = {}
        self.playerDetails = {}

    ###
    # helper tribe data cache functions
    ###

    def _getPlayerData(self, tablename):
        self.playerDetails = {}

        playersTable = DataStore.GetTable(tablename)

        for key in playersTable.Keys:
            self.playerDetails[key] = playersTable[key]

    def _addToOnlinePlayers(self, player):
        try:
            playerName = unicode(player.Name, encoding='utf-8', errors='ignore')
            self.onlinePlayers.append((player.SteamID, playerName))
            if (player.SteamID, playerName) in self.offlinePlayers:
                self.offlinePlayers.remove((player.SteamID, playerName))
        except:
            pass



    def _addToOfflinePLayers(self, player):
        try:
            playerName = unicode(player.Name, encoding='utf-8', errors='ignore')
            self.offlinePlayers.append((player.SteamID, playerName))
            if (player.SteamID, playerName) in self.onlinePlayers:
                self.onlinePlayers.remove((player.SteamID, playerName))
        except:
            pass

    def _getTribeData(self, tablename):
        tribesTable = DataStore.GetTable(tablename)
        self.tribeNames = []
        self.tribeMembers = {}

        for key in tribesTable.Keys:
            self.tribeNames.append((key, len(tribesTable[key]['tribeMembers'])))
            self.tribeMembers[key] = tribesTable[key]['tribeMembers']


        self._sortListByKey(self.tribeNames, 1,reverse=True)
        self._getPlayerData("Players")

    def _cachedTribeData(self):
        for tribe in self.tribeNames:
            self.tribeDetails[tribe[0]] = self._createTribePopup(tribe[0])


    def _sortListByKey(self, someList, element, reverse=False):
        someList.sort(key=lambda tup: tup[element], reverse=reverse)

    ###
    # helper functions end
    ###

    # MENU ITEMS
    def _makeBackground(self):
        '''
        CACHED
        :return:
        '''
        ##Util.Log("making background")
        gui = []
        #bg
        gui.append(self.componentUIImage("TribeBgUI", parent="HUD/Overlay", color="0.1 0.1 0.1 0.85", anchormin="0.105 0.165", anchormax="0.889 0.955", needsCursor=True))
        #toptray
        gui.append(self.componentUIImage("toptray", parent="TribeBgUI", color="0.2 0.2 0.2 0.35", anchormin="0.0 0.97", anchormax="1.0 1.0"))
        # toptitle
        gui.append(self.componentUIText(text="Tribe and Player Info Panel", parent="TribeBgUI", color="0.8 1.0 1.0 0.95", fontSize="13", anchormin="0.01 0.965", anchormax="0.5 0.99"))

        #close button text
        gui.append(self.componentUIText(text="close", parent="TribeBgUI", align="MiddleCenter", color="0.8 1.0 1.0 0.95", fontSize="13", anchormin="0.96 0.968", anchormax="0.995 0.999"))
        gui.append(self.componentUIButton(command="tribeUI.close" ,parent="TribeBgUI", color="0.8 1.0 1.0 0.15",anchormin="0.96 0.968", anchormax="0.995 0.999"))

        tribesUI = json.to_json(gui)
        objectList = json.makepretty(tribesUI)

        return objectList

    def _makeMenu(self, selection):
        '''
        NOT CACHED
        :param selection:
        :return:
        '''
        menuItems = [("Tribes", "tribeUI.tribes"), ("Players", "tribeUI.players.online"), ("You", "tribeUI.you"), ("Help", 'tribeUI.help.tribes')]

        #self.destroyOverlay(self, selection)
        gui = []

        gui.append(self.componentUIImage("MainMenu", parent="TribeBgUI", color="0.6 0.2 0.2 0.05", anchormin="0.0 0.89", anchormax="0.999 0.96"))

        anchormin_x = 0.005
        anchormin_y = 0.1
        anchormax_x = 0.1
        anchormax_y = 0.89
        for item in menuItems:
            anchormin = str(anchormin_x) + ' ' + str(anchormin_y)
            anchormax = str(anchormax_x) + ' ' + str(anchormax_y)

            if item[0] == selection:
                color = "1.0 0.3 0.3 0.95"
            else:
                color = "1.0 0.9 0.9 0.95"
            gui.append(self.componentUIText(text=item[0], parent="MainMenu", color=color,  align="MiddleCenter", fontSize="16", anchormin=anchormin, anchormax=anchormax))
            gui.append(self.componentUIButton(command=item[1], parent="MainMenu", color="0.8 1.0 1.0 0.15", anchormin=anchormin, anchormax=anchormax))





            anchormin_x += 0.1
            anchormax_x += 0.1


        menuUI = json.to_json(gui)
        objectList = json.makepretty(menuUI)

        return objectList

    # OFFLINE AND ONLINE PLAYERS LIST
    def _createPlayersView(self, selection):
        '''
        NOT CACHED
        :param selection:
        :return:
        '''
        playersViewButtons = [('Online', 'tribeUI.players.online'), ('Offline', 'tribeUI.players.offline')]
        gui = []

        anchormin_x = 0.105
        anchormin_y = 0.95
        anchormax_x = 0.19
        anchormax_y = 0.99

        gui.append(self.componentUIImage("playersView", parent="TribeBgUI", color="0.2 0.1 0.1 0.25", anchormin="0.000 0.08", anchormax="0.999 0.88"))

        for i, button in enumerate(playersViewButtons):
            if button[0] == selection:
                color = "1.0 0.3 0.3 0.95"
            else:
                color = "1.0 0.9 0.9 0.95"
            anchormin = str(anchormin_x)+' '+str(anchormin_y)
            anchormax = str(anchormax_x)+' '+str(anchormax_y)
            gui.append(self.componentUIText(text=button[0], parent="playersView", color=color, align="MiddleCenter", fontSize="16", anchormin=anchormin, anchormax=anchormax))
            gui.append(self.componentUIButton(command=button[1], parent="playersView", color="0.8 1.0 1.0 0.15", anchormin=anchormin, anchormax=anchormax))
            anchormin_x += 0.1
            anchormax_x += 0.1


        playersView = json.to_json(gui)
        objectList = json.makepretty(playersView)

        return objectList


    def _playerListObject(self, playerList, selection):
        '''
        :param playerList: list
        :return: objectList for UI generation
        '''


        gui = []

        gui.append(self.componentUIImage("playerList", parent="playersView", color="0.1 0.1 0.1 0.90", anchormin="0.001 0.0", anchormax="0.999 0.93"))

        anchormin_x = 0.002
        anchormin_y = 0.955
        anchormax_x = 0.097
        anchormax_y = 0.995

        for i, pl in enumerate(playerList):
            if i!=0  and i%20 == 0:
                anchormin_x += 0.1
                anchormin_y = 0.955
                anchormax_x += 0.1
                anchormax_y = 0.995
            anchormin = str(anchormin_x) + ' ' +str(anchormin_y)
            anchormax = str(anchormax_x) + ' '+ str(anchormax_y)
            gui.append(self.componentUIText(text=str(pl[1]), parent="playerList", color="1.0 0.9 0.9 0.95", align="MiddleCenter", fontSize="11", anchormin=anchormin, anchormax=anchormax))
            gui.append(self.componentUIButton(command='tribe.player '+str(pl[0]), parent="playerList", color="0.8 1.0 1.0 0.15", anchormin=anchormin, anchormax=anchormax))
            anchormin_y -= 0.05
            anchormax_y -= 0.05

        playerListUI = json.to_json(gui)
        objectList = json.makepretty(playerListUI)

        return objectList

    def _createPlayerPopup(self, playerID):

        # windowSizeX=len(self.tribeMembers[tribeName])/10. * 0.25
        # #Util.Log(str(windowSizeX))
        gui = []
        playerData = DataStore.Get('Players', playerID)

        if Server.FindPlayer(playerID):
            onlineStatus = 'Now'
        else:
            onlineStatus = str(round((time.time() - playerData['lastonline'])/3600, 2))+ ' hours ago'
        timeOnline = str(round(playerData['timeonline'],2))+' hours'

        columnTitles = ("Player Details:", "Statistics:", "Top Weapons:")
        playerDetails = (('Tribe', playerData['tribe']), ('Tribe Rank', playerData['tribeRank']), ('Last Online', onlineStatus), ('Time Online', timeOnline),('Res gathered', playerData['ResStatistics']))
        statistics = (('Killls', playerData['PVPstatistics']['kills']), ('Deaths', playerData['PVPstatistics']['deaths']), ('Suicides', playerData['PVPstatistics']['suicides']),('Max Range', playerData['PVPstatistics']['max_range']))
        topWeapons = []

        weaponUse = []
        for weapon in playerData['WeaponKills'].keys():
            weaponUse.append((weapon, playerData['WeaponKills'][weapon]))
        weaponUse.sort(key=lambda tup: tup[1], reverse=True)
        for i in range(len(weaponUse)):
            topWeapons.append((weaponUse[i][0], weaponUse[i][1]))
            if i > 5:
                break

        columns = [playerDetails, statistics, topWeapons]

        ##Util.Log(str(self.tribeMembers[tribeName]))
        gui.append(self.componentUIImage(playerID, parent="playerList", color="0.4 0.4 0.4 0.98", anchormin="0.0 0.01", anchormax="0.999 0.99"))
        gui.append(self.componentUIText(text=playerData['name'], parent=playerID, color="1.0 0.9 0.9 0.95", align="MiddleCenter", fontSize="16", anchormin="0.0 0.94", anchormax="0.99 0.99"))


        for i, title in enumerate(columnTitles):
            anchormin_x = 0.01+(i*0.2)
            anchormin_y = 0.85
            anchormax_x = 0.3+(i*0.2)
            anchormax_y = 0.9
            anchormin = str(anchormin_x) + ' ' + str(anchormin_y)
            anchormax = str(anchormax_x) + ' ' + str(anchormax_y)
            gui.append(self.componentUIText(text=columnTitles[i], parent=playerID, color="1.0 0.9 0.9 0.95", fontSize="13", anchormin=anchormin, anchormax=anchormax))
            for j, detail in enumerate(columns[i]):
                anchormin_y = 0.85-((j+1)*0.05)
                anchormax_y = 0.9-((j+1)*0.05)
                anchormin = str(anchormin_x) + ' ' + str(anchormin_y)
                anchormax = str(anchormax_x) + ' ' + str(anchormax_y)
                gui.append(self.componentUIText(text=columns[i][j][0]+': '+str(columns[i][j][1]), parent=playerID, color="1.0 0.9 0.9 0.95", fontSize="13", anchormin=anchormin, anchormax=anchormax))


        gui.append(self.componentUIText(text="Click here to close", parent=playerID, color="1.0 0.3 0.3 0.95", align="MiddleCenter", fontSize="11", anchormin="0.0 0.05", anchormax="1.0 0.09"))
        gui.append(self.componentUIButton(command="tribe.player.close", parent=playerID, close=playerID, color="0.8 1.0 1.0 0.1", anchormin="0.0 0.05", anchormax="1.0 0.09" ))

        tribeDetails = json.to_json(gui)
        objectList = json.makepretty(tribeDetails)

        return objectList

    # TRIBE DATA

    def _createTribesView(self, tribeData):
        gui = []

        gui.append(self.componentUIImage('tribesView', parent="TribeBgUI", color="0.1 0.1 0.1 0.90", anchormin="0.000 0.08", anchormax="0.999 0.88"))

        anchormin_x = 0.002
        anchormin_y = 0.9
        anchormax_x = 0.15
        anchormax_y = 0.99

        for i, tribeName in enumerate(self.tribeNames):
            if i!=0  and i%9 == 0:
                anchormin_x += 0.15
                anchormin_y = 0.9
                anchormax_x += 0.15
                anchormax_y = 0.99
            anchormin = str(anchormin_x) + ' ' +str(anchormin_y)
            anchormax = str(anchormax_x) + ' '+ str(anchormax_y)
            name = tribeName[0]+' ('+str(tribeName[1])+' members)'
            ##Util.Log("tribedetails"+str(self.tribeMembers[tribeName[0]]))
            gui.append(self.componentUIText(text=name, parent="tribesView", color="1.0 0.9 0.9 0.95", align="MiddleCenter", fontSize="13", anchormin=anchormin, anchormax=anchormax))
            gui.append(self.componentUIButton(command="tribe.members "+tribeName[0], parent="tribesView", color="0.8 1.0 1.0 0.15", anchormin=anchormin, anchormax=anchormax))
            anchormin_y -= 0.1
            anchormax_y -= 0.1

        playerListUI = json.to_json(gui)
        objectList = json.makepretty(playerListUI)

        return objectList

    def _createTribePopup(self, tribeName):

        # windowSizeX=len(self.tribeMembers[tribeName])/10. * 0.25
        # #Util.Log(str(windowSizeX))
        gui = []
        anchormin_x = 0.01
        anchormin_y = 0.85
        anchormax_x = 0.2
        anchormax_y = 0.89

        ##Util.Log(str(self.tribeMembers[tribeName]))
        gui.append(self.componentUIImage(tribeName, parent="TribeBgUI", color="0.4 0.4 0.4 0.98", anchormin="0.2 0.15", anchormax="0.9 0.88"))
        gui.append(self.componentUIButton(command="tribe.details.close", parent=tribeName, close=tribeName, color="0.8 1.0 1.0 0.0", anchormin="0.0 0.0", anchormax="1.0 1.0" ))
        gui.append(self.componentUIText(text="Tribename: " + tribeName, parent=tribeName, color="1.0 0.9 0.9 0.95", align="MiddleCenter", fontSize="16", anchormin="0.0 0.94", anchormax="0.99 0.99"))

        gui.append(self.componentUIText(text="Members: ", parent=tribeName, color="1.0 0.9 0.9 0.95", fontSize="15", anchormin="0.01 0.89", anchormax="0.2 0.93"))
        for i, pl in enumerate(self.tribeMembers[tribeName]):
            ##Util.Log(str(self.playerDetails[pl]))
            if i!=0  and i%15 == 0:
                anchormin_x += 0.21
                anchormin_y = 0.85
                anchormax_x += 0.2
                anchormax_y = 0.89
            anchormin = str(anchormin_x) + ' ' +str(anchormin_y)
            anchormax = str(anchormax_x) + ' '+ str(anchormax_y)
            gui.append(self.componentUIText(text=self.playerDetails[pl]['name'], parent=tribeName, color="1.0 0.9 0.9 0.95", align="MiddleCenter", fontSize="13", anchormin=anchormin, anchormax=anchormax))
            gui.append(self.componentUIButton(command='tribe.player', parent=tribeName, color="0.8 1.0 1.0 0.25", anchormin=anchormin, anchormax=anchormax))
            anchormin_y -= 0.05
            anchormax_y -= 0.05

        gui.append(self.componentUIText(text="click anywhere on this window to close", parent=tribeName, color="1.0 0.3 0.3 0.95", align="MiddleCenter", fontSize="9", anchormin="0.0 0.05", anchormax="0.99 0.09"))

        tribeDetails = json.to_json(gui)
        objectList = json.makepretty(tribeDetails)

        return objectList

    # HELP SECTION
    def _createHelpMenu(self, selection):
        '''
        NOT CACHED
        :param selection:
        :return:
        '''
        helpButtons = [('Tribes', 'tribeUI.help.tribes'), ('Door System', 'tribeUI.help.doors'), ('AntiOfflineRaid', 'tribeUI.help.aor'),('Server Info', 'tribeUI.help.server')]
        gui = []

        anchormin_x = 0.105
        anchormin_y = 0.95
        anchormax_x = 0.19
        anchormax_y = 0.99

        gui.append(self.componentUIImage("helpView", parent="TribeBgUI", color="0.2 0.1 0.1 0.25", anchormin="0.000 0.08", anchormax="0.999 0.88"))

        for i, button in enumerate(helpButtons):
            if button[1] == selection:
                color = "1.0 0.3 0.3 0.95"
            else:
                color = "1.0 0.9 0.9 0.95"
            anchormin = str(anchormin_x)+' '+str(anchormin_y)
            anchormax = str(anchormax_x)+' '+str(anchormax_y)
            gui.append(self.componentUIText(text=button[0], parent="helpView", color=color, align="MiddleCenter", fontSize="13", anchormin=anchormin, anchormax=anchormax))
            gui.append(self.componentUIButton(command=button[1], parent="helpView", color="0.8 1.0 1.0 0.15", anchormin=anchormin, anchormax=anchormax))
            anchormin_x += 0.1
            anchormax_x += 0.1


        helpView = json.to_json(gui)
        objectList = json.makepretty(helpView)

        return objectList

    def _createHelpScreen(self, selection):
        '''
        :param playerList: list
        :return: objectList for UI generation
        '''

        helpText = {'tribeUI.help.aor':"ANTIOFFLINERAID\n\n" \
                     "The point of the AntiOfflineRaid system is, well, to prevent offline raid.\n" \
                     "Since it's one of the kind, you'll have to get to know how it works.\n\n" \
                     "Basically, when you go offline, your buildings get total protection from any player made damage for 24 hours.\n" \
                     "In case you don't come online in the next 24 hours, your building will be susceptible to damage.\n" \
                     "So, if you can't play, be sure to log in at least once in that 24 hour period to refresh the timer." \
                     "AntiofflineRaid system doesn't prevent decay!\n\n" \
                     "if a player attacks you or one of or your buildings, while you are online, you and the attacking player will be flagged with a 15 minute timer.\n" \
                     "If you log off while the timer is still on, when the timer runs out it will be extended for another 15 minutes, and you're building will not be protected until that timer runs out.\n" \
                     "That will prevent logouts in the middle of the raid to prevent raiders to take what they came for.\n" \
                     "So, if you wan't to protect your stuff, you'll have to fight for it!\n\n" \
                     "Tribe system is implemented to prevent players that are in the tribe to trigger AntiOfflineRaid system mechanisms.\n" \
                     "If you're playing with someone, join a Tribe to avoid any inconvenience and get some benefits.\n" \
                     "More about tribe mechanism in Tribes help section.\n\n"\
                     "In you get raided, raiders might put their walls on the location they entered through.\n" \
                     "If you suspect such actions ware taken, type /owner in chat and hit your walls with the Hammer. It will tell you who do they belong to.\n"\
                     "Turn the owner check off when you're done with repeated /owner command in chat.",
        'tribeUI.help.tribes':"TRIBES\n\n" \
                       "If you wan't to live with someone, or use his doors, you'll have to join the tribe with him.\n" \
                       "Tribe members can access all doors belonging to other tribe members. \n" \
                       "If you're not part of the Tribe, you won't be able to use doors on tribe member buildings, even if they don't have a code lock, or you know the lock code.\n" \
                       "More about door changes read in Doors help section.\n\n" \
                       "When you're in a Tribe, aggression flags are applied to the whole Tribe\n" \
                       "Timer for offline raid protection counts from the moment last member of the tribe went offline\n" \
                       "Tribe members are not flagged if they attack each other.\n\n" \
                       "Tribe system is managed by chat commands." \
                       "Available commands are:\n" \
                       " - /trcreate TribeName- Create a tribe, name must be 3-10 chars \n" \
                       " - /trlist - List tribes \n" \
                       " - /trinvite PlayerName - Invite player to your tribe\n" \
                       " - /traccept - Accept tribe invite \n" \
                       " - /trdetails - Get tribe details \n" \
                       " - /trleave - leave your tribe \n" \
                       " - /trdeny - deny tribe invite \n" \
                       " - /trkick -  kick member from tribe \n\n" \
                       "You can also type /trhelp in chat to get the list of available commands.\n\n",
        'tribeUI.help.doors':"DOORS\n\n" \
                      "Door system was implemented for two reasons:\n" \
                      " 1. We couldn't allow players using door on buildings whose owners were offline.\n" \
                      " 2. There's a rare glitch, or a hack, that lets people open doors without the code authorization.\n" \
                      "   - this system prevents both problems.\n\n" \
                      "When you place a door, they are bound to your SteamID. Only you can open and close them.\n"\
                      "So there's no real need for code locks on doors any longer.\n" \
                      "IMPORTANT: \n"\
                      "  - owner of the door frame is the owner of the door\n" \
                      "  - shutters are treated as doors, owner of the baars is the owner of the shutters, so to be able to open them you have to place window bars first\n\n" \
                      "If you're member of a Tribe, all tribe members will be able to access your doors automagically.\n\n" \
                      "If you need some privacy, put code locks on chests. \n" \
                      "That will prevent anyone opening them without the code.\n\n",
        'tribeUI.help.server':"SERVER INNFO\n\n" \
                        " - decay lowered to 25% effectiveness\n" \
                        " - crafting times of External stone walls is increased to 2 minutes for wooden, and 4 minutes for stone walls\n\n" \
                        "If you want to hide the top menu, write /hidemenu in chat. Type /showmenu to show it again.\n\n" \
                        "\n\n\nIf you got any questions, ask in chat, someone will know the answer.\n" \
                        "For any problems with the server plugins, contact the server owner, or plugin developer, Pan Devas on Steam.\n" \
                        "\nJoin our Steam Group ''CroHQ Rust TribeWars'' for server updates and additional information."}

        gui = []

        gui.append(self.componentUIImage(selection, parent="helpView", color="0.1 0.1 0.1 0.90", anchormin="0.001 0.0", anchormax="0.999 0.93"))
        gui.append(self.componentUIText(text="TEXT", parent=selection, color="1.0 0.9 0.9 0.95", fontSize="13", anchormin="0.01 0.0", anchormax="0.999 0.93"))


        playerListUI = json.to_json(gui)
        objectList = json.makepretty(playerListUI)

        return objectList.Replace("TEXT", helpText[selection])


###
## CACHED DATA GENERATION END
###

class GameUI(InterfaceComponents):

    def __init__(self, player):
        self.player = player

    def createOverlay(self, objectlist):
        ##Util.Log("creating game overlay")
        CommunityEntity.ServerInstance.ClientRPCEx(Network.SendInfo(self.player.basePlayer.net.connection), None, "AddUI", Facepunch.ObjectList(objectlist))

    def destroyOverlay(self, name):
        Util.Log(str(name))
        CommunityEntity.ServerInstance.ClientRPCEx(Network.SendInfo(self.player.basePlayer.net.connection), None, "DestroyUI", Facepunch.ObjectList(name))

    def createButtons(self):
        buttons = [("Tribes", 'tribeUI.tribes'), ("Players", 'tribeUI.players.online'), ("Help", 'tribeUI.help.tribes')]

        gui = []
        gui.append(self.componentUIImage('TribeMenuButtons', parent="HUD", color="0.1 0.1 0.1 0.75", anchormin="0.0 0.005", anchormax="0.3 0.05"))
        anchormin_x = 0.01
        anchormin_y = 0.01
        anchormax_x = 0.2
        anchormax_y = 0.99
        for button in buttons:
            anchormin = str(anchormin_x) + ' ' +str(anchormin_y)
            anchormax = str(anchormax_x) + ' '+ str(anchormax_y)
            gui.append(self.componentUIText(text=button[0], parent="TribeMenuButtons", color="1.0 1.0 1.0 0.8",  align="MiddleCenter", fontSize="13", anchormin=anchormin, anchormax=anchormax))
            gui.append(self.componentUIButton(command=button[1], parent="TribeMenuButtons", color="0.8 0.8 0.9 0.35", anchormin=anchormin, anchormax=anchormax))
            anchormin_x += 0.2
            anchormin_y = 0.01
            anchormax_x += 0.2
            anchormax_y = 0.99
        gui.append(self.componentUIText(text="Press Enter or Tab to use the menu", parent="TribeMenuButtons", color="0.8 0.7 0.7 0.7", align="MiddleCenter", fontSize="8", anchormin="0.6 0.01", anchormax="1.0 0.999"))

        playerListUI = json.to_json(gui)
        objectList = json.makepretty(playerListUI)

        self.createOverlay(objectList)

class GTribes(cachedMenuData):

    def On_PluginInit(self):
        '''
        self.overlays holds the overlay objects for reference
        :return:
        '''
        # dict for holding overlays with playerID keys
        self.overlays = {}
        self.playersWithMenu = {}

        # for cached data
        self.onlinePlayers = []
        self.offlinePlayers = []
        self.tribeDetails = {}

        for player in Server.ActivePlayers:
            self._addToOnlinePlayers(player)

        for player in Server.OfflinePlayers.Values:
            self._addToOfflinePLayers(player)

        self._sortListByKey(self.onlinePlayers, 1)
        self._sortListByKey(self.offlinePlayers, 1)
        # cached variables
        self.tribesData = self._getTribeData("Tribes")
        self._cachedTribeData()
        # cached object lists
        self.backGround = self._makeBackground()
        self.onlinePlayersObjectList = self._playerListObject(self.onlinePlayers, "Online")
        self.offlinePlayersObjectList = self._playerListObject(self.offlinePlayers, "Offline")

        self.tribesViewObjectList = self._createTribesView(self.tribesData)




    def createGUI(self, player, currentView, selection=None, popup=None):
        views =  ["Tribes", "Players", "You"]

        if player.SteamID in self.overlays.keys():
            ui = self.overlays[player.SteamID]
        elif player.SteamID not in self.overlays.keys():
            ui = CreateUI(player)
            ui.makeBackground(self.backGround)
            ui.currentView = None
            ui.selection = None

            self.overlays[player.SteamID] = ui

        if ui.selection != selection or ui.currentView != currentView or ui.playerPopup != popup:
            if ui.currentView != currentView and ui.currentView != None:
                ui.destroyOverlay(ui.currentView)
            if ui.selection != selection or ui.selection != None:
                ui.destroyOverlay(ui.selection)


            ui.currentView = currentView
            ui.selection = selection

            if currentView == "tribesView":
                ui.makeMenu(self._makeMenu("Tribes"))
                ui.createTribesView(self.tribesViewObjectList)
                if selection:
                    ui.createTribePopup(self.tribeDetails[selection])
            if currentView == "playersView":
                ui.makeMenu(self._makeMenu("Players"))
                ui.createPlayersView(self._createPlayersView(selection))
                if selection == 'Online':
                    ui.createPlayerList(self.onlinePlayersObjectList)
                    if popup:
                        ui.destroyOverlay(ui.playerPopup)
                        ui.playerPopup = popup
                        ui.createPlayerPopup(self._createPlayerPopup(popup))
                elif selection == 'Offline':
                    ui.createPlayerList(self.offlinePlayersObjectList)
                    if popup:
                        ui.destroyOverlay(ui.playerPopup)
                        ui.playerPopup = popup
                        ui.createPlayerPopup(self._createPlayerPopup(popup))

            if currentView == 'playerStats':
                ui.makeMenu(self._makeMenu("You"))
                ui.createPlayerStatistics(selection)

            if currentView == 'helpView':
                ui.makeMenu(self._makeMenu("Help"))
                ui.createHelpMenu(self._createHelpMenu(selection))
                ui.destroyOverlay(selection)
                ui.createHelpScreen(self._createHelpScreen(selection))


            # elif currentView == 'tribeDetails':
            #     #not cached yet
            #     ui.createTribePopup(self._createTribePopup(selection))


    def destroyGUI(self, player):
        ui = self.overlays[player.SteamID]
        ui.destroyOverlay("TribeBgUI")
        ui.currentView = None
        self.overlays.pop(player.SteamID, None)


    def On_ClientConsole(self, cce):
        '''
        detektira sve tekst inpute kao clientconsole commands....
        :param cce:
        :return:
        '''

        #Util.Log(str(cce.cmd))
        commands = ['tribeUI.create', 'tribeUI.close', 'tribeUI.tribes', 'tribeUI.players.online',
                    'tribeUI.players.offline', 'tribeUI.you', 'tribe.members',
                    'tribeUI.help', 'tribeUI.help.doors', 'tribeUI.help.tribes','tribeUI.help.aor',
                    'tribeUI.help.server', 'tribe.details.close', 'tribe.player', 'tribe.player.close']

        if cce.cmd in commands:
            player = cce.User
            playerID = player.SteamID
            ##Util.Log(str(player.Name)+"detekcija " + str(cce.cmd))
            #
            if cce.cmd == 'tribeUI.create':
                self.createGUI(player, "playersView", "Online")

            if cce.cmd == 'tribeUI.close':
                self.destroyGUI(player)

            if cce.cmd == 'tribeUI.tribes':
                self.createGUI(player, "tribesView")

            if cce.cmd == 'tribeUI.players.online':
                self.createGUI(player, "playersView", "Online")

            if cce.cmd == 'tribeUI.players.offline':
                self.createGUI(player, "playersView", "Offline")

            if cce.cmd == 'tribeUI.you':
                self.createGUI(player, "playerStats")

            if cce.cmd == 'tribe.members':
                tribeName = str.join('', cce.Args)
                self.createGUI(player, "tribesView", tribeName)

            if cce.cmd == 'tribe.details.close':
                self.createGUI(player, "tribesView")

            if cce.cmd == 'tribe.player':
                playerDetailsID = str.join('', cce.Args)
                ui = self.overlays[playerID]
                self.createGUI(player, ui.currentView, ui.selection, playerDetailsID)

            if cce.cmd == 'tribe.player.close':
                playerDetailsID = str.join('', cce.Args)
                ui = self.overlays[playerID]
                ui.playerPopup = None
                self.createGUI(player, ui.currentView, ui.selection)



            # tribe menu & submenu
            if cce.cmd == 'tribeUI.help' or cce.cmd == 'tribeUI.help.tribes':
                self.createGUI(player, "helpView", 'tribeUI.help.tribes')
            if cce.cmd == 'tribeUI.help.doors':
                self.createGUI(player, "helpView", 'tribeUI.help.doors')
            if cce.cmd == 'tribeUI.help.aor':
                self.createGUI(player, "helpView", 'tribeUI.help.aor')
            if cce.cmd == 'tribeUI.help.server':
                self.createGUI(player, "helpView", 'tribeUI.help.server')




    def On_Command(self, cmd):
        command = cmd.cmd
        player = cmd.User
        playerID = player.SteamID
        tribeDataRefreshCommands = ['trcreate', 'trleave', 'trkick', 'traccept']

        commands = ('gwho', 'help', 'ci!', 'di!', 'showmenu', 'hidemenu')
        if command in commands:
            if command == 'gwho':
                self.createGUI(player, "playersView", "Online")
            elif command == 'help':
                self.createGUI(player, "helpView", 'tribeUI.help.server')

            elif command == 'ci!':
                for pl in Server.ActivePlayers:
                    int = GameUI(pl)
                    self.playersWithMenu[pl.SteamID] = int
                    int.createButtons()

            elif command == 'di!':
                for pl in Server.ActivePlayers:
                    int = self.playersWithMenu[pl.SteamID]
                    int.destroyOverlay('TribeMenuButtons')
                    self.playersWithMenu.pop(pl.SteamID)

            elif command == 'showmenu':
                if playerID not in self.playersWithMenu.keys():
                    int = GameUI(player)
                    self.playersWithMenu[playerID] = int
                    int.createButtons()

            elif command == 'hidemenu':
                int = self.playersWithMenu[player.SteamID]
                int.destroyOverlay('TribeMenuButtons')
                self.playersWithMenu.pop(playerID)


        elif command in tribeDataRefreshCommands:
            self._getTribeData('Tribes')
            self._cachedTribeData()
            self.tribesViewObjectList = self._createTribesView(self.tribesData)



    def On_PlayerConnected(self, player):
        Server.Broadcast(player.Name+" connected.")
        self._addToOnlinePlayers(player)
        self._sortListByKey(self.onlinePlayers, 1)
        self.onlinePlayersObjectList = self._playerListObject(self.onlinePlayers, "Online")
        self.offlinePlayersObjectList = self._playerListObject(self.offlinePlayers, "Offline")

    def On_PlayerDisconnected(self, player):
        int = self.playersWithMenu[player.SteamID]
        int.destroyOverlay('TribeMenuButtons')
        self.playersWithMenu.pop(player.SteamID)
        self._addToOfflinePLayers(player)
        self._sortListByKey(self.onlinePlayers, 1)
        self.onlinePlayersObjectList = self._playerListObject(self.onlinePlayers, "Online")
        self.offlinePlayersObjectList = self._playerListObject(self.offlinePlayers, "Offline")
        self.playersWithMenu.pop(player.SteamID, None)
        Server.Broadcast(player.Name+" is now sleeping.")


    def On_PlayerWakeUp(self, player):
        if player in Server.ActivePlayers:
            if player.SteamID not in self.playersWithMenu.keys():
                int = GameUI(player)
                self.playersWithMenu[player.SteamID] = int
                int.createButtons()
