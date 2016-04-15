__author__ = 'Pan Devas'
__version__ = '1.0'

import clr
clr.AddReferenceByPartialName("Pluton.Core", "Pluton.Rust")
import Pluton.Core
import Pluton.Rust
import time

class OPRemove():
    def On_PluginInit(self):
        Commands.Register('remove').setCallback('removePart')
        DataStore.Add('lastRemove', 'system', time.time())
        self.removableItems = ("SimpleBuildingBlock", 'BuildingBlock', 'StabilityEntity')
        self.remove = []

    def checkPVPFlag(self, player):
        if player.GameID in DataStore.Keys('pvpFlags'):
            return True
        else:
            return False

    def checkLastRemove(self, player):
        if player.GameID in DataStore.Keys('lastRemove'):
            playerID = player.GameID
            lastRemove = (time.time() - DataStore.Get('lastRemove', playerID))
            if lastRemove <= 3600:
                player.Message("You can use remove in " + str(round(3600 - lastRemove, 1)) + ' seconds.')
                return False
            else:
                return True
        else:
            return True

    def On_BeingHammered(self, HurtEvent):
        '''
        :param CombatEntityHurtEvent:
        :return:
        Detects if building part was damaged and get its location and owner
        '''
        attacker = HurtEvent.Player
        victimLocation = str(HurtEvent.Victim.Location)
        victimID = HurtEvent.Victim.baseEntity.OwnerID
        hurtEntity = HurtEvent.Victim.baseEntity.GetType().ToString()

        if attacker and attacker.IsPlayer() and attacker.GameID in self.remove and hurtEntity in self.removableItems:
            if self.checkPVPFlag(attacker):
                attacker.Message("You can't remove any building parts while flaged!")
            elif not self.checkLastRemove(attacker):
                attacker.Message("You can remove one object every 3600 seconds!")
            elif attacker.GameID != victimID:
                attacker.Message("You can only remove objects that you placed yourself!")
            elif attacker.GameID == victimID:
                if not attacker.basePlayer.HasPlayerFlag(attacker.basePlayer.PlayerFlags.HasBuildingPrivilege):
                    attacker.Message("You need to have building permisions to remove the building part!")
                else:
                    HurtEvent.Victim.Kill()
                    attacker.Message("You succesfully removed a building part. Remove is turned OFF.")
                    DataStore.Add('lastRemove', attacker.GameID, time.time())
            self.remove.remove(attacker.GameID)

    def removePart(self, Args, Player):
        Util.Log('REMOVE')
        if Player.GameID not in self.remove:
            Player.Message("Remove ON, hit a building part with a hammer to destroy it.")
            self.remove.append(Player.GameID)
        else:
            Player.Message("Remove OFF")
            self.remove.remove(Player.GameID)