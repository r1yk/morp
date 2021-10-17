"""
midi_boxes.py
"""
from copy import deepcopy


class MidiBox:
    """
    MidiBox
    """

    def __init__(self, outputs=None, fx_return=False):
        self.set_outputs(outputs or [])
        self._notes_on = set()
        self._fx_loop = None
        self._is_fx_return = fx_return

    def set_outputs(self, outputs):
        """set_outputs"""
        self.outputs = outputs

    def modifier(self, message):  # pylint: disable=no-self-use
        """modifier"""
        return message

    def set_fx_loop(self, loop=None):
        """set_fx_loop"""
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

    def on_message(self, message):
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
