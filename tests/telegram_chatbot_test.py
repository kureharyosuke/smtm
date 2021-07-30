import requests
import unittest
from smtm import TelegramChatbot
from unittest.mock import *


class TelegramChatbotTests(unittest.TestCase):
    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_constructor(self):
        tcb = TelegramChatbot()
        self.assertIsNotNone(tcb)

    @patch("threading.Timer")
    def test__start_timer_start_timer_with_passed_time_value(self, mock_timer):
        tcb = TelegramChatbot()
        tcb.get_worker = MagicMock()
        tcb._start_timer(10)

        mock_timer.assert_called_once_with(10, ANY)
        callback = mock_timer.call_args[0][1]
        callback()
        tcb.get_worker.post_task.assert_called_once_with({"runnable": tcb._handle_message})

    def test__handle_message_call__start_timer_with_next_period(self):
        tcb = TelegramChatbot()
        tcb._start_timer = MagicMock()
        tcb._handle_message(None)
        tcb._handle_message(None)
        tcb._handle_message(None)
        tcb._handle_message(None)
        tcb._handle_message(None)
        tcb._handle_message(None)
        tcb._handle_message(None)
        tcb._handle_message(None)
        tcb._handle_message(None)
        tcb._handle_message(None)
        tcb._handle_message(None)
        tcb._handle_message(None)
        tcb._handle_message(None)
        tcb._handle_message(None)
        tcb._handle_message(None)
        self.assertEqual(tcb._start_timer.call_args_list[0][0][0], tcb.polling_period[1])
        self.assertEqual(tcb._start_timer.call_args_list[1][0][0], tcb.polling_period[2])
        self.assertEqual(tcb._start_timer.call_args_list[2][0][0], tcb.polling_period[3])
        self.assertEqual(tcb._start_timer.call_args_list[3][0][0], tcb.polling_period[4])
        self.assertEqual(tcb._start_timer.call_args_list[4][0][0], tcb.polling_period[5])
        self.assertEqual(tcb._start_timer.call_args_list[5][0][0], tcb.polling_period[6])
        self.assertEqual(tcb._start_timer.call_args_list[6][0][0], tcb.polling_period[7])
        self.assertEqual(tcb._start_timer.call_args_list[7][0][0], tcb.polling_period[8])
        self.assertEqual(tcb._start_timer.call_args_list[8][0][0], tcb.polling_period[9])
        self.assertEqual(tcb._start_timer.call_args_list[9][0][0], tcb.polling_period[10])
        self.assertEqual(tcb._start_timer.call_args_list[10][0][0], tcb.polling_period[11])
        self.assertEqual(tcb._start_timer.call_args_list[11][0][0], tcb.polling_period[12])
        self.assertEqual(tcb._start_timer.call_args_list[12][0][0], tcb.polling_period[12])
        self.assertEqual(tcb._start_timer.call_args_list[13][0][0], tcb.polling_period[12])

    @patch("requests.get")
    def test__get_updates_call_getUpdates_api_correctly(self, mock_get):
        tcb = TelegramChatbot()
        expected_response = {
            "ok": True,
            "result": [
                {
                    "update_id": 402107581,
                    "message": {
                        "message_id": 3,
                        "from": {
                            "id": 1819645704,
                            "is_bot": False,
                            "first_name": "msaltnet",
                            "language_code": "ko",
                        },
                        "chat": {"id": 1819645704, "first_name": "msaltnet", "type": "private"},
                        "date": 1627616560,
                        "text": "hello~",
                    },
                }
            ],
        }
        dummy_response = MagicMock()
        dummy_response.json.return_value = expected_response
        mock_get.return_value = dummy_response
        updates = tcb._get_updates()
        self.assertEqual(updates, expected_response)
        self.assertEqual(mock_get.call_args[0][0].find("https://api.telegram.org/"), 0)

    @patch("requests.get")
    def test__get_updates_return_None_when_receive_invalid_data(self, mock_get):
        tcb = TelegramChatbot()
        dummy_response = MagicMock()
        dummy_response.json.side_effect = ValueError()
        mock_get.return_value = dummy_response

        updates = tcb._get_updates()
        self.assertEqual(updates, None)

    @patch("requests.get")
    def test__get_updates_return_None_when_receive_response_error(self, mock_get):
        tcb = TelegramChatbot()
        dummy_response = MagicMock()
        dummy_response.json.return_value = [{"market": "apple"}, {"market": "banana"}]
        dummy_response.raise_for_status.side_effect = requests.exceptions.HTTPError(
            "HTTPError dummy exception"
        )
        mock_get.return_value = dummy_response

        updates = tcb._get_updates()
        self.assertEqual(updates, None)

    @patch("requests.get")
    def test__get_updates_return_None_when_connection_fail(self, mock_get):
        tcb = TelegramChatbot()
        dummy_response = MagicMock()
        dummy_response.json.return_value = [{"market": "apple"}, {"market": "banana"}]
        dummy_response.raise_for_status.side_effect = requests.exceptions.RequestException(
            "RequestException dummy exception"
        )
        mock_get.return_value = dummy_response

        updates = tcb._get_updates()
        self.assertEqual(updates, None)
