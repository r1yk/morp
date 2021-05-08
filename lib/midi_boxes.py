"""
midi_boxes.py
"""
from copy import deepcopy
from mido import open_output, open_input, Message  # pylint: disable=no-name-in-module


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

    def receive_message(self, message, fx_return=False):
        """receive_message"""
        if message.type == 'note_on' and message.velocity > 0:
            self.note_on(message, fx_return)
        else:
            self.note_off(message, fx_return)

    def note_on(self, message, fx_return=False):
        """note_on"""
        self.route_message(message, fx_return)
        self.notes_on = list(set([*self.notes_on, message.note]))

    def note_off(self, message, fx_return=False):
        """note_off"""
        self.route_message(message, fx_return)
        self.notes_on = list(
            filter(lambda note: note == message.note, self.notes_on))

    def route_message(self, message, fx_return=False):
        """route_message"""
        if self._fx_loop and not fx_return:
            self._fx_loop.receive_message(message)
        elif len(self.outputs) > 0:
            for output in self.outputs:
                output.receive_message(message, self._is_fx_return)


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

    def receive_message(self, message):
        """ route_message """
        if len(self._boxes) > 0:
            self._boxes[0].receive_message(message)

    def set_return(self, return_to):
        """ set_return """
        box_count = len(self._boxes)
        if box_count > 0:
            terminus = self._boxes[box_count - 1]
            terminus.set_is_fx_return(True)
            terminus.set_outputs([*terminus.outputs, return_to])


class MidiOut(MidiBox):
    """
    MidiOut
    """

    def __init__(self, output_name):
        self.output = open_output(output_name)
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
        self.input = open_input(input_name)
        self.name = input_name
        self.input.callback = self.receive_message
        super().__init__()


class Harmonizer(MidiBox):
    """
    Harmonizer
    """

    def __init__(self):
        self.name = 'harmonizer'
        self.voices = []
        super().__init__()

    def receive_message(self, message, fx_return=False):
        super().receive_message(message, fx_return)
        for voice in self.voices:
            super().receive_message(message.copy(note=message.note + voice), fx_return)


class Shadow(MidiBox):
    """
    Shadow
    """

    def __init__(self):
        self.name = 'shadow'
        self.note_cache = []
        self.interval = 3
        self.feedback = 2
        self.decay_factor = 0.3
        super().__init__()

    def modifier(self, message):
        self.note_cache.insert(0, message)
        messages = [message]
        for i in range(self.feedback):
            if i * self.interval < len(self.note_cache):
                to_add = self.note_cache[i * self.interval]
                messages.append(to_add.copy(velocity=round(
                    to_add.velocity * self.decay_factor)
                ))
            else:
                break

        if len(self.note_cache) > self.interval * self.feedback:
            self.note_cache.pop()

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

    def note_on(self, message, fx_return=False):
        if self.pedaling:
            self.pedaling = False
            for note in self.pedal_notes:
                super().note_off(Message('note_off', note=note), fx_return)
            self.notes_on = []
            self.pedal_notes = []
        super().note_on(message, fx_return)

    def note_off(self, message, fx_return=False):
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
