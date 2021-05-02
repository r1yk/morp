"""
midi_setup.py
"""
# pylint: disable=no-member
import mido
from lib.midi_boxes import MidiOut, MidiIn


def get_midi_devices():
    """ get_midi_devices """
    in_ports = mido.get_input_names()
    for i, port in enumerate(in_ports):
        print(f"{i+1}: {port}")

    in_choice = in_ports[int(input('Enter input port number: ')) - 1]

    out_ports = mido.get_output_names()
    for i, port in enumerate(out_ports):
        print(f"{i+1}: {port}")

    out_choice = out_ports[int(input('Enter output port number: ')) - 1]

    return (MidiIn(in_choice), MidiOut(out_choice))
