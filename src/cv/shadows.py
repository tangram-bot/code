import logging
import math
import numpy as np
import cv.trackbar as tb
from pyniryo import cv2, show_img_and_check_close
from model import ShadowPoint, Point, Edge, ShadowEdge, Shadow, edges_equal_direction_sensitive
from random import random


L = logging.getLogger('CV-Shadows')


def find_shadows(img) -> list[Shadow]:
    features = __find_shadow_features(img)
    
    L.debug('Found Features:')
    L.debug(features)

    shadows = __process_shadow_features(features, img)

    show_img_and_check_close('Shadows', img)

    return shadows


def __find_shadow_features(img) -> list[ShadowPoint]:
    img_gray = cv2.cvtColor(img.copy(), cv2.COLOR_BGR2GRAY)
    
    threshold1 = cv2.getTrackbarPos(tb.TB_CANNY_1, tb.NW_SHADOW)
    threshold2 = cv2.getTrackbarPos(tb.TB_CANNY_2, tb.NW_SHADOW)
    img_canny = cv2.Canny(img_gray, threshold1, threshold2)

    kernel_size = 2
    kernel = np.ones((kernel_size, kernel_size))
    img_edges = cv2.dilate(img_canny, kernel, iterations=1)

    contours, _ = cv2.findContours(img_edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)

    shadows = contours_to_shadows(contours)

    return shadows

def __get_area(points: list[Point]) -> float:
    accumulator = 0
    for i in range(len(points)):
        accumulator += points[i].x * (points[(i+1) % len(points)].y - points[i-1].y)

    area = abs(0.5 * accumulator)
    area_scaled = (area / 14290)
    area_rounded = round(area_scaled * 2) / 2

    return area_rounded


def __process_shadow_features(features: list[ShadowPoint], img) -> list[Shadow]:
    shadows: list[Shadow] = []

    for shadow in features:
        angles_1, angles_2 = calculate_angles(shadow)

        fix_angles(angles_1)
        fix_angles(angles_2)

        remove_straight_angles(shadow, angles_1, angles_2)


        # Ecken markieren
        points = []
        for c in shadow.points:
            center = [int(c.x), int(c.y)]
            points.append(center)
        hsv = np.uint8([[[ int(random() * 255), 255, 255 ]]])  
        bgr = cv2.cvtColor(hsv, cv2.COLOR_HSV2BGR).flatten()
        bgr = (int(bgr[0]), int(bgr[1]), int(bgr[2]))
        cv2.polylines(img, np.array([points]), True, bgr, 3)
        for c in points:
            cv2.circle(img, c, 5, (0, 0, 0), -1)
            cv2.circle(img, c, 3, (255, 255, 255), -1)


        # Innenwinkelsumme jedes Polygons kann mithilfe dieser Formel berechnet werden
        ideal_int_angle_sum = ( len(shadow.points) - 2 ) * 180

        interior_angles = angles_1 if (ideal_int_angle_sum == sum(angles_1)) else angles_2

        area = __get_area(shadow.points)

        L.debug('Anzahl Ecken=%d; Winkelsumme=%d°; Winkel=%s; Fläche=%f' % (len(shadow.points), ideal_int_angle_sum, interior_angles, area))

        shadows.append(Shadow(shadow.points, interior_angles, area))

    return shadows







#==================================#
# HELPER FUNCTIONS - FIND FEATURES #
#==================================#


def contours_to_shadows(contours: list) -> list[ShadowPoint]:
    shadows = []

    for c in contours:

        if cv2.contourArea(c) < cv2.getTrackbarPos(tb.TB_CONT_AR, tb.NW_SHADOW):
            continue

        accuracy = cv2.getTrackbarPos(tb.TB_CORN_ACC, tb.NW_SHADOW)
        perimeter = cv2.arcLength(c, True)
        corners = cv2.approxPolyDP(c, perimeter * 0.0001 * accuracy, False)
        points = corners_to_points(corners)

        # Punkte mit ähnlichen Koordinaten zusammenfassen
        summarize_similar_points(points)

        # Kanten aus Eckpunkten generieren
        edges = generate_edges(points)
        
        # Punkte finden, an denen die Figur zerlegt werden kann
        split_vertices = find_split_points(edges)

        if len(split_vertices) > 0:
            print('Shadow kann', len(split_vertices), 'Mal zerlegt werden')
        else:
            print('Shadow kann nicht zerlegt werden')

        sub_shadows = split_shadow(edges, split_vertices)
 
        for sub_shadow in sub_shadows:
            shadows.append(sub_shadow)

    shadows = sort_shadow_edges(shadows)

    return shadows



