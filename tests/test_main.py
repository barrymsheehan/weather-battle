import json
import unittest
import app.main
from app.main import load_config
from unittest.mock import patch, mock_open

class TestLoadConfig(unittest.TestCase):
    """Test cases for the load_config() function"""

    def set_up(self):
        """Reset the global config before each test"""
        app.main.config = {}

    def test_load_config_success(self):
        """Test successful loading of a valid config file"""
        mock_config_data = {
            "cities": {
                "city_1": "London",
                "city_2": "Paris"
            },
            "thresholds": {
                "hot": 30,
                "cold": 5
            }
        }

        mock_file_content = json.dumps(mock_config_data)

        with patch("builtins.open", mock_open(read_data=mock_file_content)):
            load_config()
            
        # Assert config was loaded correctly
        self.assertEqual(app.main.config, mock_config_data)
        self.assertIn("cities", app.main.config)
        self.assertIn("thresholds", app.main.config)