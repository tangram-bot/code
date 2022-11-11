import logging
import numpy as np
from typing import List
from model import Point, Block, BlockType, Shadow
from helper import vector_angle


L = logging.getLogger('Solver')


class MoveInstruction:
    block: Block
    position: Point
    rotation: float

    def __init__(self, block: Block, position: Point, rotation: float) -> None:
        self.block = block
        self.position = position
        self.rotation = rotation


def solve(blocks: List[Block], shadows: list[Shadow]) -> list[MoveInstruction]:
    instructions: list[MoveInstruction] = []
    
    # Sort shadows by area in ascending order
    shadows.sort(key=lambda p: p.area)

    instr = __check_plain_blocks(blocks, shadows)
    instructions.extend(instr)


    # for shadow in shadows:
    #     instr = __solve_shadow(blocks, shadow)
    #     instructions += instr

    return instructions


def __check_plain_blocks(blocks: list[Block], shadows: list[Shadow]) -> list[MoveInstruction]:
    """
    Überprüft, ob Shadows existieren, die genau aus einem Block bestehen.
    """

    instructions: list[MoveInstruction] = []

    # shadows muss rückwärts durchlaufen werden, weil Elemente entfernt werden
    for s_idx in range( len(shadows) - 1, -1, -1 ):
        shadow: Shadow = shadows[s_idx]

        for b_idx, block in enumerate(blocks):
            if len(shadow.vertices) == len(block.vertices) and shadow.area == block.area:

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


def __get_block_rotation(shadow: Shadow, block: Block) -> float:
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

    print('ROTATION', rotation, rotation(shadow))
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

def __solve_shadow(blocks: list[Block], shadow: Shadow) -> list[MoveInstruction]:

    pass
