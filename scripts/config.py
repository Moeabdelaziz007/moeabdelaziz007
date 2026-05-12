import os

# Base directory is the parent of the scripts directory
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Common directories
ASSETS_DIR = os.path.join(PROJECT_ROOT, 'assets')

# Common files
README_PATH = os.path.join(PROJECT_ROOT, 'README.md')

# Telemetry Tags
START_TAG = '<!-- START_LIVE_DATA -->'
END_TAG = '<!-- END_LIVE_DATA -->'
