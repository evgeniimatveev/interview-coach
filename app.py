"""HF Spaces entry point — seeds demo data then runs the dashboard."""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from seed_demo import seed_if_empty
seed_if_empty()

exec(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "dashboard.py")).read())
