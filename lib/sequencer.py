"""
sequencer.py
"""
from mido import Message
from lib.midi import MidiIn
from lib.midi_box import MidiBox


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
    def clock_source(self):
        """ clock_source getter """
        return self._clock_source

    @clock_source.setter
    def clock_source(self, clock_source: MidiIn):
        self._clock_source = clock_source

    @property
    def count(self):
        """ count getter """
        return self._count

    @count.setter
    def count(self, count):
        self._count = count
        self._clocks_per_measure = 24 * self._count

    @property
    def subdivision(self):
        """ subdivision getter """
        return self._subdivision

    @subdivision.setter
    def subdivision(self, subdivision):
        self._subdivision = subdivision

    @property
    def pattern(self):
        """ pattern getter """
        return self._pattern

    @pattern.setter
    def pattern(self, new_pattern):
        last_message = max(new_pattern.keys())
        self._pattern = {
            'notes': new_pattern,
            'measure_count': (last_message // self._clocks_per_measure) + 1
        }

    @property
    def playing(self):
        """ playing getter """
        return self._playing

    @playing.setter
    def playing(self, is_playing: bool):
        self._recording = not is_playing
        self._playing = is_playing

    @property
    def recording(self):
        """ recording getter """
        return self._recording

    @recording.setter
    def recording(self, is_recording: bool):
        self._playing = not is_recording
        self._recording = is_recording

    def load(self, data):
        """load"""

    def on_note(self, message, fx_return=False):
        super().on_note(message, fx_return)
        if self.recording and not fx_return:
            notes = self._recording_pattern.get(self._clock_count, [])
            notes.append(message.copy())
            self._recording_pattern[self._clock_count] = notes

    def _metronome(self, message):
        super().route_message(message, True)

    def on_clock(self, _, fx_return=False):
        if self.playing:
            messages = self.pattern.get('notes').get(self._clock_count)
            for message in messages or []:
                super().on_message(message.copy(), fx_return)
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
