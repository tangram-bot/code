import logging
import math
import numpy as np
from typing import List, Tuple
from pyniryo import cv2, show_img_and_check_close
from helper import rotate_around_center, vector_angle
from tangram import LENGTH_FACTOR, Block, Shadow, AREA_FACTOR, SHAPES


L = logging.getLogger('CV')

NW_BLOCKS = 'CV: Blocks'
NW_SHADOW = 'CV: Shadow'


def create_trackbar_uis():
    cv2.namedWindow('CV: Blocks')
    cv2.createTrackbar('Blur Kernel',       NW_BLOCKS,  1,      10,     lambda x: x)
    cv2.createTrackbar('Mask Lower H',      NW_BLOCKS,  0,      255,    lambda x: x)
    cv2.createTrackbar('Mask Lower S',      NW_BLOCKS,  0,      255,    lambda x: x)
    cv2.createTrackbar('Mask Lower V',      NW_BLOCKS,  30,     255,    lambda x: x)
    cv2.createTrackbar('Mask Upper H',      NW_BLOCKS,  115,    255,    lambda x: x)
    cv2.createTrackbar('Mask Upper S',      NW_BLOCKS,  255,    255,    lambda x: x)
    cv2.createTrackbar('Mask Upper V',      NW_BLOCKS,  255,    255,    lambda x: x)
    cv2.createTrackbar('Canny 1',           NW_BLOCKS,  0,      255,    lambda x: x)
    cv2.createTrackbar('Canny 2',           NW_BLOCKS,  0,      255,    lambda x: x)
    cv2.createTrackbar('Dilate Kernel',     NW_BLOCKS,  1,      10,     lambda x: x)
    cv2.createTrackbar('Min Contour Area',  NW_BLOCKS,  200,    500,    lambda x: x)
    cv2.createTrackbar('Corner Accuracy',   NW_BLOCKS,  5,      1000,   lambda x: x)

    cv2.namedWindow('CV: Shadow')
    cv2.createTrackbar('Blur Kernel',       NW_SHADOW,  2,      10,     lambda x: x)
    cv2.createTrackbar('Canny 1',           NW_SHADOW,  0,      255,    lambda x: x)
    cv2.createTrackbar('Canny 2',           NW_SHADOW,  0,      255,    lambda x: x)
    cv2.createTrackbar('Dilate Kernel',     NW_SHADOW,  1,      10,     lambda x: x)
    cv2.createTrackbar('Min Contour Area',  NW_SHADOW,  200,    500,    lambda x: x)
    cv2.createTrackbar('Corner Accuracy',   NW_SHADOW,  5,      1000,   lambda x: x)







def find_blocks(img) -> List[Block]:
    features = __find_block_features(img)

    L.debug('Found Features:')
    L.debug(features)

    blocks = __process_block_features(features, img)

    show_img_and_check_close('After Processing', img)

    for block in blocks:
        x = block.vertices.copy()

        # Skalieren
        for i in range(len(x)):
            x[i] = (x[i][0] * LENGTH_FACTOR, x[i][1] * LENGTH_FACTOR)

        # Center
        x_sum = 0
        y_sum = 0
        for xx in x:
            x_sum += xx[0]
            y_sum += xx[1]
        x_sum //= len(x)
        y_sum //= len(x)
        
        # Verschieben
        for i in range(len(x)):
            x[i] = (x[i][0] + block.position[0] - x_sum, x[i][1] + block.position[1] - y_sum)

        # Rotate shape
        x = rotate_around_center(x, block.position, block.rotation)

        # Convert vertices' coordinates to integers
        for i in range(len(x)):
            x[i] = (round(x[i][0]), round(x[i][1]))
        
        # Draw shape after rotating
        cv2.polylines(img, pts=np.array([x]), color=(0, 255, 0), thickness=3, isClosed=True)
        # Draw shape's center
        cv2.circle(img, block.position, 5, (100, 100, 100), -1)


    show_img_and_check_close('TEST', img)

    return blocks




