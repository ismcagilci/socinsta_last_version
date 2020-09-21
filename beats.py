#!/usr/bin/env python3

import subprocess

# Simple command
subprocess.call(['celery -A socinsta beat -l info'], shell=True)
