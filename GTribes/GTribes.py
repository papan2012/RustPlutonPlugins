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

#CACHE PART


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


    def componentUIButton(self, command, parent, color=None, anchormin=None, anchormax=None):
        components = []
        button = {"type": "UnityEngine.UI.Button", "command": command}

        if command:
            button['command'] = command
        if color:
            button['color'] = color

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

    def createOverlay(self, objectlist):
        CommunityEntity.ServerInstance.ClientRPCEx(Network.SendInfo(self.player.basePlayer.net.connection), None, "AddUI", Facepunch.ObjectList(objectlist))

    def destroyOverlay(self, name):
        CommunityEntity.ServerInstance.ClientRPCEx(Network.SendInfo(self.player.basePlayer.net.connection), None, "DestroyUI", Facepunch.ObjectList(name))

    def makeBackground(self):
        gui = []
        #bg
        gui.append(self.componentUIImage("TribeBgUI", color="0.1 0.1 0.1 0.85", anchormin="0.105 0.165", anchormax="0.889 0.955", needsCursor=True))
        #toptray
        gui.append(self.componentUIImage("toptray", parent="TribeBgUI", color="0.2 0.2 0.2 0.35", anchormin="0.0 0.97", anchormax="1.0 1.0"))
        # toptitle
        gui.append(self.componentUIText(text="Tribe and Player Info Panel", parent="TribeBgUI", color="0.8 1.0 1.0 0.95", fontSize="13", anchormin="0.01 0.965", anchormax="0.5 0.99"))

        #close button text
        gui.append(self.componentUIText(text="close", parent="TribeBgUI", align="MiddleCenter", color="0.8 1.0 1.0 0.95", fontSize="13", anchormin="0.96 0.968", anchormax="0.995 0.999"))
        gui.append(self.componentUIButton(command="tribeUI.close" ,parent="TribeBgUI", color="0.8 1.0 1.0 0.15",anchormin="0.96 0.968", anchormax="0.995 0.999"))

        tribesUI = json.to_json(gui)
        objectList = json.makepretty(tribesUI)

        self.createOverlay(objectList)


    def makeMenu(self, selection):
        menuItems = [("Tribes", "tribeUI.tribes"), ("Players", "tribeUI.players.online"), ("You", "tribeUI.you")]

        #self.destroyOverlay(self, selection)
        gui = []

        self.destroyOverlay("MainMenu")

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
                #gui.append(self.componentUIText(text=item[0], parent="MainMenu", color=color,  align="MiddleCenter", fontSize="16", anchormin=anchormin, anchormax=anchormax))
            else:
                color = "1.0 0.9 0.9 0.95"
            gui.append(self.componentUIText(text=item[0], parent="MainMenu", color=color,  align="MiddleCenter", fontSize="16", anchormin=anchormin, anchormax=anchormax))
            gui.append(self.componentUIButton(command=item[1], parent="MainMenu", color="0.8 1.0 1.0 0.15", anchormin=anchormin, anchormax=anchormax))



            anchormin_x += 0.1
            anchormax_x += 0.1


        menuUI = json.to_json(gui)
        objectList = json.makepretty(menuUI)

        self.createOverlay(objectList)

    ###
    # PLAYERS VIEW
    ###

    def createPlayersView(self, selection):
        playersViewButtons = [('Online', 'tribeUI.players.online'), ('Offline', 'tribeUI.players.offline')]
        gui = []

        self.destroyOverlay(self.currentView)
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


        self.createOverlay(objectList)


    def createPlayerList(self, objectList):
        '''
        :return:
        '''

        self.destroyOverlay('playerList')
        #Util.Log('creating player list')
        self.currentView = 'playersView'
        self.createOverlay(objectList)

    ###
    # TRIBE VIEW
    ###

    def createTribesView(self, selection):
        self.destroyOverlay(self.currentView)

        gui = []

        gui.append(self.componentUIImage('tribeView', parent="TribeBgUI", color="0.1 0.1 0.1 0.90", anchormin="0.000 0.08", anchormax="0.999 0.88"))
        gui.append(self.componentUIText(text="This is Tribe info panel. It's under development, will be implementation soon.", parent="tribeView", color="1.0 0.9 0.9 0.95", fontSize="16", anchormin="0.001 0.0", anchormax="0.999 0.93"))
        playerListUI = json.to_json(gui)
        objectList = json.makepretty(playerListUI)

        self.currentView = 'tribeView'

        self.createOverlay(objectList)

    ###
    # PLAYER VIEW
    ###

    def createPlayerView(self, selection):
        self.destroyOverlay(self.currentView)

        gui = []

        gui.append(self.componentUIImage('tribeView', parent="TribeBgUI", color="0.1 0.1 0.1 0.90", anchormin="0.000 0.08", anchormax="0.999 0.88"))
        gui.append(self.componentUIText(text="This is You info panel. It's under development, will be implementation soon.", parent="tribeView", color="1.0 0.9 0.9 0.95", fontSize="16", anchormin="0.001 0.0", anchormax="0.999 0.93"))
        playerListUI = json.to_json(gui)
        objectList = json.makepretty(playerListUI)

        self.currentView = 'tribeView'

        self.createOverlay(objectList)


