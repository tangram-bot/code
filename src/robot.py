import atexit
import logging
import os
import random
import numpy as np
import pickle
from pyniryo2 import NiryoRobot
from pyniryo import uncompress_image, undistort_image, vision, cv2
from math import pi
from os import getenv
from PIL import Image
from exception import TangramException
from main import get_run_env
from solver import MoveInstruction
import math
import signal


L = logging.getLogger('Robot')

IMAGE_WIDTH = 905
IMAGE_HEIGHT = 640

SCAN_POSE_BLOCKS = [0.01, 0.15, 0.35, 0.0, pi/2, 1.57]
SCAN_POSE_SHADOW = [-0.005, -0.14, 0.35, 0.0, pi/2, -1.57]

PICK_AND_PLACE_HEIGHT = 0.0015
MOVEMENT_HEIGHT = 0.2
GRIPPER_BASE_ROTATION=pi/2

WORKSPACE_WIDTH = 297
WORKSPACE_HEIGHT = 210
WORKSPACE_RATIO = WORKSPACE_WIDTH / WORKSPACE_HEIGHT

import pyniryo.vision.markers_detection as x
x.IM_EXTRACT_SMALL_SIDE_PIXELS = IMAGE_HEIGHT

bot: NiryoRobot = None
mtx = None
dist = None
capture = None

camera_calibration = pickle.load(open("resources/camera_calib.p", "rb" ))


GRIPPER_OFFSET= (-0.009, 0.0)

def get_high_res_camera_intrinsics():
    return camera_calibration["mtx"], camera_calibration["dist"]


def init() -> None:
    global bot
    global mtx
    global dist
    global capture

    ip = getenv('NIRYO_IP')
    if(get_run_env() == "dev"):
        L.info("DEV runtime, mocking robot")
        return
    
    L.info('Connecting...')
    bot = NiryoRobot(ip)

    L.info('Calibrating...')
    bot.arm.calibrate_auto()

    bot.tool.update_tool()

    mtx, dist = get_high_res_camera_intrinsics()


def mock_image(folder):
    path = f"resources/img/{folder}/"
    files = os.listdir(path)
    img_file = random.choice(files)

    img = Image.open(f"{path}{img_file}")    
    img = np.asarray(img)
    img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

    return img


def scan_blocks():
    if(bot == None): 
        return mock_image("blocks")

    # move to scan position
    bot.arm.move_pose(SCAN_POSE_BLOCKS)
    bot.arm.move_pose(SCAN_POSE_BLOCKS)
    bot.arm.move_pose(SCAN_POSE_BLOCKS) # maybe this fixes some issues with not recognizing the workspace, maybe not, has to be observed
    
    ws = take_picture()

    return ws


def scan_shadow():
    if(bot == None):
        return mock_image("shadow")

    bot.arm.move_pose(SCAN_POSE_SHADOW)
    bot.arm.move_pose(SCAN_POSE_SHADOW)
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
        raise TangramException('Could not extract workspace from image')

    return ws


def gripper_offset(rotate, negate_constant_offset):

    multiplyer = -1 if negate_constant_offset else 1

    gripper_offset_x = math.cos(rotate) * GRIPPER_OFFSET[0] - math.sin(rotate) * GRIPPER_OFFSET[1]
    gripper_offset_y = math.sin(rotate) * GRIPPER_OFFSET[0] + math.cos(rotate) * GRIPPER_OFFSET[1]
    return gripper_offset_x - 0.006 * multiplyer, gripper_offset_y - 0.002 * multiplyer

def pick(x, y, flip: bool) -> None:
    if(bot == None):
        return

    L.info(f"picking from {x}, {y}")
    # fix hardware with software
    # the gripper is not centered, so the position has to be corrected
    # this has to be done in place() as well, but there dynamically, as the gripper will rotate to the right orientation
    
    rotation = 0
    if flip:
        rotation = pi
    offset: tuple[float, float] = gripper_offset(rotation, False)

    pose_up = bot.vision.get_target_pose_from_rel("blocks", MOVEMENT_HEIGHT, x, y, 0)
    pose_down = bot.vision.get_target_pose_from_rel("blocks", PICK_AND_PLACE_HEIGHT, x, y, 0)

    pose_up.yaw = rotation
    pose_down.yaw = rotation

    pose_up.x += offset[0]
    pose_up.y += offset[1]

    pose_down.x += offset[0]
    pose_down.y += offset[1]

    # move to position
    bot.tool.open_gripper()
    bot.arm.move_pose(pose_up)
    bot.arm.move_linear_pose(pose_down)
    # pick object
    
    bot.tool.close_gripper()
    bot.arm.move_linear_pose(pose_up)


def place(x, y, rotate) -> None:
    if(bot == None):
        return

    L.info(f"Placing to {x}, {y}")

    rotate = math.radians(rotate)

    gripper_offset_x, gripper_offset_y = gripper_offset(rotate, True)

    pose_up = bot.vision.get_target_pose_from_rel("shadow", MOVEMENT_HEIGHT, x, y, 0)
    pose_down = bot.vision.get_target_pose_from_rel("shadow", PICK_AND_PLACE_HEIGHT, x, y, 0)

    pose_up.roll = 0
    pose_down.roll = 0

    pose_up.yaw = rotate
    pose_down.yaw = rotate

    pose_up.x += gripper_offset_x
    pose_up.y += gripper_offset_y

    pose_down.x += gripper_offset_x
    pose_down.y += gripper_offset_y

    # move to position
    bot.arm.move_pose(pose_up)
    bot.arm.move_linear_pose(pose_down)
    # place object
    bot.tool.open_gripper()
    bot.arm.move_linear_pose(pose_up)


def shutdown() -> None:
    if(bot == None):
        return

    L.info('Shutting down...')
    bot.arm.go_to_sleep()

def close() -> None:
    if(bot == None):
        return
    
    L.info('Closing connection...')
    bot.end()
    exit(0)

def move_blocks(instructions: list[MoveInstruction]) -> None:
    for instruction in instructions:
        # blatt liegt auf der anderen seite -> 180 grad gedreht, rotation von 0, bedeutet 180 grad nach rechts
        rotation = instruction.rotation + 180
        if(rotation > 180):
            # rotation größer 180 muss durch die drehung im pick abgefangen werden
            rotation = rotation - 180
        pick(instruction.block.center.x / IMAGE_WIDTH, instruction.block.center.y / IMAGE_HEIGHT, instruction.rotation < 0)
        place(instruction.position.x / IMAGE_WIDTH, instruction.position.y / IMAGE_HEIGHT, rotation - 180 )
    

atexit.register(close)
if get_run_env() != "dev":
    signal.signal(signal.SIGINT, lambda _, __: close)