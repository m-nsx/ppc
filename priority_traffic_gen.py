# Importe le module common pour avoir accès aux constantes globales
import common
# Importe le module pickle pour la sérialisation des objets
import pickle as p
# Importe le module os pour envoyer des signaux
import os

import math as m
import signal as sg
import time as t
import random as r

size = common.CANVAS_SIZE

# GÉNÉRATION DE TRAFIC À VÉHICULES PRIORITAIRES CONDITIONS NORMALES
# Tente de générer à intervalles régulier des véhicules ayant une source et une destination aléatoire
# Chaque véhicule possède un identifiant unique généré lui aussi à l'invocation de l'objet
# Une fois généré le véhicule est communiqué au processus coordinator via message queue
# Tous les véhicules générés par cette fonction sont prioritaires

def priority_traffic_gen(stop):

    directions = common.DIRECTIONS
    vehicle_id = 0

    try:
        while not stop.is_set():
            if vehicle_id < common.MAX_TOTAL_VEHICLES:
                # Génère un véhicule à intervalle régulier, défini dans common par PRIORITY_SPAWN_INTERVAL
                t.sleep(common.PRIORITY_SPAWN_INTERVAL)
                src = r.choice(directions)
                dst = r.choice(directions)
                # Vérifie et empêche que la source et la destination soient identiques
                while src == dst:
                    dst = r.choice(directions)

                formatted_id = "p" + str(vehicle_id)
                if common.DEBUG:
                    print(f"\033[92m[DEBUG][ptg] Véhicule prioritaire généré avec l'identifiant {formatted_id}\033[0m")

                try:
                    if src == 'N':
                        x,y = m.floor(size/2 - size*0.025), 0
                    elif src == 'E':
                        x,y = 0, m.floor(size/2 + size*0.025)
                    elif src == 'S':
                        x,y = m.floor(size/2 + size*0.025), size
                    elif src == 'W':
                        x,y = size, m.floor(size/2 - size*0.025)
                    if common.DEBUG:
                            print(f"\033[92m[DEBUG][ntg] Les coordonnées ont été générées avec succès\033[0m")
                except:
                    print("\033[91m[ERREUR][ntg] Échec de la génération des coordonnées initiales\033[0m")

                try:
                    turn = common.turn(src, dst)
                    v = common.Vehicle(formatted_id, 1, src, dst, x, y, turn)
                    if common.DEBUG:
                        print(f"\033[92m[DEBUG][ptg] L'objet a été créé avec succès\033[0m")
                except:
                    print("\033[91m[ERREUR][ntg] Échec de la création de l'objet\033[0m")

                try:
                    sv = p.dumps(v)
                    if common.DEBUG:
                        print(f"\033[92m[DEBUG][ptg] L'objet a été sérialisé avec succès\033[0m")
                except:
                    print("\033[91m[ERREUR][ptg] Échec de la sérialisation de l'objet\033[0m")

                if src == 'N':
                    common.north_queue.send(sv)
                    if common.DEBUG:
                        print(f"\033[92m[DEBUG][ptg] Véhicule {formatted_id} envoyé à common.north_queue\033[0m")
                elif src == 'E':
                    common.east_queue.send(sv)
                    if common.DEBUG:
                        print(f"\033[92m[DEBUG][ptg] Véhicule {formatted_id} envoyé à common.east_queue\033[0m")
                elif src == 'S':
                    common.south_queue.send(sv)
                    if common.DEBUG:
                        print(f"\033[92m[DEBUG][ptg] Véhicule {formatted_id} envoyé à common.south_queue\033[0m")
                elif src == 'W':
                    common.west_queue.send(sv)
                    if common.DEBUG:
                        print(f"\033[92m[DEBUG][ptg] Véhicule {formatted_id} envoyé à common.west_queue\033[0m")

                vehicle_id += 1

                ssrc = src.encode()

                # Envoie l'information de souuce au processus lights
                common.priority_queue.send(ssrc)

                # Envoi du signal SIGINT pour indiquer la présence d'un véhicule prioritaire au processus lights
                try:
                    if common.DEBUG:
                        print(f"\033[92m[DEBUG][ptg] Lights PID is {common.LIGHTS_PID}\033[0m")
                    os.kill(common.LIGHTS_PID, sg.SIGINT)
                    if common.DEBUG:
                        print(f"\033[92m[DEBUG][ptg] Signal SIGINT envoyé au processus lights de PID : {common.LIGHTS_PID}\033[0m")
                except ProcessLookupError:
                    print(f"\033[91m[ERREUR][ptg] Processus de PID {common.LIGHTS_PID} non trouvé\033[0m")
                except:
                    print("\033[91m[ERREUR][ptg] Erreur lors de l'envoi du signal SIGINT\033[0m")

    except:
        print("\033[91m[ERREUR][ptg] Erreur lors de la génération de trafic\033[0m")
        stop.set()

    finally:
        print("[ptg] Processus terminé")
        stop.set()