"""Harmonizer effects"""
from typing import List, Set
from mido import Message
from ..midi_box import MidiBox


class Autotune(MidiBox):
    """
    `Autotune` works like the name-brand equivalent. A `scale` can be provided that restricts
    the pitches that are allowed. Each member of `scale` should be a scale tone between 0-12 where
    0 corresponds to C, 3 corresponds to Eb, etc.

    When `autocorrect=True` is used, notes that do not fall within the scale will be "rounded"
    to their nearest neighbor within the scale.

    When `autocorrect=False` is used, notes that do not fall within the scale are ignored entirely.
    """

    def __init__(self, scale: Set[int] = None, autocorrect: bool = True):
        self._scale = scale or set()
        self._autocorrect = autocorrect
        super().__init__()

    @property
    def scale(self) -> set:
        """Return the set of allowable scale tones."""
        return self._scale

    @scale.setter
    def scale(self, scale: Set[int]) -> None:
        self._scale = set(scale)

    @property
    def autocorrect(self) -> bool:
        """Return whether `autocorrect` is currently on."""
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
    `Harmonizer is a MIDI effect that overlays additional notes upon receiving
    `note_on` messages.
    """

    def __init__(self, voices: Set[int]):
        self._voices = voices or set()
        super().__init__()

    @property
    def voices(self) -> Set[int]:
        """Return the current voices to overlay on incoming messages"""
        return self._voices

    @voices.setter
    def voices(self, voices: Set[int]):
        self._voices = voices

    def modifier(self, message: Message) -> List[Message]:
        return [message, *[message.copy(note=message.note + voice) for voice in self.voices]]
