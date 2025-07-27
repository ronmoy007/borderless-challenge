import unittest
from unittest.mock import Mock
import json
from pre_process_message import (
    PreProcessMessage,
    MissingFieldException,
    MissingValueException,
    DuplicateTradeIDException,
    InvalidJSONException,
)

class TestPreProcessMessage(unittest.TestCase):
    def setUp(self):
        self.processor = PreProcessMessage()

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
        result = self.processor.pre_process_message(ws, message)
        # Ensure trade ID IS added (happy path)
        self.assertEqual(result["trade_id"], 12345)

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
        with self.assertRaises(MissingFieldException):
            self.processor.pre_process_message(ws, message)

        # Ensure no trade ID was added
        self.assertEqual(self.processor.list_trade_id_received, set())

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
        with self.assertRaises(MissingValueException):
            self.processor.pre_process_message(ws, message)

        # Ensure no trade ID was added
        self.assertEqual(self.processor.list_trade_id_received, set())

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
        self.processor.pre_process_message(None, message) # First time trade data is valid and added
        with self.assertRaises(DuplicateTradeIDException):
            self.processor.pre_process_message(None, message) # Second time should raise exception due to duplicate ID

    def test_invalid_json(self):
        ws = Mock()
        message = "{invalid_json"
        with self.assertRaises(InvalidJSONException):
            self.processor.pre_process_message(ws, message)
        
        # Ensure no trade ID was added
        self.assertEqual(self.processor.list_trade_id_received, set())

if __name__ == "__main__":
    unittest.main()