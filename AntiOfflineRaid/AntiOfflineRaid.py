__author__ = 'PanDevas'
__version__ = '1.12'

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
        self.protectedItems = ('Door')

        settings = self.loadIniSettings()
        self.flaggedPlayers = []
        self.notifiedPlayers = []
        self.disconnectedPlayers = {}
        self.timerLenght = int(settings.GetSetting("settings", "pvptimerLenght"))
        self.nofityTimer = int(settings.GetSetting("settings", "notifyTimerPeriod"))
        self.offlineProtectionTimeout = int(settings.GetSetting("settings", "offlineProtectionTimeout"))
        self.reAgress = {}
        self.tribereAgress = {}
        self.tribeDiscPlayers = {}
        self.reFlag = True # used to avoid extra checks, timers extends in check one per minute



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

    def _reflag(self, playerID):
        playerData = DataStore.Get('Players', playerID)
        reAgressTime = time.time()
        self.reAgress[playerID] = reAgressTime


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
        # players still get damaged
        if str(HurtEvent.DamageType) in ignoredDamagesList and HurtEvent.Victim.IsBuildingPart():
            damageAmounts = HurtEvent.DamageAmounts
            for i, d in enumerate(damageAmounts):
                if damageAmounts[i] != 0.0:
                    damageAmounts[i] = 0.0
                HurtEvent.DamageAmounts = damageAmounts

        #if attacker and attacker.IsPlayer() and HurtEvent.Victim.IsBuildingPart():
        if attacker and attacker.IsPlayer() and str(HurtEvent.DamageType) not in ignoredDamagesList and (HurtEvent.Victim.IsBuildingPart() or hurtEntity in self.protectedItems):
            attackerID = attacker.SteamID
            victimLocation = HurtEvent.Victim.Location
            victimID = DataStore.Get("BuildingPartOwner", victimLocation)
            victimData = DataStore.Get("Players", victimID)

            # victimID check for database debuging
            if not victimID:
                Util.Log("AOR: Victim not found "+str(victimLocation))

            if (attackerID and victimID) and (attackerID != victimID) and (not self.victInAttTribe(attackerID, victimID)):
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
                    #try except for debugging
                    try:
                        attackerName = attacker.Name
                    except:
                        attackerName = attacker
                    Util.Log(str(victim.Name)+' attacked by '+str(attackerName))
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
                    if not self.checkPVPFlag(attackerID):
                        self.checkTribeBeforeFlag(attackerID)
                    if not self.checkPVPFlag(victimID) and Server.FindPlayer(victimID):
                        self.checkTribeBeforeFlag(victimID)


    def victInAttTribe(self, attackerID, victimID):
        '''
        Used for avoiding flaging between members
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
        if playerID in self.flaggedPlayers:
            return True
        elif playerID in self.disconnectedPlayers.keys():
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
            Util.Log("Tribe survivor, protecting")
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
                    Util.Log("Player online: "+player.Name)
                    return False
                    break
                elif (time.time() - playerD['lastonline']) < self.offlineProtectionTimeout and not self.checkPVPFlag(tribeMemberID):
                    Util.Log("Protecting tribe member house")
                    protect = True
            return protect
        else:
            Util.Log("Not protecting for offline"+str(playerID)+' timecheck: '+str((time.time() - playerData['lastonline']) < self.offlineProtectionTimeout))
            return False


    def checkTribeBeforeFlag(self, playerID):
        '''
        If player in Survivors, flag all members in Tribe
        :param playerID:
        :return:
        '''
        playerD = DataStore.Get('Players', playerID)

        if playerD['tribe'] != 'Survivors':
            tribeD = DataStore.Get('Tribes', playerD['tribe'])

            for memberID in tribeD['tribeMembers']:
                player = Server.FindPlayer(memberID)
                if player:
                    if not self.checkPVPFlag(memberID):
                        self.tribereAgress[playerD['tribe']] = time.time()
                        self.flagPlayerPVP(player, self.timerLenght)
                    else:
                        self.tribereAgress[playerD['tribe']] = time.time()
        else:
            player = Server.FindPlayer(playerID)
            if player:
                if not self.checkPVPFlag(playerID):
                    self.flagPlayerPVP(player, self.timerLenght )
                else:
                    self._reflag(playerID)


    def flagPlayerPVP(self, player, timerLenght):
        '''
        flags players or extends the initial timer if happened while flaged
        :param playerID:
        :param timerLenght:
        :return: None
        '''

        if not self.checkPVPFlag(player.SteamID):
            self.flaggedPlayers.append(player.SteamID)
            self._createNotification(player)
        fpData = Plugin.CreateDict()
        fpData['SteamID'] = player.SteamID
        if timerLenght > 0:
            Util.Log("Creating timer "+ player.Name)
            Plugin.CreateParallelTimer("PVPFlag", timerLenght*1000, fpData).Start()


    def PVPFlagCallback(self, timer):
        data = timer.Args

        playerID = data['SteamID']
        playerD = DataStore.Get("Players", playerID)
        player = Server.FindPlayer(playerID)

        if playerD['tribe'] == 'Survivors' and playerID in self.disconnectedPlayers.keys():
            #napravi timer kill i podesi novi timer od vremena disconnecta
            self.disconnectedPlayers.pop(playerID, None)
        elif playerD['tribe'] == 'Survivors':
            if playerID in self.reAgress.keys():
                now = time.time()
                timeDiff = now - self.reAgress[playerID]
                self.reAgress.pop(playerID, None)
                timer.Kill()
                self.flagPlayerPVP(player, timeDiff)
            else:
                timer.Kill()
                self.flaggedPlayers.remove(playerID)
                if player:
                    self._removeNotification(player)

        if playerD['tribe'] != 'Survivors':
            now = time.time()
            tribe = playerD['tribe']
            timeDiff = now - self.tribereAgress[tribe]
            if timeDiff < self.timerLenght:
                timer.Kill()
                self.reAgress.pop(playerID, None)
                self.flagPlayerPVP(player, int(timeDiff))
            else:
                timer.Kill()
                self.flaggedPlayers.remove(playerID)
                if player:
                    self._removeNotification(player)

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
                for playerID in self.flaggedPlayers:
                    playerIDS.append(playerID)
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

                for playerID in self.flaggedPlayers:
                    player = Server.FindPlayer(playerID)
                    if player:
                        Util.Log(player.Name)
                        flags.remove(playerID)
                        self._removeNotification(player)
                        self.reAgress.pop(playerID, None)
                    else:
                        Util.Log("removing flag for offline player")
                        flags.remove(playerID)
                        self.reAgress.pop(playerID, None)
                self.flaggedPlayers = flags


    def On_PlayerDied(self, pde):
        attacker = pde.Attacker
        victim = pde.Victim
        if attacker and attacker != victim:
            if attacker.IsPlayer():
                distance = round(Util.GetVectorsDistance(attacker.Location, victim.Location), 2)
                Server.Broadcast(attacker.Name+ " killed " + victim.Name + " using "+ str(pde.Weapon.Name) + ", with a hit to " + pde.HitBone+ " from "+str(distance)+" meters.")
            else:
                name = str(attacker.Name.split('/')[-1].split('.')[0])
                Server.Broadcast(victim.Name + " was killed by " + name)

        else:
            Server.Broadcast(victim.Name + " died from " + str(pde.DamageType))


    def On_PlayerDisconnected(self, player):
        now = time.time()
        playerID = player.SteamID
        playerData = DataStore.Get('Players', playerID)
        if playerID in self.flaggedPlayers:
            self.disconnectedPlayers[playerID] = now
        if playerData['tribe'] != 'Survivors':
            self.tribereAgress[playerData['tribe']] = now


    def On_PlayerWakeUp(self, player):
        if player in Server.ActivePlayers:
            if player.SteamID in self.flaggedPlayers and player.SteamID in self.disconnectedPlayers.keys():
                self._createNotification(player)
                self.disconnectedPlayers.pop(player.SteamID, None)