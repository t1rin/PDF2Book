from dataclasses import dataclass
from enum import IntEnum

from ...core import get_positions_pages


class SIDE(IntEnum):
    LEFT = 0
    TOP = 1

@dataclass
class Page:
    margin: int
    texture: int

@dataclass
class BlockPages:
    pages: list[Page]
    side: SIDE
    alpha: int
    beta: int
    is_vertical: bool
    pos: list[int]

@dataclass
class BookPart:
    blocks: list[BlockPages]
    pos: list[int]

@dataclass
class Book:
    parts: list[BookPart]

class RULE(IntEnum):
    FREE = 0   # свободный, части двигаются без препятствий
    LOGIC = 1  # логичный, двигается так, как в реальной жизни

class VisualBook:
    def __init__(self):
        self.book: None | Book = None
        self.q_parts: int = 0
        self.q_blocks: int = 0
        self.format: tuple[int] = (595, 842)
        self.rule = RULE.LOGIC

        self._padding_between_parts = 3

    def new_book(self, q_parts=4, q_blocks=5, is_vertical=False, format=(595, 842)):
        book = Book(parts=[])
        for i in range(q_parts):
            part = BookPart(
                pos=[i*self._padding_between_parts, 0, format[1]], 
                blocks=[])
            for j in range(q_blocks):
                block = BlockPages(
                    pages=[], side=SIDE.LEFT, alpha=0, beta=0, 
                    is_vertical=is_vertical, pos=[0, 0, 0])
                for k in range(4):
                    page = Page(margin=5, texture=0)
                    #page.texture = id(_clean_texture(format))
                    block.pages.append(page)
                part.blocks.append(block)
            book.parts.append(part)
        self.book = book
        self.q_parts = q_parts
        self.q_blocks = q_blocks
        self.format = format
    
    def load_textures(self, textures: list):
        if self.book is None:
            print("Книга не инициализирована")
            return
        
        q_pages_on_block = 4 * self.q_blocks
        positions_pages = []
        for i in range(self.q_parts):
            positions_pages += [pos + i * q_pages_on_block
                for pos in get_positions_pages(q_pages_on_block)]

        idx = 0
        for i in range(self.q_parts):
            for j in range(self.q_blocks):
                for k in range(4):
                    self.book.parts[i].blocks[j].pages[k].texture = \
                        textures[positions_pages[idx]]
                    idx += 1
       
    def set_pos_book_part(self, part_index: int, pos: list[int]):
        self.book.parts[part_index].pos = pos

    def set_pos_block_pages(self, block_index: int, pos: int):
        part_ind = block_index // self.q_blocks
        block_ind = block_index % self.q_blocks
        self.book.parts[part_ind].blocks[block_ind].pos = pos

    def set_alpha_block_pages(self, block_index: int, alpha: int):
        part_ind = block_index // self.q_blocks
        block_ind = block_index % self.q_blocks
        self.book.parts[part_ind].blocks[block_ind].alpha = alpha

    def set_beta_block_pages(self, block_index: int, beta: int):
        part_ind = block_index // self.q_blocks
        block_ind = block_index % self.q_blocks
        self.book.parts[part_ind].blocks[block_ind].beta = beta
        
    def _is_params_normal(self, **kwargs):
        ...

    def solve_visualization(self):
        ... # высчитывает положение всех страниц в 3D (с учетом направленности страниц(текстур))