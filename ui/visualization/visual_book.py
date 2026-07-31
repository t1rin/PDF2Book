from functools import wraps
import copy

from core import get_positions_pages
from core.config import formats as formats_sizes
from .geometry import pages_intersect, calculate_vertices, get_quad_distance
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
        
        if self._rule == RULE.LOGIC:
            if not self._is_params_normal(**all_kwargs):
                print(f"warning: {func.__name__} заблокирован")
                return
        
        return func(self, *args, **kwargs)
    return wrapper

class VisualBook:
    def __init__(self, parent, padding=250):
        self._app = parent
        self._rule = RULE.LOGIC
        self._book: Book

        self._padding_between_parts: int = padding
        self._default_texture = self._app.texture_manager.get_clean_texture(
            format_name=self._app.pdf_imposer.params.format
        )

        self.active_block: tuple[int, int] = (0, 0)
        self.cache_planes: list[int] = []
        self.cache_textures: list[list[int]] = []
        self.need_reload: bool = False

        for _ in range(len(formats_sizes)):
            self.cache_textures.append([])

        self.new_book()

    def new_book(self, q_parts=1, q_blocks=1, 
                 page_size=(841, 1189), side=SIDE.LEFT):
        page_size = tuple([self._app.scale * value for value in page_size])
        book = Book(parts=[], q_parts=q_parts, q_blocks=q_blocks, 
                    page_size=page_size, side=side)
        for i in range(q_parts):
            part = BookPart(pos=[-page_size[0]/2, page_size[1]/2, 
                                 -i*self._padding_between_parts], 
                            blocks=[])
            for j in range(q_blocks):
                block = BlockPages(
                    pages=[], pos=[0, 0, 0], alpha=0, beta=0)
                for k in range(4):
                    page = Page(texture=self._default_texture)
                    block.pages.append(page)
                part.blocks.append(block)
            book.parts.append(part)
        self._book = book
        self._q_parts = q_parts
        self._q_blocks = q_blocks
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
                for k in [3, 0, 1, 2]:
                    if positions_pages[idx] < len(textures):
                        self._book.parts[i].blocks[j].pages[k].texture = \
                            textures[positions_pages[idx]]
                    else:
                        self._book.parts[i].blocks[j].pages[k].texture = \
                            self._default_texture
                    idx += 1
    
    @with_rule
    def set(self, *, 
            part_index: int | None = None, 
            block_index: int | None = None, 
            page_size: tuple[int, int] | None = None, 
            side: SIDE | None = None, pos: list[int] | None = None, 
            alpha: int | None = None, beta: int | None = None,
            default_texture: int | str | None = None, rule: RULE | None = None):
        if part_index is None and block_index is None:
            if page_size is not None:
                self._book.page_size = page_size
            if side is not None:
                self._book.side = side
            if default_texture is not None:
                self._default_texture = default_texture
            if rule is not None:
                self._rule = rule
        elif part_index is not None and block_index is None:
            if not (part_index < self._q_parts):
                print("failed editing angle of page of block")
                return
            if pos is not None:
                self._book.parts[part_index].pos = pos
        elif part_index is not None and block_index is not None:
            if (self._q_parts <= part_index) or (self._q_blocks <= block_index):
                print("failed editing angle of page of block")
                return
            if alpha is not None:
                self._book.parts[part_index].blocks[block_index].alpha = alpha
            if beta is not None:
                self._book.parts[part_index].blocks[block_index].beta = beta
            if pos is not None:
                self._book.parts[part_index].blocks[block_index].pos = pos

    def get(self, param: str, 
            part_ind: int | None = None, 
            block_ind: int | None = None):
        params = {
            'q_parts': self._book.q_parts,
            'q_blocks': self._book.q_blocks,
            'page_size': self._book.page_size,
            'side': self._book.side,
        }

        part = None
        if part_ind is not None and part_ind < len(self._book.parts):
            part = self._book.parts[part_ind]
        
        if part:
            params['part_pos'] = part.pos
            if block_ind is not None and block_ind < len(part.blocks):
                block = part.blocks[block_ind]
                params['block_pos'] = block.pos
                params['alpha'] = block.alpha
                params['beta'] = block.beta
        
        return params.get(param)

    def _is_params_normal(self, **kwargs):
        book_copy = copy.deepcopy(self._book)

        for attr in ['side', 'margin', 'page_size']:
            if attr in kwargs:
                setattr(book_copy, attr, kwargs[attr])

        if 'part_index' not in kwargs and 'block_index' in kwargs:
            return False
        elif 'part_index' in kwargs and 'block_index' not in kwargs and 'pos' in kwargs:
            book_copy.parts[kwargs['part_index']].pos = kwargs['pos']
        elif 'part_index' in kwargs and 'block_index' in kwargs:
            part_ind = kwargs['part_index']
            block_ind = kwargs['block_index']
            block = book_copy.parts[part_ind].blocks[block_ind]
            for attr in ['pos', 'alpha', 'beta']:
                if attr in kwargs:
                    setattr(block, attr, kwargs[attr])

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
                if page1['block_num'] != page2['block_num']:
                    if pages_intersect(page1['vertices'], page2['vertices']):
                        return False

        return True

    def _sort_sheets_vertices(self, camera_pos):
        self._sheets_vertices.sort(
            key=lambda s: get_quad_distance(s['vertices'], camera_pos),
            reverse=True)

    def is_order_changed(self, camera_pos):
        old_order = [sheet_vertices['page_num']
                     for sheet_vertices in self._sheets_vertices]
        self._sort_sheets_vertices(camera_pos)
        order = [sheet_vertices['page_num']
                 for sheet_vertices in self._sheets_vertices]
        return order != old_order

    def solve_visualization(self, camera_pos=None):
        sheets_vertices = calculate_vertices(self._book)
        if sheets_vertices is None:
            return
        self._sheets_vertices = sheets_vertices
        
        if camera_pos is not None:
            self._sort_sheets_vertices(camera_pos)

        return self._sheets_vertices
    