"""
midi_boxes.py
"""
from copy import deepcopy
from mido import open_output, open_input  # pylint: disable=no-name-in-module


class MidiBox:
    """
    MidiBox
    """

    def __init__(self, outputs=None):
        self.set_outputs(outputs or [])
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

    def _on_input(self, message, output):
        """_on_input"""
        if isinstance(message, list):
            for note in message:
                output.handle_message(self.modifier(note), self._is_fx_return)
        else:
            output.handle_message(self.modifier(message), self._is_fx_return)

    def handle_message(self, message, fx_return=False):
        """handle_message"""
        if self._fx_loop and not fx_return:
            self._fx_loop.handle_message(message)
        elif len(self.outputs) > 0:
            for output in self.outputs:
                self._on_input(message, output)


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

    def handle_message(self, message):
        """ handle_message """
        if len(self._boxes) > 0:
            self._boxes[0].handle_message(message)

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

    def handle_message(self, message, fx_return=False):
        """ handle_message """
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
        self.input.callback = self._receive_message
        super().__init__()

    def _receive_message(self, message):
        if message.type in ['note_on', 'note_off']:
            self.handle_message(message)


class Harmonizer(MidiBox):
    """
    Harmonizer
    """

    def __init__(self):
        self.name = 'harmonizer'
        self.voices = []
        super().__init__()

    def add_voices(self, message):
        """ add_voices """
        return [message.copy(note=message.note + voice) for voice in self.voices]

    def modifier(self, message):
        return [message, *self.add_voices(message)]


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


class Chopper(MidiBox):
    """
    Chopper
    """

    def __init__(self):
        self.name = 'chopper'
        super().__init__()

    def modifier(self, message):
        pass
