#!/usr/bin/env python3

import subprocess

# Simple command
subprocess.call(['celery -A socinsta worker -l info -Q deneme1,volta'], shell=True)
