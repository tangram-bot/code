#=======================#
# ENVIRONMENT VARIABLES #
#=======================#

from dotenv import load_dotenv, find_dotenv

load_dotenv(find_dotenv())

#===========#
# MAIN CODE #
#===========#

import robot
import cv
import solver


def main():
    print('[Main] HALLO!!')

    robot.init()

    # TODO: take picture

    # TODO: procecss picture & extract data

    # TODO: find solution
    
    # TODO: move blocks to correct positions

    robot.shutdown()


if __name__ == '__main__':
    main()
