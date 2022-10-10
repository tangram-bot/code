from pyniryo2 import NiryoRobot
from pyniryo import uncompress_image, show_img, undistort_image, cv2, vision
from math import pi
from os import getenv

bot: NiryoRobot = None

def init():
    bot = NiryoRobot(getenv('NIRYO_IP'))

    print('Calibrating...')
    bot.arm.calibrate_auto()

    bot.arm.move_pose([0.28, 0, 0.35, 0, pi/2, 0])

def set_max_velocity(max_vel):
    bot.arm.set_arm_max_velocity(max_vel)


# mtx, dist = bot.vision.get_camera_intrinsics()


# while True:
#     img = bot.vision.get_img_compressed()
#     img = uncompress_image(img)
#     img = undistort_image(img, mtx, dist)

#     ws = vision.extract_img_workspace(img, (36/23.6))

#     if ws is None:
#         continue

#     ws = vision.threshold_hsv(ws, [0, 92, 64], [6, 220, 255])

#     show_img('ws', ws)

# bot.arm.go_to_sleep()
