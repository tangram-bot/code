from pyniryo import *

ip = '10.3.10.14'

bot = NiryoRobot(ip)

bot.set_arm_max_velocity(20)

print('Calibrating...')
bot.calibrate_auto()

print('Homing...')
bot.move_to_home_pose()

while True:
    img_compressed = bot.get_img_compressed()
    img = uncompress_image(img_compressed)

    show_img('img', img)

    if cv2.waitKey(1) == ord('q'):
        break



# def move_joints(j1, j2, j3, j4, j5, j6):
#     j1 = radians(j1)
#     j2 = radians(j2)
#     j3 = radians(j3)
#     j4 = radians(j4)
#     j5 = radians(j5)
#     j6 = radians(j6)

#     # bot.arm.move_joints([j1, j2, j3, j4, j5, j6])

# print('Abfahrt!')

# # bot.end()
