# Offline Protection mod for Rust 

## This mod was made for the Rust server I was administrating as part of CroHQ Gaming community project.

## Features:

clan system, limited to 5 members (Tribes)

* shared doors (handled by SteamID)

* offline protection that lasts 24 hours

* double the crafting speed when in cupboard radius with building privilege

* UI for Tribes, Player statistics and Help

* +100% sulfur gather, +50% Wood gather

* few stacks fixes, mostly food items (10-20 per stack)


## Steam group:

CroHQ Rust TribeWars

## Brief description of the relevant plugins:

### Tribes Mechanism 
allow you to play in a bigger group.

### Offline protection Mechanism
protects your buildings for 24 hour after you log out.

### Door System
Doors are bound to your SteamID, and only you and your Tribe members can open them. There's no need for code locks, other then putting them on chests to get some privacy, if you need it, and to prevent doors to be picked up if you are caught off guard and killed with the doors open.


Everyone is a “Survivor” when they join the Server. No one can open your doors but you, even without the lock (handled via SteamID). If you want to share living spaces with someone, you'll have to form a Tribe.

So, buildings built by you, or anyone from your tribe, have shared doors between each member.

When you're in a tribe, protection mechanism works for the whole Tribe. That is, when at least one member is online, all buildings are vulnerable., when no one from the tribe is, all tribe member buildings are protected. 24 hour protection period lasts from the moment the last person in the tribe logged off, and applies to all tribe member buildings.

If a player engages in PVP combat and damage is dealt to him or his buildings, or they do damage to other players or their buildings, they will be flagged for PVP, and that flag lasts for 20 minutes from last aggression.

If a player disconnect while they are flagged, they will get additional timer of 20 minutes after the pvp aggression timer runs out.

So, basically, that gives raiders 20 minutes window to raid a target, it the target disconnected while flagged.

That will prevent players login off while someone is trying to raid them.

### ADDITIONAL MODIFICATIONS:

Decay damage reduced to 20% - if you have only an hour or two to play, we want to minimize the grinding for you as much as possible. Focus more on finding stuff in the world, and interaction with people, instead of repairing your base.

Sulfur gather rate increased 100% to provide player easier to obtain explosives. Experience has shown that on vanilla gather rates you can't get enough explosives to raid you own base, compared with the building materials you gather while gathering sulfur.

Wood gather rate increased by 50%

*Crafting speed doubled when crafting inside cupboard radius with building privileges. *

Double the crafting speed for all items when in cupboard radius with building privilege

There will be additional changes depending on the situations, updates and general game play breaking issues. We will always try to “balance" the "Vanilla" type server, thus modifying the game to be more of a survival type game, then anything else.
