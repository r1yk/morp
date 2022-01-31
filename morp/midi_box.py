# pylint: disable=no-member
"""
midi_boxes.py
"""
from copy import deepcopy
from typing import List, Union
import mido


class MidiBox:
    """
    A `MidiBox` is the generic parent for all MIDI FX boxes. It handles incoming messages,
    and manages connections to MIDI FX loops, other `MidiBoxes`, and external MIDI devices.
    """

    def __init__(self,
                 outputs: List['MidiBox'] = None,
                 fx_return: bool = False):
        """
        Create a new instance of a MidiBox.

        Arguments:
            - `outputs`: a list of existing `MidiBoxes` that should receive messages from this one
            - `fx_return`: a boolean representing whether or not this `MidiBox` outputs
                           to an FX loop return
        """
        self._notes_on = set()
        self._fx_loop = None
        self._fx_return = fx_return
        self.set_outputs(outputs or [])

    def set_outputs(self, outputs: List['MidiBox']):
        """Send the output of this `MidiBox` to a list of other `MidiBoxes`."""
        self.outputs = outputs
        self.assign_fx_loop(self._fx_loop)

    def modifier(self, message: mido.Message) -> Union[mido.Message, List[mido.Message]]:
        """
        Change something about a message before sending it to an output.
        Override this method in subclasses of MidiBox as desired!
        """
        return message

    def assign_fx_loop(self, loop: 'EffectsLoop'):
        """
        Make a copy of an existing `EffectsLoop`, and hook it up to the effect send/return.
        """
        if loop:
            new_loop = deepcopy(loop)
            new_loop.set_return(self)
            self._fx_loop = new_loop

    @property
    def fx_return(self):
        """
        Return whether or not this `MidiBox` is the last one in an FX loop.
        """
        return self._fx_return

    @fx_return.setter
    def fx_return(self, fx_return: bool):
        self._fx_return = fx_return

    def on_message(self, message: mido.Message):
        """
        Accept incoming MIDI `Messages`, and dispatch event handlers.
        """
        if message.type != 'clock':
            modified = self.modifier(message)
            if isinstance(modified, list):
                for note in modified:
                    self.on_note(note)
            else:
                self.on_note(message)
        else:
            self.on_clock(message)

    def on_note(self, message: mido.Message):
        """
        Handle MIDI `Messages` that where `type` is `note_on` or `note_off`.
        """
        if message.type == 'note_on' and message.velocity > 0:
            self.on_note_on(message)
        elif message.type == 'note_off':
            self.on_note_off(message)

    def on_note_on(self, message: mido.Message):
        """
        Handle MIDI `Messages` that where `type` is `note_on`.
        """
        if message.note not in self._notes_on:
            self.route_message(message)
            self._notes_on.add(message.note)

    def on_note_off(self, message: mido.Message):
        """
        Handle MIDI `Messages` that where `type` is `note_off`.
        """
        self.route_message(message)
        self._notes_on.discard(message.note)

    def on_clock(self, message: mido.Message):
        """
        Handle MIDI `Messages` that where `type` is `clock`.
        """
        self.route_message(message)

    def route_message(self, message: mido.Message, through: bool = False):
        """
        Dispatch this message to either the FX loop or the output(s) as appropriate.
        """
        if self._fx_loop and not (self.fx_return or through):
            self._fx_loop.on_message(message)
        elif len(self.outputs) > 0:
            for output in self.outputs:
                output.on_message(message)


class MidiOut(MidiBox):
    """
    A `MidiOut is a `MidiBox` that maintains a connection to an external MIDI device.
    """

    def __init__(self, output_name: str):
        self.name = output_name
        self.output = output_name
        super().__init__()

    @property
    def output(self):
        """Return the underlying mido `output` object."""
        return self._output

    @output.setter
    def output(self, output_name: str):
        """Connect to an external MIDI device when its name is provided."""
        self.name = output_name
        if output_name:
            self._output = mido.open_output(output_name)
        else:
            self._output = None

    def route_message(self, message, through=False):
        """Forward this message to the external MIDI device."""
        self.output.send(message)

    def close(self):
        """Close the connection to this external MIDI device."""
        self.output.close()

    def __hash__(self):
        return hash(self.name)


class MidiIn(MidiBox):
    """
    A `MidiIn` is a `MidiBox` that maintains a connection to an external
    MIDI device used for generating input.
    """

    def __init__(self, input_name: str):
        self.name = input_name
        self.input = input_name
        super().__init__()

    @property
    def input(self):
        """Get the underlying mido `input` object."""
        return self._input

    @input.setter
    def input(self, input_name: str):
        """Open a connection to a specificed `input_name`."""
        self.name = input_name
        if input_name:
            self._input = mido.open_input(input_name)
            self._input.callback = self.on_message
        else:
            self._input = None

    def close(self):
        """Close the connection to this MIDI device."""
        self.input.close()

    def __hash__(self):
        return hash(self.name)


class EffectsLoop:
    """
    A `EffectsLoop` is an ordered sequence of `MidiBoxes`.
    The output of one `MidiBox` is sent to the next.
    Each instance of a `EffectsLoop` may connect to its own output.
    """

    def __init__(self, boxes: List[MidiBox]):
        self._boxes = boxes or []
        # Connect the interior MidiBoxes to each other
        # The final one is left unconnected so that the Loop may be reused by many MidiBoxes
        for i in range(0, len(boxes) - 1):
            boxes[i].set_outputs([*boxes[i].outputs, boxes[i + 1]])

    @property
    def boxes(self) -> List[MidiBox]:
        """Get a list of the MidiBoxes in this loop"""
        return self._boxes

    def on_message(self, message: mido.Message):
        """Simply forward the message to the first MidiBox in the loop. """
        if len(self.boxes) > 0:
            self.boxes[0].on_message(message)

    def set_return(self, return_to: MidiBox):
        """Specify where this instance of a `EffectsLoop` should return its output."""
        box_count = len(self._boxes)
        if box_count > 0:
            terminus = self._boxes[box_count - 1]
            terminus.fx_return = True
            terminus.set_outputs([*return_to.outputs])
