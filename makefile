default: run
export PYTHONPATH := $(shell pwd)
run:
	venv/bin/python game/play.py
