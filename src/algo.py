import math
from tangram import BLOCKS, Block, Shadow
import numpy as np

#============#
# FUNKTIONEN #
#============#

def block_area(block: Block):
    return block.area


#===========#
# VARIABLEN #
#===========#

shadow = Shadow((
    (0, 100), (100, 0), (200, 100), (100, 200)
))

blocks = BLOCKS.copy()


#=============#
# ALGORITHMUS #
#=============#

# Abbruch, wenn shadow größer als alle Blöcke zusammen
area_sum = 0
for b in blocks:
    area_sum += b.area
if area_sum < shadow.area:
    print('Shadow ist zu groß')
    exit()

# Blöcke absteigend nach Größe sortieren
blocks.sort(key=block_area, reverse=True)

# Blöcke entfernen, die größer sind als shadow
tmp = []
for b in blocks:
    if b.area <= shadow.area:
        tmp.append(b)
blocks = tmp




def alg(shadow: Shadow, blocks: list[Block]):
    b = blocks[0]

    print('\nalg()', b.name)

    for s_vertex in range(len(shadow.vertices)):
        s_angle = shadow.interior_angles[s_vertex]

        for b_vertex in range(len(b.vertices)):
            b_angle = b.interior_angles[b_vertex]

            if b_angle > s_angle:
                continue

            angle_diff = s_angle - b_angle

            if angle_diff == 0:
                vec_a = shadow.get_vertex(s_vertex)
                vec_b = shadow.get_vertex(s_vertex - 1)

                vec = np.subtract(vec_b, vec_a)

                b.place(b_vertex, shadow.vertices[s_vertex], vec)

                # 



            # - Block an Schenkel A anlegen
            # - überspringen, wenn Schnittmenge von Block und Shadow < 99%
            # - Block von Shadow abziehen und aus blcks entfernen
            # - alg(shdw2, blcks)
            # Falls kein Ergebnis: Block an Schenkel B anlegen und wiederholen

        

solution = alg(shadow, blocks)