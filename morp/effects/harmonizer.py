"""Harmonizer effects"""
from mido import Message
from ..midi_box import MidiBox


class Autotune(MidiBox):
    """Autotune"""

    def __init__(self, scale: set = None, autocorrect: bool = True):
        self._scale = scale or set()
        self._autocorrect = autocorrect
        super().__init__()

    @property
    def scale(self) -> set:
        """Return the scale."""
        return self._scale

    @scale.setter
    def scale(self, scale: set) -> None:
        self._scale = set(scale)

    @property
    def autocorrect(self) -> bool:
        """Return whether autocorrect is currently on."""
        return self._autocorrect

    @autocorrect.setter
    def autocorrect(self, autocorrect: bool) -> None:
        self._autocorrect = autocorrect

    def on_note(self, message: Message) -> None:
        """Restrict the note to the provided scale, and proceed as normal."""
        note = message.note % 12
        if note in self.scale:
            super().on_note(message)
        elif self.autocorrect:
            # Find the scale note that is closest to this note in either direction

            new_note = message.note + \
                min([scale_note - note for scale_note in self.scale], key=abs)
            super().on_note(message.copy(note=new_note))


class Harmonizer(MidiBox):
    """
    Harmonizer
    """

    def __init__(self, voices=None):
        self.voices = voices or []
        super().__init__()

    def modifier(self, message):
        return [message, *[message.copy(note=message.note + voice) for voice in self.voices]]
