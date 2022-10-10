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
    robot.init()
    robot.set_max_velocity(100)


if __name__ == '__main__':
    main()
