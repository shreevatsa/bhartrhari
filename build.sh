#!/bin/sh
set -euxo pipefail
python3 gen/data.py && python3 gen/gen.py
