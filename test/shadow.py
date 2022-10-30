from math import floor, sqrt
import math
from pyniryo import cv2 as cv, show_img_and_check_close
import numpy as np


cv.namedWindow('Sliders')
cv.createTrackbar('T1', 'Sliders', 280, 1000, lambda x: x)
cv.createTrackbar('T2', 'Sliders', 800, 1000, lambda x: x)
cv.createTrackbar('Area', 'Sliders', 50, 500, lambda x: x)
cv.createTrackbar('Corner Acc', 'Sliders', 20, 100, lambda x: x)


img = cv.imread('img/shadow/ronald.png')




def gibt_es_die_kante_schon(edges, a, b) -> bool:
    for edge in edges:
        eps = 10
        
        # vorwärts
        if entfernung(edge[0], a) < eps and entfernung(edge[1], b) < eps:
            return True

        # rückwärts
        if entfernung(edge[0], b) < eps and entfernung(edge[1], a) < eps:
            return True

    return False


def entfernung(a, b) -> float:
    return np.linalg.norm((a-b), 2)




def tri_wok(edges:list, start_vertex:str, current_vertex:str, split_vertices:list[str]) -> list | None:
    # sind wir wieder am start_vertex?
    if current_vertex == start_vertex:
        return []

    # sind wir an einem split vertex, der nicht start_vertex ist?
    for sv in split_vertices:
        v_str = str(sv)
        if v_str == current_vertex and v_str != start_vertex:
            return None

    # weiter den Kanten folgen
    for e_idx in range(len(edges)):
        edge = edges[e_idx]
        for i in range(2):
            v_str = str(edge[i])
            if v_str == current_vertex:
                ee = edges.copy()
                ee.pop(e_idx)

                sub_shadow = tri_wok(ee, start_vertex, str(edge[1-i]), split_vertices)

                if sub_shadow is None:
                    return None
                
                sub_shadow.append(edge)
                return sub_shadow

    return None




