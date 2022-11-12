#=============#
# PREPARATION #
#=============#

import argparse
from dotenv import load_dotenv, find_dotenv
import logging
from audio import play, AudioFile


load_dotenv(find_dotenv())
parser = argparse.ArgumentParser("env")
parser.add_argument('-e', '--env', default="dev")
parser.add_argument('-tb', '--trackbars', nargs='?', const='')
parser.add_argument('-s', '--sound', nargs='?', const='')

args = parser.parse_args()

def get_run_env():
    return args.env

def show_trackbars():
    return args.trackbars is not None

def play_sound() -> bool:
    return args.sound is not None

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
    play(AudioFile.START)
    # Initialize & calibrate robot
    robot.init()

    play(AudioFile.SCAN_BLOCKS)
    # Take pictures of blocks & shadow
    img_blocks = robot.scan_blocks()

    play(AudioFile.SCAN_SHADOW)
    img_shadow = robot.scan_shadow()

    play(AudioFile.SOLVE_START)
    # Procecss pictures & extract data
    blocks = cv.find_blocks(img_blocks)
    shadows = cv.find_shadows(img_shadow)

    # Find solution
    solution = solver.solve(blocks, shadows)
    play(AudioFile.SOLVE_END)
    
    # TODO: Handling if no solution could be found
    # if solution is None:
    # ...
    
    # TODO: Move blocks to correct positions
    # play(AudioFile.MOVE_BLOCKS)
    # robot.move_blocks(solution)

    play(AudioFile.FINISH)
    # We're done, the robot can go to sleep
    robot.shutdown()

    while True:
        cv2.waitKey(1)


if __name__ == '__main__':
    main()
