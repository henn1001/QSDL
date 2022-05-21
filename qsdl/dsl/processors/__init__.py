from enum import Enum


class CrudGeneratorEnum(str, Enum):
    GET_ALL = "GET_ALL"
    CREATE = "CREATE"
    GET = "GET"
    REPLACE = "REPLACE"
    UPDATE = "UPDATE"
    DELETE = "DELETE"
    ADD = "ADD"
    REMOVE = "REMOVE"

    @classmethod
    def has_member_key(cls, key):
        return key in cls.__members__
