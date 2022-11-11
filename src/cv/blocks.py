import logging
import numpy as np
import cv.trackbar as tb
from pyniryo import cv2, show_img_and_check_close
from helper import vector_angle
from model import LENGTH_FACTOR, Block, Point
from cv.features import BlockFeature


L = logging.getLogger('CV-Blocks')


def find_blocks(img) -> list[Block]:
    features = __find_block_features(img)

    L.debug('Found Features:')
    L.debug(features)

    blocks = __process_block_features(features, img)

    __draw_blocks(img, blocks)

    show_img_and_check_close('Blocks', img)

    return blocks


def __find_block_features(img) -> list[BlockFeature]:
    # Blur image to reduce noise
    img_blur = blur(img)
    
    # Apply color mask to find colored areas
    img_mask = color_mask(img_blur)
    
    # Apply edge detection
    img_edge = find_edges(img_mask)

    features: list[BlockFeature] = []

    for contour in find_contours(img_edge):

        # Skip if contour is too small
        if contour_too_small(contour):
            continue

        # Find corners of the contour
        corners = find_corners(contour)

        # Get the block's center
        center = get_center(corners)

        features.append(BlockFeature(corners, center, cv2.contourArea(contour)))


        __draw_contour(img, contour)
        __draw_corners(img, corners)
        __draw_center(img, center)
        __draw_contour_info(img, contour, corners)


    # show_img_and_check_close('Blocks: Color Mask', img_mask)

    return features


def __process_block_features(features: list[BlockFeature], img) -> list[Block]:
    blocks: list[Block] = []

    for feature in features:
        vertex_count = feature.get_vertex_count()
        area = feature.get_scaled_area()
        int_angles = feature.get_interior_angles()

        if vertex_count == 4 and area == 1.0:

            if max(int_angles) == 135.0:
                block = __process_parallelogram(feature, img)
                blocks.append(block)

            else:
                block = __process_square(feature, img)
                blocks.append(block)

        elif vertex_count == 3:

            if area == 0.5:
                block = __process_small_triangle(feature, img)
                blocks.append(block)

            elif area == 1.0:
                block = __process_medium_triangle(feature, img)
                blocks.append(block)

            elif area == 2.0:
                block = __process_large_triangle(feature, img)
                blocks.append(block)

        else:
            print('Invalid Feature:', feature)
        
    return blocks


def __process_parallelogram(feature: BlockFeature, img) -> Block:
    interior_angles = feature.get_interior_angles()
    ref_vertex = feature.vertices[interior_angles.index(45)]
                
    angle = vector_angle(ref_vertex - feature.center.to_np_array(), (-1, -2)) % 180

    cv2.line(img, feature.center.to_np_array(), ref_vertex[0], (255, 0, 0), 3)
    L.debug(f'PARALLELOGRAM: center={feature.center} angle={angle}°')

    return Block([Point(0, 0), Point(1, 1), Point(1, 2), Point(0, 1)], [45, 135, 45, 135], 1.0, feature.center, angle)


def __process_square(feature: BlockFeature, img) -> Block:
    ref_vertex = feature.vertices[0]

    for v in feature.vertices:
        if v[0][1] < ref_vertex[0][1]:
            ref_vertex = v
    
    angle = vector_angle(ref_vertex - feature.center.to_np_array(), (-1, -1)) % 90
    
    cv2.line(img, feature.center.to_np_array(), ref_vertex[0], (255, 0, 0), 3)
    L.debug(f'SQUARE: center={feature.center} angle={angle}°')

    return Block([Point(0, 0), Point(1, 0), Point(1, 1), Point(0, 1)], [90, 90, 90, 90], 1.0, feature.center, angle)


def __process_small_triangle(feature: BlockFeature, img) -> Block:
    interior_angles = feature.get_interior_angles()
    ref_vertex = feature.vertices[interior_angles.index(90)]
                
    angle = vector_angle(ref_vertex - feature.center.to_np_array(), (-1, -1))

    # Fix rotation > 180°
    cross = np.cross((ref_vertex-feature.center.to_np_array()), (-1, -1))
    if cross > 0:
        angle = 360 - angle
    
    cv2.line(img, feature.center.to_np_array(), ref_vertex[0], (255, 0, 0), 3)
    L.debug(f'SMALL TRIANGLE: center={feature.center} angle={angle}°')

    return Block([Point(0, 0), Point(1, 0), Point(0, 1)], [90, 45, 45], 0.5, feature.center, angle)


