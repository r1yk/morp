# morp
`morp` is an easy-to-use utility for managing MIDI inputs and outputs, and for manipulating the messages sent between them. It is built on top of the open source [Mido](https://github.com/mido/mido) project.

`morp` can be used as a virtual patch bay between MIDI-compliant entities like physical MIDI controllers connected via USB, and software instruments in your DAW of choice. In addition, morp provides MIDI "effects boxes" that are analogous to the effects pedals an electric guitarist might use. However, instead of manipulating audio signals, `morp`'s effects manipulate the MIDI messages themselves before they're synthesized as audio. `morp` provides a few default effects boxes that I thought were neat, and also allows the user to create their own custom effects.

## Installation
```sh
pip install git+https://github.com/r1yk/morp.git
```

## Examples

### Opening MIDI input devices

```python
from morp import MidiService
midi_service = MidiService()

available_inputs = midi_service.get_inputs()
> ['My Hardware Device Input', 'My Software Instrument Input']

midi_input = midi_service.open_input('My Software Device Input')
```

### Opening MIDI output devices
```python
available_outputs = midi_service.get_outputs()
> ['My Hardware Device Output', 'My Software Instrument Output']

midi_output = midi_service.open_output('My Hardware Device Output')
```

### Connecting inputs to outputs
```python
midi_input.set_outputs([midi_output])
```

### Adding an effects loop
```python
from morp import EffectsLoop
from morp.effects import Autotune, Harmonizer

# Fix all notes to a Cminor7 arpeggio 
# where 0 = C, 3 = Eb, 7 = G, 10 = Bb
cminor7 = Autotune(scale={0, 3, 7, 10})

# For all incoming notes, add another note an octave lower
suboctave = Harmonizer(voices={-12})

# Create an effects loop from these 2 effects
fx_loop = EffectsLoop([cminor7, suboctave])

# Assign the new effects loop to the MIDI input
midi_input.assign_fx_loop(fx_loop)
```

### Creating custom effects
A custom effect can be created quickly by creating a subclass of `MidiBox` and writing new implementations of its methods. For example, your custom effect may need to override `MidiBox.on_note_on` but not `MidiBox.on_note_off`. Below is an example of a custom effect that simply reduces the pitch of all incoming notes by a half-step:
```python
from morp import MidiBox

class CustomEffect(MidiBox):
    def on_note(self, message):
        half_step_down = message.copy(note=message.note - 1)
        super().on_note(half_step_down)

custom_effect = CustomEffect()
custom_fx_loop = EffectsLoop([custom_effect])
midi_input.assign_fx_loop(custom_fx_loop)
```
Refer to the `MidiBox` class in `morp/effects/midi_box.py` to see all the MIDI message handlers that are available to be overridden!

### Running tests
```sh
python3 -m unittest discover -v -s ./tests -p test_*.py
```