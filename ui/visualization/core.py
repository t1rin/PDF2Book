from dataclasses import dataclass
from enum import IntEnum


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

    def new_book(self, q_parts=4, q_blocks=5, format=(595, 842)):
        book = Book(parts=[])
        for i in range(q_parts):
            part = BookPart(pos=[0, 0], blocks=[])
            for j in range(q_blocks):
                block = BlockPages(
                    pages=[], side=SIDE.LEFT, alpha=0, beta=0, pos=[0, 0])
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
        idx = 0
        for i in range(self.q_parts):
            for j in range(self.q_blocks):
                for k in range(4):
                    self.book.parts[i].blocks[j].pages[k].texture = textures[idx]
                    idx += 1
                    
    def set_pos_book_part(self, part_index: int, value: int):
        if self.rule:
            ... # меняет позицию части, с учетом правил

    def set_pos_block_pages(self, block_index: int, value: int):
        if self.rule:
            ... # меняет позицию блока, с учетом правил

    def set_alpha_block_pages(self, block_index: int, value: int):
        if self.rule:
            ... # меняет угол 1ой страницы, с учетом правил

    def set_beta_block_pages(self, block_index: int, value: int):
        if self.rule:
            ... # меняет угол 2ой страницы, с учетом правил
        
    def solve_visualization(self):
        ... # высчитывает положение всех страниц в 3D (с учетом направленности страниц(текстур))