__author__ = 'PanDevas'
__version__ = '0.1'

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
        self.timerLenght = 900
        self.nofityTimer = 60
        self.offlineProtectionTimeout = 86400

    def On_CombatEntityHurt(self, HurtEvent):
        '''
        :param CombatEntityHurtEvent:
        :return:
        Detects if building part was damaged and get its location and owner
        '''

        if HurtEvent.Attacker and HurtEvent.Attacker.IsPlayer() and HurtEvent.Victim.IsBuildingPart():
            attacker = HurtEvent.Attacker
            victimLocation = HurtEvent.Victim.Location
            victimID = DataStore.Get("BuildingPartOwner", victimLocation)
            victimData = DataStore.Get('Players', victimID)
            victim = Find.Player(str(victimID))

            Util.Log(victimID+' '+str(victim) + victimData['name'])

            if not victim:
                 playerOffline = True
            else:
                 victim = Find.Player(victimID)
                 playerOffline = False


            damageAmounts = HurtEvent.DamageAmounts
            if attacker and attacker.SteamID != victimID and not self.checkPVPFlag(attacker.SteamID):
                Util.Log("PVB - Flaging attacker" + attacker.Name)
                self.flagPlayerPVP(attacker)


            if playerOffline and not self.checkPVPFlag(victimID) and not self.protectForOffline(victimID) and not checkTribeConditions(victimID):
                Util.Log("PVB - Building protected")
                #nullify the damage if victim is offline and not marked for pvp
                for i, d in enumerate(damageAmounts):
                    if damageAmounts[i] != 0.0:
                        damageAmounts[i] = 0.0
                HurtEvent.DamageAmounts=damageAmounts

            elif not playerOffline and self.checkPVPFlag(victimID) and attacker.SteamID != victimID:
                # if victim is active, and not flagged
                Util.Log("PVB - Flaging victim "+ str(victim))
                if self.checkPVPFlag(victimID):
                    self.flagPlayerPVP(victim)



    def On_PlayerHurt(self, HurtEvent):

        attacker = HurtEvent.Attacker
        victim = HurtEvent.Victim
        if attacker and attacker.IsPlayer() and victim.IsPlayer():
            attackerID = attacker.SteamID
            victimID = victim.SteamID
            # players can hurt themself and not beeing flagged (CHANGE to !=)
            if attackerID != victimID:
                #Server.Broadcast("Player "+HurtEvent.Victim.Name+ " was damaged by "+HurtEvent.Attacker.Name)
                if not self.checkPVPFlag(attackerID):
                    Util.Log("PVP Flag attacker "+attacker.Name)
                    self.flagPlayerPVP(attacker)
                if not self.checkPVPFlag(victimID):
                    Util.Log("PVP Flag victim "+victim.Name)
                    self.flagPlayerPVP(victim)


    def checkTribeConditions(self, playerID):
        '''
        TODO
        :param player:
        :return:
        '''
        playerData = DataStore.Get('Players', playerID)
        playerTribe = playerData.playerData['tribe']
        if playerTribe != 'Ronins':
            playerTribeData = DataStore.Get['Tribes', playerTribe]
            tribeMembers = playerTribeData.tribeData['tribeMembers']
            for tribeMemberID in tribeMembers:
                tribeMember = Find.Player(tribeMemberID)
                if tribeMember or (tribeMember in self.flaggedPlayers):
                    return True
                else:
                    return False
        else:
            player.Message("You are a Ronin")
            return True

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
            self.flaggedPlayers.append(player)
            fpData = Plugin.CreateDict()
            fpData['SteamID'] = player.SteamID

            Plugin.CreateParallelTimer("PVPFlag", self.timerLenght*1000, fpData).Start()


    def PVPFlagCallback(self, timer):
        timer.Kill()
        data = timer.Args

        playerID = data['SteamID']
        playerName = DataStore.Get("Players", plyerID)
        Util.Log('Unflaging player '+str(playerID)+playerName)
        if playerID in self.flaggedPlayers:
            self.flaggedPlayers.remove(playerID)

    def notifyPlayer(self, player):
        if player not in self.notifiedPlayers:
            self.notifiedPlayers.append(player)
            pData = Plugin.CreateDict()
            pData['player'] = player

            Plugin.CreateParallelTimer('notify', self.nofityTimer*1000, pData).Start()

    def notifyCallback(self, timer):
        timer.Kill()
        data = timer.args

        player = data['player']
        self.notifiedPlayers.remove(player)

    def checkPVPFlag(self, playerID):
        if playerID in self.flaggedPlayers:
            return True
        else:
            return False

    def protectForOffline(self, playerID):
        '''
        Turns of protection for players that war offline for more then 24 hours

        :param player:
        :return: bool
        '''
        playerData = DataStore.Get('Players', playerID)
        Util.Log('PlayerID'+ str(DataStore.Get('Players', playerID)))
        Util.Log("lastonline"+ str(playerData['lastonline']))


        #if time player is online is greater then offline protect timer, stop prottecting
        if (time.time() - playerData['lastonline']) > self.offlineProtectionTimeout:
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
                player.MessageFrom("AOR", "You are flagged, your buildings won't be protected if you go offline until you're flagged!")
            else:
                player.MessageFrom("AOR", "You are not flagged")

        if command == 'aor':
            player.Message("Antiraid system works in the following way:")
            player.Message("When you go offline, your buildings are protected for 24 hours from player damage.")
            player.Message("If you attack or someone attacks you or your buildings, you'll be flagged for 15 minutes.")
            player.Message("If you're flagged for pvp, and you log off, your buildings will not be protected for the next 15 minutes.")
            player.Message("Type /flag to see if you are flagged.")


