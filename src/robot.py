import logging
from pyniryo2 import NiryoRobot
from pyniryo import uncompress_image, undistort_image, vision
from math import pi
from os import getenv

from main import getRunEnv


L = logging.getLogger('Robot')

SCAN_POSE_BLOCKS = [0.01, 0.16, 0.35, 0.0, pi/2, 1.57]
SCAN_POSE_SHADOW = [-0.005, -0.155, 0.33, 0.0, pi/2, -1.57]
WS_RATIO = 36 / 23.6

bot: NiryoRobot = None
mtx = None
dist = None


def init():
    global bot
    global mtx
    global dist

    L.info('Connecting...')
    ip = getenv('NIRYO_IP') if getRunEnv() == "prod" else "127.0.0.1"
    if(getRunEnv() == "dev"):
        L.info("DEV runtime, mocking robot")
        return
    
    bot = NiryoRobot(ip)

    L.info('Calibrating...')
    bot.arm.calibrate_auto()

    bot.tool.update_tool()

    mtx, dist = bot.vision.get_camera_intrinsics()


def scan():
    if(bot == None): 
        # TODO : return mock image
        return

    bot.arm.calibrate_auto()

    # move to scan position
    bot.arm.move_pose(SCAN_POSE_BLOCKS)
    
    # take picture & get workspace
    img = take_picture()
    ws = vision.extract_img_workspace(img, WS_RATIO)

    return ws


def take_picture():
    img_comp = bot.vision.get_img_compressed()
    img_dist = uncompress_image(img_comp)
    img = undistort_image(img_dist, mtx, dist)

    return img


def pick(x, y):
    if(bot == None):
        return

    poseUp = bot.vision.get_target_pose_from_rel("blocks", 0.2, x, y, pi/2)
    poseDown = bot.vision.get_target_pose_from_rel("blocks", 0, x, y, pi/2)


    # move to position
    bot.tool.open_gripper()
    bot.arm.move_pose(poseUp)
    bot.arm.move_linear_pose(poseDown)
    # pick object
    bot.tool.close_gripper()
    bot.arm.move_linear_pose(poseUp)


def place(x, y, rotate):
    if(bot == None):
        return
    
    poseUp = bot.vision.get_target_pose_from_rel("shadow", 0.2, x, y, rotate)
    poseDown = bot.vision.get_target_pose_from_rel("shadow", 0, x, y, rotate)

    # move to position
    bot.arm.move_pose(poseUp)
    bot.arm.move_linear_pose(poseDown)

    # place object
    bot.tool.open_gripper()
    bot.arm.move_linear_pose(poseUp)


def shutdown():
    if(bot == None):
        return

    L.info('Shutting down...')
    bot.arm.go_to_sleep()
