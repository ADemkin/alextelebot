from os import remove
from tempfile import NamedTemporaryFile
from typing import Any
from unittest import TestCase
from unittest.mock import MagicMock

from hypothesis import given
from hypothesis import strategies as st

from bot import Messages


class TestMessages(TestCase):
    @given(d=st.data())
    def test_pass(self, d: Any) -> None:
        all_messages = d.draw(st.sets(st.text()).map(list))
        storage = MagicMock()
        storage.load.return_value = all_messages
        messages = Messages(storage)
        storage.load.assert_called_with()
        self.assertSequenceEqual(messages.all_messages, all_messages)
        new_message = d.draw(st.text())
        messages.add(new_message)
        self.assertIn(new_message, messages.all_messages)



