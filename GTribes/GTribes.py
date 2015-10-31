__author__ = 'PanDevas'
__version__ = '1.0'

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
        text = {"type": "UnityEngine.UI.Text",  "text": text, "parent": parent, "color": color,"fontSize": fontSize}

        if align:
            text["align"] = align

        components.append(text)

        if anchormax and anchormin:
            components.append(self.rectTransfor(anchormin, anchormax))

        UIText = self.addComponent(components, parent=parent)

        return UIText


    def componentUIButton(self, command, parent, color=None, anchormin=None, anchormax=None):
        components = []
        button = {"type": "UnityEngine.UI.Button", "command": command, "parent": parent}

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
        #self.UI = InterfaceComponents()
        self.player = player
        self.currentView = None

    def makeBackground(self):
        gui = []
        #bg
        gui.append(self.componentUIImage("TribeBgUI", color="0.1 0.1 0.1 0.85", anchormin="0.105 0.165", anchormax="0.889 0.955", needsCursor=True))
        #toptray
        gui.append(self.componentUIImage("toptray", parent="TribeBgUI", color="0.2 0.2 0.2 0.35", anchormin="0.0 0.97", anchormax="1.0 1.0"))
        # toptitle
        gui.append(self.componentUIText(text="Tribe and Player Info Panel", parent="TribeBgUI", color="0.8 1.0 1.0 0.95", fontSize="13", anchormin="0.01 0.965", anchormax="0.5 0.99"))

        #close button text
        gui.append(self.componentUIText(text="close", parent="TribeBgUI", color="0.8 1.0 1.0 0.95", fontSize="18", anchormin="0.962 0.968", anchormax="1.0 1.0"))
        gui.append(self.componentUIButton(command="tribeUI.close" ,parent="TribeBgUI", color="0.8 1.0 1.0 0.15",anchormin="0.96 0.968", anchormax="0.995 0.999"))

        tribesUI = json.to_json(gui)
        objectList = json.makepretty(tribesUI)

        self.createOverlay(objectList)
        self.makeMenu()

    def makeMenu(self):
        menuItems = [("Tribes", "tribeUI.tribes"), ("Players", "tribeUI.players.online")]
        gui = []

        anchormin_x = 0.005
        anchormin_y = 0.91
        anchormax_x = 0.1
        anchormax_y = 0.95
        for item in menuItems:
            anchormin = str(anchormin_x) + ' ' + str(anchormin_y)
            anchormax = str(anchormax_x) + ' ' + str(anchormax_y)
            Util.Log(str(anchormin))
            Util.Log(str(anchormax))
            gui.append(self.componentUIText(text=item[0], parent="TribeBgUI", color="1.0 0.9 0.9 0.95",  align="MiddleCenter", fontSize="16", anchormin=anchormin, anchormax=anchormax))
            gui.append(self.componentUIButton(command=item[1], parent="TribeBgUI", color="0.8 1.0 1.0 0.15", anchormin=anchormin, anchormax=anchormax))
            anchormin_x += 0.1
            anchormax_x += 0.1


        menuUI = json.to_json(gui)
        objectList = json.makepretty(menuUI)

        #Util.Log(str(objectList))
        self.createOverlay(objectList)


    def createOverlay(self, objectlist):
        CommunityEntity.ServerInstance.ClientRPCEx(Network.SendInfo(self.player.basePlayer.net.connection), None, "AddUI", Facepunch.ObjectList(objectlist))

    def destroyOverlay(self, name):
        Util.Log('destroying '+str(name))
        CommunityEntity.ServerInstance.ClientRPCEx(Network.SendInfo(self.player.basePlayer.net.connection), None, "DestroyUI", Facepunch.ObjectList(name))


    def createPlayerView(self):
        playerViewButtons = [('Online', 'tribeUI.players.online'), ('Offline', 'tribeUI.players.offline')]
        gui = []

        anchormin_x = 0.1
        anchormin_y = 0.95
        anchormax_x = 0.19
        anchormax_y = 0.99

        gui.append(self.componentUIImage("playerView", parent="TribeBgUI", color="0.1 0.1 0.1 0.25", anchormin="0.001 0.10", anchormax="0.999 0.88"))
        # gui.append(self.componentUIText(text="TEST", parent="PlayerButtons", color="1.0 0.9 0.9 0.95", align="MiddleCenter", fontSize="16", anchormin="0.0 0.0", anchormax="1.0 1.0"))
        # gui.append(self.componentUIButton(command="TEST", parent="PlayerButtons", color="0.8 1.0 1.0 0.15"))


        for i, button in enumerate(playerViewButtons):
            anchormin = str(anchormin_x)+' '+str(anchormin_y)
            anchormax = str(anchormax_x)+' '+str(anchormax_y)
            gui.append(self.componentUIText(text=button[0], parent="playerView", color="1.0 0.9 0.9 0.95", align="MiddleCenter", fontSize="16", anchormin=anchormin, anchormax=anchormax))
            gui.append(self.componentUIButton(command=button[1], parent="playerView", color="0.8 1.0 1.0 0.15", anchormin=anchormin, anchormax=anchormax))
            anchormin_x += 0.1
            anchormax_x += 0.1


        playerView = json.to_json(gui)
        objectList = json.makepretty(playerView)

        Util.Log(str(objectList))

        self.createOverlay(objectList)


    def createPlayerList(self, playerList):
        '''
        TODO
        needs to accept list of players for pagination
        :return:
        '''

        Util.Log('creating player list')
        gui = []

        gui.append(self.componentUIImage('playerList', parent="playerView", color="0.1 0.1 0.1 0.85", anchormin="0.001 0.1", anchormax="0.999 0.82"))

        anchormin_x = 0.005
        anchormin_y = 0.95
        anchormax_x = 0.1
        anchormax_y = 0.99

        for i, pl in enumerate(playerList):
            if i!=0  and i%20 == 0:
                anchormin_x += 0.1
                anchormin_y = 0.95
                anchormax_x += 0.1
                anchormax_y = 0.99
            anchormin = str(anchormin_x) + ' ' +str(anchormin_y)
            anchormax = str(anchormax_x) + ' '+ str(anchormax_y)
            gui.append(self.componentUIText(text="player "+str(pl), parent="playerList", color="1.0 0.9 0.9 0.95", align="MiddleCenter", fontSize="16", anchormin=anchormin, anchormax=anchormax))
            gui.append(self.componentUIButton(command="player "+str(pl), parent="playerList", color="0.8 1.0 1.0 0.15", anchormin=anchormin, anchormax=anchormax))
            # Util.Log(str(pl.Name))
            #gui.append(self.componentUIText(text=pl.Name, parent="TribeBgUI", color="1.0 0.9 0.9 0.95", align="MiddleCenter", fontSize="16", anchormin=anchormin, anchormax=anchormax))
            # gui.append(self.componentUIButton(ommand="tribe+pl.Name", parent="TribeBgUI", color="0.8 1.0 1.0 0.15", canchormin=anchormin, anchormax=anchormax))
            anchormin_y -= 0.05
            anchormax_y -= 0.05

        playerListUI = json.to_json(gui)
        objectList = json.makepretty(playerListUI)

        self.currentView = 'playerView'

        #Util.Log(str(objectList))

        self.createOverlay(objectList)

    def createTribesView(self, player):
        pass

