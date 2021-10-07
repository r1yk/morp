"""
midi_boxes.py
"""
from copy import deepcopy
from mido import Message


class MidiBox:
    """
    MidiBox
    """

    def __init__(self, outputs=None):
        self.set_outputs(outputs or [])
        self.notes_on = []
        self._fx_loop = None
        self._is_fx_return = False

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

    def set_is_fx_return(self, is_return=True):
        """set_is_fx_return"""
        self._is_fx_return = is_return

    def on_message(self, message, fx_return=False):
        """on_message"""
        if message.type != 'clock':
            modified = self.modifier(message)
            if isinstance(modified, list):
                for note in modified:
                    self.on_note(note, fx_return)
            else:
                self.on_note(message, fx_return)
        else:
            self.on_clock(message, fx_return)

    def on_note(self, message, fx_return=False):
        """on_note"""
        if message.type == 'note_on' and message.velocity > 0:
            self.on_note_on(message, fx_return)
        elif message.type == 'note_off':
            self.on_note_off(message, fx_return)

    def on_note_on(self, message, fx_return=False):
        """on_note_on"""
        self.route_message(message, fx_return)
        self.notes_on = list(set([*self.notes_on, message.note]))

    def on_note_off(self, message, fx_return=False):
        """on_note_off"""
        self.route_message(message, fx_return)
        self.notes_on = list(
            filter(lambda note: note != message.note, self.notes_on))

    def on_clock(self, _, fx_return=False):
        """ on_clock """
        self.route_message(_, fx_return)

    def route_message(self, message, fx_return=False):
        """route_message"""
        if self._fx_loop and not fx_return:
            self._fx_loop.on_message(message)
        elif len(self.outputs) > 0:
            # TODO: Figure out how to run these outputs in parallel
            for output in self.outputs:
                output.on_message(message, self._is_fx_return)


class Harmonizer(MidiBox):
    """
    Harmonizer
    """

    def __init__(self, voices=None):
        self.name = 'harmonizer'
        self.voices = voices or []
        super().__init__()

    def modifier(self, message):
        return [message, *[message.copy(note=message.note + voice) for voice in self.voices]]


class Shadow(MidiBox):
    """
    Shadow
    """

    def __init__(self):
        self.name = 'shadow'
        self.message_cache = []
        self.period = 7
        self.decay_by = 0.8
        self.repeat = 5
        self.length = self.period * self.repeat

        super().__init__()

    def modifier(self, message):
        messages = [message]
        for i in range(self.period - 1, len(self.message_cache), self.period):
            self.message_cache[i].velocity = round(
                self.message_cache[i].velocity * self.decay_by)
            messages.append(self.message_cache[i])
        self.message_cache.insert(0, message)
        if len(self.message_cache) > self.length:
            self.message_cache.pop()
        return messages


class Pedal(MidiBox):
    """
    Pedal (as in sustain pedal)
    """

    def __init__(self):
        self.name = 'pedal'
        self.pedaling = False
        self.pedal_notes = []
        super().__init__()

    def on_note_on(self, message, fx_return=False):
        if self.pedaling:
            self.pedaling = False
            for note in self.pedal_notes:
                super().on_note_off(Message('note_off', note=note), fx_return)
            self.notes_on = []
            self.pedal_notes = []
        super().on_note_on(message, fx_return)

    def on_note_off(self, message, fx_return=False):
        self.pedal_notes = list(set([*self.pedal_notes, message.note]))
        if len(self.notes_on) == 1:
            self.pedaling = True
        self.notes_on = list(
            filter(lambda note: note == message.note, self.notes_on))


class Chopper(MidiBox):
    """
    Chopper
    """

    def __init__(self):
        self.name = 'chopper'
        super().__init__()

    def modifier(self, message):
        pass
