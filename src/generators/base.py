from abc import ABC, abstractmethod


AUDIT_NULLS = {
    "created_by": None,
    "created_date": None,
    "last_modified_by": None,
    "last_modified_date": None,
}


class Generator(ABC):
    table: str

    @abstractmethod
    def generate(self, context):
        raise NotImplementedError

