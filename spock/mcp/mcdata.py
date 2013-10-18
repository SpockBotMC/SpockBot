#Most of the data formats, structures, and magic values

MC_PROTOCOL_VERSION = 78
SERVER_TO_CLIENT = 0x01
CLIENT_TO_SERVER = 0x02
SERVER_LIST_PING_MAGIC = 0x01

data_types = {
	"bool": ('?', 1),
	"ubyte": ('B', 1),
	"byte": ('b', 1),
	"ushort": ('H', 2),
	"short": ('h', 2),
	"uint": ('I', 4),
	"int": ('i', 4),
	"long": ('q', 8),
	"float": ('f', 4),
	"double": ('d', 8),
}

blocks = {
	0x00: "Air",
	0x01: "Stone",
	0x02: "Grass Block",
	0x03: "Dirt",
	0x04: "Cobblestone",
	0x05: "Wooden Planks",
	0x06: "Sapling",
	0x07: "Bedrock",
	0x08: "Water",
	0x09: "Stationary Water",
	0x0A: "Lava",
	0x0B: "Stationary Lava",
	0x0C: "Sand",
	0x0D: "Gravel",
	0x0E: "Gold Ore",
	0x0F: "Iron Ore",
	0x10: "Coal Ore",
	0x11: "Wood",
	0x12: "Leaves",
	0x13: "Sponge",
	0x14: "Glass",
	0x15: "Lapis Lazuli Ore",
	0x16: "Lapis Lazuli Block",
	0x17: "Dispenser",
	0x18: "Sandstone",
	0x19: "Note Block",
	0x1A: "Bed",
	0x1B: "Powered Rail",
	0x1C: "Detector Rail",
	0x1D: "Sticky Piston",
	0x1E: "Cobweb",
	0x1F: "Tall Grass",
	0x20: "Dead Bush",
	0x21: "Piston",
	0x22: "Pison Extension",
	0x23: "Wool",
	0x24: "Piston Move Block",
	0x25: "Dandelion",
	0x26: "Rose",
	0x27: "Brown Mushroom",
	0x28: "Red Mushroom",
	0x29: "Gold Block",
	0x2A: "Iron Block",
	0x2B: "Double Stone Slab",
	0x2C: "Stone Slab",
	0x2D: "Bricks",
	0x2E: "TNT",
	0x2F: "Bookshelf",
	0x30: "Moss Stone",
	0x31: "Obsidian",
	0x32: "Torch",
	0x33: "Fire",
	0x34: "Monster Spawner",
	0x35: "Oak Wood Stairs",
	0x36: "Chest",
	0x37: "Redstone Wire",
	0x38: "Diamond Ore",
	0x39: "Diamond Block",
	0x3A: "Crafting Table",
	0x3B: "Wheat",
	0x3C: "Farmland",
	0x3D: "Furnace",
	0x3E: "Burning Furnace",
	0x3F: "Sign Post",
	0x40: "Wood Door",
	0x41: "Ladder",
	0x42: "Rail",
	0x43: "Cobblestone Stairs",
	0x44: "Wall Sign",
	0x45: "Lever",
	0x46: "Stone Pressure Plate",
	0x47: "Iron Door",
	0x48: "Wood Pressure Plate",
	0x49: "Redstone Ore",
	0x4A: "Glowing Redstone Ore",
	0x4B: "Redstone Torch (Off)",
	0x4C: "Redstone Torch (On)",
	0x4D: "Stone Button",
	0x4E: "Snow",
	0x4F: "Ice",
	0x50: "Snow Block",
	0x51: "Cactus",
	0x52: "Clay Block",
	0x53: "Sugar Cane",
	0x54: "Jukebox",
	0x55: "Fence",
	0x56: "Pumpkin",
	0x57: "Netherrack",
	0x58: "Soul Sand",
	0x59: "Glowstone Block",
	0x5A: "Nether Portal",
	0x5B: "Jack 'o' Lantern",
	0x5C: "Cake Block",
	0x5D: "Redstone Repeater (Off)",
	0x5E: "Redstone Repeater (On)",
	0x5F: "Locked Chest", #If only this were a real thing
	0x60: "Trapdoor",
	0x61: "Monster Egg",
	0x62: "Stone Bricks",
	0x63: "Huge Brown Mushroom",
	0x64: "Huge Red Mushroom",
	0x65: "Iron Bars",
	0x66: "Glass Pane",
	0x67: "Melon",
	0x68: "Pumpkin Stem",
	0x69: "Melon Stem",
	0x6A: "Vines",
	0x6B: "Fence Gate",
	0x6C: "Brick Stairs",
	0x6D: "Stone Brick Stairs",
	0x6E: "Mycelium",
	0x6F: "Lily Pad",
	0x70: "Nether Brick",
	0x71: "Nether Brick Fence",
	0x72: "Nether Brick Stairs",
	0x73: "Nether Wart",
	0x74: "Enchantment Table",
	0x75: "Brewing Stand",
	0x76: "Cauldron",
	0x77: "End Portal",
	0x78: "End Portal Frame",
	0x79: "End Stone",
	0x7A: "Dragon Egg",
	0x7B: "Redstone Lamp (Off)",
	0x7C: "Redstone Lamp (On)",
	0x7D: "Wood Double Slab",
	0x7E: "Wood Slab",
	0x7F: "Cocoa Pod",
	0x80: "Sandstone Stairs",
	0x81: "Emerald Ore",
	0x82: "Ender Chest",
	0x83: "Tripwire Hook",
	0x84: "Tripwire",
	0x85: "Emerald Block",
	0x86: "Spruce Wood Stairs",
	0x87: "Brich Wood Stairs",
	0x88: "Jungle Wood Stairs",
	0x89: "Command Block",
	0x8A: "Beacon",
	0x8B: "Cobblestone Wall",
	0x8C: "Flower Pot",
	0x8D: "Carrots",
	0x8E: "Potatoes",
	0x8F: "Wood Button",
	0x90: "Mob Head",
	0x91: "Anvil",
	0x92: "Trapped Chest",
	0x93: "Weighted Plate (Light)",
	0x94: "Weighted Plate (Heavy)",
	0x95: "Redstone Comparator (Off)",
	0x96: "Redstone Comparator (On)",
	0x97: "Daylight Sensor",
	0x98: "Redstone Block",
	0x99: "Nether Quartz Ore",
	0x9A: "Hopper",
	0x9B: "Quartz Block",
	0x9C: "Quartz Stairs",
	0x9D: "Activator Rail",
	0x9E: "Dropper",
}

