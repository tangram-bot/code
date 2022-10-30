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



# Checks if edges contains the edge between a and b 
def edge_exists(edges: list, a, b) -> bool:
    for edge in edges:
        eps = 10
        
        # vorwärts
        if distance(edge[0], a) < eps and distance(edge[1], b) < eps:
            return True

        # rückwärts
        if distance(edge[0], b) < eps and distance(edge[1], a) < eps:
            return True

    return False


# Calculates and returns the distance between the points a and b
def distance(a, b) -> float:
    return np.linalg.norm((a-b), 2)




# edges:            A list of all available edges
# start_vertex:     Vertex where the current path started
# current_vertex:   Current vertex from which the next edge is searched
# split_vertices:   A list of all points where the shadow can be split
def tri_wok(edges: list, start_vertex: str, current_vertex: str, split_vertices: list[str]) -> list | None:

    # sind wir wieder am start_vertex?
    # Falls ja: Pfad ist vollständig -> wir müssen nicht weiter suchen
    if current_vertex == start_vertex:
        return []

    # sind wir an einem Split Vertex, der nicht start_vertex ist?
    # falls ja: Abbruch
    for sv in split_vertices:
        v_str = str(sv)
        if v_str == current_vertex and v_str != start_vertex:
            return None

    # weiter den Kanten folgen
    for e_idx in range(len(edges)):
        edge = edges[e_idx]

        # Beide Endpunkte der Kante betrachten
        for i in range(2):
            v_str = str(edge[i])

            # Wenn v_str == current_vertex, dann grenzt edge an den aktuellen Vertex
            # => die Kante kommt für den Pfad in Frage
            if v_str == current_vertex:

                # Aktuelle Kante aus edges entfernen, damit sie bei
                # rekursiven Aufrufen nicht erneut benutzt wird
                ee = edges.copy()
                ee.pop(e_idx)

                # Rekursiver Aufruf, um den Pfad weiter aufzubauen
                sub_shadow = tri_wok(ee, start_vertex, str(edge[1-i]), split_vertices)

                # None wird nur zurückgegeben, wenn der Pfad ungültig ist
                # es kann also einfach weitergegeben werden
                if sub_shadow is None:
                    return None
                
                # Aktuelle Kante zum Shadow hinzufügen, wenn der Pfad gültig ist
                sub_shadow.append(edge)

                return sub_shadow

    return None




def magic() -> None:
    # TODO: ggf. Blur

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

                if distance(a, b) < 10:
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


        # Kanten aus Eckpunkten generieren
        edges = []
        for i in range(len(corners)):
            a = corners[i]
            b = corners[i-1]

            # TODO: ist das Kunst oder kann das weg?
            # ähnliche Punkte wurden oben zusammengefasst, diese Überprüfung müsste überflüssig sein
            if distance(a, b) < 10:
                continue

            # Falls es noch keine Kante zwischen a und b gibt, füge sie zu edges hinzu
            if len(edges) == 0 or not edge_exists(edges, a, b):
                edges.append([a, b])




        # Prüfen, ob die Figur in kleiner Figuren zerlegt werden kann
        x: dict[str, int] = {}
        # Zählen, wieviele Kante an jedem Eckpunkt anliegen
        for edge in edges:
            for i in range(2):
                a = edge[i]
                val = x.setdefault(str(a), 0)
                x[str(a)] = val + 1
        
        # Die Figur kann nur an Punkten zerlegt werden, an denen mindestens
        # vier Kanten anliegen
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



    # Kanten im (oder gegen den) Uhrzeigersinn sortierern
    shadows_e = []
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

        # Die Namen der Variablen sind ein bisschen blöd gewählt
        # Wir können uns hier noch nicht sicher sein, welche Winkel
        # innen und welche außen liegen. Das ist erst weiter unten
        # mit ideal_int_angle_count möglich.
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


        # Alle Winkel müssen Vielfache von 45° sein
        # Hier werden Messungenauigkeiten entfernt
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
            
        # Innenwinkelsumme jedes Polygons kann mithilfe dieser Formel berechnet werden
        ideal_int_angle_count = ( len(shadow) - 2 ) * 180

        # Mit ideal_int_angle_count können wir hier schauen,
        # was innen und was außen ist
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
