from abc import ABC, abstractmethod


class AbstractBrewClient(ABC):
    """An abstract base class representing a brew client.
    Defines the interface for brew client implementations.
    """

    @abstractmethod
    def start_brew(self, recipe: dict) -> None:
        """Start a brewing process with the given recipe."""
        pass

    @abstractmethod
    def stop_brew(self) -> None:
        """Stop the current brewing process."""
        pass

    @abstractmethod
    def get_brew_status(self) -> dict:
        """Get the current status of the brewing process."""
        pass