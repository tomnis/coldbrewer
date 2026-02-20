from abc import ABC, abstractmethod
from typing import Tuple, Optional, Dict, Any, Type

from config import *
from model import *


# Strategy Registry
BREW_STRATEGY_REGISTRY: Dict[BrewStrategyType, Type["AbstractBrewStrategy"]] = {}


def register_strategy(strategy_type: BrewStrategyType):
    """Decorator to register a brew strategy."""
    def decorator(cls: Type["AbstractBrewStrategy"]) -> Type["AbstractBrewStrategy"]:
        BREW_STRATEGY_REGISTRY[strategy_type] = cls
        return cls
    return decorator


def create_brew_strategy(strategy_type: BrewStrategyType, params: Dict[str, Any], base_params: Dict[str, Any]) -> "AbstractBrewStrategy":
    """Factory function to create a brew strategy from the registry."""
    if strategy_type not in BREW_STRATEGY_REGISTRY:
        raise ValueError(f"Unknown strategy type: {strategy_type}. Available: {list(BREW_STRATEGY_REGISTRY.keys())}")
    return BREW_STRATEGY_REGISTRY[strategy_type].from_params(params, base_params)


class AbstractBrewStrategy(ABC):
    """encapsulates a brewing strategy for controlling the brew process. assumes that lock strategy has already been handled"""

    @abstractmethod
    def step(self, flow_rate: Optional[float], current_weight: Optional[float]) -> Tuple[ValveCommand, int]:
        """Perform a single step in the brewing strategy. """
        pass

    @classmethod
    @abstractmethod
    def get_params_schema(cls) -> Dict[str, Any]:
        """Return JSON schema for strategy-specific parameters."""
        pass

    @classmethod
    @abstractmethod
    def from_params(cls, strategy_params: Dict[str, Any], base_params: Dict[str, Any]) -> "AbstractBrewStrategy":
        """Create strategy instance from strategy params and base params."""
        pass


@register_strategy(BrewStrategyType.DEFAULT)
class DefaultBrewStrategy(AbstractBrewStrategy):
    """A simple default brewing strategy, naively opening or closing the valve based on the current flow rate."""

    def __init__(self, target_flow_rate: float = None, scale_interval: float = None, valve_interval: float = None, 
                 epsilon: float = None, target_weight: float = None, vessel_weight: float = None):
        # Set defaults
        if target_flow_rate is None:
            target_flow_rate = COLDBREW_TARGET_FLOW_RATE
        if scale_interval is None:
            scale_interval = COLDBREW_SCALE_READ_INTERVAL
        if valve_interval is None:
            valve_interval = COLDBREW_VALVE_INTERVAL_SECONDS
        if epsilon is None:
            epsilon = COLDBREW_EPSILON
        if target_weight is None:
            target_weight = COLDBREW_TARGET_WEIGHT_GRAMS
        if vessel_weight is None:
            vessel_weight = COLDBREW_VESSEL_WEIGHT_GRAMS
        
        self.target_flow_rate = target_flow_rate
        self.scale_interval = scale_interval
        self.valve_interval = valve_interval
        self.epsilon = epsilon
        self.target_weight = target_weight
        self.vessel_weight = vessel_weight
        self.coffee_target = target_weight - vessel_weight

    @classmethod
    def get_params_schema(cls) -> Dict[str, Any]:
        """Return JSON schema for default strategy parameters (none needed)."""
        return {}

    @classmethod
    def from_params(cls, strategy_params: Dict[str, Any], base_params: Dict[str, Any]) -> "DefaultBrewStrategy":
        return DefaultBrewStrategy(
            target_flow_rate=base_params.get("target_flow_rate", COLDBREW_TARGET_FLOW_RATE),
            scale_interval=base_params.get("scale_interval", COLDBREW_SCALE_READ_INTERVAL),
            valve_interval=base_params.get("valve_interval", COLDBREW_VALVE_INTERVAL_SECONDS),
            epsilon=base_params.get("epsilon", COLDBREW_EPSILON),
            target_weight=base_params.get("target_weight", COLDBREW_TARGET_WEIGHT_GRAMS),
            vessel_weight=base_params.get("vessel_weight", COLDBREW_VESSEL_WEIGHT_GRAMS),
        )

    @classmethod
    def from_request(cls, req: StartBrewRequest) -> "DefaultBrewStrategy":
        return DefaultBrewStrategy(
            target_flow_rate=req.target_flow_rate,
            scale_interval=req.scale_interval,
            valve_interval=req.valve_interval,
            epsilon=req.epsilon,
            target_weight=req.target_weight,
            vessel_weight=req.vessel_weight,
        )

    def step(self, current_flow_rate: Optional[float], current_weight: Optional[float]) -> Tuple[ValveCommand, int]:
        """Perform a single step in the default brewing strategy."""
        coffee_weight = (current_weight - self.vessel_weight) if current_weight is not None else None
        if coffee_weight is not None and coffee_weight >= self.coffee_target:
            logger.info(f"target weight reached: {coffee_weight}g (coffee) >= {self.coffee_target}g (coffee target)")
            return ValveCommand.STOP, 0
        
        current_flow_rate_str = "None" if current_flow_rate is None else f"{current_flow_rate:.4f}g/s"
        msg = f"current flow rate: {current_flow_rate_str}"
        if current_flow_rate is None:
            logger.info("result is none")
            return ValveCommand.NOOP, self.valve_interval
        elif abs(self.target_flow_rate - current_flow_rate) <= self.epsilon:
            logger.info(f"{msg} (just right)")
            return ValveCommand.NOOP, self.valve_interval * 2
        elif current_flow_rate <= self.target_flow_rate:
            logger.info(f"{msg} (too slow)")
            return ValveCommand.FORWARD, self.valve_interval
        else:
            logger.info(f"{msg} (too fast)")
            return ValveCommand.BACKWARD, self.valve_interval


