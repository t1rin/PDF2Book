import numpy as np

import math

from .data_structures import Book, SIDE


def pages_intersect(page1_vertices, page2_vertices):
    alpha = get_plane(page1_vertices)
    beta = get_plane(page2_vertices)
    line_intersection = get_intersection(alpha, beta)
    if line_intersection is None:
        return False
    edges = get_edges_page(page1_vertices) + get_edges_page(page2_vertices)
    for edge in edges:
        if are_lines_equal(edge, line_intersection):
            return False
    if is_line_in_rectangle(line_intersection, page1_vertices) and \
       is_line_in_rectangle(line_intersection, page2_vertices):
        return True
    return False
    

def get_plane(vertices):
    r0_vector = np.array(vertices[0])
    vector1 = np.array(vertices[1]) - r0_vector
    vector2 = np.array(vertices[3]) - r0_vector
    return (r0_vector, vector1, vector2)

def get_intersection(alpha, beta, tol=1e-8):
    r1, u, v = alpha
    r2, p, q = beta
    n1 = np.cross(u, v)
    n2 = np.cross(p, q)
    s = np.cross(n1, n2)
    
    if np.linalg.norm(s) < tol:
        return

    delta = r2 - r1
    A = np.column_stack([v, -p, -q])
    sol, _, _, _ = np.linalg.lstsq(A, delta, rcond=None)
    t, _, _ = sol
    r0 = r1 + 0 * u + t * v
    return r0, s

def get_edges_page(vertices):
    edges = []
    for i in range(4):
        edges.append((
            np.array(vertices[i]),
            np.array(vertices[(i+1)%4]) - np.array(vertices[i])
        ))
    return edges

def are_lines_equal(line1, line2, tol=1e-8):
    r0_1, v1 = line1
    r0_2, v2 = line2

    cross_prod = np.cross(v1, v2)
    if np.linalg.norm(cross_prod) > tol:
        return False
    
    idx = np.argmax(np.abs(v2))
    if abs(v2[idx]) < tol:
        return np.linalg.norm(r0_1 - r0_2) < tol
    t = (r0_1[idx] - r0_2[idx]) / v2[idx]
    
    return np.linalg.norm(r0_1 - (r0_2 + t * v2)) < tol

def is_line_in_rectangle(line, rect_vertices, tol=1e-8):
    r0, d = line
    
    if np.linalg.norm(d) < tol:
        return point_in_rectangle(r0, rect_vertices, tol)
    
    r1, axis1, axis2 = get_plane(rect_vertices)
    
    len1 = np.linalg.norm(axis1)
    len2 = np.linalg.norm(axis2)
    
    if len1 < tol or len2 < tol:
        return False
    
    e1 = axis1 / len1
    e2 = axis2 / len2
    
    normal = np.cross(e1, e2)
    if abs(np.dot(d, normal)) > tol:
        return False
    
    dist = np.dot(r0 - r1, normal)
    if abs(dist) > tol:
        return False
    
    u0 = np.dot(r0 - r1, e1)
    v0 = np.dot(r0 - r1, e2)
    
    du = np.dot(d, e1)
    dv = np.dot(d, e2)
    
    t_min = -np.inf
    t_max = np.inf
    
    if abs(du) > tol:
        t1 = -u0 / du
        t2 = (len1 - u0) / du
        t_min = max(t_min, min(t1, t2))
        t_max = min(t_max, max(t1, t2))
    else:
        if u0 < -tol or u0 > len1 + tol:
            return False
    
    if abs(dv) > tol:
        t1 = -v0 / dv
        t2 = (len2 - v0) / dv
        t_min = max(t_min, min(t1, t2))
        t_max = min(t_max, max(t1, t2))
    else:
        if v0 < -tol or v0 > len2 + tol:
            return False
    
    if t_max - t_min > tol:
        return True
    
    return False

def point_in_rectangle(point, rect_vertices, tol=1e-8):
    r1, axis1, axis2 = get_plane(rect_vertices)
    
    len1 = np.linalg.norm(axis1)
    len2 = np.linalg.norm(axis2)
    
    if len1 < tol or len2 < tol:
        return False
    
    e1 = axis1 / len1
    e2 = axis2 / len2
    
    u = np.dot(point - r1, e1)
    v = np.dot(point - r1, e2)
    
    return (-tol <= u <= len1 + tol) and (-tol <= v <= len2 + tol)

def get_scale_multiplier(distance):
    if distance < 100:
        return distance * 0.03
    elif distance < 500:
        return distance * 0.04 
    elif distance < 2000:
        return distance * 0.06
    elif distance < 5000:
        return distance * 0.1
    else:
        return distance * 0.15

def calculate_vertices(book: Book):
    sheets_vertices = []
            
    w, h = book.format
    
    local_vertices = [
        [0, 0, 0],
        [w, 0, 0],
        [w, -h, 0],
        [0, -h, 0]
    ]
            
    for part_idx, part in enumerate(book.parts):
        if len(part.pos) != 3:
            print("Incorrect position")
            return
        
        for block_idx, block in enumerate(part.blocks):
            if len(block.pos) != 3:
                print("Incorrect position")
                return
            
            base = np.array(part.pos) + np.array(block.pos)
            
            alpha_rad = math.radians(block.alpha)
            beta_rad = math.radians(block.beta)
            
            angles = [alpha_rad, beta_rad]
            for angle in set(angles):
                vertices = []
                textures = []

                for v in local_vertices:
                    match book.side:
                        case SIDE.LEFT:
                            final = base + np.array([v[0] * math.cos(angle), 
                                                    v[1],
                                                    v[2] * math.sin(angle)])
                        case SIDE.TOP:
                            final = base + np.array([v[0], 
                                                    v[1] * math.cos(angle),
                                                    v[2] * math.sin(angle)])
                    vertices.append(final.tolist())
                
                surface_id = angles.index(angle)
                for i, page in enumerate(block.pages):
                    if surface_id == i // 2:
                        textures.append(page.texture)
            
                block_index = part_idx * len(part.blocks) + block_idx

                sheets_vertices.append({
                    'part_index': part_idx,
                    'block_index': block_index,
                    'surface': surface_id,
                    'side': book.side,
                    'angle': angle,
                    'textures': textures,
                    'vertices': vertices
                })
                
    return sheets_vertices