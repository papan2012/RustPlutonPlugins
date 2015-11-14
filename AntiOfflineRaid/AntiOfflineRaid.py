__author__ = 'PanDevas'
__version__ = '1.51'

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


# Thanks to Jakkee for helping me with overview thingy <3
flagmark = [
    {
        "name": "flagui",
        "parent": "Overlay",
        "components":
        [
            {
                "type": "UnityEngine.UI.Image",
                "color": "0.1 0.1 0.1 0.5",
            },
            {
                "type": "RectTransform",
                "anchormin": "0.005 0.975",
                "anchormax": "0.05 0.995"
            }
        ]
    },
    {
        "parent": "flagui",
        "components":
        [
            {
                "type": "UnityEngine.UI.Text",
                "text": "[TEXT]",
                "color":  "0.9 0.1 0.1 0.8",
                "fontSize": 11,
                "align": "MiddleCenter",
            },
            {
                "type": "RectTransform",
                "anchormin": "0.005 0.005",
                "anchormax": "0.99 0.995"
            }
        ]
    }
]
string = json.encode(flagmark)
flagged = json.makepretty(string)


class AntiOfflineRaid():

    def On_PluginInit(self):
        DataStore.Add('PVPFlags', 'flagtableinit', time.time())
        self.protectedItems = ('Door')

        settings = self.loadIniSettings()
        self.timerLenght = int(settings.GetSetting("settings", "pvptimerLenght"))
        self.nofityTimer = int(settings.GetSetting("settings", "notifyTimerPeriod"))
        self.offlineProtectionTimeout = int(settings.GetSetting("settings", "offlineProtectionTimeout"))

        self.flaggedPlayers = []
        self.tribeAgress = {}
        self.notifiedPlayers = []


    def loadIniSettings(self):
        if not Plugin.IniExists("settings"):
            Plugin.CreateIni("settings")
            ini = Plugin.GetIni("settings")
            ini.AddSetting("settings", "pvptimerLenght", "900")
            ini.AddSetting("settings", "notifyTimerPeriod", "30")
            ini.AddSetting("settings", "offlineProtectionTimeout", "86400")
            ini.Save()
        return Plugin.GetIni("settings")

    def _createNotification(self, player):
        flagText = "Flaged "
        CommunityEntity.ServerInstance.ClientRPCEx(Network.SendInfo(player.basePlayer.net.connection), None, "AddUI", Facepunch.ObjectList(flagged.Replace("[TEXT]", flagText)))

    def _removeNotification(self, player):
        CommunityEntity.ServerInstance.ClientRPCEx(Network.SendInfo(player.basePlayer.net.connection), None, "DestroyUI", Facepunch.ObjectList("flagui"))

    def On_CombatEntityHurt(self, HurtEvent):
        '''
        :param CombatEntityHurtEvent:
        :return:
        Detects if building part was damaged and get its location and owner
        '''
        attacker = HurtEvent.Attacker
        victimLocation = HurtEvent.Victim.Location
        hurtEntity = HurtEvent.Victim.baseEntity.GetType().ToString()

        ignoredDamagesList = ['Heat']
        # Have to nulify heat damage for calculations, taking 10 times longer (incendiary rockets and ammo)
        # best solution for now is to have it do zero dmg to buildings and avoiding checks
        # players and deployables will still get damaged
        if str(HurtEvent.DamageType) in ignoredDamagesList and (HurtEvent.Victim.IsBuildingPart() or hurtEntity in self.protectedItems):
            damageAmounts = HurtEvent.DamageAmounts
            for i, d in enumerate(damageAmounts):
                if damageAmounts[i] != 0.0:
                    damageAmounts[i] = 0.0
                HurtEvent.DamageAmounts = damageAmounts


        if attacker and attacker.IsPlayer() and str(HurtEvent.DamageType) not in ignoredDamagesList and (HurtEvent.Victim.IsBuildingPart() or hurtEntity in self.protectedItems):
            attackerID = attacker.SteamID
            victimLocation = HurtEvent.Victim.Location
            victimID = DataStore.Get("BuildingPartOwner", victimLocation)
            victimData = DataStore.Get("Players", victimID)

            # victimID check for database debuging
            if not victimID:
                Util.Log("AOR: Victim not found "+str(victimLocation))

            if (attackerID and victimID) and (attackerID != victimID) and not self.victInAttTribe(attackerID, victimID):
                victimData = DataStore.Get('Players', victimID)
                victimName = victimData['name']
                victim = Server.FindPlayer(victimID)
                damageAmounts = HurtEvent.DamageAmounts

                self.checkTribeBeforeFlag(attackerID)
                if self.protectForOffline(victimID):
                    for i, d in enumerate(damageAmounts):
                        if damageAmounts[i] != 0.0:
                            damageAmounts[i] = 0.0
                    HurtEvent.DamageAmounts = damageAmounts
                    self.notifyPlayer(attackerID, victimName)
                elif victim or victimData['tribe'] != "Survivors":
                    Util.Log("Flagging "+victimData['tribe'])
                    self.checkTribeBeforeFlag(victimID)
                else:
                    Util.Log("All checks bypassed, shouldn't happen "+victimID+' '+victimData['tribe'])


    def On_PlayerHurt(self, HurtEvent):

        attacker = HurtEvent.Attacker
        victim = HurtEvent.Victim

        if attacker and victim:
            if attacker.IsPlayer() and victim.IsPlayer():
                attackerID = attacker.SteamID
                victimID = victim.SteamID
                if attackerID != victimID and not self.victInAttTribe(attackerID, victimID):
                    self.checkTribeBeforeFlag(attackerID)
                    self.checkTribeBeforeFlag(victimID)


    def victInAttTribe(self, attackerID, victimID):
        '''
        Used for avoiding flaging between tribe members and self flaging
        :param attackerID:
        :param victimID:
        :return: bool
        '''
        attackerD = DataStore.Get("Players", attackerID)
        victimD = DataStore.Get("Players", victimID)

        if attackerD['tribe'] == 'Survivors' and victimD['tribe'] == 'Survivors':
            return False
        elif attackerD['tribe'] == victimD['tribe']:
            return True
        else:
            return False


    def checkPVPFlag(self, playerID):
        Util.Log(str(DataStore.Keys('PVPFlags')))
        if playerID in DataStore.Keys('PVPFlags'):
            Util.Log("player already flagged")
            return True
        else:
            return False


    def protectForOffline(self, playerID):
        '''
        Turns off protection for players until they are more then 24 hours offline
        Works for whole Tribe, only one member refreshes all timers

        :param player:
        :return: bool
        '''
        playerData = DataStore.Get('Players', playerID)
        player = Server.FindPlayer(playerID)
        if not player and (playerData['tribe'] == 'Survivors') and ((time.time() - playerData['lastonline']) < self.offlineProtectionTimeout) and not self.checkPVPFlag(playerID):
            Util.Log("Tribe Survivor, player offline for "+str((time.time() - playerData['lastonline'])))
            return True
        elif playerData['tribe'] != 'Survivors':
            playerTribe = playerData['tribe']
            playerTribeData = DataStore.Get('Tribes', playerTribe)
            tribeMembers = playerTribeData['tribeMembers']
            protect = False
            for tribeMemberID in tribeMembers:
                playerD = DataStore.Get('Players', tribeMemberID)
                player = Server.FindPlayer(tribeMemberID)
                if player:
                    #Util.Log("Founda player online")
                    return False
                    break
                elif (time.time() - playerD['lastonline']) < self.offlineProtectionTimeout and not self.checkPVPFlag(tribeMemberID):
                    #Util.Log("Should be protected")
                    protect = True
            #Util.Log("returning tribe protect "+str(protect))
            return protect
        else:
            #Util.Log("Not protecting")
            return False


    def checkTribeBeforeFlag(self, playerID):
        '''
        Flag player in Survivors, flag all members in Tribe
        :param playerID:
        :return:
        '''
        playerD = DataStore.Get('Players', playerID)

        if playerD['tribe'] != 'Survivors':
            tribeD = DataStore.Get('Tribes', playerD['tribe'])

            for memberID in tribeD['tribeMembers']:
                player = Server.FindPlayer(memberID)
                if player and not self.checkPVPFlag(memberID):
                    Util.Log("Flagging member "+player.Name)
                    self.flagPlayerPVP(memberID, self.timerLenght)
                    DataStore.Add('PVPFlags', memberID, time.time())
                else:
                    DataStore.Add('PVPFlags', memberID, time.time())
        else:
            if not self.checkPVPFlag(playerID):
                DataStore.Add('PVPFlags', playerID, time.time())
                self.flagPlayerPVP(playerID, self.timerLenght)
            else:
                DataStore.Add('PVPFlags', playerID, time.time())

    def flagPlayerPVP(self, playerID, timerLenght):
        '''
        flags players or extends the initial timer if happened while flaged
        :param playerID:
        :param timerLenght:
        :return: None
        '''
        player = Server.FindPlayer(playerID)
        self._createNotification(player)
        fpData = Plugin.CreateDict()
        fpData['SteamID'] = playerID
        Util.Log("creating timer for "+str(timerLenght))
        Plugin.CreateParallelTimer("PVPFlag", timerLenght*1000, fpData).Start()



    def PVPFlagCallback(self, timer):
        data = timer.Args

        playerID = data['SteamID']
        playerD = DataStore.Get("Players", playerID)
        player = Server.FindPlayer(playerID)

        #if playerD['tribe'] == 'Survivors':
        lastAggresion = DataStore.Get("PVPFlags", playerID)
        if lastAggresion:
            timediff = self.timerLenght - (time.time() - lastAggresion)
        else:
            timer.Kill()

        if timediff > 0:
            if player:
                timer.Kill()
                self.flagPlayerPVP(playerID, timediff)
            else:
                if playerD['tribe'] == 'Survivors':
                    Util.Log("Timer will run one more cycle for disconnected player if survivor")
                    DataStore.Add('PVPFlags', playerID, time.time())
        else:
            timer.Kill()
            DataStore.Remove('PVPFlags', playerID)
            if player:
                self._removeNotification(player)
            Util.Log("killing timer for player "+playerD['name'])


    def notifyPlayer(self, playerID, victimName):
        player = Server.FindPlayer(playerID)
        if playerID not in self.notifiedPlayers:
            self.notifiedPlayers.append(playerID)
            pData = Plugin.CreateDict()
            pData['playerID'] = playerID
            player.MessageFrom("AOR", "Player "+victimName+" is offline and you can't damage his buildings!")
            Plugin.CreateParallelTimer('notify', self.nofityTimer*1000, pData).Start()


    def notifyCallback(self, timer):
        timer.Kill()
        data = timer.Args

        playerID = data['playerID']
        self.notifiedPlayers.remove(playerID)

    def On_Command(self, cmd):
        player = cmd.User
        command = cmd.cmd
        args = str.join(' ', cmd.args)
        commands = ('flag', 'flags', 'aor', 'clearflags1')

        if command in commands:
            if command == 'flag':
                if self.checkPVPFlag(player.SteamID):
                    player.MessageFrom("AOR", "You are flagged, your buildings won't be protected if you go offline while you're flagged!")
                else:
                    player.MessageFrom("AOR", "You are not flagged")

            elif command == 'flags':
                players = []
                for playerID in DataStore.Keys('PVPFlags'):
                    player = Server.FindPlayer(playerID)
                    if player:
                        players.append(player.Name)
                    else:
                        for player in Server.OfflinePlayers.Values:
                            if playerID == player.SteamID:
                                players.append(player.Name)

                Util.Log(str(players))

            elif player.Name == 'PanDevas' and command == 'clearflags1':
                # Need to implement timer kill as well
                flags = list(self.flaggedPlayers)
                Util.Log("Removing flags")

                for playerID in DataStore.Keys('PVPFlags'):
                    player = Server.FindPlayer(playerID)
                    DataStore.Remove('PVPFlags', playerID)
                    if player:
                        self._removeNotification(player)


                self.flaggedPlayers = flags


    def checkTribeForOnlineMembers(self, tribe):
        '''
        When tribe member disconnects while flagged, refresh flags if no members are online
        :param tribe:
        :return: bool
        '''
        tribeData = DataStore.Get('Tribes', tribe)
        tribeMembers = tribeData['tribeMembers']
        for tribeMemberID in tribeMembers:
            player = Server.FindPlayer(tribeMemberID)
            if player:
                Util.Log("Found member online, not extending aggression")
                return True
        # if no players ware found, extend the flag for all tribe members
        for tribeMemberID in tribeMembers:
            Util.Log("Extending time for tribe member")
            DataStore.Add('PVPFlags', tribeMemberID, time.time())

    def On_PlayerDisconnected(self, player):
        now = time.time()
        playerID = player.SteamID
        playerData = DataStore.Get('Players', playerID)
        playerData['timeonline'] = player.TimeOnline/60/24
        if playerID in DataStore.Keys('PVPFlags'):
            if playerData['tribe'] != 'Survivors':
                self.checkTribeForOnlineMembers(playerData['tribe'])
            else:
                Util.Log("Survivor disconected while flaged, adding time to flag")
                DataStore.Add('PVPFlags', playerID, time.time())


    def On_PlayerWakeUp(self, player):
        if player in Server.ActivePlayers:
            playerID = player.SteamID
            if playerID in DataStore.Keys('PVPFlags'):
                lastAggresion = DataStore.Get("PVPFlags", playerID)
                timediff = self.timerLenght - (time.time() - lastAggresion)
                if timediff > 0:
                    Util.Log("Flagged player connected, creating notification for "+str(timediff)+' seconds.')
                    self.flagPlayerPVP(playerID, timediff)