def __process_medium_triangle(feature: BlockFeature, img) -> Block:
    interior_angles = feature.get_interior_angles()
    ref_vertex = feature.vertices[interior_angles.index(90)]
    
    angle = vector_angle(ref_vertex - feature.center.to_np_array(), (0, 1))

    # Fix rotation > 180°
    cross = np.cross((ref_vertex-feature.center.to_np_array()), (0, 1))
    if cross > 0:
        angle = 360 - angle
    
    cv2.line(img, feature.center.to_np_array(), ref_vertex[0], (255, 0, 0), 3)
    L.debug(f'MEDIUM TRIANGLE: center={feature.center} angle={angle}°')
    
    return Block([Point(0, 0), Point(2, 0), Point(1, 1)], [45, 45, 90], 1.0, feature.center, angle)


def __process_large_triangle(feature: BlockFeature, img) -> Block:
    interior_angles = feature.get_interior_angles()
    ref_vertex = feature.vertices[interior_angles.index(90)]
                
    angle = vector_angle(ref_vertex - feature.center.to_np_array(), (-1, -1))
    
    # Fix rotation > 180°
    cross = np.cross((ref_vertex-feature.center.to_np_array()), (-1, -1))
    if cross > 0:
        angle = 360 - angle

    cv2.line(img, feature.center.to_np_array(), ref_vertex[0], (255, 0, 0), 3)
    L.debug(f'LARGE TRIANGLE: center={feature.center} angle={angle}°')

    return Block([Point(0, 0), Point(2, 0), Point(0, 2)], [90, 45, 45], 2.0, feature.center, angle)






#=====================#
# CV HELPER FUNCTIONS #
#=====================#

def blur(img):
    kernel_size = tb.VALUES.B_BLUR_KERNEL * 2 + 1
    
    blur_kernel = (kernel_size, kernel_size)

    img_blurred = cv2.GaussianBlur(img, blur_kernel, 1)

    return img_blurred


def color_mask(img):
    lower_h = tb.VALUES.B_MASK_LOWER_H
    lower_s = tb.VALUES.B_MASK_LOWER_S
    lower_v = tb.VALUES.B_MASK_LOWER_V
    upper_h = tb.VALUES.B_MASK_UPPER_H
    upper_s = tb.VALUES.B_MASK_UPPER_S
    upper_v = tb.VALUES.B_MASK_UPPER_V

    lower = (lower_h, lower_s, lower_v)
    upper = (upper_h, upper_s, upper_v)

    img_masked = cv2.inRange(img, lower, upper)

    return img_masked


def find_edges(img):
    threshold_1 = tb.VALUES.B_CANNY_1
    threshold_2 = tb.VALUES.B_CANNY_2

    img_canny = cv2.Canny(img, threshold_1, threshold_2)
    
    kernel_size = tb.VALUES.B_DILATE_K_SIZE
    kernel = np.ones((kernel_size, kernel_size))
    img_edges = cv2.dilate(img_canny, kernel, iterations=1)

    return img_edges


def find_contours(img):
    contours, _ = cv2.findContours(img, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)

    return contours


def contour_too_small(contour):
    area = cv2.contourArea(contour)

    return area < tb.VALUES.B_MIN_CONTOUR_AREA


def find_corners(contour):
    accuracy = tb.VALUES.B_CORNER_ACCURACY

    perimeter = cv2.arcLength(contour, True)

    corners = cv2.approxPolyDP(contour, perimeter * 0.01 * accuracy, True)

    return corners


def get_center(corners) -> Point:
    x_sum = 0
    y_sum = 0
    
    for corner in corners:
        x_sum += corner[0][0]
        y_sum += corner[0][1]

    num_corners = len(corners)

    x_sum //= num_corners
    y_sum //= num_corners

    return Point(x_sum, y_sum)



#=======================#
# DRAW HELPER FUNCTIONS #
#=======================#

def __draw_contour(img, contour) -> None:
    cv2.drawContours(img, contour, -1, (0, 0, 0), 2)
    cv2.drawContours(img, contour, -1, (0, 0, 255), 1)


def __draw_corners(img, corners) -> None:
    for corner in corners:
        cv2.circle(img, corner[0], 2, (0, 0, 0), -1)
        cv2.circle(img, corner[0], 1, (0, 255, 0), -1)


def __draw_center(img, center: Point) -> None:
    cv2.circle(img, center.to_np_array(), 2, (0, 0, 0), -1)
    cv2.circle(img, center.to_np_array(), 1, (255, 0, 0), -1)


def __draw_contour_info(img, contour, corners) -> None:
    num_corners = len(corners)

    x, y, _, _ = cv2.boundingRect(corners)

    cv2.putText(img, str(num_corners) + ' ' + str(round(cv2.contourArea(contour), 2)), (x, y-10), cv2.FONT_HERSHEY_COMPLEX, 0.6, (0, 0, 0), 1)


def __draw_blocks(img, blocks: list[Block]) -> None:
    for block in blocks:
        block.draw(img, (100, 100, 0), block.rotation)
