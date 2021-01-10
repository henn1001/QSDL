from dataclasses import dataclass, field
from typing import List


@dataclass
class Operation:
    """Our Operation class"""

    name: str = None
    ref: str = None
    order: int = None
    tag: str = None
    summary: str = None
    description: str = None
    path: str = None
    method: str = None
    parameters: List[dict] = field(default_factory=list)
    request: dict = None
    response: dict = None
    parent: object = None
    childs: List[dict] = field(default_factory=list)
    is_crud: bool = False

