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


def main():
    L.info('HALLO!!')

    # Initialize & calibrate robot
    robot.init()

    img_blocks = robot.scan_blocks()
    # img_shadow = robot.scan_shadow()

    cv.create_trackbar_uis()

    # procecss picture & extract data
    blocks = cv.find_blocks(img_blocks)
    
    for b in blocks:
        robot.pick(b.position[0] / 905, b.position[1] / 640)
        robot.place(b.position[0] / 905, b.position[1] / 640, 0)

    while True:
        cv2.waitKey(1)

    # find solution
    solver.solve(blocks, shadow)
    
    # move blocks to correct positions

    robot.shutdown()


if __name__ == '__main__':
    main()
