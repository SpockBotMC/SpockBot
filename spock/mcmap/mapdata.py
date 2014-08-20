#Shamelessly stolen/adapted from Mineflayer

biomes = {
	0: {
		'display_name': 'Ocean',
				'temperature': 0.5,
	},
	1: {
		'display_name': 'Plains',
		'temperature': 0.8,
	},
	2: {
		'display_name': 'Desert',
		'temperature': 2,
	},
	3: {
		'display_name': 'Extreme Hills',
		'temperature': 0.2,
	},
	4: {
		'display_name': 'Forest',
		'temperature': 0.7,
	},
	5: {
		'display_name': 'Taiga',
		'temperature': 0.05,
	},
	6: {
		'display_name': 'Swampland',
		'temperature': 0.8,
	},
	7: {
		'temperature': 0.5,
	},
	8: {
		'display_name': 'Hell',
		'temperature': 2,
	},
	9: {
		'display_name': 'Sky',
		'temperature': 0.5,
	},
	10: {

		'display_name': 'Frozen Ocean',
		'temperature': 0,
	},
	11: {

		'display_name': 'Frozen River',
		'temperature': 0,
	},
	12: {

		'display_name': 'Ice Plains',
		'temperature': 0,
	},
	13: {

		'display_name': 'Ice Mountains',
		'temperature': 0,
	},
	14: {

		'display_name': 'Mushroom Island',
		'temperature': 0.9,
	},
	15: {

		'display_name': 'Mushroom Island Shore',
		'temperature': 0.9,
	},
	16: {

		'display_name': 'Beach',
		'temperature': 0.8,
	},
	17: {

		'display_name': 'Desert Hills',
		'temperature': 2,
	},
	18: {

		'display_name': 'Forest Hills',
		'temperature': 0.7,
	},
	19: {

		'display_name': 'Taiga Hills',
		'temperature': 0.05,
	},
	20: {

		'display_name': 'Extreme Hills Edge',
		'temperature': 0.2,
	},
	21: {

		'display_name': 'Jungle',
		'temperature': 1.2,
	},
	22: {

		'display_name': 'Jungle Hills',
		'temperature': 1.2,
	},
	23: {

		'display_name': 'Jungle Edge',
		'temperature': 0.95,
	},
	24: {

		'display_name': 'Deep Ocean',
		'temperature:': 0.5,
        },
	25: {

		'display_name': 'Stone Beach',
		'temperature:': 0.2,
	},
	26: {

		'display_name': 'Cold Beach',
		'temperature:': 0,
	},
	27: {

		'display_name': 'Birch Forest',
		'temperature:': 0.6,
	},
	28: {

		'display_name': 'Birch Forest Hills',
		'temperature:': 0.6,
	},
	29: {

		'display_name': 'Roofed Forest',
		'temperature:': 0.7,
	},
	30: {

		'display_name': 'Cold Taiga',
		'temperature:': 0,
	},
	31: {

		'display_name': 'Cold Taiga Hills',
		'temperature:': 0,
	},
	32: {

		'display_name': 'Mega Taiga',
		'temperature:': 0.3,
	},
	33: {

		'display_name': 'Mega Taiga Hills',
		'temperature:': 0.3,
	},
	34: {

		'display_name': 'Extreme Hills+',
		'temperature:': 0.2,
	},
	35: {

		'display_name': 'Savanna',
		'temperature:': 1.0,
	},
	36: {

		'display_name': 'Savanna Plateau',
		'temperature:': 1.0,
	},
	37: {

		'display_name': 'Mesa',
		'temperature:': 1.0,
	},
	38: {

		'display_name': 'Mesa Plateau F',
		'temperature:': 1.0,
	},
	39: {

		'display_name': 'Mesa Plateau',
		'temperature:': 1.0,
	},
	129: {
		'display_name': 'Sunflower Plains',
		'temperature': 0.8,
	},
}