class BlockFeature:
    vertices: List[Tuple[float, float]]
    center: Tuple[float, float]
    area: float


    def __init__(self, vertices: List[Tuple[float, float]], center: Tuple[float, float], area: float):
        self.vertices = vertices
        self.center = center
        self.area = area


    def get_vertex_count(self):
        return len(self.vertices)


    def get_scaled_area(self):
        TOLERANCE = 0.2

        area = self.area / AREA_FACTOR
        area = round(area, 1)

        if abs(0.5 - area) <= TOLERANCE:
            area = 0.5

        elif abs(1.0 - area) <= TOLERANCE:
            area = 1.0

        elif abs(2.0 - area) <= TOLERANCE:
            area = 2.0

        return area


    def get_interior_angles(self):
        TOLERANCE = 20.0

        angles: List[float] = []

        for i in range(len(self.vertices)):
            v = self.vertices[i].ravel()
            a = self.vertices[(i+1)%len(self.vertices)].ravel()
            b = self.vertices[(i-1)%len(self.vertices)].ravel()

            a = a - v
            b = b - v

            angle = math.acos( np.dot(a, b) / ( abs(np.linalg.norm(a)) * abs(np.linalg.norm(b)) ) )
            angle = math.degrees(angle)

            if abs(45.0 - angle) <= TOLERANCE:
                angle = 45.0
            elif abs(90.0 - angle) <= TOLERANCE:
                angle = 90.0
            elif abs(135.0 - angle) <= TOLERANCE:
                angle = 135.0

            angles.append(angle)

        return angles


    def __str__(self):
        return 'BlockFeature(vertices=%s, center=%s, area=%f)' % (self.vertices, self.center, self.area)


    def __repr__(self):
        return self.__str__()


def __find_block_features(img) -> List[BlockFeature]:
    # Blur image to reduce noise
    img_blur = __blur(img, NW_BLOCKS)
    
    # Apply color mask to find colored areas
    img_mask = __color_mask(img_blur, NW_BLOCKS)
    
    # Apply edge detection
    img_edge = __find_edges(img_mask, NW_BLOCKS)

    features: List[BlockFeature] = []

    for contour in __find_contours(img_edge):

        # Skip if contour is too small
        if __contour_too_small(contour, NW_BLOCKS):
            continue

        # Find corners of the contour
        corners = __find_corners(contour, NW_BLOCKS)

        # Get the block's center
        center = __get_center(corners)

        features.append(BlockFeature(corners, center, cv2.contourArea(contour)))


        __draw_contour(img, contour)
        __draw_corners(img, corners)
        __draw_center(img, center)
        __draw_contour_info(img, contour, corners)


    show_img_and_check_close('Blocks', img)
    show_img_and_check_close('Blocks: Color Mask', img_mask)

    return features


def __process_block_features(features: List[BlockFeature], img) -> List[Block]:
    blocks: List[Block] = []

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
                
    angle = vector_angle(ref_vertex - feature.center, (-1, -2)) % 180

    cv2.line(img, feature.center, ref_vertex[0], (255, 0, 0), 3)
    L.debug('PARALLELOGRAM: center=%s angle=%f°' % (feature.center, angle))

    return Block(SHAPES['PA'], feature.center, angle)


def __process_square(feature: BlockFeature, img) -> Block:
    upper_vertex = None
    for v in feature.vertices:
        if upper_vertex is None:
            upper_vertex = v
        elif v[0][1] < upper_vertex[0][1]:
            upper_vertex = v

    ref_vertex = upper_vertex
    
    angle = vector_angle(ref_vertex - feature.center, (-1, -1)) % 90
    
    cv2.line(img, feature.center, ref_vertex[0], (255, 0, 0), 3)
    L.debug('SQUARE: center=%s angle=%f°' % (feature.center, angle))

    return Block(SHAPES['SQ'], feature.center, angle)


def __process_small_triangle(feature: BlockFeature, img) -> Block:
    interior_angles = feature.get_interior_angles()
    ref_vertex = feature.vertices[interior_angles.index(90)]
                
    angle = vector_angle(ref_vertex - feature.center, (-1, -1))

    # Fix rotation > 180°
    cross = np.cross((ref_vertex-feature.center), (-1, -1))
    if cross > 0:
        angle = 360 - angle
    
    cv2.line(img, feature.center, ref_vertex[0], (255, 0, 0), 3)
    L.debug('SMALL TRIANGLE: center=%s angle=%f°' % (feature.center, angle))

    return Block(SHAPES['ST'], feature.center, angle)


def __process_medium_triangle(feature: BlockFeature, img) -> Block:
    interior_angles = feature.get_interior_angles()
    ref_vertex = feature.vertices[interior_angles.index(90)]
    
    angle = vector_angle(ref_vertex - feature.center, (0, 1))

    # Fix rotation > 180°
    cross = np.cross((ref_vertex-feature.center), (0, 1))
    if cross > 0: # TODO: check if needs to be < 0
        angle = 360 - angle
    
    cv2.line(img, feature.center, ref_vertex[0], (255, 0, 0), 3)
    L.debug('MEDIUM TRIANGLE: center=%s angle=%f°' % (feature.center, angle))
    
    return Block(SHAPES['MT'], feature.center, angle)


def __process_large_triangle(feature: BlockFeature, img) -> Block:
    interior_angles = feature.get_interior_angles()
    ref_vertex = feature.vertices[interior_angles.index(90)]
                
    angle = vector_angle(ref_vertex - feature.center, (-1, -1))
    
    # Fix rotation > 180°
    cross = np.cross((ref_vertex-feature.center), (-1, -1))
    if cross > 0:
        angle = 360 - angle

    cv2.line(img, feature.center, ref_vertex[0], (255, 0, 0), 3)
    L.debug('LARGE TRIANGLE: center=%s angle=%f°' % (feature.center, angle))
    
    return Block(SHAPES['LT'], feature.center, angle)
















