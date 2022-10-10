import logging
from pyniryo2 import NiryoRobot
from pyniryo import uncompress_image, show_img, undistort_image, cv2, vision
from math import pi
from os import getenv

from main import getRunEnv


log = logging.getLogger('Robot')

bot: NiryoRobot = None


def init():
    global bot

    log.info('Connecting...')
    ip = getenv('NIRYO_IP') if getRunEnv() == "prod" else "127.0.0.1"
    if(getRunEnv() == "dev"):
        log.info("DEV runtime, mocking robot")
        return
    
    bot = NiryoRobot(ip)

    log.info('Calibrating...')
    bot.arm.request_new_calibration()

    log.info('Homing...')
    bot.arm.move_to_home_pose()


def scan():
    if(bot == None): 
            # TODO : return mock image
            return

    bot.arm.calibrate_auto()
    
    # move to scan position
    bot.arm.move_pose([0.22, 0, 0.35, 0, pi/2, 0])

    mtx, dist = bot.vision.get_camera_intrinsics()
    
    # procecss image
    img = bot.vision.get_img_compressed()
    img = uncompress_image(img)
    img = undistort_image(img, mtx, dist)

    ws = vision.extract_img_workspace(img, (36/23.6))

    return ws


def pick(x, y):
    if(bot == None):
        return
    
    pose = bot.vision.get_target_pose_from_rel("workspace_1", 0.1, x, y, pi/2)
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
    
    pose = bot.vision.get_target_pose_from_rel("workspace_1", 0.1, x, y, rotate)
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
    log.info('Shutting down...')
    bot.arm.go_to_sleep()
