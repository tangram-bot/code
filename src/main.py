#=============#
# PREPARATION #
#=============#

import argparse
import logging
from dotenv import load_dotenv, find_dotenv


load_dotenv(find_dotenv())
parser = argparse.ArgumentParser("env")
parser.add_argument('-e', '--env', default="dev")
parser.add_argument('-tb', '--trackbars', nargs='?', const='')

args = parser.parse_args()

def get_run_env():
    return args.env

def show_trackbars():
    return args.trackbars is not None

logLevels={
    'prod': logging.INFO,
}
logLevel = logLevels.get(get_run_env(), logging.DEBUG)

logging.basicConfig(format='%(asctime)s %(levelname)s\t [%(name)s] %(message)s', level=logLevel)


#===========#
# MAIN CODE #
#===========#

import robot
import cv
import solver

from pyniryo import cv2
import numpy as np
from random import random


L = logging.getLogger('Main')


def main() -> None:
    L.info('HALLO!!')

    # Initialize & calibrate robot
    robot.init()

    # Take pictures of blocks & shadow
    img_blocks = robot.scan_blocks()
    img_shadow = robot.scan_shadow()

    # Procecss pictures & extract data
    blocks = cv.find_blocks(img_blocks)
    shadows = cv.find_shadows(img_shadow)

    # Find solution
    img_temp_sol = img_shadow.copy()
    instructions = solver.solve(blocks, shadows, img_temp_sol)
    cv2.imshow('Solution Debug', img_temp_sol)

    img_solution = img_shadow.copy()
    for i in instructions:
        i.block.draw(img_solution, (int(random() * 255), int(random() * 255), int(random() * 255)), i.rotation, i.position)
    cv2.imshow('Solution', img_solution)
    
    # TODO: Handling if no solution could be found
    # if instructions is None:
    # ...

    robot.move_blocks(instructions)

    # We're done, the robot can go to sleep
    robot.shutdown()

    while True:
        cv2.waitKey(1)


if __name__ == '__main__':
    main()
