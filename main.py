#=======================#
# ENVIRONMENT VARIABLES #
#=======================#

from dotenv import load_dotenv, find_dotenv

load_dotenv(find_dotenv())

#===========#
# MAIN CODE #
#===========#

import niryo

def main():
    niryo.set_max_velocity(100)
    niryo.init()


if __name__ == '__main__':
    main()
