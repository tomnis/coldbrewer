from abc import ABC, abstractmethod
from dataclasses import dataclass


class Scale(ABC):

    def get_weight_grams(self) -> float:
        """Get the weight in grams from the scale."""
        pass


    def get_units(self) -> str:
        """Get the units of measurement from the scale."""
        pass


    def get_battery_percentage(self) -> float:
        """Get the battery percentage of the scale."""
        pass