@register_strategy(BrewStrategyType.PID)
class PIDBrewStrategy(AbstractBrewStrategy):
    """PID (Proportional-Integral-Derivative) controller for flow rate stabilization."""

    def __init__(self, target_flow_rate: float, scale_interval: float, valve_interval: float,
                 target_weight: float, vessel_weight: float,
                 kp: float, ki: float, kd: float,
                 output_min: float = -10.0, output_max: float = 10.0,
                 integral_limit: float = 100.0):
        self.target_flow_rate = target_flow_rate
        self.scale_interval = scale_interval
        self.valve_interval = valve_interval
        self.target_weight = target_weight
        self.vessel_weight = vessel_weight
        self.coffee_target = target_weight - vessel_weight
        
        # PID parameters
        self.kp = kp
        self.ki = ki
        self.kd = kd
        
        # PID state
        self.integral = 0.0
        self.prev_error = 0.0
        self.prev_timestamp = None
        
        # Output limits
        self.output_min = output_min
        self.output_max = output_max
        self.integral_limit = integral_limit

    @classmethod
    def get_params_schema(cls) -> Dict[str, Any]:
        return {
            "kp": {"type": "number", "default": 1.0, "label": "Proportional Gain (Kp)",
                   "description": "Controls response to current error"},
            "ki": {"type": "number", "default": 0.1, "label": "Integral Gain (Ki)",
                   "description": "Controls response to accumulated error"},
            "kd": {"type": "number", "default": 0.05, "label": "Derivative Gain (Kd)",
                   "description": "Controls response to rate of error change"},
            "output_min": {"type": "number", "default": -10.0, "label": "Output Min"},
            "output_max": {"type": "number", "default": 10.0, "label": "Output Max"},
            "integral_limit": {"type": "number", "default": 100.0, "label": "Integral Limit"},
        }

    @classmethod
    def from_params(cls, strategy_params: Dict[str, Any], base_params: Dict[str, Any]) -> "PIDBrewStrategy":
        return PIDBrewStrategy(
            target_flow_rate=base_params.get("target_flow_rate", COLDBREW_TARGET_FLOW_RATE),
            scale_interval=base_params.get("scale_interval", COLDBREW_SCALE_READ_INTERVAL),
            valve_interval=base_params.get("valve_interval", COLDBREW_VALVE_INTERVAL_SECONDS),
            target_weight=base_params.get("target_weight", COLDBREW_TARGET_WEIGHT_GRAMS),
            vessel_weight=base_params.get("vessel_weight", COLDBREW_VESSEL_WEIGHT_GRAMS),
            kp=strategy_params.get("kp", 1.0),
            ki=strategy_params.get("ki", 0.1),
            kd=strategy_params.get("kd", 0.05),
            output_min=strategy_params.get("output_min", -10.0),
            output_max=strategy_params.get("output_max", 10.0),
            integral_limit=strategy_params.get("integral_limit", 100.0),
        )

    def _compute_pid(self, error: float, dt: float) -> float:
        """Compute PID output."""
        # Proportional term
        p_term = self.kp * error
        
        # Integral term with anti-windup
        self.integral += error * dt
        self.integral = max(-self.integral_limit, min(self.integral_limit, self.integral_limit))
        i_term = self.ki * self.integral
        
        # Derivative term
        if dt > 0:
            d_term = self.kd * (error - self.prev_error) / dt
        else:
            d_term = 0.0
        
        # Total output
        output = p_term + i_term + d_term
        output = max(self.output_min, min(self.output_max, output))
        
        return output

    def step(self, current_flow_rate: Optional[float], current_weight: Optional[float]) -> Tuple[ValveCommand, int]:
        """Perform a single step using PID control."""
        import time
        current_time = time.time()
        
        # Check target weight
        coffee_weight = (current_weight - self.vessel_weight) if current_weight is not None else None
        if coffee_weight is not None and coffee_weight >= self.coffee_target:
            logger.info(f"target weight reached: {coffee_weight}g >= {self.coffee_target}g")
            return ValveCommand.STOP, 0
        
        if current_flow_rate is None:
            logger.info("flow rate unavailable, noop")
            return ValveCommand.NOOP, self.valve_interval
        
        # Calculate error
        error = self.target_flow_rate - current_flow_rate
        
        # Calculate time delta
        if self.prev_timestamp is not None:
            dt = current_time - self.prev_timestamp
        else:
            dt = self.valve_interval
        
        # Compute PID output
        output = self._compute_pid(error, dt)
        
        # Update state
        self.prev_error = error
        self.prev_timestamp = current_time
        
        # Map output to valve command
        # Positive output = need more flow = open valve (FORWARD)
        # Negative output = too much flow = close valve (BACKWARD)
        logger.info(f"PID: target={self.target_flow_rate:.4f}, current={current_flow_rate:.4f}, "
                   f"error={error:.4f}, output={output:.4f}")
        
        # Use a threshold to determine direction
        # Small outputs within deadband = no action
        deadband = 0.1
        if abs(output) < deadband:
            return ValveCommand.NOOP, self.valve_interval * 2
        elif output > 0:
            return ValveCommand.FORWARD, self.valve_interval
        else:
            return ValveCommand.BACKWARD, self.valve_interval


