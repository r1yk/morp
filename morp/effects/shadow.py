"""shadow.py"""
from typing import List
import mido
from ..midi_box import MidiBox


class Shadow(MidiBox):
    """
    `Shadow` is a MIDI effect that behaves a bit like a delay. The principal difference
    is that unlike a delay, `Shadow` does not have an interval of time that defines when
    a note will be echoed back. Instead, `Shadow` can serve requests like "echo this note
    back to me after 3 additional notes have passed".
    """

    def __init__(self, period: int = 4, decay: float = 0.5, repeat: int = 2):
        self._period = period
        self._decay = decay
        self._repeat = repeat
        self._length = period * repeat
        self._message_cache = []
        super().__init__()

    @property
    def decay(self):
        """Get how much each successive appearance of a note should have its velocity reduced by"""
        return self._decay

    @decay.setter
    def decay(self, decay: float):
        self._decay = decay

    @property
    def period(self) -> int:
        """Get the amount of notes that must be received before the first one is echoed back"""
        return self._period

    @period.setter
    def period(self, period: int):
        self._period = period
        self._length = period * self.repeat

    @property
    def repeat(self) -> int:
        """Get the maximum amount of times that a given note can be echoed back"""
        return self._repeat

    @repeat.setter
    def repeat(self, repeat: int):
        self._repeat = repeat
        self._length = self.period * repeat

    def modifier(self, message: mido.Message) -> List[mido.Message]:
        messages = [message]
        for i in range(self.period - 1, len(self._message_cache), self.period):
            self._message_cache[i].velocity = round(
                self._message_cache[i].velocity * (1 - self.decay))
            messages.append(self._message_cache[i])
        self._message_cache.insert(0, message)
        if len(self._message_cache) > self._length:
            self._message_cache.pop()
        return messages
