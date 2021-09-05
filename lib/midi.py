# pylint: disable=no-member
"""
midi.py
"""
import mido
from lib.midi_box import MidiBox


class MidiOut(MidiBox):
    """
    MidiOut
    """

    def __init__(self, output_name):
        self.output = mido.open_output(output_name)
        self.name = output_name
        print('opened {}'.format(output_name))
        super().__init__()

    def route_message(self, message, fx_return=False):
        """ route_message """
        if isinstance(message, list):
            for note in message:
                self.output.send(note)
        else:
            self.output.send(message)


class MidiIn(MidiBox):
    """
    MidiIn
    """

    def __init__(self, input_name):
        self.input = mido.open_input(input_name)
        self.name = input_name
        self.input.callback = self.on_message
        super().__init__()


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


def get_midi_devices():
    """ get_midi_devices """
    in_ports = mido.get_input_names()
    for i, port in enumerate(in_ports):
        print(f"{i+1}: {port}")

    in_choice = in_ports[int(input('Enter input port number: ')) - 1]
    midi_in = MidiIn(in_choice)
    out_ports = mido.get_output_names()
    for i, port in enumerate(out_ports):
        print(f"{i+1}: {port}")

    out_choice = out_ports[int(input('Enter output port number: ')) - 1]
    midi_out = MidiOut(out_choice)

    return (midi_in, midi_out)
