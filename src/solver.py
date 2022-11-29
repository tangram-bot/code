import logging
from typing import List
from model import Point, Block, BlockType, Shadow, Edge
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


from cv import find_shadows
cyk = 0
def solve(blocks: List[Block], img_shadow) -> list[MoveInstruction]:
    """
    Ermittelt eine Lösung für die übergebenen Blöcke und Shadows
    """
    global cyk
    cyk += 1
    cv2.imshow(str(cyk), img_shadow)

    shadows = find_shadows(img_shadow.copy())

    print('\n', len(blocks), [b.btype._name_ for b in blocks], '\n')

    # __check_too_few_blocks(blocks, shadows)

    instructions: list[MoveInstruction] = []
    
    # instr = __check_plain_blocks(blocks, shadows)
    # instructions.extend(instr)

    instr = __solve_rest(blocks, shadows, img_shadow.copy())
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

    tmp_blocks = blocks.copy()

    instructions: list[MoveInstruction] = []

    for s in shadows:
        
        im = np.zeros(shape=img.shape, dtype=np.uint8)
        cv2.fillPoly(im, Point.list_to_np_array(s.vertices), 255)

        instr = __solve_loop(tmp_blocks, s, im)

        if instr is None:
            L.info(f'Couldn\'t find a solution for {s}')
            continue

        instructions.extend(instr)

    return instructions

from pyniryo import cv2
import numpy as np
def __solve_loop(blocks: list[Block], shadow: Shadow, m_img) -> list[MoveInstruction] | None:

    for b_idx, b in enumerate(blocks):
        for sv_idx, sv in enumerate(shadow.vertices):

            # if b.area > shadow.area:
            #     continue

            for bv_idx, bv in enumerate(b.vertices):

                img = m_img.copy()

                # Verhältnis der Innenwinkel bei sv und bv
                angle_ratio = shadow.interior_angles[sv_idx] / b.interior_angles[bv_idx]

                # Winkel vom Block ist größer als der des Shadows
                # => Block passt nicht an diese Stelle
                if angle_ratio < 1:
                    continue

                # # Winkel vom Block und Shadow sind gleich groß
                # # => Block muss nur ein mal angelegt werden
                # elif angle_ratio == 1:

                color = cv2.cvtColor(img, cv2.COLOR_GRAY2BGR)
                cv2.line(color, sv.to_np_int_array(), shadow.get_vertex(sv_idx-1).to_np_int_array(), (0, 255, 0), 1)
                cv2.line(color, sv.to_np_int_array(), shadow.get_vertex(sv_idx+1).to_np_int_array(), (0, 0, 255), 1)

                s_vec = shadow.get_vertex(sv_idx-1) - sv
                b_vec = b.get_vertex(bv_idx-1) - bv
                angle = Point.angle(s_vec, b_vec, True)

                if angle_ratio == 1:
                    s_vec2 = shadow.get_vertex(sv_idx+1) - sv
                    b_vec2 = b.get_vertex(bv_idx+1) - bv
                    angle2 = Point.angle(s_vec2, b_vec2, True)

                    if angle2 - angle > 180:
                        angle += 360
                    if angle - angle2 > 180:
                        angle2 += 360

                    aa = np.linalg.norm(s_vec.to_np_array())
                    bb = np.linalg.norm(s_vec2.to_np_array())
                    cc = aa + bb
                    aa = aa / cc
                    bb = bb / cc
                    angle = (aa * angle + bb * angle2)



                block_vertices = b.get_scaled_vertices()
                block_vertices = Point.move_points(block_vertices, sv-block_vertices[bv_idx])
                block_vertices = Point.rotate_around_point(block_vertices, sv, angle)

                
                im = np.zeros(shape=img.shape, dtype=np.uint8)
                cv2.fillPoly(im, Point.list_to_np_array(block_vertices), 255)

                diff = cv2.subtract(im, img)
                diff = cv2.erode(diff, np.ones((5, 5)))
                diff = cv2.dilate(diff, np.ones((5, 5)))
                summ = np.sum(diff==255)
                if summ > 100:
                    continue

                cv2.fillPoly(img, Point.list_to_np_array(block_vertices), 200)

                cv2.fillPoly(img, Point.list_to_np_array(block_vertices), 0)
                img = cv2.erode(img, np.ones((5, 5)))
                img = cv2.dilate(img, np.ones((5, 5)))

                # genutzten Block entfernen
                # print('\n')
                # print('REMOVE', remaining_blocks[b_idx].btype)
                blocks.pop(b_idx)
                # print([b.btype for b in blocks])
                # print([b.btype for b in remaining_blocks])
                
                # TODO: rekursiver Aufruf
                instructions = solve(blocks, img)

                if instructions is None:
                    blocks.append(b)
                    continue

                center = Point.get_center(block_vertices)

                angle -= b.rotation

                instructions.append(MoveInstruction(b, center, angle))

                # blocks.pop(b_idx)


                return instructions

                # # Winkel vom Block ist kleiner als der des Shadows
                # # => Block muss an beide Kanten angelegt werden
                # else:
                #     pass

    return None


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
        # point_in_shadow = False
        for se in shadow:
            if be.intersects_with(se):
                return True
            # e = Edge(be.p1, be.p1 + Point(1, 0))
            # s, t = intersection_parameters(e, se)
            # if(s > 0):
            #     point_in_shadow = not point_in_shadow
            
        # if(not point_in_shadow):
        #     return True
    # block_points = [be.p1 for be in block]
    # shadow_points = [se.p1 for se in shadow]

    # print("intersect")

    # for test_point in block_points:

    #     print(test_point, bv)
    #     if(test_point == bv):
    #         print("cont")
    #         continue

    #     sum = 0

    #     for sp_idx in range(len(shadow_points)):
    #         shadow_point_1 = shadow_points[sp_idx - 1]
    #         shadow_point_2 = shadow_points[sp_idx]

    #         if(shadow_point_1 == test_point or shadow_point_2 == test_point):
    #             continue

    #         vector_1 = shadow_point_1.to_np_int_array() - test_point.to_np_int_array()
    #         vector_2 = shadow_point_2.to_np_int_array() - test_point.to_np_int_array()

    #         sum += helper.vector_angle(vector_1, vector_2)

    #     print(sum)
    #     print()

    #     if(sum < 350):
    #        return True

    return False
