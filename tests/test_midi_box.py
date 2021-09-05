# pylint: disable-all
import unittest
import mido
import tests.mocks as mocks
from lib.midi import MidiIn, MidiOut, Loop
from lib.midi_box import Harmonizer


class TestMidiBox(unittest.TestCase):
    def setUp(self):
        self.midi_in = MidiIn('device 1')
        self.midi_out = MidiOut('device 2')
        self.midi_out.output.send = unittest.mock.Mock(
            name='self.midi_out_send')

    def test_midi_input_output(self):
        # Create a mocked MIDI message and send it to the input
        message = mocks.MockMidiMessage('note_on', 60, 60)
        self.midi_in.on_message(message)
        self.midi_out.output.send.assert_not_called()

        # Hook up the output to the input, and make sure it receives the message
        # and sends it to its output device
        self.midi_in.set_outputs([self.midi_out])
        self.midi_in.on_message(message)
        self.midi_out.output.send.assert_called_once_with(message)

        # Add an empty Loop onto the input, and make sure nothing breaks
        self.midi_out.output.send.reset_mock()
        self.midi_in.set_fx_loop(Loop([MidiIn()]))
        self.midi_in.on_message(message)
        self.midi_out.output.send.assert_called_once_with(message)


if __name__ == '__main__':
    unittest.main()
