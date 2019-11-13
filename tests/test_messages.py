from os import remove
from tempfile import NamedTemporaryFile
from typing import Any
from typing import List
from unittest import TestCase
from unittest.mock import MagicMock

from hypothesis import given
from hypothesis import strategies as st

from bot import Messages


class TestMessages(TestCase):
    @given(d=st.data())
    def test_get_messages_are_unique(self, d: Any) -> None:
        messages_all = d.draw(st.sets(st.text()).map(list))
        storage = MagicMock()
        storage.load.return_value = messages_all
        messages = Messages(storage)
        storage.load.assert_called_with()
        messages_got: List[str] = []
        for _ in enumerate(messages_all):
            message_got = messages.get()
            self.assertNotIn(message_got, messages_got)
            messages_got.append(message_got)
        self.assertSequenceEqual(sorted(messages_got), sorted(messages_all))

    @given(d=st.data())
    def test_add_message_will_appear_in_get_messages(self, d: Any) -> None:
        messages_all = d.draw(st.sets(st.text()).map(list))
        storage = MagicMock()
        storage.load.return_value = messages_all
        messages = Messages(storage)
        storage.load.assert_called_with()
        new_message = d.draw(st.text().filter(lambda x: x not in messages_all))
        messages.add(new_message)
        messages_all.append(new_message)
        storage.save.assert_called_with(sorted(messages_all))
        self.assertIn(
            new_message,
            [messages.get() for _ in range(len(messages_all) * 2)],
        )

    def test_get_message_from_empty_loaded_message(self) -> None:
        storage = MagicMock()
        storage.load.return_value = []
        messages = Messages(storage)
        storage.load.assert_called_with()
        self.assertEqual(messages.get(), '')