blocks = {
	0: {
		'display_name': 'Air',
		'name': 'air',
		'hardness': 0,
		'stack_size': None,
		'diggable': False,
		'bounding_box': 'empty'
	},
	1: {
		'display_name': 'Stone',
		'name': 'stone',
		'hardness': 1.5,
		'stack_size': 64,
		'diggable': True,
		'bounding_box': 'block',
		'material': 'rock',
		'harvest_tools': (270, 274, 257, 278, 285),
	},
	2: {
		'display_name': 'Grass Block',
		'name': 'grass',
		'hardness': 0.6,
		'stack_size': 64,
		'diggable': True,
		'bounding_box': 'block',
		'material': 'dirt'
	},
	3: {
		'display_name': 'Dirt',
		'name': 'dirt',
		'hardness': 0.5,
		'stack_size': 64,
		'diggable': True,
		'bounding_box': 'block',
		'material': 'dirt'
	},
	4: {
		'display_name': 'Cobblestone',
		'name': 'stonebrick',
		'hardness': 2,
		'stack_size': 64,
		'diggable': True,
		'bounding_box': 'block',
		'material': 'rock',
		'harvest_tools': (270, 274, 257, 278, 285),
	},
	5: {
		'display_name': 'Wooden Planks',
		'name': 'wood',
		'hardness': 2,
		'stack_size': 64,
		'diggable': True,
		'bounding_box': 'block',
		'material': 'wood'
	},
	6: {
		'display_name': 'Sapling',
		'name': 'sapling',
		'hardness': 0,
		'stack_size': 64,
		'diggable': True,
		'bounding_box': 'empty'
	},
	7: {
		'display_name': 'Bedrock',
		'name': 'bedrock',
		'hardness': None,
		'stack_size': 64,
		'diggable': False,
		'bounding_box': 'block'
	},
	8: {
		'display_name': 'Water',
		'name': 'water',
		'hardness': 100,
		'stack_size': 64,
		'diggable': False,
		'bounding_box': 'empty'
	},
	9: {
		'display_name': 'Stationary Water',
		'name': 'waterStationary',
		'hardness': 100,
		'stack_size': 64,
		'diggable': False,
		'bounding_box': 'empty'
	},
	10: {
		'display_name': 'Lava',
		'name': 'lava',
		'hardness': 0,
		'stack_size': 64,
		'diggable': False,
		'bounding_box': 'empty'
	},
	11: {
		'display_name': 'Stationary Lava',
		'name': 'lavaStationary',
		'hardness': 100,
		'stack_size': 64,
		'diggable': False,
		'bounding_box': 'empty'
	},
	12: {
		'display_name': 'Sand',
		'name': 'sand',
		'hardness': 0.5,
		'stack_size': 64,
		'diggable': True,
		'bounding_box': 'block',
		'material': 'dirt'
	},
	13: {
		'display_name': 'Gravel',
		'name': 'gravel',
		'hardness': 0.6,
		'stack_size': 64,
		'diggable': True,
		'bounding_box': 'block',
		'material': 'dirt'
	},
	14: {
		'display_name': 'Gold Ore',
		'name': 'oreGold',
		'hardness': 3,
		'stack_size': 64,
		'diggable': True,
		'bounding_box': 'block',
		'material': 'rock',
		'harvest_tools': (257, 278),
	},
	15: {
		'display_name': 'Iron Ore',
		'name': 'oreIron',
		'hardness': 3,
		'stack_size': 64,
		'diggable': True,
		'bounding_box': 'block',
		'material': 'rock',
		'harvest_tools': (274, 257, 278),
	},
	16: {
		'display_name': 'Coal Ore',
		'name': 'oreCoal',
		'hardness': 3,
		'stack_size': 64,
		'diggable': True,
		'bounding_box': 'block',
		'material': 'rock',
		'harvest_tools': (270, 274, 257, 278, 285),
	},
	17: {
		'display_name': 'Wood',
		'name': 'log',
		'hardness': 2,
		'stack_size': 64,
		'diggable': True,
		'bounding_box': 'block',
		'material': 'wood'
	},
	18: {
		'display_name': 'Leaves',
		'name': 'leaves',
		'hardness': 0.2,
		'stack_size': 64,
		'diggable': True,
		'bounding_box': 'block',
		'material': 'leaves'
	},
	19: {
		'display_name': 'Sponge',
		'name': 'sponge',
		'hardness': 0.6,
		'stack_size': 64,
		'diggable': True,
		'bounding_box': 'block'
	},
	20: {
		'display_name': 'Glass',
		'name': 'glass',
		'hardness': 0.3,
		'stack_size': 64,
		'diggable': True,
		'bounding_box': 'block'
	},
	21: {
		'display_name': 'Lapis Lazuli Ore',
		'name': 'oreLapis',
		'hardness': 3,
		'stack_size': 64,
		'diggable': True,
		'bounding_box': 'block',
		'material': 'rock',
		'harvest_tools': (274, 257, 278),
	},
	22: {
		'display_name': 'Lapis Lazuli Block',
		'name': 'blockLapis',
		'hardness': 3,
		'stack_size': 64,
		'diggable': True,
		'bounding_box': 'block',
		'material': 'rock',
		'harvest_tools': (274, 257, 278),
	},
	23: {
		'display_name': 'Dispenser',
		'name': 'dispenser',
		'hardness': 3.5,
		'stack_size': 64,
		'diggable': True,
		'bounding_box': 'block',
		'material': 'rock',
		'harvest_tools': (270, 274, 257, 278, 285),
	},
	24: {
		'display_name': 'Sandstone',
		'name': 'sandStone',
		'hardness': 0.8,
		'stack_size': 64,
		'diggable': True,
		'bounding_box': 'block',
		'material': 'rock',
		'harvest_tools': (270, 274, 257, 278, 285),
	},
	25: {
		'display_name': 'Note Block',
		'name': 'musicBlock',
		'hardness': 0.8,
		'stack_size': 64,
		'diggable': True,
		'bounding_box': 'block',
		'material': 'wood'
	},
	26: {
		'display_name': 'Bed',
		'name': 'bed',
		'hardness': 0.2,
		'stack_size': 1,
		'diggable': True,
		'bounding_box': 'block'
	},
	27: {
		'display_name': 'Powered Rail',
		'name': 'goldenRail',
		'hardness': 0.7,
		'stack_size': 64,
		'diggable': True,
		'bounding_box': 'empty',
		'material': 'rock'
	},
	28: {
		'display_name': 'Detector Rail',
		'name': 'detectorRail',
		'hardness': 0.7,
		'stack_size': 64,
		'diggable': True,
		'bounding_box': 'empty',
		'material': 'rock'
	},
	29: {
		'display_name': 'Sticky Piston',
		'name': 'pistonStickyBase',
		'hardness': 0,
		'stack_size': 64,
		'diggable': True,
		'bounding_box': 'block'
	},
	30: {
		'display_name': 'Cobweb',
		'name': 'web',
		'hardness': 4,
		'stack_size': 64,
		'diggable': True,
		'bounding_box': 'empty',
		'material': 'web',
		'harvest_tools': (359, 267, 268, 272, 276, 283),
	},
	31: {
		'display_name': 'Grass',
		'name': 'tallgrass',
		'hardness': 0,
		'stack_size': 64,
		'diggable': True,
		'bounding_box': 'empty'
	},
	32: {
		'display_name': 'Dead Bush',
		'name': 'deadbush',
		'hardness': 0,
		'stack_size': 64,
		'diggable': True,
		'bounding_box': 'empty'
	},
	33: {
		'display_name': 'Piston',
		'name': 'pistonBase',
		'hardness': 0,
		'stack_size': 64,
		'diggable': True,
		'bounding_box': 'block'
	},
	34: {
		'name': 'pistonExtension',
		'display_name': 'Piston Extension',
		'hardness': 0,
		'stack_size': 64,
		'diggable': True,
		'bounding_box': 'block'
	},
	35: {
		'display_name': 'Wool',
		'name': 'cloth',
		'hardness': 0.8,
		'stack_size': 64,
		'diggable': True,
		'bounding_box': 'block',
		'material': 'wool'
	},
	36: {
		'name': 'blockMovedByPiston',
		'display_name': 'Block Moved by Piston',
		'hardness': 0,
		'stack_size': 64,
		'diggable': False,
		'bounding_box': 'block'
	},
	37: {
		'display_name': 'Flower',
		'name': 'flower',
		'hardness': 0,
		'stack_size': 64,
		'diggable': True,
		'bounding_box': 'empty'
	},
	38: {
		'display_name': 'Rose',
		'name': 'rose',
		'hardness': 0,
		'stack_size': 64,
		'diggable': True,
		'bounding_box': 'empty'
	},
	39: {
		'display_name': 'Brown Mushroom',
		'name': 'mushroomBrown',
		'hardness': 0,
		'stack_size': 64,
		'diggable': True,
		'bounding_box': 'empty'
	},
	40: {
		'display_name': 'Red Mushroom',
		'name': 'mushroomRed',
		'hardness': 0,
		'stack_size': 64,
		'diggable': True,
		'bounding_box': 'empty'
	},
	41: {
		'display_name': 'Block of Gold',
		'name': 'blockGold',
		'hardness': 3,
		'stack_size': 64,
		'diggable': True,
		'bounding_box': 'block',
		'material': 'rock',
		'harvest_tools': (257, 278),
	},
	42: {
		'display_name': 'Block of Iron',
		'name': 'blockIron',
		'hardness': 5,
		'stack_size': 64,
		'diggable': True,
		'bounding_box': 'block',
		'material': 'rock',
		'harvest_tools': (274, 257, 278),
	},
	43: {
		'display_name': 'Double Stone Slab',
		'name': 'stoneSlabDouble',
		'hardness': 2,
		'stack_size': 64,
		'diggable': True,
		'bounding_box': 'block',
		'material': 'rock',
		'harvest_tools': (270, 274, 257, 278, 285),
	},
	44: {
		'display_name': 'Stone Slab',
		'name': 'stoneSlab',
		'hardness': 2,
		'stack_size': 64,
		'diggable': True,
		'bounding_box': 'block'
	},
	45: {
		'display_name': 'Bricks',
		'name': 'brick',
		'hardness': 2,
		'stack_size': 64,
		'diggable': True,
		'bounding_box': 'block',
		'material': 'rock',
		'harvest_tools': (270, 274, 257, 278, 285),
	},
	46: {
		'display_name': 'TNT',
		'name': 'tnt',
		'hardness': 0,
		'stack_size': 64,
		'diggable': True,
		'bounding_box': 'block'
	},
	47: {
		'display_name': 'Bookshelf',
		'name': 'bookshelf',
		'hardness': 1.5,
		'stack_size': 64,
		'diggable': True,
		'bounding_box': 'block',
		'material': 'wood'
	},
	48: {
		'display_name': 'Moss Stone',
		'name': 'stoneMoss',
		'hardness': 2,
		'stack_size': 64,
		'diggable': True,
		'bounding_box': 'block',
		'material': 'rock',
		'harvest_tools': (270, 274, 257, 278, 285),
	},
	49: {
		'display_name': 'Obsidian',
		'name': 'obsidian',
		'hardness': 50,
		'stack_size': 64,
		'diggable': True,
		'bounding_box': 'block',
		'material': 'rock',
		'harvest_tools': (278,),
	},
	50: {
		'display_name': 'Torch',
		'name': 'torch',
		'hardness': 0,
		'stack_size': 64,
		'diggable': True,
		'bounding_box': 'empty'
	},
	51: {
		'display_name': 'Fire',
		'name': 'fire',
		'hardness': 0,
		'stack_size': 64,
		'diggable': True,
		'bounding_box': 'empty'
	},
	52: {
		'display_name': 'Monster Spawner',
		'name': 'mobSpawner',
		'hardness': 5,
		'stack_size': 64,
		'diggable': True,
		'bounding_box': 'block',
		'material': 'rock',
		'harvest_tools': (270, 274, 257, 278, 285),
	},
	53: {
		'display_name': 'Wooden Stairs',
		'name': 'stairsWood',
		'hardness': 0,
		'stack_size': 64,
		'diggable': True,
		'bounding_box': 'block',
		'material': 'wood'
	},
	54: {
		'display_name': 'Chest',
		'name': 'chest',
		'hardness': 2.5,
		'stack_size': 64,
		'diggable': True,
		'bounding_box': 'block',
		'material': 'wood'
	},
	55: {
		'display_name': 'Redstone Dust',
		'name': 'redstoneDust',
		'hardness': 0,
		'stack_size': 64,
		'diggable': True,
		'bounding_box': 'empty'
	},
	56: {
		'display_name': 'Diamond Ore',
		'name': 'oreDiamond',
		'hardness': 3,
		'stack_size': 64,
		'diggable': True,
		'bounding_box': 'block',
		'material': 'rock',
		'harvest_tools': (257, 278),
	},
	57: {
		'display_name': 'Block of Diamond',
		'name': 'blockDiamond',
		'hardness': 5,
		'stack_size': 64,
		'diggable': True,
		'bounding_box': 'block',
		'material': 'rock',
		'harvest_tools': (257, 278),
	},
	58: {
		'display_name': 'Crafting Table',
		'name': 'workbench',
		'hardness': 2.5,
		'stack_size': 64,
		'diggable': True,
		'bounding_box': 'block',
		'material': 'wood'
	},
	59: {
		'display_name': 'Crops',
		'name': 'crops',
		'hardness': 0,
		'stack_size': 64,
		'diggable': True,
		'bounding_box': 'empty'
	},
	60: {
		'display_name': 'Farmland',
		'name': 'farmland',
		'hardness': 0.6,
		'stack_size': 64,
		'diggable': True,
		'bounding_box': 'block',
		'material': 'dirt'
	},
	61: {
		'display_name': 'Furnace',
		'name': 'furnace',
		'hardness': 3.5,
		'stack_size': 64,
		'diggable': True,
		'bounding_box': 'block',
		'material': 'rock',
		'harvest_tools': (270, 274, 257, 278, 285),
	},
	62: {
		'display_name': 'Burning Furnace',
		'name': 'furnaceBurning',
		'hardness': 3.5,
		'stack_size': 64,
		'diggable': True,
		'bounding_box': 'block',
		'material': 'rock',
		'harvest_tools': (270, 274, 257, 278, 285),
	},
	63: {
		'display_name': 'Sign Post',
		'name': 'signPost',
		'hardness': 1,
		'stack_size': 1,
		'diggable': True,
		'bounding_box': 'empty',
		'material': 'wood'
	},
	64: {
		'display_name': 'Wooden Door',
		'name': 'doorWood',
		'hardness': 3,
		'stack_size': 1,
		'diggable': True,
		'bounding_box': 'block',
		'material': 'wood'
	},
	65: {
		'display_name': 'Ladder',
		'name': 'ladder',
		'hardness': 0.4,
		'stack_size': 64,
		'diggable': True,
		'bounding_box': 'block'
	},
	66: {
		'display_name': 'Rail',
		'name': 'rail',
		'hardness': 0.7,
		'stack_size': 64,
		'diggable': True,
		'bounding_box': 'empty',
		'material': 'rock'
	},
	67: {
		'display_name': 'Cobblestone Stairs',
		'name': 'stairsStone',
		'hardness': 0,
		'stack_size': 64,
		'diggable': True,
		'bounding_box': 'block',
		'material': 'rock',
		'harvest_tools': (270, 274, 257, 278, 285),
	},
	68: {
		'display_name': 'Wall Sign',
		'name': 'signWall',
		'hardness': 1,
		'stack_size': 1,
		'diggable': True,
		'bounding_box': 'empty'
	},
	69: {
		'display_name': 'Lever',
		'name': 'lever',
		'hardness': 0.5,
		'stack_size': 64,
		'diggable': True,
		'bounding_box': 'empty'
	},
	70: {
		'display_name': 'Stone Pressure Plate',
		'name': 'stonePressurePlate',
		'hardness': 0.5,
		'stack_size': 64,
		'diggable': True,
		'bounding_box': 'empty',
		'material': 'rock',
		'harvest_tools': (270, 274, 257, 278, 285),
	},
	71: {
		'display_name': 'Iron Door',
		'name': 'doorIron',
		'hardness': 5,
		'stack_size': 1,
		'diggable': True,
		'bounding_box': 'block',
		'material': 'rock',
		'harvest_tools': (270, 274, 257, 278, 285),
	},
	72: {
		'display_name': 'Wooden Pressure Plate',
		'name': 'woodPressurePlate',
		'hardness': 0.5,
		'stack_size': 64,
		'diggable': True,
		'bounding_box': 'empty',
		'material': 'wood'
	},
	73: {
		'display_name': 'Redstone Ore',
		'name': 'oreRedstone',
		'hardness': 3,
		'stack_size': 64,
		'diggable': True,
		'bounding_box': 'block',
		'material': 'rock',
		'harvest_tools': (257, 278),
	},
	74: {
		'display_name': 'Glowing Redstone Ore',
		'name': 'oreRedstoneGlowing',
		'hardness': 3,
		'stack_size': 64,
		'diggable': True,
		'bounding_box': 'block',
		'material': 'rock',
		'harvest_tools': (257, 278),
	},
	75: {
		'display_name': 'Redstone Torch (Inactive)',
		'name': 'notGateInactive',
		'hardness': 0,
		'stack_size': 64,
		'diggable': True,
		'bounding_box': 'empty'
	},
	76: {
		'display_name': 'Redstone Torch (Active)',
		'name': 'notGateActive',
		'hardness': 0,
		'stack_size': 64,
		'diggable': True,
		'bounding_box': 'empty'
	},
	77: {
		'display_name': 'Stone Button',
		'name': 'buttonStone',
		'hardness': 0.5,
		'stack_size': 64,
		'diggable': True,
		'bounding_box': 'empty'
	},
	78: {
		'display_name': 'Snow',
		'name': 'snow',
		'hardness': 0.1,
		'stack_size': 64,
		'diggable': True,
		'bounding_box': 'empty',
		'material': 'dirt',
		'harvest_tools': (269, 273, 256, 277, 284),
	},
	79: {
		'display_name': 'Ice',
		'name': 'ice',
		'hardness': 0.5,
		'stack_size': 64,
		'diggable': True,
		'bounding_box': 'block',
		'material': 'rock'
	},
	80: {
		'display_name': 'Snow Block',
		'name': 'snowBlock',
		'hardness': 0.2,
		'stack_size': 64,
		'diggable': True,
		'bounding_box': 'block',
		'material': 'dirt',
		'harvest_tools': (269, 273, 256, 277, 284),
	},
	81: {
		'display_name': 'Cactus',
		'name': 'cactus',
		'hardness': 0.4,
		'stack_size': 64,
		'diggable': True,
		'bounding_box': 'block'
	},
	82: {
		'display_name': 'Clay',
		'name': 'clay',
		'hardness': 0.6,
		'stack_size': 64,
		'diggable': True,
		'bounding_box': 'block',
		'material': 'dirt'
	},
	83: {
		'display_name': 'Sugar cane',
		'name': 'reeds',
		'hardness': 0,
		'stack_size': 64,
		'diggable': True,
		'bounding_box': 'empty'
	},
	84: {
		'display_name': 'Jukebox',
		'name': 'jukebox',
		'hardness': 2,
		'stack_size': 64,
		'diggable': True,
		'bounding_box': 'block',
		'material': 'wood'
	},
	85: {
		'display_name': 'Fence',
		'name': 'fence',
		'hardness': 2,
		'stack_size': 64,
		'diggable': True,
		'bounding_box': 'block',
		'material': 'wood'
	},
	86: {
		'display_name': 'Pumpkin',
		'name': 'pumpkin',
		'hardness': 1,
		'stack_size': 64,
		'diggable': True,
		'bounding_box': 'block',
		'material': 'plant'
	},
	87: {
		'display_name': 'Netherrack',
		'name': 'hellrock',
		'hardness': 0.4,
		'stack_size': 64,
		'diggable': True,
		'bounding_box': 'block',
		'material': 'rock',
		'harvest_tools': (270, 274, 257, 278, 285),
	},
	88: {
		'display_name': 'Soul Sand',
		'name': 'hellsand',
		'hardness': 0.5,
		'stack_size': 64,
		'diggable': True,
		'bounding_box': 'block',
		'material': 'dirt'
	},
	89: {
		'display_name': 'Glowstone',
		'name': 'lightgem',
		'hardness': 0.3,
		'stack_size': 64,
		'diggable': True,
		'bounding_box': 'block'
	},
	90: {
		'display_name': 'Portal',
		'name': 'portal',
		'hardness': None,
		'stack_size': 64,
		'diggable': False,
		'bounding_box': 'empty'
	},
	91: {
		'display_name': 'Jack \'o\' Lantern',
		'name': 'litpumpkin',
		'hardness': 1,
		'stack_size': 64,
		'diggable': True,
		'bounding_box': 'block',
		'material': 'plant'
	},
	92: {
		'display_name': 'Cake',
		'name': 'cake',
		'hardness': 0.5,
		'stack_size': 1,
		'diggable': True,
		'bounding_box': 'block'
	},
	93: {
		'display_name': 'Redstone Repeater (Inactive)',
		'name': 'redstoneRepeaterInactive',
		'hardness': 0,
		'stack_size': 64,
		'diggable': True,
		'bounding_box': 'block'
	},
	94: {
		'display_name': 'Redstone Repeater (Active)',
		'name': 'redstoneRepeaterActive',
		'hardness': 0,
		'stack_size': 64,
		'diggable': True,
		'bounding_box': 'block'
	},
	95: {
		'display_name': 'Locked chest',
		'name': 'lockedchest',
		'hardness': 0,
		'stack_size': 64,
		'diggable': True,
		'bounding_box': 'block'
	},
	96: {
		'display_name': 'Trapdoor',
		'name': 'trapdoor',
		'hardness': 3,
		'stack_size': 64,
		'diggable': True,
		'bounding_box': 'block',
		'material': 'wood'
	},
	97: {
		'display_name': 'Monster Egg',
		'name': 'monsterStoneEgg',
		'hardness': 0.75,
		'stack_size': 64,
		'diggable': True,
		'bounding_box': 'block'
	},
	98: {
		'display_name': 'Stone Brick',
		'name': 'stonebricksmooth',
		'hardness': 1.5,
		'stack_size': 64,
		'diggable': True,
		'bounding_box': 'block',
		'material': 'rock',
		'harvest_tools': (270, 274, 257, 278, 285),
	},
	99: {
		'display_name': 'Huge Brown Mushroom',
		'name': 'mushroomHugeBrown',
		'hardness': 0.2,
		'stack_size': 64,
		'diggable': True,
		'bounding_box': 'block',
		'material': 'wood'
	},
	100: {
		'display_name': 'Huge Red Mushroom',
		'name': 'mushroomHugeRed',
		'hardness': 0.2,
		'stack_size': 64,
		'diggable': True,
		'bounding_box': 'block',
		'material': 'wood'
	},
	101: {
		'display_name': 'Iron Bars',
		'name': 'fenceIron',
		'hardness': 5,
		'stack_size': 64,
		'diggable': True,
		'bounding_box': 'block',
		'material': 'rock',
		'harvest_tools': (270, 274, 257, 278, 285),
	},
	102: {
		'display_name': 'Glass Pane',
		'name': 'thinGlass',
		'hardness': 0.3,
		'stack_size': 64,
		'diggable': True,
		'bounding_box': 'block'
	},
	103: {
		'display_name': 'Melon',
		'name': 'melon',
		'hardness': 1,
		'stack_size': 64,
		'diggable': True,
		'bounding_box': 'block',
		'material': 'melon'
	},
	104: {
		'display_name': 'Pumpkin Stem',
		'name': 'pumpkinStem',
		'hardness': 0,
		'stack_size': 64,
		'diggable': True,
		'bounding_box': 'empty'
	},
	105: {
		'display_name': 'Melon Stem',
		'name': 'melonStem',
		'hardness': 0,
		'stack_size': 64,
		'diggable': True,
		'bounding_box': 'empty'
	},
	106: {
		'display_name': 'Vines',
		'name': 'vine',
		'hardness': 0.2,
		'stack_size': 64,
		'diggable': True,
		'bounding_box': 'empty',
		'material': 'plant'
	},
	107: {
		'display_name': 'Fence Gate',
		'name': 'fenceGate',
		'hardness': 2,
		'stack_size': 64,
		'diggable': True,
		'bounding_box': 'block',
		'material': 'wood'
	},
	108: {
		'display_name': 'Brick Stairs',
		'name': 'stairsBrick',
		'hardness': 0,
		'stack_size': 64,
		'diggable': True,
		'bounding_box': 'block',
		'material': 'rock',
		'harvest_tools': (270, 274, 257, 278, 285),
	},
	109: {
		'display_name': 'Stone Brick Stairs',
		'name': 'stairsStoneBrickSmooth',
		'hardness': 0,
		'stack_size': 64,
		'diggable': True,
		'bounding_box': 'block',
		'material': 'rock',
		'harvest_tools': (270, 274, 257, 278, 285),
	},
	110: {
		'display_name': 'Mycelium',
		'name': 'mycel',
		'hardness': 0.6,
		'stack_size': 64,
		'diggable': True,
		'bounding_box': 'block',
		'material': 'dirt'
	},
	111: {
		'display_name': 'Lily Pad',
		'name': 'waterlily',
		'hardness': 0,
		'stack_size': 64,
		'diggable': True,
		'bounding_box': 'block'
	},
	112: {
		'display_name': 'Nether Brick',
		'name': 'netherBrick',
		'hardness': 2,
		'stack_size': 64,
		'diggable': True,
		'bounding_box': 'block',
		'material': 'rock',
		'harvest_tools': (270, 274, 257, 278, 285),
	},
	113: {
		'display_name': 'Nether Brick Fence',
		'name': 'netherFence',
		'hardness': 2,
		'stack_size': 64,
		'diggable': True,
		'bounding_box': 'block',
		'material': 'rock',
		'harvest_tools': (270, 274, 257, 278, 285),
	},
	114: {
		'display_name': 'Nether Brick Stairs',
		'name': 'stairsNetherBrick',
		'hardness': 0,
		'stack_size': 64,
		'diggable': True,
		'bounding_box': 'block',
		'material': 'rock',
		'harvest_tools': (270, 274, 257, 278, 285),
	},
	115: {
		'display_name': 'Nether Wart',
		'name': 'netherStalk',
		'hardness': 0,
		'stack_size': 64,
		'diggable': True,
		'bounding_box': 'empty'
	},
	116: {
		'display_name': 'Enchantment Table',
		'name': 'enchantmentTable',
		'hardness': 5,
		'stack_size': 64,
		'diggable': True,
		'bounding_box': 'block',
		'material': 'rock',
		'harvest_tools': (270, 274, 257, 278, 285),
	},
	117: {
		'display_name': 'Brewing Stand',
		'name': 'brewingStand',
		'hardness': 0.5,
		'stack_size': 64,
		'diggable': True,
		'bounding_box': 'block',
		'material': 'rock',
		'harvest_tools': (270, 274, 257, 278, 285),
	},
	118: {
		'display_name': 'Cauldron',
		'name': 'cauldron',
		'hardness': 2,
		'stack_size': 64,
		'diggable': True,
		'bounding_box': 'block',
		'material': 'rock',
		'harvest_tools': (270, 274, 257, 278, 285),
	},
	119: {
		'name': 'endPortal',
		'display_name': 'End Portal',
		'hardness': None,
		'stack_size': 64,
		'diggable': False,
		'bounding_box': 'empty'
	},
	120: {
		'display_name': 'End Portal Frame',
		'name': 'endPortalFrame',
		'hardness': None,
		'stack_size': 64,
		'diggable': False,
		'bounding_box': 'block'
	},
	121: {
		'display_name': 'End Stone',
		'name': 'whiteStone',
		'hardness': 3,
		'stack_size': 64,
		'diggable': True,
		'bounding_box': 'block',
		'material': 'rock',
		'harvest_tools': (270, 274, 257, 278, 285),
	},
	122: {
		'display_name': 'Dragon Egg',
		'name': 'dragonEgg',
		'hardness': 3,
		'stack_size': 64,
		'diggable': True,
		'bounding_box': 'block'
	},
	123: {
		'display_name': 'Redstone Lamp (Inactive)',
		'name': 'redstoneLightInactive',
		'hardness': 0.3,
		'stack_size': 64,
		'diggable': True,
		'bounding_box': 'block'
	},
	124: {
		'display_name': 'Redstone Lamp (Active)',
		'name': 'redstoneLightActive',
		'hardness': 0.3,
		'stack_size': 64,
		'diggable': True,
		'bounding_box': 'block'
	},
	125: {
		'display_name': 'Wooden Double Slab',
		'name': 'woodSlabDouble',
		'hardness': 2,
		'stack_size': 64,
		'diggable': True,
		'bounding_box': 'block',
		'material': 'wood'
	},
	126: {
		'display_name': 'Wooden Slab',
		'name': 'woodSlab',
		'hardness': 2,
		'stack_size': 64,
		'diggable': True,
		'bounding_box': 'block'
	},
	127: {
		'display_name': 'Cocoa Pod',
		'name': 'cocoa',
		'hardness': 0.2,
		'stack_size': 64,
		'diggable': True,
		'bounding_box': 'block',
		'material': 'plant'
	},
	128: {
		'display_name': 'Sandstone Stairs',
		'name': 'stairsSandStone',
		'hardness': 0,
		'stack_size': 64,
		'diggable': True,
		'bounding_box': 'block',
		'material': 'rock',
		'harvest_tools': (270, 274, 257, 278, 285),
	},
	129: {
		'display_name': 'Emerald Ore',
		'name': 'oreEmerald',
		'hardness': 3,
		'stack_size': 64,
		'diggable': True,
		'bounding_box': 'block',
		'material': 'rock',
		'harvest_tools': (257, 278),
	},
	130: {
		'display_name': 'Ender Chest',
		'name': 'enderChest',
		'hardness': 22.5,
		'stack_size': 64,
		'diggable': True,
		'bounding_box': 'block',
		'material': 'rock',
		'harvest_tools': (270, 274, 257, 278, 285),
	},
	131: {
		'display_name': 'Tripwire Hook',
		'name': 'tripWireSource',
		'hardness': 0,
		'stack_size': 64,
		'diggable': True,
		'bounding_box': 'block'
	},
	132: {
		'display_name': 'Tripwire',
		'name': 'tripWire',
		'hardness': 0,
		'stack_size': 64,
		'diggable': True,
		'bounding_box': 'empty'
	},
	133: {
		'display_name': 'Block of Emerald',
		'name': 'blockEmerald',
		'hardness': 5,
		'stack_size': 64,
		'diggable': True,
		'bounding_box': 'block',
		'material': 'rock',
		'harvest_tools': (257, 278),
	},
	134: {
		'display_name': 'Spruce Wood Stairs',
		'name': 'stairsWoodSpruce',
		'hardness': 0,
		'stack_size': 64,
		'diggable': True,
		'bounding_box': 'block'
	},
	135: {
		'display_name': 'Birch Wood Stairs',
		'name': 'stairsWoodBirch',
		'hardness': 0,
		'stack_size': 64,
		'diggable': True,
		'bounding_box': 'block'
	},
	136: {
		'display_name': 'Jungle Wood Stairs',
		'name': 'stairsWoodJungle',
		'hardness': 0,
		'stack_size': 64,
		'diggable': True,
		'bounding_box': 'block'
	},
	137: {
		'display_name': 'Command Block',
		'name': 'commandBlock',
		'hardness': 0,
		'stack_size': 64,
		'diggable': True,
		'bounding_box': 'block',
		'material': 'rock',
		'harvest_tools': (270, 274, 257, 278, 285),
	},
	138: {
		'display_name': 'Beacon',
		'name': 'beacon',
		'hardness': 3,
		'stack_size': 64,
		'diggable': True,
		'bounding_box': 'block'
	},
	139: {
		'display_name': 'Cobblestone Wall',
		'name': 'cobbleWall',
		'hardness': 0,
		'stack_size': 64,
		'diggable': True,
		'bounding_box': 'block',
		'material': 'rock',
		'harvest_tools': (270, 274, 257, 278, 285),
	},
	140: {
		'display_name': 'Flower Pot',
		'name': 'flowerPot',
		'hardness': 0,
		'stack_size': 64,
		'diggable': True,
		'bounding_box': 'block'
	},
	141: {
		'display_name': 'Carrots',
		'name': 'carrots',
		'hardness': 0,
		'stack_size': 64,
		'diggable': True,
		'bounding_box': 'empty'
	},
	142: {
		'display_name': 'Potatoes',
		'name': 'potatoes',
		'hardness': 0,
		'stack_size': 64,
		'diggable': True,
		'bounding_box': 'empty'
	},
	143: {
		'display_name': 'Wooden Button',
		'name': 'buttonWood',
		'hardness': 0.5,
		'stack_size': 64,
		'diggable': True,
		'bounding_box': 'empty'
	},
	144: {
		'display_name': 'Mob Head',
		'name': 'skull',
		'hardness': 1,
		'stack_size': 64,
		'diggable': True,
		'bounding_box': 'block'
	},
	145: {
		'display_name': 'Anvil',
		'name': 'anvil',
		'hardness': 5,
		'stack_size': 64,
		'diggable': True,
		'bounding_box': 'block',
		'material': 'rock',
		'harvest_tools': (270, 274, 257, 278, 285),
	},
	146: {
		'display_name': 'Trapped Chest',
		'name': 'trappedChest',
		'hardness': 2.5,
		'stack_size': 64,
		'diggable': True,
		'bounding_box': 'block',
		'material': 'wood'
	},
	147: {
		'display_name': 'Weighted Pressure plate (Light)',
		'name': 'pressurePlateWeightedLight',
		'hardness': 0.5,
		'stack_size': 64,
		'diggable': True,
		'bounding_box': 'empty',
		'material': 'rock',
		'harvest_tools': (270, 274, 257, 278, 285),
	},
	148: {
		'display_name': 'Weighted Pressure plate (Heavy)',
		'name': 'pressurePlateWeightedHeavy',
		'hardness': 0.5,
		'stack_size': 64,
		'diggable': True,
		'bounding_box': 'empty',
		'material': 'rock',
		'harvest_tools': (270, 274, 257, 278, 285),
	},
	149: {
		'display_name': 'Redstone Comparator (Inactive)',
		'name': 'redstoneComparatorInactive',
		'hardness': 0,
		'stack_size': 64,
		'diggable': True,
		'bounding_box': 'block'
	},
	150: {
		'display_name': 'Redstone Comparator (Active)',
		'name': 'redstoneComparatorActive',
		'hardness': 0,
		'stack_size': 64,
		'diggable': True,
		'bounding_box': 'block'
	},
	151: {
		'display_name': 'Daylight Sensor',
		'name': 'daylightSensor',
		'hardness': 0.2,
		'stack_size': 64,
		'diggable': True,
		'bounding_box': 'block',
		'material': 'wood'
	},
	152: {
		'display_name': 'Block of Redstone',
		'name': 'redstoneBlock',
		'hardness': 5,
		'stack_size': 64,
		'diggable': True,
		'bounding_box': 'block',
		'material': 'rock',
		'harvest_tools': (270, 274, 257, 278, 285),
	},
	153: {
		'display_name': 'Nether Quartz Ore',
		'name': 'netherQuartzOre',
		'hardness': 3,
		'stack_size': 64,
		'diggable': True,
		'bounding_box': 'block',
		'material': 'rock',
		'harvest_tools': (270, 274, 257, 278, 285),
	},
	154: {
		'display_name': 'Hopper',
		'name': 'hopper',
		'hardness': 3,
		'stack_size': 64,
		'diggable': True,
		'bounding_box': 'block',
		'material': 'rock',
		'harvest_tools': (270, 274, 257, 278, 285),
	},
	155: {
		'display_name': 'Block of Quartz',
		'name': 'quartzBlock',
		'hardness': 0.8,
		'stack_size': 64,
		'diggable': True,
		'bounding_box': 'block',
		'material': 'rock',
		'harvest_tools': (270, 274, 257, 278, 285),
	},
	156: {
		'display_name': 'Quartz Stairs',
		'name': 'quartzStairs',
		'hardness': 0.8,
		'stack_size': 64,
		'diggable': True,
		'bounding_box': 'block',
		'material': 'rock',
		'harvest_tools': (270, 274, 257, 278, 285),
	},
	157: {
		'display_name': 'Activator Rail',
		'name': 'activatorRail',
		'hardness': 0.7,
		'stack_size': 64,
		'diggable': True,
		'bounding_box': 'empty',
		'material': 'rock'
	},
	158: {
		'display_name': 'Dropper',
		'name': 'dropper',
		'hardness': 3.5,
		'stack_size': 64,
		'diggable': True,
		'bounding_box': 'block',
		'material': 'rock',
		'harvest_tools': (270, 274, 257, 278, 285),
	},
}
blocks = tuple(blocks[i] for i in range(len(blocks)))