def magic():
    img2 = cv.cvtColor(img.copy(), cv.COLOR_BGR2GRAY)
    img_canny = cv.Canny(img2, cv.getTrackbarPos('T1', 'Sliders'), cv.getTrackbarPos('T2', 'Sliders'))

    kernel_size = 1
    kernel = np.ones((kernel_size, kernel_size))
    img_edges = cv.dilate(img_canny, kernel, iterations=1)


    img3 = img.copy()





    contours, _ = cv.findContours(img_edges, cv.RETR_EXTERNAL, cv.CHAIN_APPROX_NONE)

    shadows = []

    for c in contours:

        if cv.contourArea(c) < cv.getTrackbarPos('Area', 'Sliders'):
            continue
        
        
        cv.drawContours(img3, c, -1, (255, 0, 255), 2)


        accuracy = cv.getTrackbarPos('Corner Acc', 'Sliders')
        perimeter = cv.arcLength(c, True)
        corners = cv.approxPolyDP(c, perimeter * 0.0001 * accuracy, False)


        # Punkte mit ähnlichen Koordinaten zusammenfassen
        for i in range(len(corners)):
            a = corners[i]
            
            indexs = [i]
            x_sum = a[0][0]
            y_sum = a[0][1]

            for j in range(len(corners)):
                if i == j: 
                    continue

                b = corners[j]

                if entfernung(a, b) < 10:
                    indexs.append(j)
                    x_sum += b[0][0]
                    y_sum += b[0][1]

            x_sum /= len(indexs)
            y_sum /= len(indexs)

            for idx in indexs:
                corners[idx] = [x_sum, y_sum]



        # Ecken markieren
        for c in corners:
            cv.circle(img3, c[0], 5, (0, 0, 0), -1)
            cv.circle(img3, c[0], 4, (0, 255, 0), -1)


        # Kanten generieren
        edges = []
        for i in range(len(corners)):
            a = corners[i]
            b = corners[i-1]

            if entfernung(a, b) < 10:
                continue

            if len(edges) == 0 or not gibt_es_die_kante_schon(edges, a, b):
                edges.append([a, b])


        # Prüfen, ob die Figur in kleiner Figuren zerlegt werden kann
        x: dict[str, int] = {}
        for edge in edges:
            for i in range(2):
                a = edge[i]
                val = x.setdefault(str(a), 0)
                x[str(a)] = val + 1
        
        split_vertices: list[str] = []

        for k, v in x.items():
            if v >= 4:
                split_vertices.append(k)

        if len(split_vertices) > 0:
            print('Shadow kann', len(split_vertices), 'Mal zerlegt werden')
        else:
            print('Shadow kann nicht zerlegt werden')

        # Form zerlegen, falls möglich
        for start_vertex in split_vertices:
            for e_idx in range(len(edges)):
                found_sub_shadow = False

                edge = edges[e_idx]
                for i in range(2):
                    e_str = str(edge[i])
                    if e_str == start_vertex:
                        ee = edges.copy()
                        ee.pop(e_idx)

                        sub_shadow = tri_wok(ee, start_vertex, str(edge[1-i]), split_vertices)

                        if sub_shadow is None:
                            continue

                        sub_shadow.append(edge)


                        # remove sub_shadow from edges
                        for ss_edge in sub_shadow:
                            for ee_idx in range(len(edges)):
                                eedge = edges[ee_idx]
                                if str(ss_edge) == str(eedge):
                                    edges.pop(ee_idx)
                                    break

                        # TODO: close hole in edges

                        shadows.append(sub_shadow)

                        found_sub_shadow = True

                        break

                if found_sub_shadow:
                    break

        shadows.append(edges)


    shadows_e = []

    # Kanten im (oder gegen den) Uhrzeigersinn sortierern

    for shadow in shadows:
        shadow_e = [shadow[0][0][0]]

        while len(shadow) > 0:
            for edge_idx in range(len(shadow)):
                edge = shadow[edge_idx]
                found = False
                for i in range(2):
                    if edge[i][0][0] == shadow_e[len(shadow_e)-1][0] and edge[i][0][1] == shadow_e[len(shadow_e)-1][1]:
                        shadow_e.append(edge[1-i][0])
                        shadow.pop(edge_idx)
                        found = True
                        break
                if found:
                    break

        # Start- und Endpunkt sind gleich -> einer kann weg
        shadow_e.pop(0)

        shadows_e.append(shadow_e)


    # Innenwinkel
    for shadow in shadows_e:
        print('\n\nDas ist mein Shadow. Er hat', len(shadow), 'Ecken:')

        int_angles: list[float] = []
        out_angles: list[float] = []

        for i in range(len(shadow)):

            v = shadow[i]
            a = shadow[(i+1)%len(shadow)]
            b = shadow[(i-1)%len(shadow)]

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

            int_angles.append(angle)
            out_angles.append(360 - angle)


        # Winkel auf 45° runden
        # (Alle Winkel müssen Vielfache von 45° sein)
        for i in range(len(int_angles)):
            for j in range(8):
                perfect_angle = (j+1)*45
                if abs( perfect_angle - int_angles[i] ) <= 22.5:
                    int_angles[i] = perfect_angle
                    break

        for i in range(len(out_angles)):
            for j in range(8):
                perfect_angle = (j+1)*45
                if abs( perfect_angle - out_angles[i] ) <= 22.5:
                    out_angles[i] = perfect_angle
                    break
            

        ideal_int_angle_count = ( len(shadow) - 2 ) * 180

        if ideal_int_angle_count == sum(int_angles):
            print('Winkelsumme: ' + str(sum(int_angles)) + '°')
            print(int_angles)
        else:
            print('Winkelsumme: ' + str(sum(out_angles)) + '°')
            print(out_angles)

        # TODO: Ecken mit 180°-Winkel entfernen


                

    show_img_and_check_close('Img', img3)
    # show_img_and_check_close('Canny', img_canny)
    # show_img_and_check_close('Ronald', img_edges)

while True:
    magic()
    break


while True:
    cv.waitKey(1)
