import time

from config import *
from fastapi import FastAPI
from typing import Union, Tuple

from scale import Scale
from valve import Valve

def initialize_hardware() -> Tuple[Scale, Valve]:
    if COLDBREW_IS_PROD:
        from LunarScale import LunarScale
        from MotorKitValve import MotorKitValve
        s: Scale = LunarScale(COLDBREW_SCALE_MAC_ADDRESS)
        s.connect()
        v: Valve = MotorKitValve()
    else:
        from scale import MockScale
        from valve import MockValve
        s: Scale = MockScale()
        v: Valve= MockValve()
    return s, v

scale, valve = initialize_hardware()

app = FastAPI()

@app.get("/")
def read_root():
    return {"Hello": "World"}

@app.get("/scale")
def read_weight():
    weight = scale.get_weight()
    battery_pct = scale.get_battery_percentage()
    units = scale.get_units()
    return {"weight": weight, "battery_pct": battery_pct, "units": units}  # Placeholder value in grams

@app.post("/valve/forward/{num_steps}")
def step_forward(num_steps: int=1, q: str | None = None):
    for i in range(num_steps):
        valve.step_forward()
        time.sleep(0.1)
    return {"status": f"stepped forward {num_steps} step(s)"}  # Placeholder response

@app.post("/valve/backward/{num_steps}")
def step_backward(num_steps: int=1, q: Union[str, None] = None):
    for i in range(num_steps):
        valve.step_backward()
        time.sleep(0.1)
    return {"status": f"stepped backward {num_steps} step(s)"}  # Placeholder response