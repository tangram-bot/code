import logging
import random
import numpy as np
from pyniryo2 import NiryoRobot
from pyniryo import uncompress_image, undistort_image, vision, cv2
from math import pi
from os import getenv
from PIL import Image

from main import get_run_env


L = logging.getLogger('Robot')

SCAN_POSE_BLOCKS = [0.01, 0.16, 0.35, 0.0, pi/2, 1.57]
SCAN_POSE_SHADOW = [-0.005, -0.155, 0.33, 0.0, pi/2, -1.57]

WORKSPACE_WIDTH = 297
WORKSPACE_HEIGHT = 210
PICK_AND_PLACE_HEIGHT = 0.0015
MOVEMENT_HEIGHT = 0.2
GRIPPER_BASE_ROTATION=pi/2
WORKSPACE_RATIO = WORKSPACE_WIDTH / WORKSPACE_HEIGHT

MOCK_IMG_FILES = ["test-01.png", "test-02.png", "test-03.png"]

bot: NiryoRobot = None
mtx = None
dist = None


def init():
    global bot
    global mtx
    global dist

    L.info('Connecting...')
    ip = getenv('NIRYO_IP') if get_run_env() == "prod" else "127.0.0.1"
    if(get_run_env() == "dev"):
        L.info("DEV runtime, mocking robot")
        return
    
    bot = NiryoRobot(ip)

    L.info('Calibrating...')
    bot.arm.calibrate_auto()

    bot.tool.update_tool()

    mtx, dist = bot.vision.get_camera_intrinsics()


# TODO: Separate Mock-Bilder für Blocks und Shadow
def mock_image():
    img_file = random.choice(MOCK_IMG_FILES)
    
    img = Image.open(f"img/{img_file}")
    
    img = np.asarray(img)
    
    img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

    return img


def scan_blocks():
    if(bot == None): 
        return mock_image()

    bot.arm.calibrate_auto()

    # move to scan position
    bot.arm.move_pose(SCAN_POSE_BLOCKS)
    bot.arm.move_pose(SCAN_POSE_BLOCKS) # maybe this fixes some issues with not recognizing the workspace, maybe not, has to be observed
    
    ws = take_picture()

    return ws


def scan_shadow():
    if(bot == None):
        return mock_image()

    bot.arm.calibrate_auto()

    bot.arm.move_pose(SCAN_POSE_SHADOW)

    ws = take_picture()

    return ws


def take_picture():
    L.info("Taking picture")
    img_comp = bot.vision.get_img_compressed()
    
    img_dist = uncompress_image(img_comp)
    
    img = undistort_image(img_dist, mtx, dist)

    ws = vision.extract_img_workspace(img, WORKSPACE_RATIO)

    if ws is None:
        raise Exception('Could not extract workspace from image')

    return ws


def pick(x, y):
    if(bot == None):
        return

    L.info(f"picking from {x}, {y}")

    # fix hardware with software
    # the gripper is not centered, so the position has to be corrected
    # this has to be done in place() as well, but there dynamically, as the gripper will rotate to the right orientation
    x = min(x + 0.05, 1)
    y = max(y - 0.01, 0)

    pose_up = bot.vision.get_target_pose_from_rel("blocks", MOVEMENT_HEIGHT, x, y, GRIPPER_BASE_ROTATION)
    pose_down = bot.vision.get_target_pose_from_rel("blocks", PICK_AND_PLACE_HEIGHT, x, y, GRIPPER_BASE_ROTATION)


    # move to position
    bot.tool.open_gripper()
    bot.arm.move_pose(pose_up)
    bot.arm.move_linear_pose(pose_down)
    # pick object
    
    bot.tool.close_gripper()
    bot.arm.move_linear_pose(pose_up)


def place(x, y, rotate):
    if(bot == None):
        return

    L.info(f"Placing to {x}, {y}")

    # rotation of 0 should be the same direction as the source rotation
    # but because the piece of paper is on the other side of the robot, is has to be corrected here
    rotate -= GRIPPER_BASE_ROTATION
    
    pose_up = bot.vision.get_target_pose_from_rel("shadow", MOVEMENT_HEIGHT, x, y, rotate)
    pose_down = bot.vision.get_target_pose_from_rel("shadow", PICK_AND_PLACE_HEIGHT, x, y, rotate)

    # move to position
    bot.arm.move_pose(pose_up)
    bot.arm.move_linear_pose(pose_down)
    # place object
    bot.tool.open_gripper()
    bot.arm.move_linear_pose(pose_up)


def shutdown():
    if(bot == None):
        return

    L.info('Shutting down...')
    bot.arm.go_to_sleep()
