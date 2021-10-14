"""Freeze effect"""
from mido import Message
from ..midi_box import MidiBox


class Freeze(MidiBox):
    """
    Freeze
    """

    def __init__(self):
        self._frozen = False
        self._frozen_notes = set()
        super().__init__()

    def _cancel_freeze(self) -> None:
        for note in self._frozen_notes:
            super().on_note_off(Message('note_off', note=note))
        self._frozen = False
        self._notes_on.clear()
        self._frozen_notes.clear()

    def on_note_on(self, message) -> None:
        """If frozen, turn off any frozen notes to make way for this new one."""
        if self._frozen:
            self._cancel_freeze()

        super().on_note_on(message)

    def on_note_off(self, message) -> None:
        """
        Suppress a call to `super().on_note_off`.
        If this was the last note in a group to be released, begin the freeze.
        """
        self._frozen_notes.add(message.note)
        if len(self._notes_on) == 1:
            self._frozen = True
        self._notes_on.discard(message.note)
