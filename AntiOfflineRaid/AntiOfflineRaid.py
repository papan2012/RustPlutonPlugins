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
        "components":
        [
            {
                "type": "UnityEngine.UI.Image",
                "color": "0.1 0.1 0.1 0.3",
            },
            {
                "type": "RectTransform",
                "anchormin": "0.005 0.975",
                "anchormax": "0.15 0.995"
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
                "anchormax": "0.15 0.995"
            }
        ]
    }
]
string = json.encode(flagmark)
flagged = json.makepretty(string)


class AntiOfflineRaid():

    def On_PluginInit(self):
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

        self.ownerCheckTools = ("Stone Hatchet", "Hatchet")
        self.buildingOwnerInfo = []

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
        Util.Log(str(player.Name))
        CommunityEntity.ServerInstance.ClientRPCEx(Network.SendInfo(player.basePlayer.net.connection), None, "AddUI", Facepunch.ObjectList(flagged.Replace("[TEXT]", flagText)))

    def _removeNotification(self, player):
        CommunityEntity.ServerInstance.ClientRPCEx(Network.SendInfo(player.basePlayer.net.connection), None, "DestroyUI", Facepunch.ObjectList("flagui"))

    def _reflag(self, playerID):
        playerData = DataStore.Get('Players', playerID)
        reAgressTime = time.time()
        self.reAgress[playerID] = reAgressTime

        if playerData['tribe'] != 'Survivors':
            self.tribereAgress[playerData['tribe']] = reAgressTime

    def On_BeingHammered(self, he):
        '''
        this is a dirty workaround
        '''
        if he.Victim.baseEntity.GetType().ToString() == "BuildingBlock":
            player = he.Player
            location = he.Victim.Location
            victimID = DataStore.Get("BuildingPartOwner", location)
            if not victimID:
                if player.Name == 'PanDevas':
                    player.Message("building was not found")
                # else:
                #     DataStore.Add("BuildingPartOwner", location, player.SteamID)
            if victimID and player.SteamID in self.buildingOwnerInfo:
                victimID = DataStore.Get("BuildingPartOwner", location)
                victim = Server.FindPlayer(victimID).Name
                if not victim:
                    for pl in Server.SleepingPlayers:
                        if pl.SteamID == victimID:
                            victim = pl.Name
                player.Message("This building belongs to "+str(victim))


    def On_CombatEntityHurt(self, HurtEvent):
        '''
        :param CombatEntityHurtEvent:
        :return:
        Detects if building part was damaged and get its location and owner
        '''

        attacker = HurtEvent.Attacker
        victimLocation = HurtEvent.Victim.Location

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
        if attacker and attacker.IsPlayer() and str(HurtEvent.DamageType) not in ignoredDamagesList and HurtEvent.Victim.IsBuildingPart():
            attackerID = attacker.SteamID
            victimLocation = HurtEvent.Victim.Location
            victimID = DataStore.Get("BuildingPartOwner", victimLocation)

            # victimID check for database debuging
            if not victimID:
                Util.Log("AOR: Victim not found "+str(victimLocation))
            # elif attackerID in self.buildingOwnerInfo:
            #     if HurtEvent.Weapon.Name in self.ownerCheckTools:
            #         attacker.Message("This building belongs to "+str(Server.FindPlayer(victimID).Name))

            # trying to reduce checks for reflag to once every minute
            # for now only checks reagression, maybe extand to count from first aggression
            #Moram odvojiti za attackera i victim
      #       if attackerID in self.reAgress.keys() and victimID in self.reAgress.keys():
      # #          Util.Log(" time: " +str(time.time() - self.reAgress[attackerID]))
      #           if (time.time() - self.reAgress[attackerID]) < 60000 and (time.time() - self.reAgress[victimID]) < 60000:
      #               self.reFlag = False
      #       else:
      #           self.reFlag = True
      #           Util.Log('reflag')
            #uncomment condition below to see the speed advantage
            #Util.Log(str(dontreFlag))

            if (attackerID and victimID) and (attackerID != victimID) and (not self.victInAttTribe(attackerID, victimID)):
                victimData = DataStore.Get('Players', victimID)
                victimName = victimData['name']
                victim = Server.FindPlayer(str(victimID))
                damageAmounts = HurtEvent.DamageAmounts

                self.checkTribeBeforeFlag(attackerID)

                if self.protectForOffline(victimID) and not self.tribeConditions(victimID):
                    for i, d in enumerate(damageAmounts):
                        if damageAmounts[i] != 0.0:
                            damageAmounts[i] = 0.0
                    HurtEvent.DamageAmounts = damageAmounts
                    self.notifyPlayer(attackerID, victimName)

                if victim:
                    self.checkTribeBeforeFlag(victimID)

    def On_PlayerHurt(self, HurtEvent):

        attacker = HurtEvent.Attacker
        victim = HurtEvent.Victim

        if attacker and victim:
            if attacker and attacker.IsPlayer() and victim.IsPlayer():
                attackerID = attacker.SteamID
                victimID = victim.SteamID
                #Util.Log("Player "+attacker.Name+" is attacking "+victim.Name)
                if attackerID != victimID and not self.victInAttTribe(attackerID, victimID):
                    if not self.checkPVPFlag(attackerID):
                        self.checkTribeBeforeFlag(attackerID)
                    if not self.checkPVPFlag(victimID) and Server.FindPlayer(victimID):
                        self.checkTribeBeforeFlag(victimID)
        # # performance test
        # now = time.time()
        # Util.Log("On_PlayerHurt took "+str(now-self.now))
        # # performance test end

    def victInAttTribe(self, attackerID, victimID):
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
        if (playerData['tribe'] == 'Survivors') and ((time.time() - playerData['lastonline']) < self.offlineProtectionTimeout) and not self.checkPVPFlag(playerID):
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
                    return False
                    break
                elif (time.time() - playerD['lastonline']) < self.offlineProtectionTimeout and not self.checkPVPFlag(tribeMemberID):
                    protect = True
            return protect
        else:
            return False


    def tribeConditions(self, playerID):
        '''
        return True if other members online or flagged
        True if tribe is Survivors
        False if tribe is not raidable
        :param player:
        :return: bool
        '''
        playerData = DataStore.Get('Players', playerID)
        playerName = playerData['name']
        playerTribe = playerData['tribe']
        if playerTribe != 'Survivors':
            playerTribeData = DataStore.Get('Tribes', playerTribe)
            tribeMembers = playerTribeData['tribeMembers']
            for tribeMemberID in tribeMembers:
                tribeMember = Server.FindPlayer(tribeMemberID)
                raidable = False
                if tribeMember or self.checkPVPFlag(tribeMemberID):
                    return True
                else:
                    return False
        else:
            player = Server.FindPlayer(playerID)
            if player:
                return True
            else:
                return False


    def checkTribeBeforeFlag(self, playerID):
        '''
        If player in Survivors, flag all members in Tribe
        :param playerID:
        :return:
        '''
        playerD = DataStore.Get('Players', playerID)
        player = Server.FindPlayer(playerID)
        if playerD['tribe'] != 'Survivors':
            tribeD = DataStore.Get('Tribes', playerD['tribe'])
            for memberID in tribeD['tribeMembers']:
                if player:
                    if not self.checkPVPFlag(playerID):
                        self.flagPlayerPVP(player.SteamID, self.timerLenght)
                        self.tribereAgress[playerD['tribe']] = time.time()
                    else:
                        self._reflag(playerID)
        else:
            if player:
                if not self.checkPVPFlag(playerID):
                    self.flagPlayerPVP(player.SteamID, self.timerLenght )
                else:
                    self._reflag(playerID)


    def flagPlayerPVP(self, playerID, timerLenght):
        '''
        flags players or extends the initial timer if happened while flaged
        :param playerID:
        :param timerLenght:
        :return: None
        '''
        player = Server.FindPlayer(playerID)
        if not self.checkPVPFlag(playerID):
            self.flaggedPlayers.append(playerID)
            self._createNotification(player)
        fpData = Plugin.CreateDict()
        fpData['SteamID'] = playerID
        if timerLenght == 0:
            timerLenght = 1
        Plugin.CreateParallelTimer("PVPFlag", timerLenght*1000, fpData).Start()


    def PVPFlagCallback(self, timer):
        data = timer.Args

        playerID = data['SteamID']
        playerD = DataStore.Get("Players", playerID)
        playerName = playerD['name']

        if playerD['tribe'] == 'Survivors' and playerID in self.disconnectedPlayers.keys():
            #napravi timer kill i podesi novi timer od vremena disconnecta
            self.disconnectedPlayers.pop(playerID, None)
        elif playerD['tribe'] == 'Survivors':
            if playerID in self.reAgress.keys():
                now = time.time()
                timeDiff = now - self.reAgress[playerID]
                self.reAgress.pop(playerID, None)
                timer.Kill()
                self.flagPlayerPVP(playerID, timeDiff)
            else:
                timer.Kill()
                #Util.Log("Killing timer for player "+playerName)
                player = Server.FindPlayer(playerID)
                self.flaggedPlayers.remove(playerID)
                if player:
                    self._removeNotification(player)

        if playerD['tribe'] != 'Survivors':
            now = time.time()
            player = Server.FindPlayer(playerID)
            tribe = playerD['tribe']
            timeDiff = now - self.tribereAgress[tribe]
            if timeDiff < self.timerLenght:
                #Util.Log("reflaging tribe member")
                timer.Kill()
                self.reAgress.pop(playerID, None)
                self.flagPlayerPVP(playerID, int(timeDiff))
            else:
                #Util.Log("killing tribe timer")
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

        if command == 'flag':
            if self.checkPVPFlag(player.SteamID):
                player.MessageFrom("AOR", "You are flagged, your buildings won't be protected if you go offline while you're flagged!")
            else:
                player.MessageFrom("AOR", "You are not flagged")

        if command == 'flags':
            players = []
            for playerID in self.flaggedPlayers:
                player = Server.FindPlayer(playerID)
                players.append(player.Name)
            Util.Log(str(players))

        if command == 'aor':
            player.Message("Antiraid system works in the following way:")
            player.Message("When you go offline, your buildings are protected for 24 hours from player damage.")
            player.Message("If you attack or someone attacks you or your buildings, you'll be flagged for 15 minutes.")
            player.Message("If you're flagged for pvp, and you log off, your buildings will not be protected for the next 15 minutes.")
            player.Message("Type /flag to see if you are flagged.")

        if command == 'clearflags1':
            for playerID in self.flaggedPlayers:
                player = Server.FindPlayer(playerID)
                if player:
                    self.flaggedPlayers.remove(playerID)
                    Util.Log("Clearing all flags!")
                    self._removeNotification(player)
                    self.reAgress.pop(playerID, None)
        if command == 'owner':
            if player.SteamID not in self.buildingOwnerInfo:
                self.buildingOwnerInfo.append(player.SteamID)
            else:
                self.buildingOwnerInfo.remove(player.SteamID)

    def On_PlayerDied(self, pde):
        attacker = pde.Attacker
        victim = pde.Victim
        if attacker and attacker != victim:
            if attacker.IsPlayer():
                Server.Broadcast(attacker.Name+ " killed " + victim.Name + " using "+ str(pde.Weapon.Name) + ", with a hit to " + pde.HitBone)
            else:
                name = str(attacker.Name.split('/')[-1].split('.')[0])
                Server.Broadcast(victim.Name + " was killed by " + name)

        else:
            Server.Broadcast(victim.Name + " died from " + str(pde.DamageType))


    def On_PlayerDisconnected(self, player):
        now = time.time()
        playerID = player.SteamID
        playerData = DataStore.Get('Players', playerID)
        if playerID not in self.disconnectedPlayers.keys() and playerID in self.flaggedPlayers:
            self.disconnectedPlayers[playerID] = now
        if playerData['tribe'] != 'Survivors':
            self.tribereAgress[playerData['tribe']] = now


    def On_PlayerConnected(self, player):
        playerID = player.SteamID
        if playerID in self.disconnectedPlayers.keys():
            self.disconnectedPlayers.pop(playerID, None)



    def On_PlayerWakeUp(self, player):
        if player.SteamID in self.flaggedPlayers:
            self._createNotification(player)
