from functools import wraps
import copy

from core import get_positions_pages
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
    def __init__(self, rule=RULE.LOGIC):
        self.rule = rule
        self._book: Book

        self._padding_between_parts = 3

        self.new_book(q_parts=0, q_blocks=0)

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
        self._book = book
        self._q_parts = q_parts
        self._q_blocks = q_blocks
        self._format = format
        self._sheets_vertices = []
    
    def load_textures(self, textures: list):
        q_pages_on_block = 4 * self._q_blocks
        positions_pages = []
        for i in range(self._q_parts):
            positions_pages += [pos + i * q_pages_on_block
                for pos in get_positions_pages(q_pages_on_block)]

        idx = 0
        for i in range(self._q_parts):
            for j in range(self._q_blocks):
                for k in range(4):
                    self._book.parts[i].blocks[j].pages[k].texture = \
                        textures[positions_pages[idx]]
                    idx += 1
    
    @with_rule
    def set_pos_book_part(self, part_index: int, pos: list[int]):
        if self._q_parts <= part_index:
            print("failed editing position of part")
            return
        self._book.parts[part_index].pos = pos

    @with_rule
    def set_pos_block_pages(self, block_index: int, pos: int):
        part_index = block_index // self._q_blocks
        block_index = block_index % self._q_blocks
        if (self._q_parts <= part_index) or (self._q_blocks <= block_index):
            print("failed editing position of block")
            return
        self._book.parts[part_index].blocks[block_index].pos = pos

    @with_rule
    def set_angle_block_pages(self, block_index: int, alpha: int | None = None,
                                                      beta: int | None = None):
        part_index = block_index // self._q_blocks
        block_index = block_index % self._q_blocks
        if (self._q_parts <= part_index) or (self._q_blocks <= block_index):
            print("failed editing angle of page of block")
            return
        if alpha is not None:
            self._book.parts[part_index].blocks[block_index].alpha = alpha
        if beta is not None:
            self._book.parts[part_index].blocks[block_index].beta = beta
        
    def _is_params_normal(self, **kwargs):
        book_copy = copy.deepcopy(self._book)
        if 'part_index' in kwargs and 'pos' in kwargs:
            book_copy.parts[kwargs['part_index']].pos = kwargs['pos']
        elif 'block_index' in kwargs:
            part_ind = kwargs['block_index'] // self._q_blocks
            block_ind = kwargs['block_index'] % self._q_blocks
            if 'pos' in kwargs:
                book_copy.parts[part_ind].blocks[block_ind].pos = kwargs['pos']
            elif 'alpha' in kwargs:
                book_copy.parts[part_ind].blocks[block_ind].alpha = kwargs['alpha']
            elif 'beta' in kwargs:
                book_copy.parts[part_ind].blocks[block_ind].beta = kwargs['beta']

        for i in range(self._q_parts):
            for j in range(self._q_blocks):
                alpha = book_copy.parts[i].blocks[j].alpha
                beta = book_copy.parts[i].blocks[j].beta
                if not (beta <= alpha < 180):
                    return False

        sheets_vertices = calculate_vertices(book_copy)
        if sheets_vertices is None:
            return False
    
        for i, page1 in enumerate(sheets_vertices):
            for j, page2 in enumerate(sheets_vertices):
                if j < i + 1:
                    continue
                
                if page1['block_index'] != page2['block_index']:
                    if pages_intersect(page1['vertices'], page2['vertices']):
                        return False

        return True

    def solve_visualization(self):
        sheets_vertices = calculate_vertices(self._book)
        if sheets_vertices is None:
            return
        self._sheets_vertices = sheets_vertices
        return sheets_vertices
    