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


# Thanks to Jakkee for helping me with overview thingy <3
broadcastgui = [
    {
        "name": "broadcastui",
        #"parent": "Overlay",
        "components":
        [
            {
                "type": "UnityEngine.UI.Image",
                "color": "0.1 0.1 0.1 0.4",
            },
            {
                "type": "RectTransform",
                "anchormin": "0.005 0.975",
                "anchormax": "0.035 0.995"
            }
        ]
    },
    {
        "parent": "broadcastui",
        "components":
        [
            {
                "type": "UnityEngine.UI.Text",
                "text": "[TEXT]",
                "color":  "0.9 0.1 0.1 0.8",
                "fontSize": 10,
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
string = json.encode(broadcastgui)
broadcast = json.makepretty(string)


class AntiOfflineRaid():

    def On_PluginInit(self):
        self.flaggedPlayers = []
        self.notifiedPlayers = []
        self.disconnectedPlayers = {}
        self.timerLenght = 900
        self.nofityTimer = 30
        self.offlineProtectionTimeout = 86400

    def On_CombatEntityHurt(self, HurtEvent):
        '''
        :param CombatEntityHurtEvent:
        :return:
        Detects if building part was damaged and get its location and owner
        '''

        attacker = HurtEvent.Attacker
        ignoredDamagesList = ['ElectricShock', 'Heat', 'Cold']
        if attacker and attacker.IsPlayer() and str(HurtEvent.DamageType) not in ignoredDamagesList:

            attackerID = attacker.SteamID
            victimLocation = HurtEvent.Victim.Location
            victimID = DataStore.Get("BuildingPartOwner", victimLocation)

            #dodao victimID jer mi ponekad vraca Null (moguci datastore issue?)
            if victimID and HurtEvent.Victim.IsBuildingPart() and not self.checkAttVictTribe(attackerID, victimID):
                Util.Log('attackerID '+str(attackerID))
                Util.Log('victimID ' + str(victimID))
                victimData = DataStore.Get('Players', victimID)
                victim = Server.FindPlayer(str(victimID))

                if not victim:
                    victimName = victimData['name']
                    playerOffline = True
                else:
                    victim = Server.FindPlayer(victimID)
                    playerOffline = False

                damageAmounts = HurtEvent.DamageAmounts
                if attackerID != victimID and not self.victInAttTribe(attackerID, victimID) and attackerID not in self.flaggedPlayers:
                    self.checkTribeBeforeFlag(attackerID)

                if playerOffline and (self.protectForOffline(victimID) and not self.tribeConditions(victimID)):
                    for i, d in enumerate(damageAmounts):
                        if damageAmounts[i] != 0.0:
                            damageAmounts[i] = 0.0
                    HurtEvent.DamageAmounts=damageAmounts
                    self.notifyPlayer(attackerID, victimName)

                elif not playerOffline and attackerID != victimID and victimID not in self.flaggedPlayers:
                    # if victim is active, and not flagged
                    self.checkTribeBeforeFlag(victimID)

    def On_PlayerHurt(self, HurtEvent):

        attacker = HurtEvent.Attacker
        victim = HurtEvent.Victim

        if attacker != None and victim != None:
            if attacker and attacker.IsPlayer() and victim.IsPlayer():
                attackerID = attacker.SteamID
                victimID = victim.SteamID
                if attackerID != victimID and not self.victInAttTribe(attackerID, victimID):
                    if not self.checkPVPFlag(attackerID):
                        self.checkTribeBeforeFlag(attackerID)
                    if not self.checkPVPFlag(victimID) and Server.FindPlayer(victimID):
                        self.checkTribeBeforeFlag(victimID)

    def victInAttTribe(self, attackerID, victimID):
        attackerD = DataStore.Get("Players", attackerID)
        victimD = DataStore.Get("Players", victimID)

        if attackerD['tribe'] == victimD['tribe']:
            return True
        else:
            return False


    def tribeConditions(self, playerID):
        '''
        returns true if other tribe members online, or flagged, otherwise False
        returns False if player in Ronins tribe
        TODO
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
                if tribeMember:
                    if tribeMember.Name != playerName or tribeMemberID in self.flaggedPlayers:
                        return True
        else:
            return False

    def checkTribeBeforeFlag(self, playerID):
        playerD = DataStore.Get('Players', playerID)
        if playerD['tribe'] != 'Ronins':
            tribeD = DataStore.Get('Tribes', playerD['tribe'])
            for memberID in tribeD['tribeMembers']:
                member = Server.FindPlayer(memberID)
                if member:
                    self.flagPlayerPVP(member.SteamID)
        else:
            self.flagPlayerPVP(playerID)


    def flagPlayerPVP(self, playerID):
        if not self.checkPVPFlag(playerID):
            player = Server.FindPlayer(playerID)
            self.flaggedPlayers.append(playerID)
            flagText = "Flagged "
            fpData = Plugin.CreateDict()
            fpData['SteamID'] = playerID
            CommunityEntity.ServerInstance.ClientRPCEx(Network.SendInfo(player.basePlayer.net.connection), None, "DestroyUI", Facepunch.ObjectList("broadcastui"))
            CommunityEntity.ServerInstance.ClientRPCEx(Network.SendInfo(player.basePlayer.net.connection), None, "AddUI", Facepunch.ObjectList(broadcast.Replace("[TEXT]", flagText)))

            Plugin.CreateParallelTimer("PVPFlag", self.timerLenght*1000, fpData).Start()


    def PVPFlagCallback(self, timer):
        data = timer.Args

        playerID = data['SteamID']
        playerD = DataStore.Get("Players", playerID)

        if playerD['tribe'] == 'Ronins' and playerID in self.disconnectedPlayers.keys():
            self.disconnectedPlayers.pop(playerID)
            # za sada produzuje timer za dodatnih 15 minuta u slucaju disconnecta. Nije tako lose, ali nije ni skroz ispravno
        elif playerD['tribe'] == 'Ronins':
            timer.Kill()
            player = Server.FindPlayer(playerID)
            if playerID in self.flaggedPlayers:
                self.flaggedPlayers.remove(playerID)
                if player:
                    CommunityEntity.ServerInstance.ClientRPCEx(Network.SendInfo(player.basePlayer.net.connection), None, "DestroyUI", Facepunch.ObjectList("broadcastui"))

        if playerD['tribe'] != 'Ronins':
            plTribeD = DataStore.Get('Tribes', playerD['tribe'])
            for memberID in plTribeD['tribeMembers']:
                if memberID in self.disconnectedPlayers.keys():
                    self.disconnectedPlayers.pop(playerID)
                else:
                    timer.Kill()
                    player = Server.FindPlayer(playerID)
                    if playerID in self.flaggedPlayers:
                        self.flaggedPlayers.remove(playerID)
                        if player:
                            CommunityEntity.ServerInstance.ClientRPCEx(Network.SendInfo(player.basePlayer.net.connection), None, "DestroyUI", Facepunch.ObjectList("broadcastui"))

    def notifyPlayer(self, playerID, victimName):
        player = Server.FindPlayer(playerID)
        if playerID not in self.notifiedPlayers:
            self.notifiedPlayers.append(playerID)
            pData = Plugin.CreateDict()
            pData['playerID'] = playerID
            player.MessageFrom("AOR", "Player "+victimName+" is offline and you can't damage his buildings!")
            Plugin.CreateParallelTimer('notify', self.nofityTimer*1000, pData).Start()

    def checkAttVictTribe(self, attackerID, victimID):
        '''
        :param attackerID:
        :param victimID:
        :return: bool True/False if attacker and victim share Tribe
        '''
        attackerD = DataStore.Get("Players", attackerID)
        Util.Log('attvicttribe:' + attackerD['tribe'])
        victimD = DataStore.Get("Players", victimID)
        Util.Log('attvicttribe:' + victimD['tribe'])
        if attackerD['tribe'] == victimD['tribe']:
            return True
        else:
            return False


    def notifyCallback(self, timer):
        timer.Kill()
        data = timer.Args

        playerID = data['playerID']
        self.notifiedPlayers.remove(playerID)

    def checkPVPFlag(self, playerID):
        if playerID in self.flaggedPlayers:
            return True
        else:
            return False

    def protectForOffline(self, playerID):
        '''
        Turns off protection for players until they are more then 24 hours offline

        :param player:
        :return: bool
        '''
        playerData = DataStore.Get('Players', playerID)

        #if time player is online is greater then offline protect timer, stop prottecting
        if (playerData['tribe'] == 'Ronins') and ((time.time() - playerData['lastonline']) > self.offlineProtectionTimeout) and playerID not in self.flaggedPlayers:
        #Util.Log(str((time.time() - playerData['lastonline'])))
            # player offline protection is off
            return False
        elif playerData['tribe'] != 'Ronins':

            playerTribe = playerData['tribe']
            playerTribeData = DataStore.Get('Tribes', playerTribe)
            tribeMembers = playerTribeData['tribeMembers']
            for tribeMemberID in tribeMembers:
                playerD = DataStore.Get('Players', tribeMemberID)
                if (time.time() - playerD['lastonline']) < self.offlineProtectionTimeout and tribeMemberID not in self.flaggedPlayers:
                    return True
            return False
        else:
            return True

    # def On_PlayerDisconnected(self, player):
    #     # Refreshes timers in case of player disconnect under timer
    #     # TODO provjeri radi li
    #     # ovo ce trebati napraviti preko reference na timer. Ako postoji timer, ubij ga i podesi novi
    #     # fakat TODO
    #     if player.SteamID in self.flaggedPlayers:
    #         self.flaggedPlayers.remove(player.SteamID)
    #         self.flagPlayerPVP(player)


    def On_Command(self, cmd):
        player = cmd.User
        command = cmd.cmd
        args = str.join(' ', cmd.args)

        if command == 'flag':
            if self.checkPVPFlag(player.SteamID):
                player.MessageFrom("AOR", "You are flagged, your buildings won't be protected if you go offline while you're flagged!")
            else:
                player.MessageFrom("AOR", "You are not flagged")

        if command == 'aor':
            player.Message("Antiraid system works in the following way:")
            player.Message("When you go offline, your buildings are protected for 24 hours from player damage.")
            player.Message("If you attack or someone attacks you or your buildings, you'll be flagged for 15 minutes.")
            player.Message("If you're flagged for pvp, and you log off, your buildings will not be protected for the next 15 minutes.")
            player.Message("Type /flag to see if you are flagged.")

        if command == 'flags':
            Util.Log(str(self.flaggedPlayers))

    def On_PlayerDisconnected(self, player):
        now = time.time()
        playerID = player.SteamID
        if playerID not in self.disconnectedPlayers.keys() and playerID in self.flaggedPlayers:
            self.disconnectedPlayers[playerID] = now

    def On_PlayerConnected(self, player):
        playerID = player.SteamID
        if playerID in self.disconnectedPlayers:
            self.disconnectedPlayers.pop(playerID)