class GameUI(InterfaceComponents):

    def __init__(self, player):
        self.player = player

    def createOverlay(self, objectlist):
        #Util.Log("creating game overlay")
        CommunityEntity.ServerInstance.ClientRPCEx(Network.SendInfo(self.player.basePlayer.net.connection), None, "AddUI", Facepunch.ObjectList(objectlist))

    def destroyOverlay(self, name):
        #Util.Log('destroying '+str(name))
        CommunityEntity.ServerInstance.ClientRPCEx(Network.SendInfo(self.player.basePlayer.net.connection), None, "DestroyUI", Facepunch.ObjectList(name))

    def createButtons(self):
        buttons = [("Tribes", 'tribeUI.tribes'), ("Players", 'tribeUI.players.online'), ("Help", 'help.create')]

        gui = []
        gui.append(self.componentUIImage('TribeMenuButtons', color="0.1 0.1 0.1 0.40", anchormin="0.15 0.975", anchormax="0.999 0.999"))
        anchormin_x = 0.002
        anchormin_y = 0.002
        anchormax_x = 0.1
        anchormax_y = 0.999
        for button in buttons:
            anchormin = str(anchormin_x) + ' ' +str(anchormin_y)
            anchormax = str(anchormax_x) + ' '+ str(anchormax_y)
            gui.append(self.componentUIText(text=button[0], parent="TribeMenuButtons", color="0.1 0.8 0.1 0.90",  align="MiddleCenter", fontSize="13", anchormin=anchormin, anchormax=anchormax))
            gui.append(self.componentUIButton(command=button[1], parent="TribeMenuButtons", color="0.7 0.7 0.7 0.35", anchormin=anchormin, anchormax=anchormax))
            anchormin_x += 0.1
            anchormin_y = 0.002
            anchormax_x += 0.1
            anchormax_y = 0.999

        playerListUI = json.to_json(gui)
        objectList = json.makepretty(playerListUI)

        self.createOverlay(objectList)