names = {
	0x00: "Keep Alive",
	0x01: "Login Request",
	0x02: "Handshake",
	0x03: "Chat Message",
	0x04: "Time Update",
	0x05: "Entity Equipment",
	0x06: "Spawn Position",
	0x07: "Use Entity",
	0x08: "Update Health",
	0x09: "Respawn",
	0x0A: "Player",
	0x0B: "Player Position",
	0x0C: "Player Look",
	0x0D: "Player Position and Look",
	0x0E: "Player Digging",
	0x0F: "Player Block Placement",
	0x10: "Held Item Change",
	0x11: "Use Bed",
	0x12: "Animation",
	0x13: "Entity Action",
	0x14: "Spawn Named Entity",
	0x16: "Collect item",
	0x17: "Spawn Object/Vehicle",
	0x18: "Spawn Mob",
	0x19: "Spawn Painting",
	0x1A: "Spawn Experience Orb",
	0x1B: "Steer Vehicle",
	0x1C: "Entity Velocity",
	0x1D: "Destroy Entity",
	0x1E: "Entity",
	0x1F: "Entity Relative Move",
	0x20: "Entity Look",
	0x21: "Entity Look And Relative Move",
	0x22: "Entity Teleport",
	0x23: "Entity Head Look",
	0x26: "Entity Status",
	0x27: "Attach Entity",
	0x28: "Entity Metadata",
	0x29: "Entity Effect",
	0x2A: "Remove Entity Effect",
	0x2B: "Set Experience",
	0x2C: "Entity Properties",
	0x33: "Chunk Data",
	0x34: "Multi Block Change",
	0x35: "Block Change",
	0x36: "Block Action",
	0x37: "Block Break Animation",
	0x38: "Map Chunk Bulk",
	0x3C: "Explosion",
	0x3D: "Sound Or Particle Effect",
	0x3E: "Named Sound Effect",
	0x3F: "Particle",
	0x46: "Changed Game State",
	0x47: "Global Entity",
	0x64: "Open Window",
	0x65: "Close Window",
	0x66: "Click Window",
	0x67: "Set Slot",
	0x68: "Set Window Items",
	0x69: "Update Window Property",
	0x6A: "Confirm Transaction",
	0x6B: "Creative Inventory Action",
	0x6C: "Enchant Item",
	0x82: "Update Sign",
	0x83: "Item Data",
	0x84: "Update Tile Entity",
	0x85: "Tile Editor Open",
	0xC8: "Increment Statistic",
	0xC9: "Player List Item",
	0xCA: "Player Abilities",
	0xCB: "Tab-complete",
	0xCC: "Client Settings",
	0xCD: "Client Statuses",
	0xCE: "Create Scoreboard",
	0xCF: "Update Score",
	0xD0: "Display Scoreboard",
	0xD1: "Teams",
	0xFA: "Plugin Message",
	0xFC: "Encryption Key Response",
	0xFD: "Encryption Key Request",
	0xFE: "Server List Ping",
	0xFF: "Disconnect",
}

