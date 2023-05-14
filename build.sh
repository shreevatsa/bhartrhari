#!/bin/sh
set -eux
python3 gen/data.py && python3 gen/gen.py
