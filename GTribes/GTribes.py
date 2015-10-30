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


    def componentUIText(self, color=None, text=None, fontSize=None, name=None, parent=None, align=None, anchormin=None, anchormax=None):
        components = []
        text = {"type": "UnityEngine.UI.Text", "color": color, "text": text, "fontSize": fontSize}

        if align:
            text["align"] = align

        components.append(text)

        if anchormax and anchormin:
            components.append(self.rectTransfor(anchormin, anchormax))

        UIText = self.addComponent(components, parent=parent)

        return UIText


    def componentUIButton(self, parent=None, name=None, command=None, color=None, anchormin=None, anchormax=None):
        components = []
        button = {"type": "UnityEngine.UI.Button"}

        if name:
            button['name'] = name
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

    def makeBackground(self):
        gui = []
        #bg
        gui.append(self.componentUIImage("TribeBgUI", color="0.1 0.1 0.1 0.85", anchormin="0.105 0.165", anchormax="0.895 0.955", needsCursor=True))
        #toptray
        gui.append(self.componentUIImage("toptray", parent="TribeBgUI", color="0.2 0.2 0.2 0.35", anchormin="0.0 0.97", anchormax="1.0 1.0"))
        # toptitle
        gui.append(self.componentUIText(color="0.8 1.0 1.0 0.95", text="Tribe and Player Info Panel", fontSize="13", parent="TribeBgUI", anchormin="0.01 0.965", anchormax="0.5 0.99", name="close"))

        #close button text
        gui.append(self.componentUIText(color="0.8 1.0 1.0 0.95", text="close", fontSize="18", parent="TribeBgUI", anchormin="0.962 0.97", anchormax="1.0 1.0", name="close"))
        gui.append(self.componentUIButton(color="0.8 1.0 1.0 0.15", name="closeButton", parent="TribeBgUI", anchormin="0.96 0.97", anchormax="0.995 0.999", command="tribe.close"))

        tribesUI = json.to_json(gui)
        objectList = json.makepretty(tribesUI)

        self.createOverlay(objectList)
        self.makeMenu()

    def makeMenu(self):
        menuItems = [("Tribes", "tribe.tribes"), ("Players", "tribe.players")]
        gui = []

        anchormin_x = 0.005
        anchormin_y = 0.92
        anchormax_x = 0.1
        anchormax_y = 0.95
        for i, item in enumerate(menuItems):
            anchormin = str(anchormin_x) + ' ' + str(anchormin_y)
            anchormax = str(anchormax_x) + ' ' + str(anchormax_y)
            Util.Log(str(anchormin))
            Util.Log(str(anchormax))
            gui.append(self.componentUIText(color="1.0 0.9 0.9 0.95", name=item, text=menuItems[i][0], parent="TribeBgUI", align="MiddleCenter", fontSize="16", anchormin=anchormin, anchormax=anchormax))
            gui.append(self.componentUIButton(color="0.8 1.0 1.0 0.15", name=item, command=menuItems[i][1], parent="TribeBgUI", anchormin=anchormin, anchormax=anchormax))
            anchormin_x += 0.1
            anchormax_x += 0.1


        menuUI = json.to_json(gui)
        objectList = json.makepretty(menuUI)

        Util.Log(str(objectList))
        self.createOverlay(objectList)


    def createOverlay(self, objectlist):
        CommunityEntity.ServerInstance.ClientRPCEx(Network.SendInfo(self.player.basePlayer.net.connection), None, "AddUI", Facepunch.ObjectList(objectlist))

    def destroyOverlay(self, name):
        CommunityEntity.ServerInstance.ClientRPCEx(Network.SendInfo(self.player.basePlayer.net.connection), None, "DestroyUI", Facepunch.ObjectList(name))

    def createPlayerView(self, player):
        pass

    def createTribesView(self, player):
        pass

class GTribes():

    def On_PluginInit(self):
        '''
        self.overlays holds the overlay objects for reference
        :return:
        '''
        self.overlays = {}

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

        if cce.cmd == 'tribe.create':
            if playerID not in self.overlays.keys():
                Util.Log("Creating overlay for "+ player.Name)
                ui = CreateUI(player)
                ui.makeBackground()
                self.overlays[playerID] = ui
        if cce.cmd == "tribe.close":
            if playerID in self.overlays.keys():
                Util.Log('Destroying overlay for '+player.Name)
                ui = self.overlays[playerID]
                ui.destroyOverlay("TribeBgUI")
                self.overlays.pop(playerID, None)
