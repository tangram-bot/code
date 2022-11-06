#=============#
# PREPARATION #
#=============#

import argparse
from dotenv import load_dotenv, find_dotenv
import logging


load_dotenv(find_dotenv())
parser = argparse.ArgumentParser("env")
parser.add_argument('-e', '--env', default="dev")

args = parser.parse_args()

def get_run_env():
    return args.env

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


L = logging.getLogger('Main')


def main() -> None:
    L.info('HALLO!!')

    # Initialize & calibrate robot
    robot.init()

    # Take pictures of blocks & shadow
    img_blocks = robot.scan_blocks()
    img_shadow = robot.scan_shadow()

    cv.create_trackbar_uis()

    # Procecss pictures & extract data
    blocks = cv.find_blocks(img_blocks)
    shadows = cv.find_shadows(img_shadow)

    # Find solution
    solution = solver.solve(blocks, shadows)
    
    # TODO: Handling if no solution could be found
    # if solution is None:
    # ...

    # TODO: Move blocks to correct positions
    # robot.move_blocks(solution)

    # We're done, the robot can go to sleep
    robot.shutdown()


if __name__ == '__main__':
    main()
