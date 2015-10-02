"""
These constants are used in some plugins, but do not belong there.
Some of them can later be extracted from minecraft-data
"""

###########
# PHYSICS #
###########

CLIENT_TICK_RATE = 0.05
PLAYER_HEIGHT = 1.80
PLAYER_WIDTH = 0.6

# These values are strictly for player and maybe mob physics, different types
# of entities have different drag coefficients and gravitational accelerations
# Someone who isn't nickelpro can go do all the other possible values if they
# want

PHY_GAV_ACC = 0.08
PHY_WLK_ACC = 0.10
PHY_FLY_ACC = 0.05
PHY_JMP_ACC = 0.02

PHY_JMP_ABS = 0.42

PHY_SOULSAND = 0.40
PHY_BASE_DRG = 0.98

PHY_DRG_MUL = 0.91
PHY_SPR_MUL = 1.30
PHY_JMP_MUL = 0.2

# Slipperiness value for normal materials
BASE_GND_SLIP = 0.6

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

INV_OUTSIDE_WINDOW = -999
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