class KalmanFilter:
    """
    A simple 1D Kalman Filter for smoothing flow rate measurements.
    
    State: x = flow rate (g/s)
    Process model: x_k = x_{k-1} + w (random walk)
    Measurement model: z_k = x_k + v (noisy observation)
    
    Parameters:
        q: Process noise covariance (how much the flow naturally varies)
        r: Measurement noise covariance (how noisy our sensor readings are)
    """
    
    def __init__(self, q: float = 0.001, r: float = 0.1, initial_estimate: float = 0.0, initial_error: float = 1.0):
        self.q = q  # Process noise covariance
        self.r = r  # Measurement noise covariance
        
        self.x = initial_estimate  # Current state estimate
        self.p = initial_error      # Current estimate error covariance
        self.is_initialized = initial_error < 1e9  # Have we received our first measurement?
    
    def update(self, measurement: float) -> float:
        """
        Update the filter with a new measurement.
        
        Args:
            measurement: The raw flow rate reading from the sensor
            
        Returns:
            The filtered (smoothed) flow rate estimate
        """
        if measurement is None:
            return self.x
        
        if not self.is_initialized:
            # First measurement - just use it as our initial estimate
            self.x = measurement
            self.p = self.r
            self.is_initialized = True
            return self.x
        
        # Prediction step: predict current state and error
        # Since we're using a random walk model, x_pred = x_prev
        x_pred = self.x
        p_pred = self.p + self.q
        
        # Update step: incorporate the measurement
        # Kalman gain
        k = p_pred / (p_pred + self.r)
        
        # Update state estimate
        self.x = x_pred + k * (measurement - x_pred)
        
        # Update error estimate
        self.p = (1 - k) * p_pred
        
        return self.x
    
    def reset(self):
        """Reset the filter to its initial state."""
        self.x = 0.0
        self.p = 1.0
        self.is_initialized = False


