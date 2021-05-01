from copy import deepcopy
from mido import open_output, open_input


class MidiBox:
	def __init__(self, outputs=None):
		self.set_outputs(outputs)
		self._fx_loop = None
		self._is_fx_return = False

	def modifier(self, message):
		return message

	def set_fx_loop(self, loop=None):
		new_loop = deepcopy(loop)
		new_loop._set_return(self)
		self._fx_loop = new_loop

	def set_is_fx_return(self, is_return = True):
		self._is_fx_return = is_return

	def set_outputs(self, outputs=None):
		self._outputs = outputs or []

	def _handle_message(self, message, output):
		if isinstance(message, list):
			for note in message:
				output._on_input(self.modifier(note), self._is_fx_return)
		else:
			output._on_input(self.modifier(message), self._is_fx_return)

	def _on_input(self, message, fx_return=False):
		if self._fx_loop and not fx_return:
			self._fx_loop._handle_message(message)
		elif len(self._outputs) > 0:
			for output in self._outputs:
				self._handle_message(message, output)

	def _on_fx_return(self, message):
		self._on_input(message, True)


class Loop:
	def __init__(self, boxes=[]):
		self._boxes = boxes
		# Connect the interior MidiBoxes to each other
		# The final one is left unconnected so that the Loop may be reused by many MidiBoxes
		for i in range(0, len(boxes) - 1):
			# TODO: merge assigned outputs with pre-existing outputs
			boxes[i].set_outputs([boxes[i + 1]])
	
	def _handle_message(self, message):
		if len(self._boxes) > 0:
			self._boxes[0]._on_input(message)

	def _set_return(self, return_to):
		box_count = len(self._boxes)
		if box_count > 0:
			terminus = self._boxes[box_count - 1]
			terminus.set_is_fx_return(True)
			# TODO: merge assigned outputs with pre-existing outputs
			terminus.set_outputs([return_to])


class MidiOut(MidiBox):
	def __init__(self, output_name):
		self.output = open_output(output_name)
		self.name = output_name
		print('opened {}'.format(output_name))

	def _on_input(self, message, fx_return=False):
		if isinstance(message, list):
			for note in message:
				self.output.send(note)
		else:
			self.output.send(message)

class MidiIn(MidiBox):
	def __init__(self, input_name):
		self.input = open_input(input_name)
		self.input.callback = self._receive_message
		super().__init__()

	def _receive_message(self, message):
		if message.type in ['note_on', 'note_off']:
			self._on_input(message)

class Harmonizer(MidiBox):
	def __init__(self):
		self.name = 'harmonizer'
		self.voices = []
		super().__init__()

	def add_voices(self, message):
		return [message.copy(note = message.note + voice) for voice in self.voices]

	def modifier(self, message):
		return [message, *self.add_voices(message)]


class Shadow(MidiBox):
	def __init__(self):
		self.name ='shadow'
		self.note_cache = []
		self.interval = 3
		self.feedback = 2
		self.decay_factor = 0.3
		super().__init__()


	def modifier(self, message):
		self.note_cache.insert(0, message)
		messages = [message]
		for i in range(self.feedback):
			if i * self.interval < len(self.note_cache):
				toAdd = self.note_cache[i * self.interval]
				messages.append(toAdd.copy(velocity = round(toAdd.velocity * self.decay_factor)))
			else:
				break
		
		if len(self.note_cache) > self.interval * self.feedback:
			self.note_cache.pop()

		return messages