coverage erase
coverage run -m unittest tests.test_midi_box
coverage html --include=lib/*.py --fail-under=85