import logging
from pyniryo2 import NiryoRobot
from pyniryo import uncompress_image, show_img, undistort_image, cv2, vision
from math import pi
from os import getenv


log = logging.getLogger('Robot')

bot: NiryoRobot = None


def init():
    global bot

    log.info('Connecting to robot...')
    bot = NiryoRobot(getenv('NIRYO_IP'))

    log.info('Calibrating...')
    bot.arm.calibrate_auto()

    log.info('Homing...')
    bot.arm.move_to_home_pose()


def scan():
    # self.bot.arm.move_pose([0.28, 0, 0.35, 0, pi/2, 0])

    # mtx, dist = bot.vision.get_camera_intrinsics()
    
    # img = bot.vision.get_img_compressed()
    # img = uncompress_image(img)
    # img = undistort_image(img, mtx, dist)

    # ws = vision.extract_img_workspace(img, (36/23.6))

    # if ws is None:
    #     continue

    pass


def shutdown():
    log.info('Shutting down...')
    bot.arm.go_to_sleep()
