from os import fsync
from typing import Sequence
import json


class Storage:
    def __init__(self, data_file: str) -> None:
        self.data_file = data_file

    def load(self) -> Sequence[str]:
        with open(self.data_file, "rb") as fd:
            return json.loads(fd.read().decode('utf-8'))

    def save(self, messages: Sequence[str]) -> None:
        messages_json = json.dumps(messages, ensure_ascii=False)
        with open(self.data_file, "wb") as fd:
            fd.write(messages_json.encode('utf-8'))
            fd.flush()
            fsync(fd.fileno())
