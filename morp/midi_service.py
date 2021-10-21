# pylint: disable=no-member broad-except
"""
midi.py
"""
from typing import List, Set, Union
import mido
from .midi_box import MidiBox, MidiIn, MidiOut


class MidiService:
    """MidiService"""

    def __init__(self):
        self._open_inputs = set()
        self._open_outputs = set()
        self._error_inputs = set()
        self._error_outputs = set()

    @property
    def open_inputs(self) -> Set[MidiIn]:
        """Return the set of MidiIns currently in use"""
        return self._open_inputs

    @property
    def error_inputs(self) -> Set[str]:
        """Return the set of input names that encountered an error"""
        return self._error_inputs

    @property
    def open_outputs(self) -> Set[MidiOut]:
        """Return the set of MidiOuts currently in use"""
        return self._open_outputs

    @property
    def error_outputs(self) -> Set[str]:
        """Return the set of output names that encountered an error"""
        return self._error_outputs

    def get_inputs(self) -> Set[str]:
        """Return a set of names available as input devices"""
        return set(mido.get_input_names())

    def get_outputs(self) -> Set[str]:
        """Return a set of names available as output devices"""
        return set(mido.get_output_names())

    def open_input(self, input_name: str) -> Union[MidiIn, None]:
        """Open the requested input device by name, and return a `MidiIn` on success"""
        try:
            new_input = MidiIn(input_name)
            self.error_inputs.discard(input_name)
            self.open_inputs.add(new_input)
            return new_input
        except OSError as error:
            print(error)
            self.error_inputs.add(input_name)
            return None

    def close_input(self, input_name: str) -> None:
        """Close the specified input device by name"""
        for open_input in list(self.open_inputs):
            if open_input.name == input_name:
                open_input.close()
                self.open_inputs.discard(open_input)

    def open_output(self, output_name: str) -> Union[MidiOut, None]:
        """Open the requested output device by name, and return a `MidiOut` on success"""
        try:
            new_output = MidiOut(output_name)
            self.error_outputs.discard(output_name)
            self.open_outputs.add(new_output)
            return new_output
        except Exception:
            self.error_outputs.add(output_name)
            return None

    def close_output(self, output_name: str) -> None:
        """Close the specified output device by name"""
        for open_output in list(self.open_outputs):
            if open_output.name == output_name:
                open_output.close()
                self.open_outputs.discard(open_output)


class Loop:
    """
    Loop
    """

    def __init__(self, boxes: List[MidiBox]):
        self._boxes = boxes or []
        # Connect the interior MidiBoxes to each other
        # The final one is left unconnected so that the Loop may be reused by many MidiBoxes
        for i in range(0, len(boxes) - 1):
            boxes[i].set_outputs([*boxes[i].outputs, boxes[i + 1]])

    @property
    def boxes(self) -> List[MidiBox]:
        """Get a list of the MidiBoxes in this loop"""
        return self._boxes

    def on_message(self, message: mido.Message):
        """ Simply forward the message to the first MidiBox in the loop. """
        if len(self.boxes) > 0:
            self.boxes[0].on_message(message)

    def set_return(self, return_to: MidiBox):
        """ set_return """
        box_count = len(self._boxes)
        if box_count > 0:
            terminus = self._boxes[box_count - 1]
            terminus.is_fx_return = True
            terminus.set_outputs([*return_to.outputs])
