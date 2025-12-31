import os

# TODO probably want a better name for this
COLDBREW_VALVE_URL = os.environ.get('COLDBREW_VALVE_URL', 'http://localhost:8000')
print(f"COLDBREW_VALVE_URL = {COLDBREW_VALVE_URL}")

COLDBREW_TARGET_FLOW_RATE = float(os.environ.get('COLDBREW_TARGET_FLOW_RATE', '0.05'))
COLDBREW_EPSILON = float(os.environ.get('COLDBREW_EPSILON', '0.008'))
COLDBREW_VALVE_INTERVAL_SECONDS = int(os.environ.get('COLDBREW_VALVE_INTERVAL_SECONDS', '60'))