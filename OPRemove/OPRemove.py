__author__ = 'Pan Devas'
__version__ = '1.0'

import clr
clr.AddReferenceByPartialName("Pluton.Core", "Pluton.Rust")
import Pluton.Core
import Pluton.Rust
import time

class OPRemove():
    def On_PluginInit(self):
        DataStore.Add('lastRemove', 'system', time.time())
        self.remove = []

    def checkPVPFlag(self, playerID):
        if playerID in DataStore.Keys('pvpFlags'):
            return True
        else:
            return False

    def checkLastRemove(self, player):
        if player.SteamID in DataStore.Keys('lastRemove'):
            playerID = player.SteamID
            lastRemove = (time.time() - DataStore.Get('lastRemove', playerID))/60
            if lastRemove <= 3600:
                player.Message("You removed your last object " + lastRemove + ' seconds ago.')
                return False
            else:
                return True
        else:
            return True

    def On_CombatEntityHurt(self, HurtEvent):
        '''
        :param CombatEntityHurtEvent:
        :return:
        Detects if building part was damaged and get its location and owner
        '''
        attacker = HurtEvent.Attacker
        victimLocation = str(HurtEvent.Victim.Location)
        victimID = str(he.Victim.baseEntity.OwnerID)

        if attacker and attacker.IsPlayer() and attacker.SteamID in self.remove:
            if self.checkPVPFlag(attacker.SteamID):
                attacker.Message("You can't remove any building parts while flaged!")
            elif not self.checkLastRemove(attacker):
                attacker.Message("You can remove one object awery 3600 seconds!")
            elif attacker.SteamID != victimID:
                attacker.Message("You can only remove objects that you placed yourself!")
            elif HurtEvent.Victim.IsBuildingPart() and attacker.SteamID == victimID:
                HurtEvent.Victim.Kill()
                HurtEvent.Weapon.Kill()
                attacker.Message("You succesfully removed a building part. You damaged your tool in the process.")
            player.Message("Remove OFF")
            self.remove.remove(player.SteamID)
        #Server.Broadcast(hurtEntity)


    def On_Command(self, cce):
        player = cce.User

        if cce.cmd == 'remove':
            if player.SteamID not in DataStore.
            if player.SteamID not in self.remove:
                player.Message("Remove ON, use a pickaxe to remove a building block")
                self.remove.append(player.SteamID)
            else:
                player.Message("Remove OFF")
                self.remove.remove(player.SteamID)