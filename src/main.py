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
    'dev': logging.WARNING
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
    img_shadow_raw = robot.scan_shadow()
    img_shadow = cv.prepare_shadow_image(img_shadow_raw)

    # Procecss pictures & extract data
    blocks = cv.find_blocks(img_blocks)

    # Find solution
    instructions = solver.solve(blocks, img_shadow)

    img_solution = img_shadow_raw.copy()
    for i in instructions:
        i.block.draw(img_solution, (int(random() * 255), int(random() * 255), int(random() * 255)), i.rotation+i.block.rotation, i.position)
    cv2.imshow('Solution', img_solution)
    
    # TODO: Handling if no solution could be found
    # if instructions is None:
    # ...

    robot.move_blocks(instructions)

    # We're done, the robot can go to sleep
    robot.shutdown()
    robot.close()

    while True:
        cv2.waitKey(1)


if __name__ == '__main__':
    main()
