# pylint: disable=no-member
"""
midi.py
"""
import os
import mido
from lib.midi_box import MidiBox


class MidiOut(MidiBox):
    """
    MidiOut
    """

    def __init__(self, output_name=None):
        self.output = output_name
        super().__init__()

    @property
    def output(self):
        """ output getter """
        return self._output

    @output.setter
    def output(self, output_name):
        self.name = output_name
        if output_name:
            self._output = mido.open_output(output_name)
        else:
            self._output = None

    def route_message(self, message, fx_return=False):
        """ route_message """
        self.output.send(message)


class MidiIn(MidiBox):
    """
    MidiIn
    """

    def __init__(self, input_name=os.getenv('DEFAULT_MIDI_INPUT')):
        self.input = input_name
        super().__init__()

    @property
    def input(self):
        """ input setter """
        return self._input

    @input.setter
    def input(self, input_name):
        self.name = input_name
        if input_name:
            self._input = mido.open_input(input_name)
            self._input.callback = self.on_message
        else:
            self._input = None


class Loop:
    """
    Loop
    """

    def __init__(self, boxes=None):
        self._boxes = boxes or []
        # Connect the interior MidiBoxes to each other
        # The final one is left unconnected so that the Loop may be reused by many MidiBoxes
        for i in range(0, len(boxes) - 1):
            boxes[i].set_outputs([*boxes[i].outputs, boxes[i + 1]])

    def on_message(self, message):
        """ route_message """
        if len(self._boxes) > 0:
            self._boxes[0].on_message(message)

    def set_return(self, return_to):
        """ set_return """
        box_count = len(self._boxes)
        if box_count > 0:
            terminus = self._boxes[box_count - 1]
            terminus.set_is_fx_return(True)
            terminus.set_outputs([*terminus.outputs, return_to])
