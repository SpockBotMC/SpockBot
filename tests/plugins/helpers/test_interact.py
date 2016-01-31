from unittest import TestCase

from spockbot.mcdata import constants
from spockbot.plugins.helpers.clientinfo import PlayerPosition
from spockbot.plugins.helpers.interact import InteractPlugin
from spockbot.vector import Vector3


class DataDict(dict):
    def __init__(self, **kwargs):
        super(DataDict, self).__init__(**kwargs)
        self.__dict__.update(kwargs)


class PluginLoaderMock(object):
    def provides(self, ident, obj):
        self.provides_ident = ident
        self.provides_obj = obj

    def requires(self, requirement):
        if requirement == 'ClientInfo':
            return ClientInfoMock()
        elif requirement == 'Inventory':
            return InventoryMock()
        elif requirement == 'Net':
            return NetMock()
        elif requirement == 'Channels':
            return True
        elif requirement == 'Event':
            return True
        else:
            raise AssertionError('Unexpected requirement %s' % requirement)


class NetMock(object):
    idents = []
    datas = []

    def push_packet(self, ident, data):
        data_dict = DataDict(**data)
        self.idents.append(ident)
        self.datas.append(data_dict)


class SlotMock(object):
    def get_dict(self):
        return {}


class InventoryMock(object):
    active_slot = SlotMock()


class ClientInfoMock(object):
    eid = 123
    position = PlayerPosition(1., 2., 3.)
    eye_pos = position + (0, constants.PLAYER_EYE_HEIGHT, 0)


class InteractPluginTest(TestCase):
    def setUp(self):
        ploader = PluginLoaderMock()
        self.plug = InteractPlugin(ploader, {})
        assert ploader.provides_ident == 'Interact'
        assert ploader.provides_obj == self.plug

    def test_sneak(self):
        self.assertEqual(self.plug.sneaking, False)
        self.plug.sneak()
        self.assertEqual(self.plug.sneaking, True)
        self.plug.unsneak()
        self.assertEqual(self.plug.sneaking, False)
        self.plug.sneak(sneak=True)
        self.assertEqual(self.plug.sneaking, True)
        self.plug.sneak(sneak=False)
        self.assertEqual(self.plug.sneaking, False)

    def test_sprint(self):
        self.assertEqual(self.plug.sprinting, False)
        self.plug.sprint()
        self.assertEqual(self.plug.sprinting, True)
        self.plug.unsprint()
        self.assertEqual(self.plug.sprinting, False)
        self.plug.sprint(sprint=True)
        self.assertEqual(self.plug.sprinting, True)
        self.plug.sprint(sprint=False)
        self.assertEqual(self.plug.sprinting, False)

    def test_look(self):
        self.plug.look(123.4, -42.2)
        self.assertEqual(ClientInfoMock.position.yaw, 123.4)
        self.assertEqual(ClientInfoMock.position.pitch, -42.2)

        self.plug.look_rel(1.4, 2.1)
        self.assertAlmostEqual(ClientInfoMock.position.yaw, 124.8)
        self.assertAlmostEqual(ClientInfoMock.position.pitch, -40.1)

        self.plug.look_at_rel(Vector3(1, 0, 0))
        self.assertAlmostEqual(ClientInfoMock.position.yaw, -90)
        self.assertAlmostEqual(ClientInfoMock.position.pitch, 0)

        self.plug.look_at(Vector3(0, 2 + constants.PLAYER_EYE_HEIGHT, 3))
        self.assertAlmostEqual(ClientInfoMock.position.yaw, 90)
        self.assertAlmostEqual(ClientInfoMock.position.pitch, 0)

    # TODO digging, block placement

    def test_activate_item(self):
        self.plug.activate_item()
        self.assertEqual(NetMock.datas[-1].location,
                         {'x': -1, 'y': 255, 'z': -1})
        self.assertEqual(NetMock.datas[-1].direction, -1)
        for c in 'xyz':
            self.assertEqual(getattr(NetMock.datas[-1], 'cur_pos_%s' % c),
                             -1)

        # TODO deactivate_item

    def test_entity(self):
        # interact entity should not swing arm
        entity = DataDict(eid=234, x=2, y=2 + constants.PLAYER_EYE_HEIGHT, z=4)
        self.plug.use_entity(entity)
        self.assertAlmostEqual(ClientInfoMock.position.yaw, -45)
        self.assertAlmostEqual(ClientInfoMock.position.pitch, 0)
        self.assertEqual(NetMock.datas[-1].action, constants.INTERACT_ENTITY)
        self.assertEqual(NetMock.datas[-1].target, 234)

        # attack entity should swing arm
        entity = DataDict(eid=235, x=2, y=2 + constants.PLAYER_EYE_HEIGHT, z=4)
        self.plug.use_entity(entity, action=constants.ATTACK_ENTITY)
        self.assertAlmostEqual(ClientInfoMock.position.yaw, -45)
        self.assertAlmostEqual(ClientInfoMock.position.pitch, 0)
        self.assertEqual(NetMock.datas[-2].action, constants.ATTACK_ENTITY)
        self.assertEqual(NetMock.datas[-2].target, 235)
        self.assertEqual(NetMock.idents[-1], 'PLAY>Animation')

        self.plug.auto_look = False
        entity = DataDict(eid=345, x=0, y=3 + constants.PLAYER_EYE_HEIGHT, z=3)
        self.plug.attack_entity(entity)
        # different pos, but look shouldn't have changed
        self.assertAlmostEqual(ClientInfoMock.position.yaw, -45)
        self.assertAlmostEqual(ClientInfoMock.position.pitch, 0)
        self.assertEqual(NetMock.datas[-2].action, constants.ATTACK_ENTITY)
        self.assertEqual(NetMock.datas[-2].target, 345)
        self.assertEqual(NetMock.idents[-1], 'PLAY>Animation')
        self.plug.auto_look = True

        self.plug.auto_swing = False
        entity = DataDict(eid=456, x=2, y=3 + constants.PLAYER_EYE_HEIGHT, z=3)
        self.plug.mount_vehicle(entity)
        self.assertAlmostEqual(ClientInfoMock.position.yaw, -90)
        self.assertAlmostEqual(ClientInfoMock.position.pitch, -45)
        self.assertEqual(NetMock.datas[-1].action, constants.INTERACT_ENTITY)
        self.assertEqual(NetMock.datas[-1].target, 456)
        self.plug.auto_swing = True

    def test_vehicle(self):
        self.plug.steer_vehicle(1., -2.)
        self.assertEqual(NetMock.datas[-1].flags, 0)
        self.assertAlmostEqual(NetMock.datas[-1].sideways, 1.)
        self.assertAlmostEqual(NetMock.datas[-1].forward, -2.)

        self.plug.steer_vehicle(-1., 2., jump=True, unmount=True)
        self.assertEqual(NetMock.datas[-1].flags, 3)
        self.assertAlmostEqual(NetMock.datas[-1].sideways, -1.)
        self.assertAlmostEqual(NetMock.datas[-1].forward, 2.)

        self.plug.jump_vehicle()
        self.assertEqual(NetMock.datas[-1].flags, 1)
        self.assertEqual(NetMock.datas[-1].sideways, 0.)
        self.assertEqual(NetMock.datas[-1].forward, 0.)

        self.plug.unmount_vehicle()
        self.assertEqual(NetMock.datas[-1].flags, 2)
        self.assertEqual(NetMock.datas[-1].sideways, 0.)
        self.assertEqual(NetMock.datas[-1].forward, 0.)