def corners_to_points(corners: list) -> list[Point]:
    points: list[Point] = []

    for c in corners:
        points.append(Point(c[0][0], c[0][1]))

    return points



def summarize_similar_points(points: list[Point]) -> None:
    for i in range(len(points)):

        # for every point calculate sum of x and y values for other points near the point i

        a = points[i]
        
        indexs = [i]
        x_sum = a.x
        y_sum = a.y

        for j in range(len(points)):
            if i == j: 
                continue

            b = points[j]

            if distance(a, b) < 10:
                indexs.append(j)
                x_sum += b.x
                y_sum += b.y

        # calculate averave of selected points
        x_sum /= len(indexs)
        y_sum /= len(indexs)

        # set new averaged position for point
        for idx in indexs:
            points[idx] = Point(x_sum, y_sum)



# Calculates and returns the distance between the points a and b
def distance(a: Point, b: Point) -> float:
    return np.linalg.norm((a.to_cv_array() - b.to_cv_array()), 2)



def generate_edges(corners: list[Point]) -> list[Edge]:
    edges: list[Edge] = []

    for i in range(len(corners)):
        a = corners[i]
        b = corners[i-1]

        if a == b:
            continue

        # Falls es noch keine Kante zwischen a und b gibt, füge sie zu edges hinzu
        if len(edges) == 0 or not edge_exists(edges, a, b):
            edges.append(Edge(a, b))

    return edges



# Checks if edges contains the edge between a and b 
def edge_exists(edges: list[Edge], a: Point, b: Point) -> bool:
    new_edge = Edge(a, b)
    for edge in edges:
        if edge == new_edge:
            return True

    return False



def find_split_points(edges: list[Edge]) -> list[Point]:
    # Prüfen, ob die Figur in kleiner Figuren zerlegt werden kann
    x: dict[Point, int] = {}
    # Zählen, wieviele Kante an jedem Eckpunkt anliegen
    for edge in edges:
        for i in range(2):
            a = edge.get(i)
            val = x.setdefault(a, 0)
            x[a] = val + 1
    
    # Die Figur kann nur an Punkten zerlegt werden, an denen mindestens
    # vier Kanten anliegen
    split_vertices: list[Point] = []
    for k, v in x.items():
        if v >= 4:
            split_vertices.append(k)

    return split_vertices















#=====================================#
# HELPER FUNCTIONS - PROCESS FEATURES #
#=====================================#


def calculate_angles(shadow: ShadowPoint) -> tuple[list[float], list[float]]:
    angles_1: list[float] = []
    angles_2: list[float] = []

    for i in range(len(shadow.points)):

        v = shadow.points[i].to_cv_array()
        a = shadow.points[(i+1)%len(shadow.points)].to_cv_array()
        b = shadow.points[(i-1)%len(shadow.points)].to_cv_array()

        a = a - v
        b = b - v

        dot_prod = np.dot(a, b)
        len_prod = np.linalg.norm(a, 2) * np.linalg.norm(b, 2)

        angle = math.acos(dot_prod / len_prod)
        angle = math.degrees(angle)

        # acos() gibt nur Werte <=180° zurück
        # hier korrigieren wir größere Innenwinkel
        cross_prod = np.cross(a, b)
        if cross_prod < 0:
            angle = 360 - angle

        angles_1.append(angle)
        angles_2.append(360 - angle)

    return angles_1, angles_2



# Alle Winkel müssen Vielfache von 45° sein
# Hier werden Messungenauigkeiten entfernt
def fix_angles(angles: list[float]) -> None:
    for i in range(len(angles)):
        for j in range(8):
            perfect_angle = (j+1)*45
            if abs( perfect_angle - angles[i] ) <= 22.5:
                angles[i] = perfect_angle
                break