class GTribes(InterfaceComponents):

    def On_PluginInit(self):
        '''
        self.overlays holds the overlay objects for reference
        :return:
        '''
        # dict for holding overlays with playerID keys
        self.overlays = {}

        self.defaultSelection = "Tribes"

        self.onlinePlayers = []
        self.offlinePlayers = []
        self.playersWithMenu = []

        for player in Server.ActivePlayers:
            self._addToOnlinePlayers(player)

        for player in Server.OfflinePlayers.Values:
            self._addToOfflinePLayers(player)

        self.onlinePlayersObjectList = self._playerListObject(self.onlinePlayers)
        self.offlinePlayersObjectList = self._playerListObject(self.offlinePlayers)

    ###
    ## CACHED DATA GENERATION
    ###

    def _playerListObject(self, playerList):
        '''
        :param playerList: list
        :return: objectList for UI generation
        '''


        gui = []

        gui.append(self.componentUIImage('playerList', parent="playersView", color="0.1 0.1 0.1 0.90", anchormin="0.001 0.0", anchormax="0.999 0.93"))

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
            gui.append(self.componentUIText(text=str(pl[1]), parent="playerList", color="1.0 0.9 0.9 0.95", align="MiddleCenter", fontSize="9", anchormin=anchormin, anchormax=anchormax))
            gui.append(self.componentUIButton(command="command", parent="playerList", color="0.8 1.0 1.0 0.15", anchormin=anchormin, anchormax=anchormax))
            anchormin_y -= 0.05
            anchormax_y -= 0.05

        playerListUI = json.to_json(gui)
        objectList = json.makepretty(playerListUI)

        return objectList

    ###
    ## CACHED DATA GENERATION END
    ###



    def createGUI(self, player, currentView, selection=None):
        views =  ["Tribes", "Players", "You"]

        if player.SteamID in self.overlays.keys():
            ui = self.overlays[player.SteamID]
        else:
            ui = CreateUI(player)
            ui.makeBackground()

        if ui.currentView:
             ui.destroyOverlay(ui.currentView)
        self.overlays[player.SteamID] = ui
        ui.currentView = currentView

        if currentView == "playersView":
            ui.makeMenu("Players")
            ui.createPlayersView(selection)
            if selection == 'Online':
                ui.createPlayerList(self.onlinePlayersObjectList)
            elif selection == 'Offline':
                ui.createPlayerList(self.offlinePlayersObjectList)

        elif currentView == "tribesView":
            ui.makeMenu("Tribes")
            ui.createTribesView(selection)

        elif currentView == "playerStatistics":
            ui.makeMenu("You")
            ui.createPlayerView(selection)


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

        commands = ['tribeUI.create', 'tribeUI.close', 'tribeUI.tribes', 'tribeUI.players.online', 'tribeUI.players.offline', 'tribeUI.you']
        if cce.cmd in commands:
            player = cce.User
            playerID = player.GameID
            Util.Log(str(player.Name)+"detekcija " + str(cce.cmd))

            if cce.cmd == 'tribeUI.create':
                self.createGUI(player, "playersView", "Online")

            if cce.cmd == 'tribeUI.close':
                self.destroyGUI(player)

            if cce.cmd == 'tribeUI.tribes':
                self.createGUI(player, "tribesView", "selection")

            if cce.cmd == 'tribeUI.players.online':
                self.createGUI(player, "playersView", "Online")

            if cce.cmd == 'tribeUI.players.offline':
                self.createGUI(player, "playersView", "Offline")

            if cce.cmd == 'tribeUI.you':
                self.createGUI(player, "playerStatistics", "selection")


    def On_Command(self, cmd):
        command = cmd.cmd
        player = cmd.User
        playerID = player.GameID

        if command == 'gwho':
            self.createGUI(player, "playersView", "Online")

        if command == 'ci!':
            for pl in Server.ActivePlayers:
                int = GameUI(pl)
                int.createButtons()

        if command == 'di!':
            for pl in Server.ActivePlayers:
                int = GameUI(pl)
                int.destroyOverlay('TribeMenuButtons')

        if command == 'showMenu':
            int = GameUI(player)
            int.createButtons()

        if command == 'hideMenu':
            int = GameUI(player)
            int.destroyOverlay('TribeMenuButtons')

    def On_PlayerConnected(self, player):
        self._addToOnlinePlayers(player)
        self._sortListByKey(self.onlinePlayers, 1)
        self.onlinePlayersObjectList = self._playerListObject(self.onlinePlayers)
        self.offlinePlayersObjectList = self._playerListObject(self.offlinePlayers)

    def On_PlayerDisconnected(self, player):
        self._addToOfflinePLayers(player)
        self._sortListByKey(self.onlinePlayers, 1)
        self.onlinePlayersObjectList = self._playerListObject(self.onlinePlayers)
        self.offlinePlayersObjectList = self._playerListObject(self.offlinePlayers)
        try:
            self.playersWithMenu.remove(player.SteamID)
        except:
            pass

    def On_PlayerWakeUp(self, player):
        if player.SteamID not in self.playersWithMenu:
            self.playersWithMenu.append(player.SteamID)
            int = GameUI(player)
            int.createButtons()


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

    def _sortListByKey(self, someList, element):
        self.onlinePlayers.sort(key=lambda tup: tup[element])
        self.offlinePlayers.sort(key=lambda tup:tup[element])