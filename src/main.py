import uuid
import time

from pydantic import BaseModel, Field, validator

from config import *
from fastapi import FastAPI, Query, Path
from typing import Union, Tuple, Annotated, Literal

from scale import Scale
from valve import Valve

min_steps = 1
max_steps = 16

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
brew_id = None

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


class FilterParams(BaseModel):
    brew_id: str
    @validator('brew_id')
    def brew_id_must_match(cls, v):
        if ' ' not in v:
            raise ValueError('must contain a space')
        return v.title()



@app.post("/valve/acquire")
def acquire_valve(q: str | None = None):
    global brew_id
    if brew_id is None:
        new_id = str(uuid.uuid4())
        brew_id = new_id
        return {"status": "valve acquired", "brew_id": new_id}  # Placeholder response
    else:
        print(f"brew id {brew_id} already acquired")
        return {"status": "valve already acquired"}  # Placeholder response



@app.post("/valve/release")
# TODO accept release brew id and verify matches
def release_valve(q: str | None = None):
    global brew_id
    old_id = brew_id
    brew_id = None
    return {"status": f"valve brew id ${old_id} released"}  # Placeholder response



# TODO should only allow stepping if brew_id is set
@app.post("/valve/forward/{num_steps}")
def step_forward(
        num_steps: Annotated[int, Path(title="number of steps on stepper motor", ge=min_steps, le=max_steps)],
        q: Annotated[str | None, Query(max_length=50)] = None,
):
    print(f"query param: q={q}")
    for i in range(num_steps):
        valve.step_forward()
        time.sleep(0.1)
    return {"status": f"stepped forward {num_steps} step(s)"}  # Placeholder response

@app.post("/valve/backward/{num_steps}")
def step_backward(
        num_steps: Annotated[int, Path(title="number of steps on stepper motor", ge=min_steps, le=max_steps)],
        q: Annotated[str | None, Query(alias="item-query")] = None,
):
    print(q)
    for i in range(num_steps):
        valve.step_backward()
        time.sleep(0.1)
    return {"status": f"stepped backward {num_steps} step(s)"}  # Placeholder response