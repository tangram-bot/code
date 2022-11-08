import logging
from typing import List
from model import Block, Shadow, Point


L = logging.getLogger('Solver')


class MoveInstruction:
    from_point: Point
    to_point: Point
    
    rotation: float

    def __init__(self, from_point: Point, to_point: Point, rotation: float) -> None:
        self.from_point = from_point
        self.to_point = to_point
        self.rotation = rotation


def solve(blocks: List[Block], shadows: list[Shadow]) -> list[MoveInstruction]:
    instructions: list[MoveInstruction] = []
    
    # TODO: implement :)

    return instructions
