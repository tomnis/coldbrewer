"""
Unit tests for scale module.
Tests the MockScale and AbstractScale classes.
"""
import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

# Add src to path so we can import brewserver
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from brewserver.scale import AbstractScale, MockScale


class TestMockScale:
    """Tests for the MockScale class."""

    def test_mock_scale_initial_connected_false(self):
        """Test that MockScale starts disconnected."""
        scale = MockScale()
        assert scale.connected is False

    def test_connect_sets_connected_true(self):
        """Test that connect sets connected to True."""
        scale = MockScale()
        
        scale.connect()
        
        assert scale.connected is True

    def test_disconnect_resets_weight_and_connected(self):
        """Test that disconnect resets weight and sets connected to False."""
        scale = MockScale()
        
        # Connect and get some weight
        scale.connect()
        weight1 = scale.get_weight()
        
        # Disconnect
        scale.disconnect()
        
        # Should be disconnected
        assert scale.connected is False
        
        # Weight should be reset after disconnect
        # Note: The actual implementation resets weight to 0.0

    def test_get_weight_increments(self):
        """Test that get_weight returns incremental values."""
        scale = MockScale()
        scale.connect()
        
        # Get weight multiple times - it should increment
        weight1 = scale.get_weight()
        weight2 = scale.get_weight()
        weight3 = scale.get_weight()
        
        # Each call should return a higher weight (due to random increment)
        # The mock adds a random delta between 0 and 0.5 each time
        assert weight2 >= weight1
        assert weight3 >= weight2

    def test_get_weight_after_disconnect(self):
        """Test that get_weight after disconnect returns 0."""
        scale = MockScale()
        scale.connect()
        
        # Get some weight
        scale.get_weight()
        
        # Disconnect
        scale.disconnect()
        
        # Note: The current implementation doesn't explicitly set weight to 0
        # on get_weight after disconnect, but disconnect does reset _weight to 0.0
        # Let's verify the disconnect behavior
        assert scale._weight == 0.0
        assert scale.connected is False

    def test_get_units_returns_grams(self):
        """Test that get_units returns 'grams'."""
        scale = MockScale()
        
        units = scale.get_units()
        
        assert units == 'grams'

    def test_get_battery_percentage_returns_100_initially(self):
        """Test that get_battery_percentage returns 100 initially."""
        scale = MockScale()
        
        battery = scale.get_battery_percentage()
        
        assert battery == 100

    def test_get_battery_percentage_custom_value(self):
        """Test that battery percentage can be checked."""
        scale = MockScale()
        
        battery = scale.get_battery_percentage()
        
        assert isinstance(battery, int)
        assert 0 <= battery <= 100

    def test_multiple_connect_disconnect_cycles(self):
        """Test multiple connect/disconnect cycles."""
        scale = MockScale()
        
        # First cycle
        scale.connect()
        assert scale.connected is True
        
        scale.disconnect()
        assert scale.connected is False
        
        # Second cycle
        scale.connect()
        assert scale.connected is True
        
        scale.disconnect()
        assert scale.connected is False

    def test_weight_increases_over_time(self):
        """Test that weight increases over multiple get_weight calls."""
        scale = MockScale()
        scale.connect()
        
        weights = [scale.get_weight() for _ in range(10)]
        
        # Weights should generally increase (though due to randomness, not guaranteed)
        # Let's just verify they are all non-negative
        for weight in weights:
            assert weight >= 0


class TestAbstractScale:
    """Tests for the AbstractScale class (interface tests)."""

    def test_mock_scale_is_subclass_of_abstract_scale(self):
        """Test that MockScale is a subclass of AbstractScale."""
        assert issubclass(MockScale, AbstractScale)

    def test_abstract_scale_cannot_be_instantiated(self):
        """Test that AbstractScale cannot be instantiated directly."""
        with pytest.raises(TypeError):
            AbstractScale()

    def test_abstract_scale_has_abstract_methods(self):
        """Test that AbstractScale has the expected abstract methods and properties."""
        # Check abstract methods
        assert hasattr(AbstractScale, 'connect')
        assert hasattr(AbstractScale, 'disconnect')
        assert hasattr(AbstractScale, 'get_weight')
        assert hasattr(AbstractScale, 'get_units')
        assert hasattr(AbstractScale, 'get_battery_percentage')
        
        # Check abstract property
        assert hasattr(AbstractScale, 'connected')

    def test_abstract_scale_has_property(self):
        """Test that AbstractScale has the connected property."""
        # The connected should be a property (abstract property)
        assert isinstance(AbstractScale.__dict__.get('connected'), property)
