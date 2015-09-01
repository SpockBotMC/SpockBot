"""
These constants are used in some plugins, but do not belong there.
Some of them can later be extracted from minecraft-data
"""

###########
# PHYSICS #
###########

CLIENT_TICK_RATE = 0.05
PLAYER_HEIGHT = 1.74

# Gravitational constants defined in blocks/(client tick)^2
PLAYER_ENTITY_GAV = 0.08
THROWN_ENTITY_GAV = 0.03
RIDING_ENTITY_GAV = 0.04
BLOCK_ENTITY_GAV = 0.04
ARROW_ENTITY_GAV = 0.05

# Air drag constants defined in 1/tick
PLAYER_ENTITY_DRG = 0.02
THROWN_ENTITY_DRG = 0.01
RIDING_ENTITY_DRG = 0.05
BLOCK_ENTITY_DRG = 0.02
ARROW_ENTITY_DRG = 0.01

# Player ground acceleration isn't actually linear, but we're going to pretend
# that it is. Max ground velocity for a walking client is 0.215blocks/tick, it
# takes a dozen or so ticks to get close to max velocity. Sprint is 0.28, just
# apply more acceleration to reach a higher max ground velocity
PLAYER_WLK_ACC = 0.15
PLAYER_SPR_ACC = 0.20
PLAYER_GND_DRG = 0.41

# Seems about right, not based on anything
PLAYER_JMP_ACC = 0.45

############
# INTERACT #
############

INTERACT_ENTITY = 0
ATTACK_ENTITY = 1
INTERACT_ENTITY_AT = 2

ENTITY_ACTION_SNEAK = 0
ENTITY_ACTION_UNSNEAK = 1
ENTITY_ACTION_LEAVE_BED = 2
ENTITY_ACTION_START_SPRINT = 3
ENTITY_ACTION_STOP_SPRINT = 4
ENTITY_ACTION_JUMP_HORSE = 5
ENTITY_ACTION_OPEN_INVENTORY = 6

# the six faces of a block
FACE_Y_NEG = 0
FACE_Y_POS = 1
FACE_Z_NEG = 2
FACE_Z_POS = 3
FACE_X_NEG = 4
FACE_X_POS = 5

DIG_START = 0
DIG_CANCEL = 1
DIG_FINISH = 2
DIG_DROP_STACK = 3
DIG_DROP_ITEM = 4
DIG_DEACTIVATE_ITEM = 5

#############
# INVENTORY #
#############

# the button codes used in send_click
INV_BUTTON_LEFT = 0
INV_BUTTON_RIGHT = 1
INV_BUTTON_MIDDLE = 2

INV_SLOT_NR_CURSOR = -1
INV_WINID_CURSOR = -1  # the slot that follows the cursor
# player inventory window ID/type, not opened but updated by server
INV_WINID_PLAYER = 0
INV_ITEMID_EMPTY = -1

INV_SLOTS_PLAYER = 9  # crafting and armor
INV_SLOTS_INVENTORY = 9 * 3  # above hotbar
INV_SLOTS_HOTBAR = 9
# always accessible
INV_SLOTS_PERSISTENT = INV_SLOTS_INVENTORY + INV_SLOTS_HOTBAR
