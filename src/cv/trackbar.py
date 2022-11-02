from pyniryo import cv2


# Window Names
NW_BLOCKS = 'CV: Blocks'
NW_SHADOW = 'CV: Shadow'

# Trackbar Names
TB_BLUR_K = 'Blur Kernel'
TB_MASK_L_H = 'Mask Lower H'
TB_MASK_L_S = 'Mask Lower S'
TB_MASK_L_V = 'Mask Lower V'
TB_MASK_U_H = 'Mask Upper H'
TB_MASK_U_S = 'Mask Upper S'
TB_MASK_U_V = 'Mask Upper V'
TB_CANNY_1 = 'Canny 1'
TB_CANNY_2 = 'Canny 2'
TB_DILATE_K = 'Dilate Kernel'
TB_CONT_AR = 'Min Contour Area'
TB_CORN_ACC = 'Corner Accuracy'


def create_trackbar_uis() -> None:
    cv2.namedWindow(NW_BLOCKS)
    cv2.createTrackbar(TB_BLUR_K,   NW_BLOCKS,  1,      10,     lambda x: x)
    cv2.createTrackbar(TB_MASK_L_H, NW_BLOCKS,  0,      255,    lambda x: x)
    cv2.createTrackbar(TB_MASK_L_S, NW_BLOCKS,  0,      255,    lambda x: x)
    cv2.createTrackbar(TB_MASK_L_V, NW_BLOCKS,  30,     255,    lambda x: x)
    cv2.createTrackbar(TB_MASK_U_H, NW_BLOCKS,  115,    255,    lambda x: x)
    cv2.createTrackbar(TB_MASK_U_S, NW_BLOCKS,  255,    255,    lambda x: x)
    cv2.createTrackbar(TB_MASK_U_V, NW_BLOCKS,  255,    255,    lambda x: x)
    cv2.createTrackbar(TB_CANNY_1,  NW_BLOCKS,  0,      255,    lambda x: x)
    cv2.createTrackbar(TB_CANNY_2,  NW_BLOCKS,  0,      255,    lambda x: x)
    cv2.createTrackbar(TB_DILATE_K, NW_BLOCKS,  1,      10,     lambda x: x)
    cv2.createTrackbar(TB_CONT_AR,  NW_BLOCKS,  200,    500,    lambda x: x)
    cv2.createTrackbar(TB_CORN_ACC, NW_BLOCKS,  5,      1000,   lambda x: x)

    cv2.namedWindow(NW_SHADOW)
    cv2.createTrackbar(TB_BLUR_K,   NW_SHADOW,  2,      10,     lambda x: x)
    cv2.createTrackbar(TB_CANNY_1,  NW_SHADOW,  0,      255,    lambda x: x)
    cv2.createTrackbar(TB_CANNY_2,  NW_SHADOW,  0,      255,    lambda x: x)
    cv2.createTrackbar(TB_DILATE_K, NW_SHADOW,  1,      10,     lambda x: x)
    cv2.createTrackbar(TB_CONT_AR,  NW_SHADOW,  200,    500,    lambda x: x)
    cv2.createTrackbar(TB_CORN_ACC, NW_SHADOW,  5,      1000,   lambda x: x)
