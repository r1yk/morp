# pylint: disable-all
import unittest
from morp import MidiIn, MidiOut, EffectsLoop
from morp.effects import Harmonizer, Shadow, Freeze
from mocks import MockMidiMessage


class TestMidiBox(unittest.TestCase):
    def setUp(self):
        self.midi_in = MidiIn('device 1')
        self.midi_out = MidiOut('device 2')
        self.midi_out.output.send = unittest.mock.Mock(
            name='self.midi_out_send')

    def connect_output(self):
        self.midi_in.set_outputs([self.midi_out])

    def test_midi_input_output(self):
        # Create a mocked MIDI message and send it to the input
        message = MockMidiMessage('note_on', 60, 60)
        self.midi_in.on_message(message)
        self.midi_out.output.send.assert_not_called()

        # Hook up the output to the input, and make sure it receives the message
        # and sends it to its output device
        self.connect_output()
        message_2 = MockMidiMessage('note_on', 63, 60)
        self.midi_in.on_message(message_2)
        self.midi_out.output.send.assert_called_once_with(message_2)

        # Add an empty EffectsLoop onto the input, and make sure nothing breaks
        message_3 = MockMidiMessage('note_on', 67, 60)

        self.midi_out.output.send.reset_mock()
        self.midi_in.assign_fx_loop(EffectsLoop([MidiIn('device 1')]))
        self.midi_in.on_message(message_3)
        self.midi_out.output.send.assert_called_once_with(message_3)

    def test_harmonizer(self):
        self.connect_output()
        harmonizer = Harmonizer(voices=[7, 12])
        self.midi_in.assign_fx_loop(EffectsLoop([harmonizer]))

        message = MockMidiMessage('note_on', 60, 60)
        self.midi_in.on_message(message)
        self.assertEqual(self.midi_out.output.send.call_count, 3)
        self.assertEqual(len(self.midi_out._notes_on), 3)

        # Make sure sending a corresponding note_off turns off all harmonized notes
        self.midi_in.on_message(message.copy(message_type='note_off'))
        self.assertEqual(self.midi_out.output.send.call_count, 6)
        self.assertEqual(len(self.midi_out._notes_on), 0)

        # Chain together two harmonizers for fun
        self.midi_out.output.send.reset_mock()
        harmonizer2 = Harmonizer(voices=[12, 24])
        self.midi_in.assign_fx_loop(EffectsLoop([harmonizer, harmonizer2]))
        message = MockMidiMessage('note_on', 60, 60)
        self.midi_in.on_message(message)
        self.assertEqual(self.midi_out.output.send.call_count, 7)

        # Make sure sending a corresponding note_off turns off all harmonized notes
        self.midi_in.on_message(message.copy(message_type='note_off'))
        self.assertEqual(len(self.midi_out._notes_on), 0)

    def test_shadow(self):
        self.connect_output()
        shadow = Shadow()
        self.midi_in.assign_fx_loop(EffectsLoop([shadow]))

        message1 = MockMidiMessage('note_on', 60, 60)
        self.midi_in.on_message(message1)
        self.assertEqual(self.midi_out.output.send.call_count, 1)
        self.assertEqual(len(self.midi_in._notes_on), 1)

        message2 = MockMidiMessage('note_off', 60, 60)
        self.midi_in.on_message(message2)
        self.assertEqual(self.midi_out.output.send.call_count, 2)
        self.assertEqual(len(self.midi_in._notes_on), 0)

        message3 = MockMidiMessage('note_on', 64, 60)
        self.midi_in.on_message(message1)
        self.assertEqual(self.midi_out.output.send.call_count, 3)
        self.assertEqual(len(self.midi_in._notes_on), 1)

    def test_freeze(self):
        self.connect_output()
        freeze = Freeze()
        self.midi_in.assign_fx_loop(EffectsLoop([freeze]))

        message1 = MockMidiMessage('note_on', 60, 60)
        self.midi_in.on_message(message1)
        self.assertEqual(self.midi_out.output.send.call_count, 1)

        message2 = MockMidiMessage('note_off', 60, 60)
        self.midi_in.on_message(message2)
        self.assertEqual(self.midi_out.output.send.call_count, 1)
        self.assertEqual(len(self.midi_out._notes_on), 1)

        message3 = MockMidiMessage('note_on', 64, 60)
        self.midi_in.on_message(message1)
        self.assertEqual(self.midi_out.output.send.call_count, 3)
        self.assertEqual(len(self.midi_out._notes_on), 1)


if __name__ == '__main__':
    unittest.main()
