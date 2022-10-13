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

def getRunEnv():
    return args.env

logLevels={
    'prod': logging.INFO,
    'stage': logging.INFO,
    'dev': logging.DEBUG,
}
logLevel = logLevels.get(getRunEnv(), logging.DEBUG)

logging.basicConfig(format='%(asctime)s %(levelname)s\t [%(name)s] %(message)s', level=logLevel)


#===========#
# MAIN CODE #
#===========#

import robot
import cv
import solver


L = logging.getLogger('Main')


def main():
    L.info('HALLO!!')

    robot.init()

    # take picture
    img = robot.scan()

    # procecss picture & extract data
    # while True:
    blocks, shadow = cv.process_image(img)
    b = blocks[0]

    robot.pick(b[0], b[1])

    while True:
        pass

    # find solution
    solver.solve(blocks, shadow)
    
    # move blocks to correct positions

    robot.shutdown()


if __name__ == '__main__':
    main()
