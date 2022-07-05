#!/bin/sh
export PYTHONPATH="$(dirname "$(readlink -f "${BASH_SOURCE[0]}" )" )"
LD_LIBRARY_PATH=/usr/local/cuda-10.2/targets/x86_64-linux/lib PYOPENGL_PLATFORM=egl python meshroom/ui
