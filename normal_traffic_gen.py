# Importe le module common pour avoir accès aux constantes globales
import common
# Importe le module pickle pour la sérialisation des objets
import pickle as p

import time as t
import random as r
import math as m

size = common.CANVAS_SIZE

# GÉNÉRATION DE TRAFIC CONDITIONS NORMALES
# Tente de générer à intervalles régulier des véhicules ayant une source et une destination aléatoire
# Chaque véhicule possède un identifiant unique généré lui aussi à l'invocation de l'objet
# Une fois généré le véhicule est communiqué au processus coordinator via message queue

def normal_traffic_gen(stop):

    directions = common.DIRECTIONS
    vehicle_id = 0

    try:
        while not stop.is_set():
            if vehicle_id < common.MAX_TOTAL_VEHICLES:
                t.sleep(common.NORMAL_SPAWN_INTERVAL)
                src = r.choice(directions)
                dst = r.choice(directions)
                while src == dst:
                    dst = r.choice(directions)

                formatted_id = "n" + str(vehicle_id)
                if common.DEBUG:
                    print(f"\033[92m[DEBUG][ntg] Véhicule généré avec l'identifiant {formatted_id}\033[0m")

                try:
                    if src == 'N':
                        x, y = m.floor(size/2 - size*0.025), 0
                    elif src == 'E':
                        x, y = 0, m.floor(size/2 + size*0.025)
                    elif src == 'S':
                        x, y = m.floor(size/2 + size*0.025), size
                    elif src == 'W':
                        x, y = size, m.floor(size/2 - size*0.025)
                    if common.DEBUG:
                        print(f"\033[92m[DEBUG][ntg] Les coordonnées ont été générées avec succès\033[0m")
                except Exception as e:
                    print(f"\033[91m[ERREUR][ntg] Échec de la génération des coordonnées initiales: {e}\033[0m")

                try:
                    turn = common.turn(src, dst)
                    v = common.Vehicle(formatted_id, 0, src, dst, x, y, turn)
                    if common.DEBUG:
                        print(f"\033[92m[DEBUG][ntg] L'objet a été créé avec succès\033[0m")
                except Exception as e:
                    print(f"\033[91m[ERREUR][ntg] Échec de la création de l'objet: {e}\033[0m")

                try:
                    sv = p.dumps(v)
                    if common.DEBUG:
                        print(f"\033[92m[DEBUG][ntg] L'objet a été sérialisé avec succès\033[0m")
                except Exception as e:
                    print(f"\033[91m[ERREUR][ntg] Échec de la sérialisation de l'objet: {e}\033[0m")

                try:
                    if src == 'N':
                        common.north_queue.send(sv)
                        if common.DEBUG:
                            print(f"\033[92m[DEBUG][ntg] Véhicule {formatted_id} [{v.src},{v.dst},{v.priority},p={v.src}] envoyé à common.north_queue\033[0m")
                    elif src == 'E':
                        common.east_queue.send(sv)
                        if common.DEBUG:
                            print(f"\033[92m[DEBUG][ntg] Véhicule {formatted_id} [{v.src},{v.dst},{v.priority},p={v.src}] envoyé à common.east_queue\033[0m")
                    elif src == 'S':
                        common.south_queue.send(sv)
                        if common.DEBUG:
                            print(f"\033[92m[DEBUG][ntg] Véhicule {formatted_id} [{v.src},{v.dst},{v.priority},p={v.src}] envoyé à common.south_queue\033[0m")
                    elif src == 'W':
                        common.west_queue.send(sv)
                        if common.DEBUG:
                            print(f"\033[92m[DEBUG][ntg] Véhicule {formatted_id} [{v.src},{v.dst},{v.priority},p={v.src}] envoyé à common.west_queue\033[0m")
                except Exception as e:
                    print(f"\033[91m[ERREUR][ntg] Erreur lors de l'envoi du véhicule dans la file: {e}\033[0m")
                    raise  # On peut relancer l'exception pour stopper la boucle

                vehicle_id += 1

    except Exception as e:
        print(f"\033[91m[ERREUR][ntg] Erreur lors de la génération de trafic: {e}\033[0m")
        stop.set()

    finally:
        print("[ntg] Processus terminé")
        stop.set()