# Ecken mit 180°-Winkeln entfernen
def remove_straight_angles(shadow: ShadowPoint, angles_1: list[float], angles_2: list[float]) -> None:
    to_remove: list[int] = []
    
    for i in range(len(angles_1)):
        if angles_1[i] == 180:
            to_remove.append(i)
    
    # Invert list
    # Otherwise the indexes would shift while removing elements
    to_remove = to_remove[::-1]

    for i in to_remove:
        shadow.points.pop(i)
        angles_1.pop(i)
        angles_2.pop(i)



def split_shadow(edges: list[Edge], split_vertices: list[Point]) -> list[ShadowEdge]:
    shadows: list[ShadowEdge] = []

    # Form zerlegen, falls möglich
    for start_vertex in split_vertices:
        for e_idx, edge in enumerate(edges):
            found_sub_shadow = False

            for i in range(2):
                if edge.get(i) == start_vertex:
                    ee = edges.copy()
                    ee.pop(e_idx)

                    sub_shadow = tri_wok(ee, start_vertex, edge.get(1-i), split_vertices)

                    if sub_shadow is None:
                        continue

                    sub_shadow.append(edge)


                    # remove sub_shadow from edges
                    for ss_edge in sub_shadow:
                        for ee_idx, eedge in enumerate(edges):
                            if edges_equal_direction_sensitive(eedge, ss_edge):
                                edges.pop(ee_idx)
                                break

                    shadows.append(ShadowEdge(sub_shadow))

                    found_sub_shadow = True

                    break

            if found_sub_shadow:
                break

    shadows.append(ShadowEdge(edges))

    return shadows



# edges:            A list of all available edges
# start_vertex:     Vertex where the current path started
# current_vertex:   Current vertex from which the next edge is searched
# split_vertices:   A list of all points where the shadow can be split
def tri_wok(edges: list[Edge], start_vertex: Point, current_vertex: Point, split_vertices: list[Point]) -> list[Edge] | None:

    # sind wir wieder am start_vertex?
    # Falls ja: Pfad ist vollständig -> wir müssen nicht weiter suchen
    if current_vertex == start_vertex:
        return []

    # sind wir an einem Split Vertex, der nicht start_vertex ist?
    # falls ja: Abbruch
    for sv in split_vertices:
        if sv == current_vertex and sv != start_vertex:
            return None

    # weiter den Kanten folgen
    for e_idx, edge in enumerate(edges):

        # Beide Endpunkte der Kante betrachten
        for i in range(2):

            # Wenn v_str == current_vertex, dann grenzt edge an den aktuellen Vertex
            # => die Kante kommt für den Pfad in Frage
            if edge.get(i) == current_vertex:

                # Aktuelle Kante aus edges entfernen, damit sie bei
                # rekursiven Aufrufen nicht erneut benutzt wird
                ee = edges.copy()
                ee.pop(e_idx)

                # Rekursiver Aufruf, um den Pfad weiter aufzubauen
                sub_shadow = tri_wok(ee, start_vertex, edge.get(1-i), split_vertices)

                # None wird nur zurückgegeben, wenn der Pfad ungültig ist
                # es kann also einfach weitergegeben werden
                if sub_shadow is None:
                    return None
                
                # Aktuelle Kante zum Shadow hinzufügen, wenn der Pfad gültig ist
                sub_shadow.append(edge)

                return sub_shadow

    return None



# Kanten im (oder gegen den) Uhrzeigersinn sortierern
def sort_shadow_edges(shadows: list[ShadowEdge]) -> list[ShadowPoint]:
    sorted_shadows: list[ShadowPoint] = []

    for shadow in shadows:
        sorted_points = [shadow.edges[0].p2]
        while len(shadow.edges) > 0:
            for edge_idx in range(len(shadow.edges)):
                edge = shadow.edges[edge_idx]
                found = False

                for i in range(2):
                    if edge.get(i) == sorted_points[len(sorted_points)-1]:
                        sorted_points.append(edge.get(1-i))
                        shadow.edges.pop(edge_idx)
                        found = True
                        break

                if found:
                    break

        # Start- und Endpunkt sind gleich -> einer kann weg
        sorted_points.pop(0)

        sorted_shadows.append(ShadowPoint(sorted_points))

    return sorted_shadows
