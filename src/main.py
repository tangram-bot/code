#=============#
# PREPARATION #
#=============#

from dotenv import load_dotenv, find_dotenv
import logging


load_dotenv(find_dotenv())

logging.basicConfig(format='%(asctime)s %(levelname)s\t [%(name)s] %(message)s', level=logging.INFO)


#===========#
# MAIN CODE #
#===========#

import robot
import cv
import solver


log = logging.getLogger('Main')


def main():
    log.info('HALLO!!')

    robot.init()

    # TODO: take picture

    # TODO: procecss picture & extract data

    # TODO: find solution
    
    # TODO: move blocks to correct positions

    robot.shutdown()


if __name__ == '__main__':
    main()
