from typing import Any

from eventsourcing.persistence import Transcoding


class CustomEnumTranscoding(Transcoding):
    def __init__(self, enum_class: Any):
        self.enum_class = enum_class
        self.type = enum_class
        self.name = f"{enum_class.__module__}.{enum_class.__name__}"

    def encode(self, obj: Any):
        return obj.value

    def decode(self, data: Any):
        return self.enum_class(data)
