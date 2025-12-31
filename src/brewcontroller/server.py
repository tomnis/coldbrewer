import asyncio
import uuid
import time

from contextlib import asynccontextmanager
from fastapi import FastAPI, Query, Path
from pydantic import BaseModel, validator
from typing import Annotated

from ..base.config import *
from ..base.scale import AbstractScale
from ..base.valve import AbstractValve

min_steps = 1
max_steps = 16
cur_brew_id = None

# TODO dependency injection

# TODO rename to create
def create_scale() -> AbstractScale:
    if COLDBREW_IS_PROD:
        print("Initializing production scale...")
        from ..brewcontroller.LunarScale import LunarScale
        s: AbstractScale = LunarScale(COLDBREW_SCALE_MAC_ADDRESS)
    else:
        print("Initializing mock scale...")
        from ..base.scale import MockScale
        s: AbstractScale = MockScale()
    return s


def create_valve() -> AbstractValve:
    if COLDBREW_IS_PROD:
        print("Initializing production valve...")
        from ..brewcontroller.MotorKitValve import MotorKitValve
        v: AbstractValve = MotorKitValve()
    else:
        print("Initializing mock valve...")
        from ..base.valve import MockValve
        v: AbstractValve= MockValve()
    return v


def create_time_series() -> TimeSeries:
    ts =


scale = create_scale()
valve = create_valve()

@asynccontextmanager
async def lifespan(app: FastAPI):
    print("server startup complete")
    yield
    if scale.connected:
        scale.disconnect()
    print("Shutting down, disconnected scale...")
    valve.release()
    print("Shutting down, released valve ...")

app = FastAPI(lifespan=lifespan)


# TODO move this return type to a class or pydantic model
def get_scale_status() -> dict:
    # good enough to support reconnection here. we can just powercycle the scale if anything goes wrong to get back on track
    global scale
    if not scale.connected:
        scale = create_scale()
        scale.connect()

    if scale.connected:
        weight = scale.get_weight()
        battery_pct = scale.get_battery_percentage()
        units = scale.get_units()
        return {"scale.connected": True, "weight": weight, "battery_pct": battery_pct, "units": units}
    else:
        return {"scale.connected": False}

@app.get("/scale")
def read_scale():
    return get_scale_status()




#### VALVE ENDPOINTS ####
class MatchBrewId(BaseModel):
    brew_id: str
    @validator('brew_id')
    def brew_id_must_match(cls, v):
        print(f"cur brew id: {cur_brew_id}")
        if cur_brew_id is None:
            raise ValueError('no brew_id in progress')
        elif v != cur_brew_id:
            raise ValueError('wrong brew_id')
        return v.title()


# Scale task that records data every interval
async def print_task(s):
    global cur_brew_id
    while cur_brew_id is not None:
        items = scale.get_weight()
        print(f"scale weight: {items}")
        weight = items["weight"]

        print('Hello')
        await asyncio.sleep(s)

@app.post("/brew/acquire")
async def start_brew():
    global cur_brew_id
    if cur_brew_id is None:
        new_id = str(uuid.uuid4())
        cur_brew_id = new_id
        # start a scale thread
        asyncio.create_task(print_task(5))
        return {"status": "valve acquired", "brew_id": new_id}  # Placeholder response
    else:
        print(f"brew id {cur_brew_id} already acquired")
        return {"status": "valve already acquired"}  # Placeholder response kkk

@app.post("/brew/release")
async def release_brew(brew_id: Annotated[MatchBrewId, Query()]):
    global cur_brew_id
    old_id = cur_brew_id
    cur_brew_id = None
    return {"status": f"valve brew id ${old_id} released"}  # Placeholder response

@app.post("/brew/kill")
async def end_brew():
    global cur_brew_id
    old_id = cur_brew_id
    cur_brew_id = None
    return {"status": f"valve brew id ${old_id} killed"}  # Placeholder response




@app.get("/brew/status")
def brew_status():
    global cur_brew_id
    if cur_brew_id is None:
        return {"status": "no brew in progress"}
    else:
        flow_rate = None
        return {"status": "brew in progress", "brew_id": cur_brew_id}






@app.post("/valve/forward/{num_steps}")
def step_forward(
        num_steps: Annotated[int, Path(title="number of steps on stepper motor", ge=min_steps, le=max_steps)],
        brew_id: Annotated[MatchBrewId, Query()],
):
    #print(f"cur brew id: {cur_brew_id}")
    #print(f"query param: q={brew_id}")
    for i in range(num_steps):
        valve.step_forward()
        time.sleep(0.1)
    return {"status": f"stepped forward {num_steps} step(s)"}  # Placeholder response

@app.post("/valve/backward/{num_steps}")
def step_backward(
        num_steps: Annotated[int, Path(title="number of steps on stepper motor", ge=min_steps, le=max_steps)],
        brew_id: Annotated[MatchBrewId, Query()],
):
    #print(f"cur brew id: {cur_brew_id}")
    #print(f"query param: q={brew_id}")
    for i in range(num_steps):
        valve.step_backward()
        time.sleep(0.1)
    return {"status": f"stepped backward {num_steps} step(s)"}  # Placeholder response