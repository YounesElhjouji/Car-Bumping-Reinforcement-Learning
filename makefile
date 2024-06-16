default: run
export PYTHONPATH := $(shell pwd)
run:
	venv/bin/python ppo/train.py
