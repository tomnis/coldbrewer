from abc import ABC, abstractmethod

class AbstractBrewClient(ABC):
    """An abstract base class representing a brew client.
    Defines the interface for brew client implementations.
    """

    @abstractmethod
    def acquire(self):
        """Start a brewing process with the given recipe."""
        pass

    @abstractmethod
    def release(self):
        """Stop the current brewing process."""
        pass

    @abstractmethod
    def get_current_flow_rate(self) -> float:
        """Get the current flow rate from the server."""
        pass

    @abstractmethod
    def step_forward(self):
        """Move the valve controller one step forward."""
        pass

    @abstractmethod
    def step_backward(self):
        """Move the valve controller one step backward."""
        pass

    @abstractmethod
    def return_to_start(self):
        """Return the valve to the starting position."""
        pass