"""
midi_setup.py
"""
# pylint: disable=no-member
import mido
# import rtmidi
from lib.midi_boxes import MidiOut, MidiIn

# rtmidi_out = rtmidi.MidiIn()
# rtmidi_out.open_virtual_port("MORP")


def get_midi_devices():
    """ get_midi_devices """
    in_ports = mido.get_input_names()
    for i, port in enumerate(in_ports):
        print(f"{i+1}: {port}")

    in_choice = in_ports[int(input('Enter input port number: ')) - 1]
    midi_in = MidiIn(in_choice)
    out_ports = mido.get_output_names()
    for i, port in enumerate(out_ports):
        print(f"{i+1}: {port}")

    out_choice = out_ports[int(input('Enter output port number: ')) - 1]
    midi_out = MidiOut(out_choice)

    return (midi_in, midi_out)