@register_strategy(BrewStrategyType.KALMAN_PID)
class KalmanPIDBrewStrategy(AbstractBrewStrategy):
    """
    PID controller with Kalman Filter for flow rate stabilization.
    
    Uses a Kalman Filter to smooth out noisy scale readings before
    passing them to the PID controller. This reduces jitter and
    provides more stable control.
    """
    
    def __init__(self, target_flow_rate: float, scale_interval: float, valve_interval: float,
                 target_weight: float, vessel_weight: float,
                 kp: float, ki: float, kd: float,
                 q: float, r: float,
                 output_min: float = -10.0, output_max: float = 10.0,
                 integral_limit: float = 100.0):
        self.target_flow_rate = target_flow_rate
        self.scale_interval = scale_interval
        self.valve_interval = valve_interval
        self.target_weight = target_weight
        self.vessel_weight = vessel_weight
        self.coffee_target = target_weight - vessel_weight
        
        # PID parameters
        self.kp = kp
        self.ki = ki
        self.kd = kd
        
        # PID state
        self.integral = 0.0
        self.prev_error = 0.0
        self.prev_timestamp = None
        
        # Output limits
        self.output_min = output_min
        self.output_max = output_max
        self.integral_limit = integral_limit
        
        # Kalman filter for smoothing flow rate
        self.kalman = KalmanFilter(q=q, r=r, initial_estimate=target_flow_rate)

    @classmethod
    def get_params_schema(cls) -> Dict[str, Any]:
        return {
            "kp": {"type": "number", "default": 1.0, "label": "Proportional Gain (Kp)",
                   "description": "Controls response to current error"},
            "ki": {"type": "number", "default": 0.1, "label": "Integral Gain (Ki)",
                   "description": "Controls response to accumulated error"},
            "kd": {"type": "number", "default": 0.05, "label": "Derivative Gain (Kd)",
                   "description": "Controls response to rate of error change"},
            "q": {"type": "number", "default": 0.001, "label": "Kalman Process Noise (Q)",
                   "description": "How much the flow naturally varies. Higher = more responsive to changes"},
            "r": {"type": "number", "default": 0.1, "label": "Kalman Measurement Noise (R)",
                   "description": "How noisy the sensor readings are. Higher = more smoothing"},
            "output_min": {"type": "number", "default": -10.0, "label": "Output Min"},
            "output_max": {"type": "number", "default": 10.0, "label": "Output Max"},
            "integral_limit": {"type": "number", "default": 100.0, "label": "Integral Limit"},
        }

    @classmethod
    def from_params(cls, strategy_params: Dict[str, Any], base_params: Dict[str, Any]) -> "KalmanPIDBrewStrategy":
        return KalmanPIDBrewStrategy(
            target_flow_rate=base_params.get("target_flow_rate", COLDBREW_TARGET_FLOW_RATE),
            scale_interval=base_params.get("scale_interval", COLDBREW_SCALE_READ_INTERVAL),
            valve_interval=base_params.get("valve_interval", COLDBREW_VALVE_INTERVAL_SECONDS),
            target_weight=base_params.get("target_weight", COLDBREW_TARGET_WEIGHT_GRAMS),
            vessel_weight=base_params.get("vessel_weight", COLDBREW_VESSEL_WEIGHT_GRAMS),
            kp=strategy_params.get("kp", 1.0),
            ki=strategy_params.get("ki", 0.1),
            kd=strategy_params.get("kd", 0.05),
            q=strategy_params.get("q", 0.001),
            r=strategy_params.get("r", 0.1),
            output_min=strategy_params.get("output_min", -10.0),
            output_max=strategy_params.get("output_max", 10.0),
            integral_limit=strategy_params.get("integral_limit", 100.0),
        )

    def _compute_pid(self, error: float, dt: float) -> float:
        """Compute PID output."""
        # Proportional term
        p_term = self.kp * error
        
        # Integral term with anti-windup
        self.integral += error * dt
        self.integral = max(-self.integral_limit, min(self.integral_limit, self.integral_limit))
        i_term = self.ki * self.integral
        
        # Derivative term
        if dt > 0:
            d_term = self.kd * (error - self.prev_error) / dt
        else:
            d_term = 0.0
        
        # Total output
        output = p_term + i_term + d_term
        output = max(self.output_min, min(self.output_max, output))
        
        return output

    def step(self, current_flow_rate: Optional[float], current_weight: Optional[float]) -> Tuple[ValveCommand, int]:
        """Perform a single step using Kalman-filtered PID control."""
        import time
        current_time = time.time()
        
        # Check target weight
        coffee_weight = (current_weight - self.vessel_weight) if current_weight is not None else None
        if coffee_weight is not None and coffee_weight >= self.coffee_target:
            logger.info(f"target weight reached: {coffee_weight}g >= {self.coffee_target}g")
            return ValveCommand.STOP, 0
        
        if current_flow_rate is None:
            logger.info("flow rate unavailable, noop")
            return ValveCommand.NOOP, self.valve_interval
        
        # Apply Kalman filter to smooth the flow rate
        filtered_flow_rate = self.kalman.update(current_flow_rate)
        
        # Calculate error using the filtered flow rate
        error = self.target_flow_rate - filtered_flow_rate
        
        # Calculate time delta
        if self.prev_timestamp is not None:
            dt = current_time - self.prev_timestamp
        else:
            dt = self.valve_interval
        
        # Compute PID output
        output = self._compute_pid(error, dt)
        
        # Update state
        self.prev_error = error
        self.prev_timestamp = current_time
        
        # Map output to valve command
        # Positive output = need more flow = open valve (FORWARD)
        # Negative output = too much flow = close valve (BACKWARD)
        logger.info(f"KalmanPID: target={self.target_flow_rate:.4f}, raw={current_flow_rate:.4f}, "
                   f"filtered={filtered_flow_rate:.4f}, error={error:.4f}, output={output:.4f}")
        
        # Use a threshold to determine direction
        # Small outputs within deadband = no action
        deadband = 0.1
        if abs(output) < deadband:
            return ValveCommand.NOOP, self.valve_interval * 2
        elif output > 0:
            return ValveCommand.FORWARD, self.valve_interval
        else:
            return ValveCommand.BACKWARD, self.valve_interval
