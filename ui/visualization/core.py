from functools import wraps

from ...core import get_positions_pages
from .calculate import pages_intersect, calculate_vertices
from .data_structures import *


def with_rule(func):
    @wraps(func)
    def wrapper(self, *args, **kwargs):
        param_names = list(func.__annotations__.keys())
        all_kwargs = {}
        for i, arg in enumerate(args):
            if i < len(param_names):
                all_kwargs[param_names[i]] = arg
        all_kwargs.update(kwargs)
        
        if self.rule == RULE.LOGIC:
            if not self._is_params_normal(**all_kwargs):
                print(f"warning: {func.__name__} заблокирован")
                return
        
        return func(self, *args, **kwargs)
    return wrapper

class VisualBook:
    def __init__(self):
        self.book: None | Book = None
        self.q_parts: int = 0
        self.q_blocks: int = 0
        self.rule = RULE.LOGIC

        self._page_vertices = []

        self._padding_between_parts = 3

    def new_book(self, q_parts=4, q_blocks=5, format=(595, 842)):
        book = Book(parts=[], format=format, margin=5, side=SIDE.LEFT)
        for i in range(q_parts):
            part = BookPart(
                pos=[i*self._padding_between_parts, 0, format[1]], 
                blocks=[])
            for j in range(q_blocks):
                block = BlockPages(
                    pages=[], pos=[0, 0, 0], alpha=0, beta=0)
                for k in range(4):
                    page = Page(texture=0)
                    #page.texture = id(_clean_texture(format))
                    block.pages.append(page)
                part.blocks.append(block)
            book.parts.append(part)
        self.book = book
        self.q_parts = q_parts
        self.q_blocks = q_blocks
        self._page_vertices = []
    
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
    
    @with_rule
    def set_pos_book_part(self, part_index: int, pos: list[int]):
        self.book.parts[part_index].pos = pos

    @with_rule
    def set_pos_block_pages(self, block_index: int, pos: int):
        part_ind = block_index // self.q_blocks
        block_ind = block_index % self.q_blocks
        self.book.parts[part_ind].blocks[block_ind].pos = pos

    @with_rule
    def set_alpha_block_pages(self, block_index: int, alpha: int):
        part_ind = block_index // self.q_blocks
        block_ind = block_index % self.q_blocks
        self.book.parts[part_ind].blocks[block_ind].alpha = alpha

    @with_rule
    def set_beta_block_pages(self, block_index: int, beta: int):
        part_ind = block_index // self.q_blocks
        block_ind = block_index % self.q_blocks
        self.book.parts[part_ind].blocks[block_ind].beta = beta
        
    def _is_params_normal(self, **kwargs):
        self.solve_visualization()

        book_copy = self.book.__dict__.copy()
        if 'part_index' in kwargs and 'pos' in kwargs:
            book_copy['parts'][kwargs['part_index']].pos = kwargs['pos']
        elif 'block_index' in kwargs:
            part_ind = kwargs['block_index'] // self.q_blocks
            block_ind = kwargs['block_index'] % self.q_blocks
            if 'pos' in kwargs:
                book_copy['parts'][part_ind].blocks[block_ind].pos = kwargs['pos']
            elif 'alpha' in kwargs:
                book_copy['parts'][part_ind].blocks[block_ind].alpha = kwargs['alpha']
            elif 'beta' in kwargs:
                book_copy['parts'][part_ind].blocks[block_ind].beta = kwargs['beta']

        page_vertices_copy = calculate_vertices(book_copy)
    
        for i in range(len(page_vertices_copy)):
            for j in range(i + 1, len(page_vertices_copy)):
                page1 = page_vertices_copy[i]
                page2 = page_vertices_copy[j]
                
                if (page1['part_idx'] != page2['part_idx'] or 
                    page1['block_idx'] != page2['block_idx']):
                    
                    if pages_intersect(page1['vertices'], page2['vertices']):
                        return False

        return True

    def solve_visualization(self):
        if self.book is None:
            return
        self._page_vertices = calculate_vertices(self.book)  