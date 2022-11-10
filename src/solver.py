import logging
from typing import List
from model import Point, Block, Shadow


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
                    rotation=   block.rotation # TODO: Rotation muss noch berechnet werden.
                ))

                break

    return instructions



def __solve_shadow(blocks: list[Block], shadow: Shadow) -> list[MoveInstruction]:

    pass
