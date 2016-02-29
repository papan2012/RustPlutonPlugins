__author__ = 'PanDevas'
__version__ = '1.0'

import clr
clr.AddReferenceByPartialName("Pluton.Core", "Pluton.Rust")

import Pluton.Core
import Pluton.Rust

class Sleep():

    def On_Command(self, cmd):
        command = cmd.cmd
        player = cmd.User

        if command == 'sleep':
            player.basePlayer.StartSleeping()