def find_shadow(img) -> Shadow:
    shapes = __find_shadow_shapes(img)

    return None


def __find_shadow_shapes(img):
    # Blur image to reduce noise
    img_blur = __blur(img, NW_SHADOW)
    
    # Apply edge detection
    img_edge = __find_edges(img_blur, NW_SHADOW)

    for contour in __find_contours(img_edge):

        # Skip if contour is too small
        if __contour_too_small(contour, NW_SHADOW):
            continue

        __draw_contour(img, contour)

        # Find corners of the contour
        corners = __find_corners(contour, NW_SHADOW)

        __draw_corners(img, corners)
        

        #======================================#
        # label contour with number of corners #
        #======================================#

        num_corners = len(corners)
        x, y, _, _ = cv2.boundingRect(corners)
        cv2.putText(img, str(num_corners) + ' ' + str(round(cv2.contourArea(contour), 2)), (x, y-5), cv2.FONT_HERSHEY_COMPLEX, 0.4, (0, 0, 0), 1)

    show_img_and_check_close('Shadow', img)




#=====================#
# CV HELPER FUNCTIONS #
#=====================#

def __blur(img, window_name):
    kernel_size = cv2.getTrackbarPos('Blur Kernel', window_name) * 2 + 1
    
    blur_kernel = (kernel_size, kernel_size)

    img_blurred = cv2.GaussianBlur(img, blur_kernel, 1)

    return img_blurred


def __color_mask(img, window_name):
    lower_h = cv2.getTrackbarPos('Mask Lower H', window_name)
    lower_s = cv2.getTrackbarPos('Mask Lower S', window_name)
    lower_v = cv2.getTrackbarPos('Mask Lower V', window_name)
    upper_h = cv2.getTrackbarPos('Mask Upper H', window_name)
    upper_s = cv2.getTrackbarPos('Mask Upper S', window_name)
    upper_v = cv2.getTrackbarPos('Mask Upper V', window_name)

    lower = (lower_h, lower_s, lower_v)
    upper = (upper_h, upper_s, upper_v)

    img_masked = cv2.inRange(img, lower, upper)

    return img_masked


def __find_edges(img, window_name):
    threshold_1 = cv2.getTrackbarPos('Canny 1', window_name)
    threshold_2 = cv2.getTrackbarPos('Canny 2', window_name)

    img_canny = cv2.Canny(img, threshold_1, threshold_2)
    
    kernel_size = cv2.getTrackbarPos('Dilate Kernel', window_name)

    kernel = np.ones((kernel_size, kernel_size))
    img_edges = cv2.dilate(img_canny, kernel, iterations=1)

    return img_edges


def __find_contours(img):
    contours, _ = cv2.findContours(img, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)

    return contours


def __contour_too_small(contour, window_name):
    area = cv2.contourArea(contour)

    min_contour_area = cv2.getTrackbarPos('Min Contour Area', window_name)

    return area < min_contour_area


def __find_corners(contour, window_name):
    accuracy = cv2.getTrackbarPos('Corner Accuracy', window_name)

    perimeter = cv2.arcLength(contour, True)

    corners = cv2.approxPolyDP(contour, perimeter * 0.01 * accuracy, True)

    return corners


def __get_center(corners):
    x_sum = 0
    y_sum = 0
    
    for corner in corners:
        x_sum += corner[0][0]
        y_sum += corner[0][1]

    num_corners = len(corners)

    x_sum //= num_corners
    y_sum //= num_corners

    return (x_sum, y_sum)



#=======================#
# DRAW HELPER FUNCTIONS #
#=======================#

def __draw_contour(img, contour):
    cv2.drawContours(img, contour, -1, (0, 0, 0), 2)
    cv2.drawContours(img, contour, -1, (0, 0, 255), 1)


def __draw_corners(img, corners):
    for corner in corners:
        cv2.circle(img, corner[0], 2, (0, 0, 0), -1)
        cv2.circle(img, corner[0], 1, (0, 255, 0), -1)


def __draw_center(img, center):
    cv2.circle(img, center, 2, (0, 0, 0), -1)
    cv2.circle(img, center, 1, (255, 0, 0), -1)


def __draw_contour_info(img, contour, corners):
    num_corners = len(corners)

    x, y, _, _ = cv2.boundingRect(corners)

    cv2.putText(img, str(num_corners) + ' ' + str(round(cv2.contourArea(contour), 2)), (x, y-10), cv2.FONT_HERSHEY_COMPLEX, 0.6, (0, 0, 0), 1)
