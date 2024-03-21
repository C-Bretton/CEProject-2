import unittest
from ..Zigbee2mqttClient import Zigbee2mqttMessage, Zigbee2mqttMessageType

class Zigbee2mqttMessageTests(unittest.TestCase):
    def test_parse_device_announce_message(self):
        TOPIC = "zigbee2mqtt/bridge/event"
        MESSAGE = '{"data":{"friendly_name":"0xbc33acfffe8b8ed1","ieee_address":"0xbc33acfffe8b8ed1"},"type":"device_announce"}'

        z2m_message = Zigbee2mqttMessage.parse(TOPIC, MESSAGE)

        self.assertEqual(z2m_message.data, {"friendly_name": "0xbc33acfffe8b8ed1",
                                            "ieee_address": "0xbc33acfffe8b8ed1"})
        self.assertIsNone(z2m_message.message)
        self.assertIsNone(z2m_message.meta)
        self.assertIsNone(z2m_message.status)
        self.assertEqual(z2m_message.topic, TOPIC)
        self.assertIsInstance(z2m_message.type_, Zigbee2mqttMessageType)
        self.assertEqual(z2m_message.type_,
                         Zigbee2mqttMessageType.DEVICE_ANNOUNCE)

    def test_parse_device_announced_message(self):
        TOPIC = "zigbee2mqtt/bridge/log"
        MESSAGE = '{"message":"announce","meta":{"friendly_name":"0xbc33acfffe8b8ed1"},"type":"device_announced"}'

        z2m_message = Zigbee2mqttMessage.parse(TOPIC, MESSAGE)

        self.assertIsNone(z2m_message.data)
        self.assertEqual(z2m_message.message, "announce")
        self.assertEqual(z2m_message.meta, {
                         "friendly_name": "0xbc33acfffe8b8ed1"})
        self.assertIsNone(z2m_message.status)
        self.assertEqual(z2m_message.topic, TOPIC)
        self.assertIsInstance(z2m_message.type_, Zigbee2mqttMessageType)
        self.assertEqual(z2m_message.type_,
                         Zigbee2mqttMessageType.DEVICE_ANNOUNCED)

    def test_parse_device_connected_message(self):
        TOPIC = "zigbee2mqtt/bridge/log"
        MESSAGE = '{"message":{"friendly_name":"0xbc33acfffe8b8ed1"},"type":"device_connected"}'

        z2m_message = Zigbee2mqttMessage.parse(TOPIC, MESSAGE)

        self.assertIsNone(z2m_message.data)
        self.assertEqual(z2m_message.message, {
                         "friendly_name": "0xbc33acfffe8b8ed1"})
        self.assertIsNone(z2m_message.meta)
        self.assertIsNone(z2m_message.status)
        self.assertEqual(z2m_message.topic, TOPIC)
        self.assertIsInstance(z2m_message.type_, Zigbee2mqttMessageType)
        self.assertEqual(z2m_message.type_,
                         Zigbee2mqttMessageType.DEVICE_CONNECTED)

    def test_parse_device_interview_message(self):
        TOPIC = "zigbee2mqtt/bridge/event"
        MESSAGE = '{"data":{"friendly_name":"0xbc33acfffe8b8ed1","ieee_address":"0xbc33acfffe8b8ed1","status":"started"},"type":"device_interview"}'

        z2m_message = Zigbee2mqttMessage.parse(TOPIC, MESSAGE)

        self.assertEqual(z2m_message.data, {"friendly_name": "0xbc33acfffe8b8ed1",
                                            "ieee_address": "0xbc33acfffe8b8ed1",
                                            "status": "started"})
        self.assertIsNone(z2m_message.message)
        self.assertIsNone(z2m_message.meta)
        self.assertIsNone(z2m_message.status)
        self.assertEqual(z2m_message.topic, TOPIC)
        self.assertIsInstance(z2m_message.type_, Zigbee2mqttMessageType)
        self.assertEqual(z2m_message.type_,
                         Zigbee2mqttMessageType.DEVICE_INTERVIEW)

    def test_parse_device_joined_message(self):
        TOPIC = "zigbee2mqtt/bridge/event"
        MESSAGE = '{"data":{"friendly_name":"0xbc33acfffe8b8ed1","ieee_address":"0xbc33acfffe8b8ed1"},"type":"device_joined"}'

        z2m_message = Zigbee2mqttMessage.parse(TOPIC, MESSAGE)

        self.assertEqual(z2m_message.data, {"friendly_name": "0xbc33acfffe8b8ed1",
                                            "ieee_address": "0xbc33acfffe8b8ed1"})
        self.assertIsNone(z2m_message.message)
        self.assertIsNone(z2m_message.meta)
        self.assertIsNone(z2m_message.status)
        self.assertEqual(z2m_message.topic, TOPIC)
        self.assertIsInstance(z2m_message.type_, Zigbee2mqttMessageType)
        self.assertEqual(z2m_message.type_,
                         Zigbee2mqttMessageType.DEVICE_JOINED)

    def test_parse_device_paired_message(self):
        TOPIC = "zigbee2mqtt/bridge/log"
        MESSAGE = '{"message":"interview_started","meta":{"friendly_name":"0xbc33acfffe8b8ed1"},"type":"pairing"}'

        z2m_message = Zigbee2mqttMessage.parse(TOPIC, MESSAGE)

        self.assertIsNone(z2m_message.data)
        self.assertEqual(z2m_message.message, "interview_started")
        self.assertEqual(z2m_message.meta, {
                         "friendly_name": "0xbc33acfffe8b8ed1"})
        self.assertIsNone(z2m_message.status)
        self.assertEqual(z2m_message.topic, TOPIC)
        self.assertIsInstance(z2m_message.type_, Zigbee2mqttMessageType)
        self.assertEqual(z2m_message.type_,
                         Zigbee2mqttMessageType.DEVICE_PAIRING)


if __name__ == "__main__":
    unittest.main()
