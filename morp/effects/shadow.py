"""shadow.py"""
from ..midi_box import MidiBox


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
