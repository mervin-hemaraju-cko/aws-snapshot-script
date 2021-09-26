#!/bin/bash

source secret.env

# All Tests
python -m pytest


# Single Files
#python -m pytest test_helper.py
#python -m pytest test_main.py

# Single function
#python -m pytest test_main.py::TestMain::test_get_tasks_NormalData