import logging
from typing import List
from model import Point, Block, BlockType, Shadow, Edge, intersection_parameters
from exception import TangramException


L = logging.getLogger('Solver')


class MoveInstruction:
    """
    Repräsentiert einen Pick & Place-Befehl für den Roboter
    """

    block: Block
    position: Point
    rotation: float

    def __init__(self, block: Block, position: Point, rotation: float) -> None:
        self.block = block
        self.position = position
        self.rotation = rotation


def solve(blocks: List[Block], shadows: list[Shadow], img) -> list[MoveInstruction]:
    """
    Ermittelt eine Lösung für die übergebenen Blöcke und Shadows
    """

    # __check_too_few_blocks(blocks, shadows)

    instructions: list[MoveInstruction] = []
    
    instr = __check_plain_blocks(blocks, shadows)
    instructions.extend(instr)

    instr = __solve_rest(blocks, shadows, img)
    instructions.extend(instr)

    return instructions







def __check_too_few_blocks(blocks: list[Block], shadows: list[Shadow]) -> None:
    b_area = sum([b.area for b in blocks])
    s_area = sum([s.area for s in shadows])

    if b_area < s_area:
        raise TangramException('There aren\'t enough blocks to solve this tangram')



#==============#
# PLAIN BLOCKS #
#==============#


def __check_plain_blocks(blocks: list[Block], shadows: list[Shadow]) -> list[MoveInstruction]:
    """
    Überprüft, ob Shadows existieren, die genau aus einem Block bestehen.
    """

    instructions: list[MoveInstruction] = []

    # shadows muss rückwärts durchlaufen werden, weil Elemente entfernt werden
    for s_idx in range( len(shadows) - 1, -1, -1 ):
        shadow: Shadow = shadows[s_idx]

        for b_idx, block in enumerate(blocks):
            if __shadow_block_match(shadow, block):

                blocks.pop(b_idx)
                shadows.pop(s_idx)

                print('Exact match:', block)

                instructions.append(MoveInstruction(
                    block=      block,
                    position=   shadow.get_center(),
                    rotation=   __get_block_rotation(shadow, block)
                ))

                break

    return instructions


def __shadow_block_match(shadow: Shadow, block: Block) -> bool:
    """
    Gibt True zurück, wenn shadow und block die gleiche Form und Größe haben
    """
    
    if shadow.area != block.area:
        return False

    if len(shadow.vertices) != len(block.vertices):
        return False

    # Um Quadrat und Parallelogramm unterscheiden zu können, müssen die Innenwinkel verglichen werden
    try:
        shadow.interior_angles.index(block.interior_angles[0])
    except ValueError:
        return False

    return True


def __get_block_rotation(shadow: Shadow, block: Block) -> float:
    """
    Berechnet den benötigten Winkel von block, damit shadow und block deckungsgleich sind
    """

    switch = {
        BlockType.SQUARE: (90, Point(-1, -1), 90),
        BlockType.PARALLELOGRAM: (45, Point(-1, -2), 180),
        BlockType.SMALL_TRIANGLE: (90, Point(-1, -1), 360),
        BlockType.MEDIUM_TRIANGLE: (90, Point(0, 1), 360),
        BlockType.LARGE_TRIANGLE: (90, Point(-1, -1), 360),
    }

    args = switch.get(block.btype)

    if args is None:
        raise TypeError(f'Block has an invalid type: {block.btype._name_}')

    return __angle(shadow, args[0], args[1], args[2]) - block.rotation


def __angle(shadow: Shadow, vertex_angle: int, base_rot_vec: Point, angle_mod: int) -> float:
    idx = shadow.interior_angles.index(vertex_angle)
    ref_vertex = shadow.vertices[idx]
    
    vec = ref_vertex - shadow.get_center()

    angle = Point.angle(vec, base_rot_vec, True) % angle_mod

    return angle







#====================#
# MORE COMPLEX STUFF #
#====================#


def __solve_rest(blocks: list[Block], shadows: list[Shadow], img) -> list[MoveInstruction]:
    """
    
    """

    # Shadows aufsteigend nach Größe sortieren
    shadows.sort(key=lambda p: p.area, reverse=False)
    # Blocks absteigend nach Größe sortieren
    blocks.sort(key=lambda b: b.area, reverse=True)

    instructions: list[MoveInstruction] = []

    for s in shadows:
        instr = __solve_loop(blocks, s, img)

        if instr is None:
            L.info(f'Couldn\'t find a solution for {s}')
            continue

        instructions.extend(instr)

    return instructions

