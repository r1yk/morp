#pylint: disable-all
from unittest.mock import Mock
import mido
from morp.midi import MidiOut


class MockOutput:
    def send(self, message):
        pass


class MockInput:
    def callback(self, message):
        pass


class MockMidiMessage:
    def __init__(self, message_type, note, velocity):
        self.type = message_type
        self.note = note
        self.velocity = velocity

    def copy(self, message_type=None, note=None, velocity=None):
        return MockMidiMessage(
            message_type=message_type or self.type,
            note=note or self.note,
            velocity=velocity or self.velocity)


def mido_get_input_names():
    return ['device 1', 'device 2']


def mido_get_output_names():
    return ['device 1', 'device 2']


def mido_open_output(_):
    return MockOutput()


def mido_open_input(_):
    return MockInput()


mido.get_input_names = Mock(
    name='get_input_names', return_value=mido_get_input_names())
mido.get_output_names = Mock(
    name='get_output_names', return_value=mido_get_output_names())
mido.open_input = Mock(
    name='open_input', return_value=mido_open_input('device 1'))
mido.open_output = Mock(
    name='open_output', return_value=mido_open_output('device 2'))
