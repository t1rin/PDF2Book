from __future__ import annotations

import math
from collections.abc import Sequence
from typing import Any, TypedDict

import numpy as np
import numpy.typing as npt

from core import Side
from .data_structures import Book


TOLERANCE: float = 1e-8
BLOCK_SIZE: int = 4


Vector = npt.NDArray[np.float64]
Vertex = tuple[float, float, float]
Vertices = Sequence[Vertex]
Plane = tuple[Vector, Vector, Vector]
Line = tuple[Vector, Vector]


class Candidate(TypedDict):
    page_num: int
    block_num: int
    texture: Any
    vertices: tuple[Vertex, ...]
    uv_coords: list[list[int]]


def pages_intersect(page1_vertices: Vertices, page2_vertices: Vertices) -> bool:
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


def get_plane(vertices: Vertices) -> Plane:
    r0_vector = np.array(vertices[0])
    vector1 = np.array(vertices[1]) - r0_vector
    vector2 = np.array(vertices[3]) - r0_vector
    return (r0_vector, vector1, vector2)


def get_intersection(alpha: Plane, beta: Plane, tol: float = TOLERANCE) -> Line | None:
    r1, u, v = alpha
    r2, p, q = beta
    n1 = np.cross(u, v)
    n2 = np.cross(p, q)
    s = np.cross(n1, n2)

    if np.linalg.norm(s) < tol:
        return None

    delta = r2 - r1
    A = np.column_stack([v, -p, -q])

    try:
        sol = np.linalg.solve(A, delta)
    except np.linalg.LinAlgError:
        sol, _, _, _ = np.linalg.lstsq(A, delta, rcond=None)
    t = sol[0]
    r0 = r1 + t * v
    return r0, s


def get_edges_page(vertices: Vertices) -> list[Line]:
    edges: list[Line] = []
    for i in range(4):
        edges.append((
            np.array(vertices[i]),
            np.array(vertices[(i + 1) % 4]) - np.array(vertices[i])
        ))
    return edges


def are_lines_equal(line1: Line, line2: Line, tol: float = TOLERANCE) -> bool:
    r0_1, v1 = line1
    r0_2, v2 = line2

    cross_prod = np.cross(v1, v2)
    if np.linalg.norm(cross_prod) > tol:
        return False

    idx = np.argmax(np.abs(v2))
    if abs(v2[idx]) < tol:
        return bool(np.linalg.norm(r0_1 - r0_2) < tol)
    t = (r0_1[idx] - r0_2[idx]) / v2[idx]

    return bool(np.linalg.norm(r0_1 - (r0_2 + t * v2)) < tol)


def is_line_in_rectangle(line: Line, rect_vertices: Vertices, tol: float = TOLERANCE) -> bool:
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


def point_in_rectangle(point: Vector, rect_vertices: Vertices, tol: float = TOLERANCE) -> bool:
    r1, axis1, axis2 = get_plane(rect_vertices)

    len1 = np.linalg.norm(axis1)
    len2 = np.linalg.norm(axis2)

    if len1 < tol or len2 < tol:
        return False

    e1 = axis1 / len1
    e2 = axis2 / len2

    u = np.dot(point - r1, e1)
    v = np.dot(point - r1, e2)

    return bool((-tol <= u <= len1 + tol) and (-tol <= v <= len2 + tol))


def get_scale_multiplier(distance: float) -> float:
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


def get_quad_distance(vertices: Vertices, camera_pos: Vector) -> float:
    center = np.mean(vertices, axis=0)
    distance = np.linalg.norm(center - camera_pos)
    return float(distance)


def _resolve_texture_conflict(candidates: list[Candidate]) -> Candidate:
    sorded_candidates: list[list[Candidate]] = [[], []]
    for candidate in candidates:
        page_num = candidate['page_num']
        angle_id = (page_num % 4) // 2
        sorded_candidates[angle_id].append(candidate)

    surface_id: int | None = None
    total_canditates: list[Candidate] = []
    for angle_id, group in enumerate(sorded_candidates):
        min_candidate = min(group, key=lambda c: c['page_num'])
        max_candidate = max(group, key=lambda c: c['page_num'])

        page_num = group[-1]['page_num']
        surface_id = page_num % 2

        if angle_id == surface_id:
            total_canditates.append(min_candidate)
        else:
            total_canditates.append(max_candidate)
    assert surface_id is not None
    return total_canditates[surface_id]


