__author__ = 'PanDevas'
__version__ = '1.7'

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


class OfflineProtection():

    def On_PluginInit(self):
        DataStore.Add('pvpFlags', 'flagtableinit', time.time())
        self.protectedItems = ('Door')

        if not DataStore.GetTable("pvpTribeFlags"):
            DataStore.Add("pvpTribeFlags", 'system', time.time())


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
        if player.SteamID not in self.flaggedPlayers:
            self.flaggedPlayers.append(player.SteamID)
        CommunityEntity.ServerInstance.ClientRPCEx(Network.SendInfo(player.basePlayer.net.connection), None, "AddUI", Facepunch.ObjectList(flagged.Replace("[TEXT]", flagText)))

    def _removeNotification(self, player):
        if player.SteamID in self.flaggedPlayers:
            self.flaggedPlayers.remove(player.SteamID)
        CommunityEntity.ServerInstance.ClientRPCEx(Network.SendInfo(player.basePlayer.net.connection), None, "DestroyUI", "flagui")

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
            attackerData = DataStore.Get("Players", attackerID)

            # victimID check for database debuging
            if not victimID:
                Util.Log("AOR: Victim not found "+str(victimLocation))

            if (attackerID and victimID) and (attackerID != victimID) and not self.victInAttTribe(attackerID, victimID):
                #Util.Log(attackerData['name'] + ' is attacking '+ victimData['name'])
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
                    #Util.Log("Flagging "+victimData['tribe']+', attacker '+attackerData['name'])
                    self.checkTribeBeforeFlag(victimID)
                # else:
                #     Util.Log("All checks bypassed, happens when not protected "+victimID+' '+victimData['tribe'])


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
        if playerID in DataStore.Keys('pvpFlags'):
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
            return True
        elif playerData['tribe'] != 'Survivors':
            playerTribe = playerData['tribe']
            playerTribeData = DataStore.Get('Tribes', playerTribe)
            tribeMembers = playerTribeData['tribeMembers']
            protect = False
            if playerTribe in DataStore.Keys("pvpTribeFlags"):
                return False
            else:
                for tribeMemberID in tribeMembers:
                    playerD = DataStore.Get('Players', tribeMemberID)
                    player = Server.FindPlayer(tribeMemberID)
                    if player:
                        return False
                        break
                    elif (time.time() - playerD['lastonline']) < self.offlineProtectionTimeout:
                        protect = True
            #Util.Log("Protecting tribe? "+str(protect))
            return protect
        else:
            return False


    def checkTribeBeforeFlag(self, playerID):
        '''
        Flag player in Survivors, flag all members in Tribe
        :param playerID:
        :return:
        '''
        playerD = DataStore.Get('Players', playerID)
        tribeName = playerD['tribe']



        if playerD['tribe'] != 'Survivors':
            if tribeName not in DataStore.Keys('pvpTribeFlags'):
                #Util.Log("Flaging tribe first time")
                DataStore.Add('pvpTribeFlags', tribeName, time.time())
                self.pvpTribeFlag(tribeName, self.timerLenght)
            else:
                #Util.Log("Extending aggression")
                DataStore.Add('pvpTribeFlags', tribeName, time.time())
        else:
            if not self.checkPVPFlag(playerID):
                DataStore.Add('pvpFlags', playerID, time.time())
                self.pvpPlayerFlag(playerID, self.timerLenght)
            else:
                DataStore.Add('pvpFlags', playerID, time.time())


    # TRIBE FLAGGING
    def pvpTribeFlag(self, tribeName, timerLenght):
        '''
        Flags tribe
        :param playerID:
        :param timerLenght:
        :return:
        '''
        tribeD = DataStore.Get('Tribes', tribeName)

        for memberID in tribeD['tribeMembers']:
            player = Server.FindPlayer(memberID)
            if player and memberID not in self.flaggedPlayers:
                #Util.Log("Flaging member"+player.Name)
                DataStore.Add('pvpFlags', memberID, time.time())
                self._createNotification(player)


        tmData = Plugin.CreateDict()
        tmData['tribe'] = (tribeName, tribeD)
        #Util.Log("creating timer for tribe "+str(timerLenght))
        Plugin.CreateParallelTimer("pvpTribeFlags", timerLenght*1000, tmData).Start()

        
    
    def pvpTribeFlagsCallback(self, timer):
        tribeD = timer.Args

        lastAggression = DataStore.Get("pvpTribeFlags", tribeD['tribe'][0])
        if lastAggression:
            timediff = self.timerLenght - (time.time() - lastAggression)
        else:
            timediff = 0
        #Util.Log(str(timediff))

        if timediff > 1:
            timer.Kill()
            #Util.Log("Extending timer for "+str(timediff))
            self.pvpTribeFlag(tribeD['tribe'][0], timediff)
        else:
            timer.Kill()
            #Util.Log(tribeD['tribe'][0])
            DataStore.Remove("pvpTribeFlags", tribeD['tribe'][0])
            #Util.Log("Killing tribe flag timer")
            for memberID in tribeD['tribe'][1]['tribeMembers']:
                player = Server.FindPlayer(memberID)
                if memberID in DataStore.Keys("pvpFlags"):
                    if memberID in self.flaggedPlayers:
                        self.flaggedPlayers.remove(memberID)
                    DataStore.Remove("pvpFlags", memberID)
                if player:
                    #Util.Log("Removing notification "+player.Name)
                    self._removeNotification(player)

    # END TRIBE FLAGGING

    # PLAYER FLAGGING
    def pvpPlayerFlag(self, playerID, timerLenght):
        '''
        flags players or extends the initial timer if happened while flaged
        :param playerID:
        :param timerLenght:
        :return: None
        '''
        player = Server.FindPlayer(playerID)
        if player:
            self._createNotification(player)
            fpData = Plugin.CreateDict()
            fpData['SteamID'] = playerID
            #Util.Log("Creating timer for player "+str(player.Name)+' '+str(timerLenght))
            Plugin.CreateParallelTimer("pvpPlayerFlag", timerLenght*1000, fpData).Start()


    def pvpPlayerFlagCallback(self, timer):
        data = timer.Args

        playerID = data['SteamID']
        player = Server.FindPlayer(playerID)
        lastAggression = DataStore.Get("pvpFlags", playerID)
        if lastAggression:
            timediff = self.timerLenght - (time.time() - lastAggression)
        else:
            timediff = 0

        if timediff > 1:
            if player:
                #Util.Log("Reflaging survivor "+str(playerID)+"for "+str(timediff))
                timer.Kill()
                self.pvpPlayerFlag(playerID, timediff)
            else:
                #Util.Log("Timer will run one more cycle for disconnected player "+str(playerID))
                DataStore.Add('pvpFlags', playerID, time.time())
        else:
            timer.Kill()
            DataStore.Remove('pvpFlags', playerID)
            if player:
                self._removeNotification(player)
            #Util.Log("killing timer for player "+str(playerID))


    # END PLAYER FLAGGING

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



    def checkTribeForOnlineMembers(self, tribeName):
        '''
        When tribe member disconnects while flagged, refresh flags if no members are online
        :param tribe:
        :return: bool
        '''
        tribeData = DataStore.Get('Tribes', tribeName)
        tribeMembers = tribeData['tribeMembers']
        for tribeMemberID in tribeMembers:
            player = Server.FindPlayer(tribeMemberID)
            if player in Server.ActivePlayers:
                #Util.Log("Player was found, not extending")
                return False
                break
            else:
                #Util.Log("Player not found, extending")
                extendTimer = True
        return extendTimer


    def On_PlayerDisconnected(self, player):
        now = time.time()
        playerID = player.SteamID
        playerData = DataStore.Get('Players', playerID)
        tribeName = playerData['tribe']
        #Util.Log(str(tribeName in DataStore.Keys("pvpTribeFlags")))
        if tribeName != 'Survivors' and tribeName in DataStore.Keys("pvpTribeFlags"):
            if self.checkTribeForOnlineMembers(playerData['tribe']):
                #Util.Log("Flagged tribe member disconnnected")
                DataStore.Add('pvpTribeFlags', tribeName, time.time())
                self.flaggedPlayers.remove(playerID)
                self._removeNotification(player)
        elif playerID in DataStore.Keys('pvpFlags'):
            #Util.Log("Survivor disconnected")
            DataStore.Add('pvpFlags', playerID, time.time())
            self.flaggedPlayers.remove(playerID)
            self._removeNotification(player)




    def On_PlayerWakeUp(self, player):
        playerD = DataStore.Get('Players', player.SteamID)

        if playerD['tribe'] == 'Survivors' and player.SteamID in DataStore.Keys("pvpFlags"):
            if playerID not in self.flaggedPlayers:
                self._createNotification(player)
        elif playerD['tribe'] != 'Survivors':
            if DataStore.ContainsKey("pvpTribeFlags", playerD['tribe']):
                if player.SteamID not in self.flaggedPlayers:
                    self._createNotification(player)


    def On_Command(self, cmd):
        player = cmd.User
        command = cmd.cmd
        args = str.join(' ', cmd.args)
        commands = ('flag', 'flags', 'clearflags1')

        if command in commands:
            if command == 'flag':
                if self.checkPVPFlag(player.SteamID):
                    player.MessageFrom("AOR", "You are flagged, your buildings won't be protected if you go offline while you're flagged!")
                else:
                    player.MessageFrom("AOR", "You are not flagged")

            elif command == 'flags':
                players = []
                Util.Log("Flags:")
                for playerID in DataStore.Keys('pvpFlags'):
                    player = Server.FindPlayer(playerID)
                    if player:
                        players.append(player.Name)
                    else:
                        for player in Server.OfflinePlayers.Values:
                            if playerID == player.SteamID:
                                players.append(player.Name)
                for player in players:
                    Util.Log(str(player))
                for tribe in DataStore.Keys("pvpTribeFlags"):
                    Util.Log('Tribe:'+tribe)

            elif player.Name == 'PanDevas' and command == 'clearflags1':
                # Need to implement timer kill as well
                Util.Log("Removing flags")

                for playerID in DataStore.Keys('pvpFlags'):
                    pl = Server.FindPlayer(playerID)
                    DataStore.Remove('pvpFlags', playerID)
                    if pl:
                        self._removeNotification(pl)

                for tribeName in DataStore.Keys("pvpTribeFlags"):
                    if tribeName != 'system':
                        tribeD = DataStore.Get("Tribes", tribeName)
                        Util.Log(str(tribeD['tribeMembers']))
                        for memberID in tribeD['tribeMembers']:
                            member = Server.FindPlayer(memberID)
                            if member:
                                self._removeNotification(member)
                        DataStore.Remove("pvpTribeFlags", tribeName)
                        Util.Log("Unflaged tribe "+tribeName)

                self.flaggedPlayers = []