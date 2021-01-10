from dataclasses import dataclass


@dataclass
class Scalar:
    """Our Scalar class"""

    parent: object
    name: str
