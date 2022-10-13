import logging
from pyniryo2 import NiryoRobot
from pyniryo import uncompress_image, show_img, undistort_image, cv2, vision
from math import pi
from os import getenv

from main import getRunEnv


L = logging.getLogger('Robot')

SCAN_POSE = [0.20, 0.0, 0.35, 0.0, pi/2, 0.0]
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

    L.info('Homing...')
    bot.arm.move_to_home_pose()

    mtx, dist = bot.vision.get_camera_intrinsics()


def scan():
    if(bot == None): 
        # TODO : return mock image
        return

    bot.arm.calibrate_auto()

    # move to scan position
    bot.arm.move_pose(SCAN_POSE)
    
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
    
    pose = bot.vision.get_target_pose_from_rel("labor", 0.1, x, y, pi/2)
    poseUp = pose
    poseUp.z = 0.5

    # move to position
    bot.tool.open_gripper()
    bot.arm.move_pose(poseUp)
    bot.arm.move_linear_pose(pose)
    # pick object
    bot.tool.close_gripper()
    bot.arm.move_linear_pose(poseUp)


def place(x, y, rotate):
    if(bot == None):
        return
    
    pose = bot.vision.get_target_pose_from_rel("labor", 0.1, x, y, rotate)
    poseUp = pose
    poseUp.z = 0.5

    # move to position
    bot.arm.move_pose(poseUp)
    bot.arm.move_linear_pose(pose)

    # place object
    bot.tool.open_gripper()
    bot.arm.move_linear_pose(poseUp)


def shutdown():
    if(bot == None):
        return

    L.info('Shutting down...')
    bot.arm.go_to_sleep()