structs = {
	#Keep-alive
	0x00: ("int", "value"),
	#Login request
	0x01: (
			("int", "entity_id"),
			("string", "level_type"),
			("byte", "game_mode"),
			("byte", "dimension"),
			("byte", "difficulty"),
			("byte", "not_used"),
			("ubyte", "max_players")),
	#Handshake
	0x02: (
		("byte", "protocol_version"),
		("string", "username"),
		("string", "host"),
		("int", "port")),
	#Chat message
	0x03: ("string", "text"),
	#Time update
	0x04: (
		("long", "world_age"),
		("long", "time_of_day")),
	#Entity Equipment
	0x05: (
		("int", "entity_id"),
		("short", "slot"),
		("slot", "item")),
	#Spawn position
	0x06: (
		("int", "x"),
		("int", "y"),
		("int", "z")),
	#Use entity
	0x07: (
		("int", "subject_entity_id"),
		("int", "object_entity_id"),
		("bool", "left_click")),
	#Update health
	0x08: (
		("float", "health"),
		("short", "food"),
		("float", "food_saturation")),
	#Respawn
	0x09: (
		("int", "dimension"),
		("byte", "difficulty"),
		("byte", "game_mode"),
		("short", "world_height"),
		("string", "level_type")),
	#Player
	0x0A: ("bool", "on_ground"),
	#Player position
	0x0B: (
		("double", "x"),
		("double", "y"),
		("double", "stance"),
		("double", "z"),
		("bool", "on_ground")),
	#Player look
	0x0C: (
		("float", "yaw"),
		("float", "pitch"),
		("bool", "on_ground")),
	#Player position & look
	0x0D:	{
		CLIENT_TO_SERVER: (
			("double", "x"),
			("double", "y"),
			("double", "stance"),
			("double", "z"),
			("float", "yaw"),
			("float", "pitch"),
			("bool", "on_ground")),
		SERVER_TO_CLIENT: (
			("double", "x"),
			("double", "stance"),
			("double", "y"),
			("double", "z"),
			("float", "yaw"),
			("float", "pitch"),
			("bool", "on_ground"))},
	#Player digging
	0x0E: (
		("byte", "status"),
		("int", "x"),
		("ubyte", "y"),
		("int", "z"),
		("byte", "face")),
	#Player block placement
	0x0F: (
		("int", "x"),
		("ubyte", "y"),
		("int", "z"),
		("byte", "direction"),
		("slot", "slot"),
		("byte", "cursor_x"),
		("byte", "cursor_y"),
		("byte", "cursor_z")),
	#Holding change
	0x10: ("short", "slot"),
	#Use bed
	0x11: (
		("int", "entity_id"),
		("byte", "in_bed"),
		("int", "x"),
		("ubyte", "y"),
		("int", "z")),
	#Animation
	0x12: (
		("int", "entity_id"),
		("byte", "animation")),
	#Entity action
	0x13: (
		("int", "entity_id"),
		("byte", "action"),
		("int", "jump_boost")),
	#Spawn Named Entity
	0x14: (
		("int", "entity_id"),
		("string", "player_name"),
		("int", "x"),
		("int", "y"),
		("int", "z"),
		("byte", "rotation"),
		("byte", "pitch"),
		("short", "current_item"),
		("metadata", "metadata")),
	#Collect item
	0x16: (
		("int", "subject_entity_id"),
		("int", "object_entity_id")),
	#Spawn Object/Vehicle
	0x17: (
		("int", "entity_id"),
		("byte", "type"),
		("int", "x"),
		("int", "y"),
		("int", "z"),
		("byte", "yaw"),
		("byte", "pitch"),
		("int", "object_data"),
		),
	#Spawn Mob
	0x18: (
		("int", "entity_id"),
		("byte", "type"),
		("int", "x"),
		("int", "y"),
		("int", "z"),
		("byte", "yaw"),
		("byte", "pitch"),
		("byte", "head_yaw"),
		("short", "velocity_z"),
		("short", "velocity_y"),
		("short", "velocity_x"),
		("metadata", "metadata")),
	#Spawn Painting
	0x19: (
		("int", "entity_id"),
		("string", "title"),
		("int", "x"),
		("int", "y"),
		("int", "z"), 
		("int", "direction")),
	#Spawn Experience Orb
	0x1A: (
		("int", "entity_id"),
		("int", "x"),
		("int", "y"),
		("int", "z"),
		("short", "count")),
	#Steer Vehicle
	0x1B: (
		("float", "sideways"),
		("float", "forward"),
		("bool", "jump"),
		("bool", "unmount")),
	#Entity Velocity
	0x1C: (
		("int", "entity_id"),
		("short", "x_velocity"),
		("short", "y_velocity"),
		("short", "z_velocity")),
	#Destroy Entity
	0x1D: ("byte", "data_size"),	  
	#Entity
	0x1E: ("int", "entity_id"),
	#Entity Relative Move
	0x1F: (
		("int", "entity_id"),
		("byte", "x_change"),
		("byte", "y_change"),
		("byte", "z_change")),
	#Entity Look
	0x20: (
		("int", "entity_id"),
		("byte", "yaw"),
		("byte", "pitch")),
	#Entity Look and Relative Move
	0x21: (
		("int", "entity_id"),
		("byte", "x_change"),
		("byte", "y_change"),
		("byte", "z_change"),
		("byte", "yaw"),
		("byte", "pitch")),
	#Entity Teleport
	0x22: (
		("int", "entity_id"),
		("int", "x"),
		("int", "y"),
		("int", "z"),
		("byte", "yaw"),
		("byte", "pitch")),
	#Entity Head Look
	0x23: (
		("int", "entity_id"),
		("byte", "head_yaw")),
	#Entity Status
	0x26: (
		("int", "entity_id"),
		("byte", "status")),
	#Attach Entity
	0x27: (
		("int", "entity_id"),
		("int", "vehicle_id"),
		("ubyte", "leash")),
	#Entity Metadata
	0x28: (
		("int", "entity_id"),
		("metadata", "metadata")),
	#Entity Effect
	0x29: (
		("int", "entity_id"),
		("byte", "effect_id"),
		("byte", "amplifier"),
		("short", "duration")),
	#Remove Entity Effect
	0x2A: (
		("int", "entity_id"),
		("byte", "effect_id")),
	#Set Experience
	0x2B: (
		("float", "experience_bar"),
		("short", "level"),
		("short", "total_experience")),
	#Entity Properties
	0x2C: (
		("int", "entity_id"),
		("int", "property_count")),
	#Chunk Data
	0x33: (
		("int", "x_chunk"),
		("int", "z_chunk"),
		("bool", "ground_up_continuous"),
		("ushort", "primary_bitmap"),
		("ushort", "secondary_bitmap"),
		("int", "data_size")),
	#Multi Block Change
	0x34: (
		("int", "x_chunk"),
		("int", "z_chunk"),
		("short", "record_count"),
		("int", "data_size")),
	#Block Change
	0x35: (
		("int", "x"),
		("ubyte", "y"),
		("int", "z"),
		("short", "block_id"),
		("byte", "metadata")),
	#Block Action
	0x36: (
		("int", "x"),
		("short", "y"),
		("int", "z"),
		("byte", "byte_1"),
		("byte", "byte_2"),
		("short", "block_id")),
	#Block Break Animation
	0x37: (
		("int", "entity_id"),
		("int", "x"),
		("int", "y"),
		("int", "z"),
		("byte", "destroy_stage")),
	#Map Chunk Bulk
	0x38: (
		("short", "chunk_column_count"),
		("int", "data_size"),
		("bool", "sky_light")),
	#Explosion
	0x3C: (
		("double", "x"),
		("double", "y"),
		("double", "z"),
		("float", "radius"),
		("int", "record_count")),
	#Sound or Particle Effect
	0x3D: (
		("int", "effect_id"),
		("int", "x"),
		("ubyte", "y"),
		("int", "z"),
		("int", "extra"),
		("bool", "relative_volume")),
	#Named Sound Effect
	0x3E: (
		("string", "sound_name"),
		("int", "x"),
		("int", "y"),
		("int", "z"),
		("float", "volume"),
		("byte", "pitch")),
	#Particle
	0x3F: (
		("string", "particle_name"),
		("float", "x"),
		("float", "y"),
		("float", "z"),
		("float", "offset_x"),
		("float", "offset_y"),
		("float", "offset_z"),
		("float", "particle_speed"),
		("int", "number")),
	#Change Game State
	0x46: (
		("byte", "reason"),
		("byte", "game_mode")),
	#Spawn Global Entity
	0x47: (
		("int", "entity_id"),
		("byte", "type"),
		("int", "x"),
		("int", "y"),
		("int", "z")),
	#Open Window
	0x64: (
		("byte", "window_id"),
		("byte", "inventory_type"),
		("string", "window_title"),
		("byte", "slot_count"),
		("bool", "use_title"),
		("int", "entity_id")),
	#Close Window
	0x65: ("byte", "window_id"),
	#Click Window
	0x66: (
		("byte", "window_id"),
		("short", "slot"),
		("byte", "mouse_button"),
		("short", "transaction_id"),
		("bool", "shift"),
		("slot", "slot_data")),
	#Set Slot
	0x67: (
		("byte", "window_id"),
		("short", "slot"),
		("slot", "slot_data")),
	#Set Window Items
	0x68: (
		("byte", "window_id"),
		("short", "data_size")),
	#Update Window Property
	0x69: (
		("byte", "window_id"),
		("short", "property"),
		("short", "value")),
	#Confirm Transaction
	0x6A: (
		("byte", "window_id"),
		("short", "transaction_id"),
		("bool", "accepted")),
	#Creative Inventory Action
	0x6B: (
		("short", "slot"),
		("slot", "slot_data")),
	#Enchant Item
	0x6C: (
		("byte", "window_id"),
		("byte", "enchantment")),
	#Update Sign
	0x82: (
		("int", "x"),
		("short", "y"),
		("int", "z"),
		("string", "line_1"),
		("string", "line_2"),
		("string", "line_3"),
		("string", "line_4")),
	#Item Data
	0x83: (
		("short", "item_type"),
		("short", "item_id"),
		("short", "data_size")),
	#Update Tile Entity
	0x84: (
		("int", "x"),
		("short", "y"),
		("int", "z"),
		("byte", "action"),
		("short", "data_size")),
	#Tile Editor Open
	#Purpose unkown, set on sign placement
	0x85: (
		("byte", "tile_entity_id"),
		("int", "x"),
		("int", "y"),
		("int", "z")),
	#Increment Statistic
	0xC8: (
		("int", "statistic_id"),
		("int", "amount")),
	#Player List Item
	0xC9: (
		("string", "player_name"),
		("bool", "online"),
		("short", "ping")),
	#Player Abilities
	0xCA: (
		("ubyte", "flags"),
		("float", "flying_speed"),
		("float", "walking_speed")),
	#Tab-Complete
	0xCB: ("string", "text"),
	#Client Settings
	0xCC: (
		("string", "locale"),
		("byte", "view_distance"),
		("byte", "chat_flags"),
		("byte", "difficulty"),
		("bool", "show_cape")),
	#Client Status
	0xCD: ("byte", "payload"),
	#Create Scoreboard
	0xCE: (
		("string", "name"),
		("string", "text"),
		("byte", "create")),
	#Update Score
	0xCF: (
		("string", "item_name"),
		("byte", "update"),
		("string", "score_name"),
		("int", "value")),
	#Display Scoreboard
	0xD0: (
		("byte", "position"),
		("string", "score_name")),
	#Teams
	0xD1: (
		("string", "team_name"),
		("byte", "mode")),
	#Plugin message
	0xFA: (
		("string", "channel"),
		("short", "data_size")),
	#Encryption Response
	0xFC: (), #Covered entirely in extensions
	#Encryption Request
	0xFD: ("string", "server_id"),
	#Server List Ping
	0xFE: ("ubyte", "magic"),
	#Disconnect
	0xFF: ("string", "reason")
}


#Normalize data structures
for key, val in structs.items():
	if isinstance(val, dict):
		for k in (SERVER_TO_CLIENT, CLIENT_TO_SERVER):
			if len(val[k]) and not isinstance(val[k][0], tuple):
				structs[key][k] = (val[k],)
		continue
	elif len(val) and not isinstance(val[0], tuple):
		val = (val,)
	val = {
		CLIENT_TO_SERVER: val,
		SERVER_TO_CLIENT: val}
	structs[key] = val