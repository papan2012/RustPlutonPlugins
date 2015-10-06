__author__ = 'PanDevas'
__version__ = '1.0'

import clr
clr.AddReferenceByPartialName("Pluton")

import Pluton
import sys
path = Util.GetPublicFolder()
import time


class AntiOfflineRaid():

    def On_PluginInit(self):
        self.flaggedPlayers = []
        self.notifiedPlayers = []
        #self.timerLenght = 900000
        self.timerLenght = 60
        self.nofityTimer = 60
        self.offlineProtectionTimeout = 86400

    def On_CombatEntityHurt(self, HurtEvent):
        '''
        :param CombatEntityHurtEvent:
        :return:
        Detects if building part was damaged and get its location and owner
        '''
        ignoredDamagesList = ['ElectricShock', 'Heat', 'Cold']
        if HurtEvent.Attacker and HurtEvent.Attacker.IsPlayer() and str(HurtEvent.DamageType) not in ignoredDamagesList:
            attacker = HurtEvent.Attacker
            attackerID = attacker.SteamID
            victimLocation = HurtEvent.Victim.Location
            if attacker and attacker.IsPlayer() and HurtEvent.Victim.IsBuildingPart():
                victimID = DataStore.Get("BuildingPartOwner", victimLocation)

                victimData = DataStore.Get('Players', victimID)
                victim = Server.FindPlayer(str(victimID))

                if not victim:
                    victimName = victimData['name']
                    playerOffline = True
                else:
                    victim = Server.FindPlayer(victimID)
                    playerOffline = False


                damageAmounts = HurtEvent.DamageAmounts
                if attacker and attackerID != victimID and not self.checkPVPFlag(attackerID):
                    self.flagPlayerPVP(attacker)

                if playerOffline and (self.protectForOffline(victimID) and not self.tribeConditions(victimID)):
                    for i, d in enumerate(damageAmounts):
                        if damageAmounts[i] != 0.0:
                            damageAmounts[i] = 0.0
                    HurtEvent.DamageAmounts=damageAmounts
                    self.notifyPlayer(attacker, victimName)

                elif not playerOffline and not self.checkPVPFlag(victimID) and attackerID != victimID:
                    # if victim is active, and not flagged
                    if not self.checkPVPFlag(victimID):
                        self.flagPlayerPVP(victim)

    def On_PlayerHurt(self, HurtEvent):

        attacker = HurtEvent.Attacker
        victim = HurtEvent.Victim

        if attacker != None and victim != None:
            if attacker and attacker.IsPlayer() and victim.IsPlayer():
                attackerID = attacker.SteamID
                victimID = victim.SteamID
                if attackerID != victimID:
                    if not self.checkPVPFlag(attackerID):
                        self.flagPlayerPVP(attacker)
                    if not self.checkPVPFlag(victimID):
                        self.flagPlayerPVP(victim)


    def tribeConditions(self, playerID):
        '''
        returns true if other tribe members online, or flagged, otherwise False
        returns False if player in Ronin tribe
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
            #Util.Log('Player Ronin, not in tribe, returned False ')
            return False

    def checkFriendlyFire(self, attacker, victim):
        '''
        TODO
        Players from friedslist can't flag for pvp, TODO

        :param attacker:
        :param victim:
        :return:
        '''
        pass

    def flagPlayerPVP(self, player):
        if player not in self.flaggedPlayers:
            self.flaggedPlayers.append(player.SteamID)
            fpData = Plugin.CreateDict()
            fpData['SteamID'] = player.SteamID

            Plugin.CreateParallelTimer("PVPFlag", self.timerLenght*1000, fpData).Start()


    def PVPFlagCallback(self, timer):
        timer.Kill()
        data = timer.Args

        playerID = data['SteamID']
        playerName = DataStore.Get("Players", playerID)
        if playerID in self.flaggedPlayers:
            self.flaggedPlayers.remove(playerID)

    def notifyPlayer(self, player, victimName):
        playerID = player.SteamID
        if playerID not in self.notifiedPlayers:
            self.notifiedPlayers.append(playerID)
            pData = Plugin.CreateDict()
            pData['playerID'] = playerID
            player.MessageFrom("AOR", "Player "+victimName+" is offline and you can't damage his buildings ")

            Plugin.CreateParallelTimer('notify', self.nofityTimer*1000, pData).Start()

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
        if (time.time() - playerData['lastonline']) > self.offlineProtectionTimeout:
            Util.Log(str((time.time() - playerData['lastonline'])))
            # player offline protection is off
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


