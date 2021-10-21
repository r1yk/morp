# pylint: disable=no-member
"""
midi_boxes.py
"""
from copy import deepcopy
from typing import List, Union
import mido
from .midi_service import Loop


class MidiBox:
    """
    MidiBox
    """

    def __init__(self, outputs=None, fx_return=False):
        self._notes_on = set()
        self._fx_loop = None
        self._is_fx_return = fx_return
        self.set_outputs(outputs or [])

    def set_outputs(self, outputs: List['MidiBox']):
        """set_outputs"""
        self.outputs = outputs
        self.set_fx_loop(self._fx_loop)

    def modifier(self, message: mido.Message) -> Union[mido.Message, List[mido.Message]]:
        """
        Change something about a message before sending it to an output.
        Override this method in subclasses of MidiBox as desired!
        """
        return message

    def set_fx_loop(self, loop: Loop):
        """set_fx_loop"""
        if loop:
            new_loop = deepcopy(loop)
            new_loop.set_return(self)
            self._fx_loop = new_loop

    @property
    def is_fx_return(self):
        """ is_fx_return getter """
        return self._is_fx_return

    @is_fx_return.setter
    def is_fx_return(self, fx_return: bool):
        self._is_fx_return = fx_return

    def on_message(self, message: mido.Message):
        """on_message"""
        if message.type != 'clock':
            modified = self.modifier(message)
            if isinstance(modified, list):
                for note in modified:
                    self.on_note(note)
            else:
                self.on_note(message)
        else:
            self.on_clock(message)

    def on_note(self, message):
        """on_note"""
        if message.type == 'note_on' and message.velocity > 0:
            self.on_note_on(message)
        elif message.type == 'note_off':
            self.on_note_off(message)

    def on_note_on(self, message):
        """on_note_on"""
        self.route_message(message)
        self._notes_on.add(message.note)

    def on_note_off(self, message):
        """on_note_off"""
        self.route_message(message)
        self._notes_on.discard(message.note)

    def on_clock(self, message):
        """ on_clock """
        self.route_message(message)

    def route_message(self, message, through=False):
        """route_message"""
        if self._fx_loop and not (self.is_fx_return or through):
            self._fx_loop.on_message(message)
        elif len(self.outputs) > 0:
            # TODO: Figure out how to run these outputs in parallel
            for output in self.outputs:
                output.on_message(message)


class MidiOut(MidiBox):
    """
    MidiOut
    """

    def __init__(self, output_name: str):
        self.name = output_name
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

    def route_message(self, message, through=False):
        """ route_message """
        self.output.send(message)

    def close(self):
        """Close the connection to this MIDI device"""
        self.output.close()

    def __hash__(self):
        return hash(self.name)


class MidiIn(MidiBox):
    """
    MidiIn
    """

    def __init__(self, input_name: str):
        self.name = input_name
        self.input = input_name
        super().__init__()

    @property
    def input(self):
        """ input setter """
        return self._input

    @input.setter
    def input(self, input_name: str):
        self.name = input_name
        if input_name:
            self._input = mido.open_input(input_name)
            self._input.callback = self.on_message
        else:
            self._input = None

    def close(self):
        """Close the connection to this MIDI device"""
        self.input.close()

    def __hash__(self):
        return hash(self.name)
