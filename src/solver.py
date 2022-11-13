import logging
import numpy as np
from typing import List
from model import Point, Block, BlockType, Shadow
from helper import vector_angle


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


def solve(blocks: List[Block], shadows: list[Shadow]) -> list[MoveInstruction]:
    """
    Ermittelt eine Lösung für die übergebenen Blöcke und Shadows
    """

    instructions: list[MoveInstruction] = []
    
    # Sort shadows by area in ascending order
    shadows.sort(key=lambda p: p.area)

    instr = __check_plain_blocks(blocks, shadows)
    instructions.extend(instr)

    instr = __solve_rest(blocks, shadows)
    instructions.extend(instr)

    return instructions








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
    except:
        return False

    return True


def __get_block_rotation(shadow: Shadow, block: Block) -> float:
    """
    Berechnet den benötigten Winkel von block, damit shadow und block deckungsgleich sind
    """

    switch = {
        BlockType.SQUARE: __get_angle_square,
        BlockType.PARALLELOGRAM: __get_angle_parallelogram,
        BlockType.SMALL_TRIANGLE: __get_angle_small_triangle,
        BlockType.MEDIUM_TRIANGLE: __get_angle_medium_triangle,
        BlockType.LARGE_TRIANGLE: __get_angle_large_triangle,
    }

    rotation = switch.get(block.btype)

    if rotation is None:
        raise TypeError(f'Block has an invalid type: {block.btype._name_}')

    return rotation(shadow)


def __get_angle_square(shadow: Shadow) -> float:
    ref_vertex = None

    for v in shadow.vertices:
        if ref_vertex is None or v.y < ref_vertex.y:
            ref_vertex = v

    angle = Point.angle(ref_vertex - shadow.get_center(), Point(-1, -1)) % 90

    return angle


def __get_angle_parallelogram(shadow: Shadow) -> float:
    ref_vertex = shadow.vertices[shadow.interior_angles.index(45)]
    vec = ref_vertex - shadow.get_center()

    angle = Point.angle(vec, Point(-1, -2)) % 180

    cross = np.cross(vec.to_np_array(), (-1, -2))
    if cross > 0:
        angle = 360 - angle

    return angle

def __get_angle_small_triangle(shadow: Shadow) -> float:
    ref_vertex = shadow.vertices[shadow.interior_angles.index(90)]
    vec = ref_vertex - shadow.get_center()

    angle = Point.angle(vec, Point(-1, -1))

    cross = np.cross(vec.to_np_array(), (-1, -1))
    if cross > 0:
        angle = 360 - angle

    return angle

def __get_angle_medium_triangle(shadow: Shadow) -> float:
    ref_vertex = shadow.vertices[shadow.interior_angles.index(90)]
    vec = ref_vertex - shadow.get_center()

    angle = Point.angle(vec, Point(0, 1))

    cross = np.cross(vec.to_np_array(), (0, 1))
    if cross > 0:
        angle = 360 - angle

    return angle

def __get_angle_large_triangle(shadow: Shadow) -> float:
    ref_vertex = shadow.vertices[shadow.interior_angles.index(90)]
    vec = ref_vertex - shadow.get_center()

    angle = Point.angle(vec, Point(-1, -1))

    cross = np.cross(vec.to_np_array(), (-1, -1))
    if cross > 0:
        angle = 360 - angle

    return angle









#====================#
# MORE COMPLEX STUFF #
#====================#


def __solve_rest(blocks: list[Block], shadows: list[Shadow]) -> list[MoveInstruction]:
    return []
