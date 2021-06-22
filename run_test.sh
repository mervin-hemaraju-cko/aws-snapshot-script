#!/bin/bash

source secret.env

# All Tests
python -m pytest tests/


# Single Files
#python -m pytest tests/test_helper.py
#python -m pytest tests/test_main.py

# Single function
#python -m pytest tests/test_main.py::TestMain::test_get_tasks_NormalData