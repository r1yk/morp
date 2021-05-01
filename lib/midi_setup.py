# mido.py
import mido
from lib.midi_boxes import MidiOut, MidiIn

def get_midi_devices():
	in_ports = mido.get_input_names()
	for i in range(len(in_ports)):
		print(f"{i+1}: {in_ports[i]}")

	in_choice = in_ports[int(input('Enter input port number: ')) - 1]

	out_ports = mido.get_output_names()
	for i in range(len(out_ports)):
		print(f"{i+1}: {out_ports[i]}")

	out_choice = out_ports[int(input('Enter output port number: ')) - 1]

	return (MidiIn(in_choice), MidiOut(out_choice))