def subdivide_uv(uv_coords: Vertices, n: int = 8,
                 ) -> list[tuple[Vector, ...]]:
    uv0, uv1, uv2, uv3 = [*map(np.array, uv_coords)]
    
    uvs: list[tuple[Vector, ...]] = []
    for i in range(n):
        for j in range(n):
            s0, s1 = i / n, (i + 1) / n
            t0, t1 = j / n, (j + 1) / n
            
            def lerp(a, b, t):
                return a + (b - a) * t
            
            uv00 = lerp(lerp(uv0, uv1, t0), lerp(uv3, uv2, t0), s0)
            uv10 = lerp(lerp(uv0, uv1, t1), lerp(uv3, uv2, t1), s0)
            uv11 = lerp(lerp(uv0, uv1, t1), lerp(uv3, uv2, t1), s1)
            uv01 = lerp(lerp(uv0, uv1, t0), lerp(uv3, uv2, t0), s1)
            
            uvs.append((uv00, uv10, uv11, uv01))
    
    return uvs


def subdivide_quad(vertices: Vertices, n: int = 8,
                   ) -> list[tuple[Vector, ...]]:
    vs = [*map(np.array, vertices)]

    quads: list[tuple[Vector, ...]] = []
    for i in range(n):
        for j in range(n):
            s0, s1 = i / n,     (i + 1) / n
            t0, t1 = j / n,     (j + 1) / n
            
            def lerp(a, b, t):
                return a + (b - a) * t
            
            p00 = lerp(lerp(vs[0], vs[1], t0), lerp(vs[3], vs[2], t0), s0)
            p10 = lerp(lerp(vs[0], vs[1], t1), lerp(vs[3], vs[2], t1), s0)
            p11 = lerp(lerp(vs[0], vs[1], t1), lerp(vs[3], vs[2], t1), s1)
            p01 = lerp(lerp(vs[0], vs[1], t0), lerp(vs[3], vs[2], t0), s1)
            
            quads.append((p00, p10, p11, p01))
    return quads


def calculate_vertices(book: Book, thickness: int = 3) -> list[Candidate]:
    sheets_vertices: list[Candidate] = []
    w, h = book.page_size

    local_vertices_with_uv: list[list[tuple[Vector, list[int]]]] = [[
        (np.array([0,  0, thickness / 2]), [0, 0]),
        (np.array([0, -h, thickness / 2]), [0, 1]),
        (np.array([w, -h, thickness / 2]), [1, 1]),
        (np.array([w,  0, thickness / 2]), [1, 0])],
        [
        (np.array([0,  0, -thickness / 2]), [1, 0]),
        (np.array([w,  0, -thickness / 2]), [0, 0]),
        (np.array([w, -h, -thickness / 2]), [0, 1]),
        (np.array([0, -h, -thickness / 2]), [1, 1])
    ]]

    position_map: dict[tuple[Vertex, ...], list[Candidate]] = dict()
    for part_idx, part in enumerate(book.parts):
        n_blocks = len(part.blocks)
        for block_idx, block in enumerate(part.blocks):
            base = np.array(part.pos) + np.array(block.pos)

            alpha_rad = math.radians(block.alpha)
            beta_rad = math.radians(block.beta)
            angles = (alpha_rad, beta_rad)

            block_num = part_idx * n_blocks + block_idx

            for page_idx, page in enumerate(block.pages):
                angle = angles[page_idx // 2]

                cos_a = math.cos(angle)
                sin_a = math.sin(angle)
                rotation_matrix: Vector
                match book.side:
                    case Side.LEFT | Side.RIGHT:
                        rotation_matrix = np.array([
                            [cos_a, 0, -sin_a],
                            [0,     1,      0],
                            [sin_a, 0,  cos_a]
                        ])
                    case Side.TOP:
                        rotation_matrix = np.array([
                            [1,      0,     0],
                            [0,  cos_a, sin_a],
                            [0, -sin_a, cos_a]
                        ])

                vertices: list[Vertex] = []
                uv_coords: list[list[int]] = []
                data = local_vertices_with_uv[page_idx % 2]
                if ((book.side == Side.TOP) and (page_idx % 2)):
                    coords, uvs = zip(*data)
                    shifted_uvs = uvs[2:] + uvs[:2]
                    data = list(zip(coords, shifted_uvs))
                for local_vertex, uv in data:
                    final = base + rotation_matrix.dot(local_vertex)
                    vertex = tuple(round(float(coord), 3) for coord in final)
                    assert len(vertex) == 3
                    vertices.append(vertex)
                    uv_coords.append(uv)
                vertices_: tuple[Vertex, ...] = tuple(vertices)

                page_num = block_num * BLOCK_SIZE + page_idx

                candidate: Candidate = {
                    'page_num': page_num,
                    'block_num': block_num,
                    'texture': page.texture,
                    'vertices': vertices_,
                    'uv_coords': uv_coords
                }

                position_map.setdefault(vertices_, []).append(candidate)

    for candidates in position_map.values():
        if len(candidates) == 1:
            sheets_vertices.append(candidates[0])
        else:
            sheets_vertices.append(_resolve_texture_conflict(candidates))

    return sheets_vertices