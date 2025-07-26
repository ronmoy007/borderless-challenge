import unittest
from unittest.mock import Mock
import json
import producer

class TestOnMessage(unittest.TestCase):
    def setUp(self):
        producer.list_trade_id_received.clear()

    def test_valid_message(self):
        ws = Mock()
        trade_data = {
            "e": "trade",
            "E": 1672515782136,
            "s": "BNBBTC",
            "t": 12345,
            "p": "0.001",
            "q": "100",
            "T": 1672515782136,
            "m": True,
            "M": True
        }
        message = json.dumps(trade_data)
        # Should not raise
        producer.on_message(ws, message)

        # Ensure trade ID IS added (happy path)
        self.assertIn(12345, producer.list_trade_id_received)

    def test_missing_field(self):
        ws = Mock()
        trade_data = {
            "e": "trade",
            # "E" is missing
            "s": "BNBBTC",
            "t": 12346,
            "p": "0.001",
            "q": "100",
            "T": 1672515782136,
            "m": True,
            "M": True
        }
        message = json.dumps(trade_data)
        with self.assertRaises(producer.MissingFieldException):
            producer.on_message(ws, message)

        # Ensure no trade ID was added
        self.assertNotIn(12346, producer.list_trade_id_received)

    def test_missing_value(self):
        ws = Mock()
        trade_data = {
            "e": "trade",
            "E": None,  # None value
            "s": "BNBBTC",
            "t": 12347,
            "p": "0.001",
            "q": "100",
            "T": 1672515782136,
            "m": True,
            "M": True
        }
        message = json.dumps(trade_data)
        with self.assertRaises(producer.MissingValueException):
            producer.on_message(ws, message)
        
        # Ensure no trade ID was added
        self.assertNotIn(12347, producer.list_trade_id_received)

    def test_duplicate_trade_id(self):
        ws = Mock()
        trade_data = {
            "e": "trade",
            "E": 1672515782136,
            "s": "BNBBTC",
            "t": 12348,
            "p": "0.001",
            "q": "100",
            "T": 1672515782136,
            "m": True,
            "M": True
        }
        message = json.dumps(trade_data)
        producer.on_message(ws, message) # First time trade data is valid and added
        with self.assertRaises(producer.DuplicateTradeIDException):
            producer.on_message(ws, message) # Second time should raise exception due to duplicate ID 
        
        # Ensure no trade ID was added
        self.assertIn(12348, producer.list_trade_id_received)

    def test_invalid_json(self):
        ws = Mock()
        message = "{invalid_json"
        with self.assertRaises(producer.InvalidJSONException):
            producer.on_message(ws, message)
        
        self.assertEqual(len(producer.list_trade_id_received), 0)

if __name__ == "__main__":
    unittest.main()