from pyniryo import cv2
def __solve_loop(blocks: list[Block], shadow: Shadow, img) -> list[MoveInstruction] | None:

    for sv_idx, sv in enumerate(shadow.vertices):
        for b_idx, b in enumerate(blocks):
            for bv_idx, bv in enumerate(b.vertices):

                # Verhältnis der Innenwinkel bei sv und bv
                angle_ratio = shadow.interior_angles[sv_idx] / b.interior_angles[bv_idx]

                # Winkel vom Block ist größer als der des Shadows
                # => Block passt nicht an diese Stelle
                if angle_ratio < 1:
                    continue

                # # Winkel vom Block und Shadow sind gleich groß
                # # => Block muss nur ein mal angelegt werden
                # elif angle_ratio == 1:

                cv2.line(img, shadow.get_vertex(sv_idx-1).to_np_int_array(), sv.to_np_int_array(), (255, 255, 0), 5)
                cv2.circle(img, sv.to_np_int_array(), 10, (0, 255, 255), -1)

                s_vec = shadow.get_vertex(sv_idx-1) - sv

                b_vec = b.get_vertex(bv_idx-1) - bv

                angle = Point.angle(s_vec, b_vec, True)

                block_vertices = b.get_scaled_vertices()

                block_vertices = Point.move_points(block_vertices, sv- block_vertices[bv_idx])
                block_vertices = Point.rotate_around_point(block_vertices, sv, angle)

                cv2.polylines(img, Point.list_to_np_array(block_vertices), True, (125, 0, 125), 6)

                block_edges = __to_edges(block_vertices)
                shadow_edges = __to_edges(shadow.vertices)

                # TODO: https://discordapp.com/channels/@me/799333662964449311/1041824146922946571
                if __intersecting_edges(block_edges, shadow_edges):
                    continue

                
                shadow_vertices = shadow.vertices.copy()
                block_vertices.pop(bv_idx)
                block_vertices.reverse()
                if angle_ratio == 1:
                    shadow_vertices.pop(sv_idx)
                shadow_vertices = shadow_vertices[:sv_idx] + block_vertices + shadow_vertices[sv_idx:]

                cv2.polylines(img, Point.list_to_np_array(shadow_vertices), True, (255, 255, 255), 5)

                # TODO: bisschen post processing
                # TODO: genutzte Blöcke entfernen
                # TODO: rekursiver Aufruf

                return 
                # # Winkel vom Block ist kleiner als der des Shadows
                # # => Block muss an beide Kanten angelegt werden
                # else:
                #     pass

    return []


def __valid_pos(shadow, block, sv_idx, bv_idx, angle) -> bool:
    """
    return True, wenn Block an Vertex platziert werden kann, ohne dass sich Kanten schneiden
    """

    pass



def __subtract_block():
    """
    entfernt Block aus Polygon
    """
    
    pass


def __to_edges(vertices: list[Point]) -> list[Edge]:
    edges: list[Edge] = []

    for v_idx, v in enumerate(vertices):
        edges.append(Edge(vertices[v_idx-1], v))

    return edges


def __intersecting_edges(block: list[Edge], shadow: list[Edge]) -> bool:
    for be in block:
        for se in shadow:
            if be.intersects_with(se):
                return True
    for be in block:
        if not point_in_polygon(be.p1, shadow):
           return True

    return False


def point_in_polygon(point: Point, polygon: list[Edge]):
    results = [raycast(point, polygon)]
    steps = 10
    distance = 10
    for angle in [((360 / steps) * i) for i in range(steps)]:
        p2 = Point.rotate_around_point([Point(point.x + distance, point.y)], point, angle)[0]
        results.append(raycast(p2, polygon))
    
    return results.count(True) > 1

def raycast(point: Point, edges: list[Edge]) -> bool:
    """
    performs a raycast from one point to all edges and tests with how many edges it intersects
    intersection is in positive x direction
    if point is inside the polygon, the function returns True, else False
    """
    e1: Edge = Edge(point, Point(point.x + 1, point.y))
    included = False
    for e2 in edges:
        s, t =intersection_parameters(e1, e2)

        # s > 0                => intersection in positive x-direction to point
        # t > eps && 1-t < eps => intersection on edge with eps distance to end points of edge
        if s > 0 and t > Edge.eps and t < 1-Edge.eps:
            included = not included
    return included