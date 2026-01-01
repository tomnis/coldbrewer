from abc import ABC, abstractmethod


from dataclasses import dataclass
from enum import Enum
from typing import Tuple

from config import *
from appserver.config import *

from appserver.config import COLDBREW_VALVE_INTERVAL_SECONDS


class ValveCommand(Enum):
    NOOP = 0
    FORWARD = 1
    BACKWARD = 2

@dataclass
class BrewStatusRecord:
    timestamp: float
    flow_rate: float
    target_flow_rate: float
    current_weight: float
    step_taken: int


class AbstractBrewStrategy(ABC):
    """encapsulates a brewing strategy for controlling the brew process. assumes that lock strategy has already been handled"""

    @abstractmethod
    def step(self, flow_rate: float) -> Tuple[BrewStatusRecord, int]:
        """Perform a single step in the brewing strategy. """
        pass


class DefaultBrewStrategy(AbstractBrewStrategy):

    def __init__(self, target_flow_rate=COLDBREW_TARGET_FLOW_RATE, interval=COLDBREW_VALVE_INTERVAL_SECONDS, epsilon=COLDBREW_EPSILON):
        self.target_flow_rate = target_flow_rate
        self.interval = interval
        self.epsilon = epsilon

    def step(self, current_flow_rate: float) -> Tuple[ValveCommand, int]:
        """Perform a single step in the default brewing strategy."""
        # return valve command, and sleep time
        print("====")
        print("Current flow rate:", current_flow_rate)
        if current_flow_rate is None:
            print("result is none")
            return ValveCommand.NOOP, self.interval

        elif abs(self.target_flow_rate - current_flow_rate) <= self.epsilon:
            print("just right")
            return ValveCommand.NOOP, self.interval * 2
            time.sleep(interval * 2)
        # TODO should consider microadjustments here
        elif current_flow_rate <= self.target_flow_rate:
            print("too slow")
            return ValveCommand.FORWARD, self.interval
        else:
            print("too fast")
            return ValveCommand.BACKWARD, self.interval