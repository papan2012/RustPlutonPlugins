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
        #"parent": "Overlay",
        "components":
        [
            {
                "type": "UnityEngine.UI.Image",
                "color": "0.1 0.1 0.1 0.3",
            },
            {
                "type": "RectTransform",
                "anchormin": "0.005 0.975",
                "anchormax": "0.035 0.995"
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
                "anchormax": "0.995 0.995"
            }
        ]
    }
]
string = json.encode(flagmark)
broadcast = json.makepretty(string)


class AntiOfflineRaid():

    def On_PluginInit(self):
        settings = self.loadIniSettings()
        self.flaggedPlayers = []
        self.notifiedPlayers = []
        self.disconnectedPlayers = {}
        self.timerLenght = int(settings.GetSetting("settings", "pvptimerLenght"))
        self.nofityTimer = int(settings.GetSetting("settings", "notifyTimerPeriod"))
        self.offlineProtectionTimeout = int(settings.GetSetting("settings", "offlineProtectionTimeout"))
        # self.timerLenght = 900
        # self.nofityTimer = 30
        # self.offlineProtectionTimeout = 86400

    def loadIniSettings(self):
        if not Plugin.IniExists("settings"):
            Plugin.CreateIni("settings")
            ini = Plugin.GetIni("settings")
            ini.AddSetting("settings", "pvptimerLenght", "900")
            ini.AddSetting("settings", "notifyTimerPeriod", "30")
            ini.AddSetting("settings", "offlineProtectionTimeout", "86400")
            ini.Save()
        settings = {}
        return Plugin.GetIni("settings")


    def On_CombatEntityHurt(self, HurtEvent):
        '''
        :param CombatEntityHurtEvent:
        :return:
        Detects if building part was damaged and get its location and owner
        '''

        attacker = HurtEvent.Attacker
        victimLocation = HurtEvent.Victim.Location

        ignoredDamagesList = ['ElectricShock', 'Heat', 'Cold']
        # ignoring those damage types on buildings because of excesive number of checks
        # have to find a way to speed this up, and protect from it normally
        # speed issue might be related to Util.Log

        if str(HurtEvent.DamageType) in ignoredDamagesList and HurtEvent.Victim.IsBuildingPart():
            damageAmounts = HurtEvent.DamageAmounts
            for i, d in enumerate(damageAmounts):
                if damageAmounts[i] != 0.0:
                    damageAmounts[i] = 0.0
                HurtEvent.DamageAmounts=damageAmounts


        if attacker and attacker.IsPlayer() and str(HurtEvent.DamageType) not in ignoredDamagesList and HurtEvent.Victim.IsBuildingPart():
            attackerID = attacker.SteamID
            victimLocation = HurtEvent.Victim.Location
            victimID = DataStore.Get("BuildingPartOwner", victimLocation)
            if not victimID:
                Util.Log("AOR: Victim not found "+str(victimLocation))
            if attackerID and victimID and attackerID != victimID and not self.victInAttTribe(attackerID, victimID):
                victimData = DataStore.Get('Players', victimID)
                victimName = victimData['name']
                victim = Server.FindPlayer(str(victimID))
                if attackerID not in self.flaggedPlayers or victimID not in self.flaggedPlayers:
                    Util.Log("Player "+attacker.Name + "is attacking building of player "+victimName)

                damageAmounts = HurtEvent.DamageAmounts
                if attackerID not in self.flaggedPlayers:
                    self.checkTribeBeforeFlag(attackerID)

                if self.protectForOffline(victimID) and not self.tribeConditions(victimID):
                    for i, d in enumerate(damageAmounts):
                        if damageAmounts[i] != 0.0:
                            damageAmounts[i] = 0.0
                    HurtEvent.DamageAmounts=damageAmounts
                    self.notifyPlayer(attackerID, victimName)

                elif not self.checkPVPFlag(victimID):
                    # if victim is active, and not flagged
                    self.checkTribeBeforeFlag(victimID)

    def On_PlayerHurt(self, HurtEvent):

        attacker = HurtEvent.Attacker
        victim = HurtEvent.Victim

        if attacker and victim:
            if attacker and attacker.IsPlayer() and victim.IsPlayer():
                attackerID = attacker.SteamID
                victimID = victim.SteamID
                Util.Log("Player "+attacker.Name+" is attacking "+victim.Name)
                if attackerID != victimID and not self.victInAttTribe(attackerID, victimID):
                    if not self.checkPVPFlag(attackerID):
                        self.checkTribeBeforeFlag(attackerID)
                    if not self.checkPVPFlag(victimID) and Server.FindPlayer(victimID):
                        self.checkTribeBeforeFlag(victimID)

    def victInAttTribe(self, attackerID, victimID):
        attackerD = DataStore.Get("Players", attackerID)
        victimD = DataStore.Get("Players", victimID)

        if attackerD['tribe'] == 'Ronins' and victimD['tribe'] == 'Ronins':
            return False
        elif attackerD['tribe'] == victimD['tribe']:
            return True
        else:
            return False


    def checkPVPFlag(self, playerID):
        if playerID in self.flaggedPlayers or playerID in self.disconnectedPlayers.keys():
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
        if (playerData['tribe'] == 'Ronins') and ((time.time() - playerData['lastonline']) < self.offlineProtectionTimeout) and not self.checkPVPFlag(playerID):
            return True
        elif playerData['tribe'] != 'Ronins':

            playerTribe = playerData['tribe']
            playerTribeData = DataStore.Get('Tribes', playerTribe)
            tribeMembers = playerTribeData['tribeMembers']
            protect = False
            for tribeMemberID in tribeMembers:
                playerD = DataStore.Get('Players', tribeMemberID)
                player = Server.FindPlayer(tribeMemberID)
                if player:
                    Util.Log(player.Name+' online')
                    Util.Log("Player from tribe online, not protecting")
                    return False
                    break
                elif (time.time() - playerD['lastonline']) < self.offlineProtectionTimeout and not self.checkPVPFlag(tribeMemberID):
                    protect = True
                    Util.Log("No players offline or flagged, protecting")
            return protect
        else:
            if (time.time() - playerData['lastonline']) < self.offlineProtectionTimeout:
                Util.Log("Player "+playerData['name']+" offline more then 24 hours!")
            return False


    def tribeConditions(self, playerID):
        '''
        return True if other members online or flagged
        True if tribe is Ronins
        False if tribe is not raidable
        :param player:
        :return:
        '''
        playerData = DataStore.Get('Players', playerID)
        playerName = playerData['name']
        playerTribe = playerData['tribe']
        if playerTribe != 'Ronins':
            playerTribeData = DataStore.Get('Tribes', playerTribe)
            tribeMembers = playerTribeData['tribeMembers']
            for tribeMemberID in tribeMembers:
                tribeMember = Server.FindPlayer(tribeMemberID)
                raidable = False
                if tribeMember or self.checkPVPFlag(tribeMemberID):
                    Util.Log("Tribe Member online, flagged or disconnected!")
                    return True
                else:
                    Util.Log("TribeCond not Ronins, returning "+str(raidable))
                    return False
        else:
            player = Server.FindPlayer(playerID)
            if player:
                return True
            else:
                return False


    def checkTribeBeforeFlag(self, playerID):
        '''
        If player in Ronins, flag all members in Tribe
        :param playerID:
        :return:
        '''
        playerD = DataStore.Get('Players', playerID)
        if playerD['tribe'] != 'Ronins':
            tribeD = DataStore.Get('Tribes', playerD['tribe'])
            for memberID in tribeD['tribeMembers']:
                player = Server.FindPlayer(memberID)
                if player:
                    if player.SteamID not in self.flaggedPlayers:
                        Util.Log("Flaging member "+player.Name)
                        self.flagPlayerPVP(player)
        else:
            player = Server.FindPlayer(playerID)
            if player:
                self.flagPlayerPVP(player)


    def flagPlayerPVP(self, player):
        playerID = player.SteamID
        flagText = "Flaged "

        self.flaggedPlayers.append(playerID)
        Util.Log("Creating notification for player "+player.Name)
        CommunityEntity.ServerInstance.ClientRPCEx(Network.SendInfo(player.basePlayer.net.connection), None, "AddUI", Facepunch.ObjectList(broadcast.Replace("[TEXT]", flagText)))

        fpData = Plugin.CreateDict()
        fpData['SteamID'] = playerID
        Plugin.CreateParallelTimer("PVPFlag", self.timerLenght*1000, fpData).Start()


    def PVPFlagCallback(self, timer):
        data = timer.Args

        playerID = data['SteamID']
        playerD = DataStore.Get("Players", playerID)
        playerName = playerD['name']

        if playerD['tribe'] == 'Ronins' and playerID in self.disconnectedPlayers.keys():
            Util.Log("Player "+playerName+" was in Ronins, disconnected, extending timer")
            self.disconnectedPlayers.pop(playerID, None)
        elif playerD['tribe'] == 'Ronins':
            timer.Kill()
            Util.Log("Killing timer for player "+playerName)
            player = Server.FindPlayer(playerID)
            if playerID in self.flaggedPlayers:
                self.flaggedPlayers.remove(playerID)
                if player:
                    CommunityEntity.ServerInstance.ClientRPCEx(Network.SendInfo(player.basePlayer.net.connection), None, "DestroyUI", Facepunch.ObjectList("flagui"))

        if playerD['tribe'] != 'Ronins':
            plTribeD = DataStore.Get('Tribes', playerD['tribe'])
            flags = False
            for memberID in plTribeD['tribeMembers']:
                if memberID in self.disconnectedPlayers.keys():
                    Util.Log("Timer extending, player "+str(playerD['name']+' disconnected!'))
                    self.disconnectedPlayers.pop(memberID, None)
                    flags = True
            if not flags:
                timer.Kill()
                player = Server.FindPlayer(playerID)
                if playerID in self.flaggedPlayers:
                    self.flaggedPlayers.remove(playerID)
                    if player:
                        CommunityEntity.ServerInstance.ClientRPCEx(Network.SendInfo(player.basePlayer.net.connection), None, "DestroyUI", Facepunch.ObjectList("flagui"))

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

        if command == 'clearflags':
            for playerID in self.flaggedPlayers:
                player = Server.FindPlayer(playerID)
                if player:
                    self.flaggedPlayers.remove(playerID)
                    Util.Log("Clearing all flags!")
                    CommunityEntity.ServerInstance.ClientRPCEx(Network.SendInfo(player.basePlayer.net.connection), None, "DestroyUI", Facepunch.ObjectList("flagui"))


    def On_PlayerDisconnected(self, player):
        now = time.time()
        playerID = player.SteamID
        if playerID not in self.disconnectedPlayers.keys() and playerID in self.flaggedPlayers:
            self.disconnectedPlayers[playerID] = now


    def On_PlayerConnected(self, player):
        playerID = player.SteamID
        if playerID in self.disconnectedPlayers.keys():
            self.disconnectedPlayers.pop(playerID)


    def On_PlayerWakeUp(self, player):
        flagText = "Flagged "
        if player.SteamID in self.flaggedPlayers:
            CommunityEntity.ServerInstance.ClientRPCEx(Network.SendInfo(player.basePlayer.net.connection), None, "AddUI", Facepunch.ObjectList(broadcast.Replace("[TEXT]", flagText)))