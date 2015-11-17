__author__ = 'PanDevas'
__version__ = '1.2'

import clr

clr.AddReferenceByPartialName("Pluton")
import Pluton


class TribesStatistics():

    def On_PluginInit(self):
        '''
        self.playerData = {'name': self.playerName,
                        'tribe': self.playerTribe,
                        'tribeRank': self.playerTribeRank,
                        'pendingInvites' : [],
                        'lastonline': 0,
                        'timeonline': 0,
                        'PVPstatistics': {'kills': 0, 'deaths': 0, 'suicides': 0, 'max_range': 0, 'headshots': 0},
                        'ResStatistics': 0
                        'killedBy': {playerID: 0},
                        'killed': {playerID: 0},
                        'WeaponKills': {'weapon_name':0}
                        }
        '''
        pass

    def On_PlayerDied(self, pde):
        attacker = pde.Attacker
        victim = pde.Victim

        if attacker and victim and attacker != victim:
            if attacker.IsPlayer():
                attackerData = DataStore.Get("Players", attacker.SteamID)
                victimData = DataStore.Get("Players", victim.SteamID)
                distance = round(Util.GetVectorsDistance(attacker.Location, victim.Location), 2)
                if victim:
                    Server.Broadcast(attacker.Name+ " killed " + victim.Name + " using "+ str(pde.Weapon.Name) + ", with a hit to " + pde.HitBone+ " from "+str(distance)+" meters.")
                attackerData['PVPstatistics']['kills'] +=1
                victimData['PVPstatistics']['deaths'] += 1

                # update distance
                if attackerData['PVPstatistics']['max_range'] < distance:
                    attackerData['PVPstatistics']['max_range'] = distance

                # update attacker killed list
                Util.Log("attacker killed "+attackerData['name'])
                if victim.SteamID in attackerData['killed'].keys():
                    attackerData['killed'][victim.SteamID] +=1
                else:
                    attackerData['killed'][victim.SteamID] = 1

                # update victim killedby dict
                if attacker.SteamID in victimData['killedBy'].keys():
                    victimData['killedBy'][attacker.SteamID] += 1
                else:
                    victimData['killedBy'][attacker.SteamID] = 1
                # update attacker weapon use dict
                if pde.Weapon.Name in attackerData['WeaponKills'].keys():
                    attackerData['WeaponKills'][pde.Weapon.Name] += 1
                else:
                    attackerData['WeaponKills'][pde.Weapon.Name] = 1

            else:
                victimData = DataStore.Get("Players", victim.SteamID)
                name = str(attacker.Name.split('/')[-1].split('.')[0])
                Server.Broadcast(victim.Name + " was killed by " + name)
                victimData['PVPstatistics']['deaths'] += 1

        else:
            victimData = DataStore.Get("Players", victim.SteamID)
            Server.Broadcast(victim.Name + " died from " + str(pde.DamageType))
            victimData['PVPstatistics']['deaths'] +=  1
            if str(pde.DamageType) == 'Suicide':
                victimData['PVPstatistics']['suicides'] += 1


    # ResStatistics
    def On_PlayerGathering(self, ge):
        playerID = ge.Gatherer.SteamID
        gatherAmount = ge.Amount

        playerData = DataStore.Get("Players", playerID)
        if 'ResStatistics' not in playerData.keys():
            playerData['ResStatistics'] = 0
        playerData['ResStatistics'] += gatherAmount



    def On_Command(self, cmd):
        command = cmd.cmd
        player = cmd.User

        if command == 'stats':
            playerD = DataStore.Get('Players', cmd.User.SteamID)
            for key in playerD.keys():
                player.Message(str(key)+' '+str(playerD[key]))
