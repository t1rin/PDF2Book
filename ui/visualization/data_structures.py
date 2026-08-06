from enum import IntEnum
from dataclasses import dataclass

from core import Side


class RULE(IntEnum):
    FREE = 0   # свободный, части двигаются без препятствий
    LOGIC = 1  # логичный, двигается так, как в реальной жизни

@dataclass
class Page:
    texture: int | None

@dataclass
class BlockPages:
    pages: list[Page]
    pos: list[int]
    alpha: int
    beta: int

@dataclass
class BookPart:
    blocks: list[BlockPages]
    pos: list[int]

@dataclass
class Book:
    parts: list[BookPart]
    q_parts: int
    q_blocks: int 
    page_size: tuple[int]
    side: Side
