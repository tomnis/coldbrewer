import os

# TODO probably want a better name for this
COLDBREW_VALVE_URL = os.environ.get('COLDBREW_VALVE_URL', 'http://localhost:8000')
print(f"COLDBREW_VALVE_URL = {COLDBREW_VALVE_URL}")

# the target flow rate in grams per second. Adjust the valve to maintain this flow rate.
COLDBREW_TARGET_FLOW_RATE = float(os.environ.get('COLDBREW_TARGET_FLOW_RATE', '0.05'))
print(f"COLDBREW_TARGET_FLOW_RATE = {COLDBREW_TARGET_FLOW_RATE}")

COLDBREW_EPSILON = float(os.environ.get('COLDBREW_EPSILON', '0.008'))

# how often to check the flow rate and adjust the valve (in seconds)
COLDBREW_VALVE_INTERVAL_SECONDS = int(os.environ.get('COLDBREW_VALVE_INTERVAL_SECONDS', '60'))
print(f"COLDBREW_VALVE_INTERVAL_SECONDS = {COLDBREW_VALVE_INTERVAL_SECONDS}")