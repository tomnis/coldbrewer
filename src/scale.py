from abc import ABC, abstractmethod
from dataclasses import dataclass


class Scale(ABC):

    @property
    @abstractmethod
    def connected(self) -> bool:
        """Check if the scale is connected."""
        pass

    @abstractmethod
    def connect(self):
        """Connect to the scale."""
        pass


    @abstractmethod
    def disconnect(self):
        """Disconnect from the scale."""
        pass


    @abstractmethod
    def get_weight(self) -> float:
        """Get the weight in grams from the scale."""
        pass


    @abstractmethod
    def get_units(self) -> str:
        """Get the units of measurement from the scale."""
        pass


    @abstractmethod
    def get_battery_percentage(self) -> float:
        """Get the battery percentage of the scale."""
        pass

    @abstractmethod
    def get_auto_off(self) -> int:
        """Get the auto-off time in minutes."""
        pass