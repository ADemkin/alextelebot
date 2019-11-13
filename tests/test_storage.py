from os import remove
from tempfile import NamedTemporaryFile
from typing import Any
from unittest import TestCase

from hypothesis import given
from hypothesis import strategies as st

from storage import Storage


class TestStorage(TestCase):
    @given(d=st.data())
    def test_pass(self, d: Any) -> None:
        data_file = NamedTemporaryFile(delete=False, suffix='test_data_file')
        self.addCleanup(remove, data_file.name)
        messages = d.draw(st.lists(st.text(), min_size=1))
        storage = Storage(data_file.name)
        storage.save(messages)
        messages_got = storage.load()
        self.assertSequenceEqual(messages_got, messages)
        new_message = d.draw(st.text())
        messages.append(new_message)
        storage.save(messages)
        messages_got = storage.load()
        self.assertSequenceEqual(messages_got, messages)
