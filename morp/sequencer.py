"""
sequencer.py
"""
from typing import Union
from mido import Message
from .midi_box import MidiBox, MidiIn


class Sequencer(MidiBox):
    """
    Sequencer
    """

    def __init__(self):
        self._clock_source = None
        self._playing = False
        self._recording = False
        # Default to 4/4 time signature
        self._count = 4
        self._subdivision = 4
        self._clocks_per_measure = 24 * self._count
        self._clock_count = 0
        self._measure = 0
        self._count_in = 2
        self._pattern = None
        self._recording_pattern = {}
        # 6 clocks per 16th note
        self._quantize_resolution = 6
        super().__init__()

    @property
    def clock_source(self) -> Union[MidiIn, None]:
        """ clock_source getter """
        return self._clock_source

    @clock_source.setter
    def clock_source(self, clock_source: MidiIn):
        self._clock_source = clock_source

    @property
    def count(self) -> int:
        """Get how many beats are in a measure (numerator of the time signature)"""
        return self._count

    @count.setter
    def count(self, count: int):
        self._count = count
        self._clocks_per_measure = 24 * self._count

    @property
    def subdivision(self) -> int:
        """Get the demoninator in the time signature"""
        return self._subdivision

    @subdivision.setter
    def subdivision(self, subdivision: int):
        self._subdivision = subdivision

    @property
    def pattern(self) -> Union[dict, None]:
        """Get the messages currently recorded for playback"""
        return self._pattern

    @pattern.setter
    def pattern(self, new_pattern: dict):
        last_message = max(new_pattern.keys())
        self._pattern = {
            'notes': new_pattern,
            'measure_count': (last_message // self._clocks_per_measure) + 1
        }

    @property
    def playing(self) -> bool:
        """Get whether the sequencer is actively playing its pattern"""
        return self._playing

    @playing.setter
    def playing(self, playing: bool):
        self._recording = not playing
        self._playing = playing

    @property
    def recording(self) -> bool:
        """Get whether the sequencer is currently recording new messages into its pattern"""
        return self._recording

    @recording.setter
    def recording(self, recording: bool):
        self._playing = not recording
        self._recording = recording

    def load(self, data: dict):
        """Load messages previously stored as JSON"""

    def on_note(self, message):
        super().on_note(message)
        if self.recording and not self.is_fx_return:
            notes = self._recording_pattern.get(self._clock_count, [])
            notes.append(message.copy())
            self._recording_pattern[self._clock_count] = notes

    def _metronome(self, message):
        super().route_message(message, through=True)

    def on_clock(self, _):
        if self.playing:
            messages = self.pattern.get('notes').get(self._clock_count)
            for message in messages or []:
                super().on_message(message.copy())
        if self.recording:
            position = self._clock_count % 24
            if position == 0:
                self._metronome(Message('note_on', note=100, velocity=100))
            if position == 6:
                self._metronome(Message('note_off', note=100, velocity=100))

        self._clock_count += 1
        if self.playing:
            self._clock_count %= self.pattern.get(
                'measure_count', 1) * self._clocks_per_measure

    def record(self):
        """record"""
        self.recording = True

    def play(self):
        """play"""
        self.reset()
        self.playing = True

    def stop(self):
        """stop"""
        if self.recording:
            self.pattern = self._quantize(self._recording_pattern)
        self.playing = False
        self.reset()

    def reset(self):
        """reset"""
        self._clock_count = 0
        self._measure = 0

    # After recording a pattern, quantize it by the specified resolution
    # 6 = sixteenth note
    # 12 = 8th note
    # 24 = quarter note
    def _quantize(self, pattern: dict):
        """_quantize"""
        quantized = {}
        for clock_time in pattern:
            position = clock_time % self._quantize_resolution
            nearest_neighbor = \
                (clock_time - position if position <= self._quantize_resolution // 2
                 else clock_time + (self._quantize_resolution - position)) \
                - (self._count_in * self._clocks_per_measure)

            # Don't clobber anything that's already in the nearest_neighbor slot
            notes = quantized.get(nearest_neighbor, [])
            quantized[nearest_neighbor] = [*notes, *pattern[clock_time]]

        return quantized

    # The re-imagining of the oldschool MORP thing where you enter notes one-by-one
    # This would allow the user to configure the resolution as they go
    def dictate(self):
        """dictate"""
