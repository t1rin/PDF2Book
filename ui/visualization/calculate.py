import numpy as np

import math

from .data_structures import Book, SIDE


def pages_intersect(page1_vertices, page2_vertices):
    center1 = np.mean(page1_vertices, axis=0)
    center2 = np.mean(page2_vertices, axis=0)
    
    v1 = np.array(page1_vertices[1]) - np.array(page1_vertices[0])
    v2 = np.array(page1_vertices[2]) - np.array(page1_vertices[0])
    normal1 = np.cross(v1, v2)
    normal1 = normal1 / np.linalg.norm(normal1)
    
    signs = []
    for v in page2_vertices:
        v = np.array(v)
        diff = v - center1
        sign = np.dot(diff, normal1)
        signs.append(sign)
    
    if all(s > 0 for s in signs) or all(s < 0 for s in signs):
        return False
    
    v1 = np.array(page2_vertices[1]) - np.array(page2_vertices[0])
    v2 = np.array(page2_vertices[2]) - np.array(page2_vertices[0])
    normal2 = np.cross(v1, v2)
    normal2 = normal2 / np.linalg.norm(normal2)
    
    signs2 = []
    for v in page1_vertices:
        v = np.array(v)
        diff = v - center2
        sign = np.dot(diff, normal2)
        signs2.append(sign)
    
    if all(s > 0 for s in signs2) or all(s < 0 for s in signs2):
        return False
    
    return True

def calculate_vertices(book: Book):
    page_vertices = []
            
    for part_idx, part in enumerate(book.parts):
        part_x = part.pos[0] if len(part.pos) > 0 else 0
        part_y = part.pos[1] if len(part.pos) > 1 else 0
        
        for block_idx, block in enumerate(part.blocks):
            block_x = block.pos[0] if len(block.pos) > 0 else 0
            block_y = block.pos[1] if len(block.pos) > 1 else 0
            block_z = block.pos[2] if len(block.pos) > 2 else 0
            
            base_x = part_x + block_x
            base_y = part_y + block_y
            
            for page_idx, page in enumerate(block.pages):
                if block.side == SIDE.LEFT:
                    page_offset_x = page_idx * 2
                    page_offset_y = 0
                else:
                    page_offset_x = 0
                    page_offset_y = page_idx * 2
                
                alpha_rad = math.radians(block.alpha)
                beta_rad = math.radians(block.beta)
                
                page_width = format[0] - 2 * page.margin
                page_height = format[1] - 2 * page.margin
                
                local_vertices = [
                    [-page_width/2, -page_height/2, 0],
                    [page_width/2, -page_height/2, 0],
                    [page_width/2, page_height/2, 0],
                    [-page_width/2, page_height/2, 0]
                ]
                
                vertices = []
                for v in local_vertices:
                    x = v[0]
                    y = v[1] * math.cos(alpha_rad) - v[2] * math.sin(alpha_rad)
                    z = v[1] * math.sin(alpha_rad) + v[2] * math.cos(alpha_rad)
                    
                    x2 = x * math.cos(beta_rad) + z * math.sin(beta_rad)
                    y2 = y
                    z2 = -x * math.sin(beta_rad) + z * math.cos(beta_rad)
                    
                    final_x = base_x + page_offset_x + x2
                    final_y = base_y + page_offset_y + y2
                    final_z = block_z + z2
                    
                    vertices.append([final_x, final_y, final_z])
                
                page_vertices.append({
                    'part_index': part_idx,
                    'block_index': block_idx,
                    'page_index': page_idx,
                    'texture_id': page.texture,
                    'vertices': vertices,
                    'alpha': block.alpha,
                    'beta': block.beta,
                    'side': block.side
                })
    return page_vertices