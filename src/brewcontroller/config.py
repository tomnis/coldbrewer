import os

# collect as much raw data as we can
COLDBREW_SCALE_READ_INTERVAL = float(os.getenv("COLDBREW_SCALE_READ_INTERVAL", "0.5"))