class GTribes():

    def On_PluginInit(self):
        '''
        self.overlays holds the overlay objects for reference
        :return:
        '''
        # dict for holding overlays with playerID keys
        self.overlays = {}
        
        # lists of online  and offline players
        self.onlinePlayers = range(0, 200)
        self.offlinePlayers = range(200, 0, -1)
        

    def On_Command(self, cmd):
        command = cmd.cmd
        player = cmd.User
        playerID = player.GameID

        if command == 'gt':
            ui = CreateUI(player)
            ui.makeBackground()
            self.overlays[playerID] = ui


    def On_ClientConsole(self, cce):
        '''
        detektira sve tekst inpute kao clientconsole commands....
        :param cce:
        :return:
        '''
        if cce.cmd != 'chat.say':
            player = cce.User
            playerID = player.GameID
            Util.Log("detekcija")

        if cce.cmd == 'tribeUI.create':
            if playerID not in self.overlays.keys():
                Util.Log("Creating overlay for "+ player.Name)
                ui = CreateUI(player)
                ui.makeBackground()
                self.overlays[playerID] = ui
        if cce.cmd == 'tribeUI.close':
            if playerID in self.overlays.keys():
                Util.Log('Destroying overlay for '+player.Name)
                ui = self.overlays[playerID]
                ui.destroyOverlay("TribeBgUI")
                self.overlays.pop(playerID, None)
                Util.Log(str(self.overlays.keys()))


        if cce.cmd == 'tribeUI.players.online':
            if playerID in self.overlays.keys():
                ui = self.overlays[playerID]
                if ui.currentView != 'playerView':
                    Util.Log('destroying '+str(ui.currentView))
                    ui.destroyOverlay(ui.currentView)
                    ui.currentView = 'playerView'
                    ui.createPlayerView()
                    ui.createPlayerList(self.onlinePlayers)

        if cce.cmd == 'tribeUI.players.offline':
            if playerID in self.overlays.keys():
                ui = self.overlays[playerID]
                if ui.currentView != 'playerView':
                    Util.Log('destroying '+str(ui.currentView))
                    ui.destroyOverlay(ui.currentView)
                    ui.currentView = 'playerView'
                    ui.createPlayerList(self.offlinePlayers)
