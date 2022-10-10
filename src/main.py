#=======================#
# ENVIRONMENT VARIABLES #
#=======================#

from dotenv import load_dotenv, find_dotenv

load_dotenv(find_dotenv())

#===========#
# MAIN CODE #
#===========#

from niryo import Niryo

def main():
    bot = Niryo()

    bot.init()
    bot.set_max_velocity(100)


if __name__ == '__main__':
    main()
