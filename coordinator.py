# Importe le module common pour avoir accès aux constantes globales
import common
# Importe le module pickle pour la sérialisation des objets
import pickle as p

import os
import signal as sg
import sysv_ipc as ipc
import multiprocessing as mp
import socket as so
import time as t
import math as m

# Création d'une liste pour les véhicules prêts à passer à l'intersection
vehicles = []

# PROCESSUS COORDINATOR
# Le processus coordinator est responsable de la gestion des véhicules
# Il calcule régulièrement les nouvelles coordonnées des véhicules en circulation en fonction de l'état des feux, des autres véhicules alentours et des priorités
# Les priorités sont définies par une table disponible dans common, elles sont appliquées dans l'odre suivant : right → straight → left

def coordinator(stop):
    TEMP_COLOR = 'blue'

    center_size = m.floor(abs(common.N_STOPLINE - (common.CANVAS_SIZE / 2)) * 2)
    reduced_center_size = m.floor(center_size * 0.3)
    reduced_reduced_center_size = m.floor(center_size * 0.2)
    tiny_radius = m.floor(center_size * 0)
    huge_radius = m.floor(center_size * 0.35)

    delay = common.NORMAL_SPEED/40
    tiny_delay = delay/20
    huge_delay = delay/4

    def curve(sock, v):
        x, y, src, dst, id = v.x, v.y, v.src, v.dst, v.id
        if v.priority == 1:
            color = 'red'
        else:
            color = 'blue'
        ax = x
        ay = y

        if src == 'N':
            if dst == 'E': # Right
                for forward in range(reduced_center_size):
                    sv = [ax, ay, 'gray', id, 0]
                    packet = p.dumps(sv)
                    sock.sendall(packet)
                    ay += 1
                    sv = [ax, ay, color, id, 0]
                    packet = p.dumps(sv)
                    sock.sendall(packet)
                    t.sleep(common.COORDINATOR_DELAY)
                v.x, v.y = m.floor(ax), m.floor(ay)
                x, y = v.x, v.y
                for forward in range(reduced_center_size):
                    sv = [ax, ay, 'gray', id, 4]
                    packet = p.dumps(sv)
                    sock.sendall(packet)
                    ax -= 1
                    sv = [ax, ay, color, id, 0]
                    packet = p.dumps(sv)
                    sock.sendall(packet)
                    t.sleep(common.COORDINATOR_DELAY)
                v.x, v.y = m.floor(ax), m.floor(ay)
                x, y = v.x, v.y
            elif dst == 'W': # Left
                for forward in range(reduced_center_size):
                    sv = [ax, ay, 'gray', id, 0]
                    packet = p.dumps(sv)
                    sock.sendall(packet)
                    ay += 1
                    sv = [ax, ay, color, id, 0]
                    packet = p.dumps(sv)
                    sock.sendall(packet)
                    t.sleep(common.COORDINATOR_DELAY)
                v.x, v.y = m.floor(ax), m.floor(ay)
                x, y = v.x, v.y
                for angle in range(90):
                    sv = [ax, ay, 'gray', id, 5]
                    packet = p.dumps(sv)
                    sock.sendall(packet)
                    ax = x + huge_radius * (1 - m.cos(m.radians(angle))) # Déplacement vers la droite
                    ay = y + huge_radius * m.sin(m.radians(angle)) # Déplacement vers le bas
                    sv = [ax, ay, color, id, 0]
                    packet = p.dumps(sv)
                    sock.sendall(packet)
                    t.sleep(huge_delay)
                v.x, v.y = m.floor(ax), m.floor(ay)
                x, y = v.x, v.y
                for forward in range(reduced_center_size):
                    sv = [ax, ay, 'gray', id, 0]
                    packet = p.dumps(sv)
                    sock.sendall(packet)
                    ax += 1
                    sv = [ax, ay, color, id, 0]
                    packet = p.dumps(sv)
                    sock.sendall(packet)
                    t.sleep(common.COORDINATOR_DELAY)
                v.x, v.y = m.floor(ax), m.floor(ay)
                x, y = v.x, v.y
            elif dst == 'S': # Straight
                for i in range(center_size):
                    sv = [ax, ay, 'gray', id, 0]
                    packet = p.dumps(sv)
                    sock.sendall(packet)
                    ay += 1
                    sv = [ax, ay, color, id, 0]
                    packet = p.dumps(sv)
                    sock.sendall(packet)
                    t.sleep(common.COORDINATOR_DELAY)
                v.x, v.y = m.floor(ax), m.floor(ay)
                x, y = v.x, v.y

        elif src == 'E':
            if dst == 'S': # Right
                for forward in range(reduced_center_size):
                    sv = [ax, ay, 'gray', id, 0]
                    packet = p.dumps(sv)
                    sock.sendall(packet)
                    ax += 1
                    sv = [ax, ay, color, id, 0]
                    packet = p.dumps(sv)
                    sock.sendall(packet)
                    t.sleep(common.COORDINATOR_DELAY)
                v.x, v.y = m.floor(ax), m.floor(ay)
                x, y = v.x, v.y
                for forward in range(reduced_center_size):
                    sv = [ax, ay, 'gray', id, 0]
                    packet = p.dumps(sv)
                    sock.sendall(packet)
                    ay += 1
                    sv = [ax, ay, color, id, 0]
                    packet = p.dumps(sv)
                    sock.sendall(packet)
                    t.sleep(common.COORDINATOR_DELAY)
                v.x, v.y = m.floor(ax), m.floor(ay)
                x, y = v.x, v.y
            elif dst == 'N': # Left
                for forward in range(reduced_center_size):
                    sv = [ax, ay, 'gray', id, 0]
                    packet = p.dumps(sv)
                    sock.sendall(packet)
                    ax += 1
                    sv = [ax, ay, color, id, 0]
                    packet = p.dumps(sv)
                    sock.sendall(packet)
                    t.sleep(common.COORDINATOR_DELAY)
                v.x, v.y = m.floor(ax), m.floor(ay)
                x, y = v.x, v.y
                for angle in range(90):
                    sv = [ax, ay, 'gray', id, 5]
                    packet = p.dumps(sv)
                    sock.sendall(packet)
                    ax = x + huge_radius * 1.1 * m.sin(m.radians(angle)) # Déplacement vers la droite
                    ay = y - huge_radius * 1.1 * (1 - m.cos(m.radians(angle))) # Déplacement vers le haut
                    sv = [ax, ay, color, id, 0]
                    packet = p.dumps(sv)
                    sock.sendall(packet)
                    t.sleep(huge_delay)
                v.x, v.y = m.floor(ax), m.floor(ay)
                x, y = v.x, v.y
                for forward in range(reduced_center_size):
                    sv = [ax, ay, 'gray', id, 0]
                    packet = p.dumps(sv)
                    sock.sendall(packet)
                    ay -= 1
                    sv = [ax, ay, color, id, 0]
                    packet = p.dumps(sv)
                    sock.sendall(packet)
                    t.sleep(common.COORDINATOR_DELAY)
                v.x, v.y = m.floor(ax), m.floor(ay)
                x, y = v.x, v.y
            elif dst == 'W': # Straight
                for i in range(center_size):
                    sv = [ax, ay, 'gray', id, 0]
                    packet = p.dumps(sv)
                    sock.sendall(packet)
                    ax += 1
                    sv = [ax, ay, color, id, 0]
                    packet = p.dumps(sv)
                    sock.sendall(packet)
                    t.sleep(common.COORDINATOR_DELAY)
                v.x, v.y = m.floor(ax), m.floor(ay)
                x, y = v.x, v.y
        
        elif src == 'S':
            if dst == 'W': # Right
                for forward in range(reduced_center_size):
                    sv = [ax, ay, 'gray', id, 0]
                    packet = p.dumps(sv)
                    sock.sendall(packet)
                    ay -= 1
                    sv = [ax, ay, color, id, 0]
                    packet = p.dumps(sv)
                    sock.sendall(packet)
                    t.sleep(common.COORDINATOR_DELAY)
                v.x, v.y = m.floor(ax), m.floor(ay)
                x, y = v.x, v.y
                for forward in range(reduced_center_size):
                    sv = [ax, ay, 'gray', id, 0]
                    packet = p.dumps(sv)
                    sock.sendall(packet)
                    ax += 1
                    sv = [ax, ay, color, id, 0]
                    packet = p.dumps(sv)
                    sock.sendall(packet)
                    t.sleep(common.COORDINATOR_DELAY)
                v.x, v.y = m.floor(ax), m.floor(ay)
                x, y = v.x, v.y
            elif dst == 'E': # Left
                for forward in range(reduced_center_size):
                    sv = [ax, ay, 'gray', id, 0]
                    packet = p.dumps(sv)
                    sock.sendall(packet)
                    ay -= 1
                    sv = [ax, ay, color, id, 0]
                    packet = p.dumps(sv)
                    sock.sendall(packet)
                    t.sleep(common.COORDINATOR_DELAY)
                v.x, v.y = m.floor(ax), m.floor(ay)
                x, y = v.x, v.y
                for angle in range(90):
                    sv = [ax, ay, 'gray', id, 5]
                    packet = p.dumps(sv)
                    sock.sendall(packet)
                    ax = x - huge_radius * 1.1 * (1 - m.cos(m.radians(angle))) # Déplacement vers la gauche
                    ay = y - huge_radius * 1.1 * m.sin(m.radians(angle)) # Déplacement vers le haut
                    sv = [ax, ay, color, id, 0]
                    packet = p.dumps(sv)
                    sock.sendall(packet)
                    t.sleep(huge_delay)
                v.x, v.y = m.floor(ax), m.floor(ay)
                x, y = v.x, v.y
                for forward in range(reduced_center_size):
                    sv = [ax, ay, 'gray', id, 0]
                    packet = p.dumps(sv)
                    sock.sendall(packet)
                    ax -= 1
                    sv = [ax, ay, color, id, 0]
                    packet = p.dumps(sv)
                    sock.sendall(packet)
                    t.sleep(common.COORDINATOR_DELAY)
                v.x, v.y = m.floor(ax), m.floor(ay)
                x, y = v.x, v.y
            elif dst == 'W': # Straight
                for i in range(center_size):
                    sv = [ax, ay, 'gray', id, 0]
                    packet = p.dumps(sv)
                    sock.sendall(packet)
                    ay -= 1
                    sv = [ax, ay, color, id, 0]
                    packet = p.dumps(sv)
                    sock.sendall(packet)
                    t.sleep(common.COORDINATOR_DELAY)
                v.x, v.y = m.floor(ax), m.floor(ay)
                x, y = v.x, v.y
        
        elif src == 'W':
            if dst == 'N': # Right
                for forward in range(reduced_center_size):
                    sv = [ax, ay, 'gray', id, 0]
                    packet = p.dumps(sv)
                    sock.sendall(packet)
                    ax -= 1
                    sv = [ax, ay, color, id, 0]
                    packet = p.dumps(sv)
                    sock.sendall(packet)
                    t.sleep(common.COORDINATOR_DELAY)
                v.x, v.y = m.floor(ax), m.floor(ay)
                x, y = v.x, v.y
                for forward in range(reduced_center_size):
                    sv = [ax, ay, 'gray', id, 0]
                    packet = p.dumps(sv)
                    sock.sendall(packet)
                    ay -= 1
                    sv = [ax, ay, color, id, 0]
                    packet = p.dumps(sv)
                    sock.sendall(packet)
                    t.sleep(common.COORDINATOR_DELAY)
                v.x, v.y = m.floor(ax), m.floor(ay)
                x, y = v.x, v.y
            elif dst == 'S': # Left
                for forward in range(reduced_center_size):
                    sv = [ax, ay, 'gray', id, 0]
                    packet = p.dumps(sv)
                    sock.sendall(packet)
                    ax -= 1
                    sv = [ax, ay, color, id, 0]
                    packet = p.dumps(sv)
                    sock.sendall(packet)
                    t.sleep(common.COORDINATOR_DELAY)
                v.x, v.y = m.floor(ax), m.floor(ay)
                x, y = v.x, v.y
                for angle in range(90):
                    sv = [ax, ay, 'gray', id, 5]
                    packet = p.dumps(sv)
                    sock.sendall(packet)
                    ax = x - huge_radius * 1.1 * m.sin(m.radians(angle))  # Déplacement vers la gauche
                    ay = y + huge_radius * 1.1 * (1 - m.cos(m.radians(angle)))  # Déplacement vers le bas
                    sv = [ax, ay, color, id, 0]
                    packet = p.dumps(sv)
                    sock.sendall(packet)
                    t.sleep(huge_delay)
                v.x, v.y = m.floor(ax), m.floor(ay)
                x, y = v.x, v.y
                for forward in range(reduced_center_size):
                    sv = [ax, ay, 'gray', id, 0]
                    packet = p.dumps(sv)
                    sock.sendall(packet)
                    ay += 1
                    sv = [ax, ay, color, id, 0]
                    packet = p.dumps(sv)
                    sock.sendall(packet)
                    t.sleep(common.COORDINATOR_DELAY)
                v.x, v.y = m.floor(ax), m.floor(ay)
                x, y = v.x, v.y
            elif dst == 'W': # Straight
                for i in range(center_size):
                    sv = [ax, ay, 'gray', id, 0]
                    packet = p.dumps(sv)
                    sock.sendall(packet)
                    ax -= 1
                    sv = [ax, ay, color, id, 0]
                    packet = p.dumps(sv)
                    sock.sendall(packet)
                    t.sleep(common.COORDINATOR_DELAY)
                v.x, v.y = m.floor(ax), m.floor(ay)
                x, y = v.x, v.y

    def update_coords(sock, nq, eq, sq, wq):
        # Mise à jour des véhicules dans la file nord (nq)
        for v in nq:
            null_id = 'null'
            if v.priority == 1: color = 'red'
            else: color = 'blue'
            # Liste des positions y des autres véhicules dans la même file
            y = [t.y for t in nq if t != v and t.y > v.y]  # Seuls les véhicules devant sont pris en compte
            if y:  # Si la liste n'est pas vide
                y_min = min(y)  # Trouver la position y minimale des véhicules devant
            else:
                y_min = common.CANVAS_SIZE  # Si aucun autre véhicule devant, utiliser la taille du canvas
            # Calcul de la limite de sécurité
            limit = y_min - common.VEHICLE_SIZE - common.VEHICULE_SPACING
            # Vérifier si le véhicule peut avancer
            if v.status == 0 and v.y < limit and v.y < common.N_STOPLINE:
                # Envoyer la position actuelle en gris (avant le déplacement)
                sv = [v.x, v.y, 'gray', v.id, 0]
                packet = p.dumps(sv)
                sock.sendall(packet)
                # Mettre à jour la position du véhicule
                v.y += common.NORMAL_SPEED
                # Envoyer la nouvelle position en bleu (après le déplacement)
                sv = [v.x, v.y, color, v.id, 0]
                packet = p.dumps(sv)
                sock.sendall(packet)
            elif v.status == 0 and v.y >= common.N_STOPLINE and v.y <= common.N_STOPLINE + common.STOPLINE_THRESHOLD and common.north_light.value == 1:
                if v.dst == 'S':
                    v.status = 2
                elif v.dst == 'E':
                    v.status = 3
                elif v.dst == 'W':
                    v.status = 4
                v.ax, v.ay = v.x, v.y
            elif v.status == 2: # Straight
                if v.y < common.N_STOPLINE + center_size:
                    sv = [v.ax, v.ay, 'gray', v.id, 0]
                    packet = p.dumps(sv)
                    sock.sendall(packet)
                    v.ay += 1
                    sv = [v.ax, v.ay, color, v.id, 0]
                    packet = p.dumps(sv)
                    sock.sendall(packet)
                v.x, v.y = m.floor(v.ax), m.floor(v.ay)
                x, y = v.x, v.y
                if v.y >= common.N_STOPLINE + center_size:
                    v.status = 1
            elif v.status == 3: # Right
                if v.y < common.N_STOPLINE + reduced_center_size:
                    sv = [v.ax, v.ay, 'gray', v.id, 0]
                    packet = p.dumps(sv)
                    sock.sendall(packet)
                    v.ay += 1
                    sv = [v.ax, v.ay, color, v.id, 0]
                    packet = p.dumps(sv)
                    sock.sendall(packet)
                v.x, v.y = m.floor(v.ax), m.floor(v.ay)
                x, y = v.x, v.y
                if v.y >= common.N_STOPLINE + reduced_center_size and v.x > common.E_STOPLINE + reduced_center_size:
                    sv = [v.ax, v.ay, 'gray', v.id, 4]
                    packet = p.dumps(sv)
                    sock.sendall(packet)
                    v.ax -= 1
                    sv = [v.ax, v.ay, color, v.id, 0]
                    packet = p.dumps(sv)
                    sock.sendall(packet)
                v.x, v.y = m.floor(v.ax), m.floor(v.ay)
                x, y = v.x, v.y
                if v.x <= common.E_STOPLINE + reduced_center_size:
                    v.status = 1
            elif v.status == 4: # Left
                if v.y < common.N_STOPLINE + reduced_center_size:
                    sv = [v.ax, v.ay, 'gray', v.id, 0]
                    packet = p.dumps(sv)
                    sock.sendall(packet)
                    v.ay += 1
                    sv = [v.ax, v.ay, color, v.id, 0]
                    packet = p.dumps(sv)
                    sock.sendall(packet)
                if v.angle == 0:
                    v.x, v.y = m.floor(v.ax), m.floor(v.ay)
                    x, y = v.x, v.y
                if v.y >= common.N_STOPLINE + reduced_center_size and v.angle < 90:
                    sv = [v.ax, v.ay, 'gray', v.id, 5]
                    packet = p.dumps(sv)
                    sock.sendall(packet)
                    v.angle += 1
                    v.ax = v.x + huge_radius * 1.1 * (1 - m.cos(m.radians(v.angle))) # Déplacement vers la gauche
                    v.ay = v.y + huge_radius * 1.1 * m.sin(m.radians(v.angle)) # Déplacement vers le bas
                    sv = [v.ax, v.ay, color, v.id, 0]
                    packet = p.dumps(sv)
                    sock.sendall(packet)
                if v.angle >= 90:
                    v.x, v.y = m.floor(v.ax), m.floor(v.ay)
                    x, y = v.x, v.y
                if v.angle >= 90 and v.x < common.W_STOPLINE + common.VEHICLE_SIZE / 2:
                    sv = [v.ax, v.ay, 'gray', v.id, 0]
                    packet = p.dumps(sv)
                    sock.sendall(packet)
                    v.ax += 1
                    sv = [v.ax, v.ay, color, v.id, 0]
                    packet = p.dumps(sv)
                    sock.sendall(packet)
                if v.x >= common.W_STOPLINE + common.VEHICLE_SIZE / 2:
                    v.x, v.y = m.floor(v.ax), m.floor(v.ay)
                    x, y = v.x, v.y
                    v.status = 1
            elif v.status == 1:
                id = v.id
                if id[0] == 'p':
                    # Envoi du signal SIGINT pour indiquer la présence d'un véhicule prioritaire au processus lights
                    try:
                        os.kill(common.LIGHTS_PID, sg.SIGTERM)
                        if common.DEBUG:
                            print(f"\033[92m[DEBUG][coordinator] Signal SIGTERM envoyé au processus lights de PID : {common.LIGHTS_PID}\033[0m")
                        id = 't' + id
                        v.id = id
                    except ProcessLookupError:
                        print(f"\033[91m[ERREUR][coordinator] Processus de PID {common.LIGHTS_PID} non trouvé\033[0m")
                    except:
                        print("\033[91m[ERREUR][coordinator] Erreur lors de l'envoi du signal SIGTERM\033[0m")
                if v.dst == 'E':
                    sv = [v.x, v.y, 'gray', v.id, 0]
                    packet = p.dumps(sv)
                    sock.sendall(packet)
                    # Mettre à jour la position du véhicule
                    v.x -= common.NORMAL_SPEED
                    # Envoyer la nouvelle position en bleu (après le déplacement)
                    sv = [v.x, v.y, color, v.id, 0]
                    packet = p.dumps(sv)
                    sock.sendall(packet)
                    if v.x <= 0 - common.VEHICLE_SIZE / 2:
                        nq.pop(nq.index(v))
                        del v
                elif v.dst == 'W':
                    sv = [v.x, v.y, 'gray', v.id, 0]
                    packet = p.dumps(sv)
                    sock.sendall(packet)
                    # Mettre à jour la position du véhicule
                    v.x += common.NORMAL_SPEED
                    # Envoyer la nouvelle position en bleu (après le déplacement)
                    sv = [v.x, v.y, color, v.id, 0]
                    packet = p.dumps(sv)
                    sock.sendall(packet)
                    if v.x >= common.CANVAS_SIZE + common.VEHICLE_SIZE / 2:
                        nq.pop(nq.index(v))
                        del v
                elif v.dst == 'S':
                    sv = [v.x, v.y, 'gray', v.id, 0]
                    packet = p.dumps(sv)
                    sock.sendall(packet)
                    # Mettre à jour la position du véhicule
                    v.y += common.NORMAL_SPEED
                    # Envoyer la nouvelle position en bleu (après le déplacement)
                    sv = [v.x, v.y, color, v.id, 0]
                    packet = p.dumps(sv)
                    sock.sendall(packet)
                    if v.y >= common.CANVAS_SIZE + common.VEHICLE_SIZE / 2:
                        nq.pop(nq.index(v))
                        del v
        
        # Mise à jour des véhicules dans la file est (eq)
        for v in eq:
            if v.priority == 1: color = 'red'
            else: color = 'blue'
            # Liste des positions y des autres véhicules dans la même file
            x = [t.x for t in eq if t != v and t.x > v.x]  # Seuls les véhicules devant sont pris en compte
            if x:  # Si la liste n'est pas vide
                x_min = min(x)  # Trouver la position y minimale des véhicules devant
            else:
                x_min = common.CANVAS_SIZE  # Si aucun autre véhicule devant, utiliser la taille du canvas
            # Calcul de la limite de sécurité
            limit = x_min - common.VEHICLE_SIZE - common.VEHICULE_SPACING
            # Vérifier si le véhicule peut avancer
            if v.status == 0 and v.x < limit and v.x < common.E_STOPLINE:
                # Envoyer la position actuelle en gris (avant le déplacement)
                sv = [v.x, v.y, 'gray', v.id, 0]
                packet = p.dumps(sv)
                sock.sendall(packet)
                # Mettre à jour la position du véhicule
                v.x += common.NORMAL_SPEED
                # Envoyer la nouvelle position en bleu (après le déplacement)
                sv = [v.x, v.y, color, v.id, 0]
                packet = p.dumps(sv)
                sock.sendall(packet)
            elif v.status == 0 and v.x >= common.E_STOPLINE and v.x <= common.E_STOPLINE + common.STOPLINE_THRESHOLD and common.east_light.value == 1:
                if v.dst == 'W':
                    v.status = 2
                elif v.dst == 'S':
                    v.status = 3
                elif v.dst == 'N':
                    v.status = 4
                v.ax, v.ay = v.x, v.y
            elif v.status == 2: # Straight
                if v.x < common.E_STOPLINE + center_size:
                    sv = [v.ax, v.ay, 'gray', v.id, 0]
                    packet = p.dumps(sv)
                    sock.sendall(packet)
                    v.ax += 1
                    sv = [v.ax, v.ay, color, v.id, 0]
                    packet = p.dumps(sv)
                    sock.sendall(packet)
                v.x, v.y = m.floor(v.ax), m.floor(v.ay)
                x, y = v.x, v.y
                if v.x >= common.E_STOPLINE + center_size:
                    v.status = 1
            elif v.status == 3: # Right
                if v.x < common.E_STOPLINE + reduced_center_size:
                    sv = [v.ax, v.ay, 'gray', v.id, 0]
                    packet = p.dumps(sv)
                    sock.sendall(packet)
                    v.ax += 1
                    sv = [v.ax, v.ay, color, v.id, 0]
                    packet = p.dumps(sv)
                    sock.sendall(packet)
                v.x, v.y = m.floor(v.ax), m.floor(v.ay)
                x, y = v.x, v.y
                if v.x >= common.E_STOPLINE + reduced_center_size and v.y < common.S_STOPLINE + reduced_center_size:
                    sv = [v.ax, v.ay, 'gray', v.id, 4]
                    packet = p.dumps(sv)
                    sock.sendall(packet)
                    v.ay += 1
                    sv = [v.ax, v.ay, color, v.id, 0]
                    packet = p.dumps(sv)
                    sock.sendall(packet)
                v.x, v.y = m.floor(v.ax), m.floor(v.ay)
                x, y = v.x, v.y
                if v.y >= common.S_STOPLINE + reduced_center_size:
                    v.status = 1
            elif v.status == 4: # Left
                if v.x < common.E_STOPLINE + reduced_center_size:
                    sv = [v.ax, v.ay, 'gray', v.id, 0]
                    packet = p.dumps(sv)
                    sock.sendall(packet)
                    v.ax += 1
                    sv = [v.ax, v.ay, color, v.id, 0]
                    packet = p.dumps(sv)
                    sock.sendall(packet)
                if v.angle == 0:
                    v.x, v.y = m.floor(v.ax), m.floor(v.ay)
                    x, y = v.x, v.y
                if v.x >= common.E_STOPLINE + reduced_center_size and v.angle < 90:
                    sv = [v.ax, v.ay, 'gray', v.id, 5]
                    packet = p.dumps(sv)
                    sock.sendall(packet)
                    v.angle += 1
                    v.ax = v.x + huge_radius * 1.1 * m.sin(m.radians(v.angle)) # Déplacement vers la droite
                    v.ay = v.y - huge_radius * 1.1 * (1 - m.cos(m.radians(v.angle))) # Déplacement vers le haut
                    sv = [v.ax, v.ay, color, v.id, 0]
                    packet = p.dumps(sv)
                    sock.sendall(packet)
                if v.angle >= 90:
                    v.x, v.y = m.floor(v.ax), m.floor(v.ay)
                    x, y = v.x, v.y
                if v.angle >= 90 and v.y > common.N_STOPLINE - common.VEHICLE_SIZE / 2:
                    sv = [v.ax, v.ay, 'gray', v.id, 0]
                    packet = p.dumps(sv)
                    sock.sendall(packet)
                    v.ay -= 1
                    sv = [v.ax, v.ay, color, v.id, 0]
                    packet = p.dumps(sv)
                    sock.sendall(packet)
                if v.y <= common.N_STOPLINE - common.VEHICLE_SIZE / 2:
                    v.x, v.y = m.floor(v.ax), m.floor(v.ay)
                    x, y = v.x, v.y
                    v.status = 1
            elif v.status == 1:
                id = v.id
                if id[0] == 'p':
                    # Envoi du signal SIGINT pour indiquer la présence d'un véhicule prioritaire au processus lights
                    try:
                        os.kill(common.LIGHTS_PID, sg.SIGTERM)
                        if common.DEBUG:
                            print(f"\033[92m[DEBUG][coordinator] Signal SIGTERM envoyé au processus lights de PID : {common.LIGHTS_PID}\033[0m")
                        id = 't' + id
                        v.id = id
                    except ProcessLookupError:
                        print(f"\033[91m[ERREUR][coordinator] Processus de PID {common.LIGHTS_PID} non trouvé\033[0m")
                    except:
                        print("\033[91m[ERREUR][coordinator] Erreur lors de l'envoi du signal SIGTERM\033[0m")
                if v.dst == 'S':
                    sv = [v.x, v.y, 'gray', v.id, 0]
                    packet = p.dumps(sv)
                    sock.sendall(packet)
                    # Mettre à jour la position du véhicule
                    v.y += common.NORMAL_SPEED
                    # Envoyer la nouvelle position en bleu (après le déplacement)
                    sv = [v.x, v.y, color, v.id, 0]
                    packet = p.dumps(sv)
                    sock.sendall(packet)
                    if v.y >= common.CANVAS_SIZE + common.VEHICLE_SIZE / 2:
                        eq.pop(eq.index(v))
                        del v
                elif v.dst == 'N':
                    sv = [v.x, v.y, 'gray', v.id, 0]
                    packet = p.dumps(sv)
                    sock.sendall(packet)
                    # Mettre à jour la position du véhicule
                    v.y -= common.NORMAL_SPEED
                    # Envoyer la nouvelle position en bleu (après le déplacement)
                    sv = [v.x, v.y, color, v.id, 0]
                    packet = p.dumps(sv)
                    sock.sendall(packet)
                    if v.y <= 0 - common.VEHICLE_SIZE / 2:
                        eq.pop(eq.index(v))
                        del v
                elif v.dst == 'W':
                    sv = [v.x, v.y, 'gray', v.id, 0]
                    packet = p.dumps(sv)
                    sock.sendall(packet)
                    # Mettre à jour la position du véhicule
                    v.x += common.NORMAL_SPEED
                    # Envoyer la nouvelle position en bleu (après le déplacement)
                    sv = [v.x, v.y, color, v.id, 0]
                    packet = p.dumps(sv)
                    sock.sendall(packet)
                    if v.x >= common.CANVAS_SIZE + common.VEHICLE_SIZE / 2:
                        eq.pop(eq.index(v))
                        del v

        # Mise à jour des véhicules dans la file sud (sq)
        for v in sq:
            if v.priority == 1: color = 'red'
            else: color = 'blue'
            # Liste des positions y des autres véhicules dans la même file
            y = [t.y for t in sq if t != v and t.y < v.y]
            if y:  # Si la liste n'est pas vide
                y_max = max(y)  # Trouver la position y maximale des véhicules devant
            else:
                y_max = 0
            # Calcul de la limite de sécurité
            limit = y_max + common.VEHICLE_SIZE + common.VEHICULE_SPACING
            # Vérifier si le véhicule peut avancer
            if v.status == 0 and v.y > limit and v.y > common.S_STOPLINE:
                # Envoyer la position actuelle en gris (avant le déplacement)
                sv = [v.x, v.y, 'gray', v.id, 0]
                packet = p.dumps(sv)
                sock.sendall(packet)
                # Mettre à jour la position du véhicule
                v.y -= common.NORMAL_SPEED
                # Envoyer la nouvelle position en bleu (après le déplacement)
                sv = [v.x, v.y, color, v.id, 0]
                packet = p.dumps(sv)
                sock.sendall(packet)
            elif v.status == 0 and v.y <= common.S_STOPLINE and v.y >= common.S_STOPLINE - common.STOPLINE_THRESHOLD and common.south_light.value == 1:
                if v.dst == 'N':
                    v.status = 2
                elif v.dst == 'W':
                    v.status = 3
                elif v.dst == 'E':
                    v.status = 4
                v.ax, v.ay = v.x, v.y
            elif v.status == 2: # Straight
                if v.y > common.S_STOPLINE - center_size:
                    sv = [v.ax, v.ay, 'gray', v.id, 0]
                    packet = p.dumps(sv)
                    sock.sendall(packet)
                    v.ay -= 1
                    sv = [v.ax, v.ay, color, v.id, 0]
                    packet = p.dumps(sv)
                    sock.sendall(packet)
                v.x, v.y = m.floor(v.ax), m.floor(v.ay)
                x, y = v.x, v.y
                if v.y <= common.S_STOPLINE - center_size:
                    v.status = 1
            elif v.status == 3: # Right
                if v.y > common.S_STOPLINE - reduced_center_size:
                    sv = [v.ax, v.ay, 'gray', v.id, 0]
                    packet = p.dumps(sv)
                    sock.sendall(packet)
                    v.ay -= 1
                    sv = [v.ax, v.ay, color, v.id, 0]
                    packet = p.dumps(sv)
                    sock.sendall(packet)
                v.x, v.y = m.floor(v.ax), m.floor(v.ay)
                x, y = v.x, v.y
                if v.y <= common.S_STOPLINE - reduced_center_size and v.x < common.W_STOPLINE + reduced_center_size:
                    sv = [v.ax, v.ay, 'gray', v.id, 4]
                    packet = p.dumps(sv)
                    sock.sendall(packet)
                    v.ax += 1
                    sv = [v.ax, v.ay, color, v.id, 0]
                    packet = p.dumps(sv)
                    sock.sendall(packet)
                v.x, v.y = m.floor(v.ax), m.floor(v.ay)
                x, y = v.x, v.y
                if v.x >= common.W_STOPLINE + reduced_center_size:
                    v.status = 1
            elif v.status == 4: # Left
                if v.y > common.S_STOPLINE - reduced_center_size:
                    sv = [v.ax, v.ay, 'gray', v.id, 0]
                    packet = p.dumps(sv)
                    sock.sendall(packet)
                    v.ay -= 1
                    sv = [v.ax, v.ay, color, v.id, 0]
                    packet = p.dumps(sv)
                    sock.sendall(packet)
                if v.angle == 0:
                    v.x, v.y = m.floor(v.ax), m.floor(v.ay)
                    x, y = v.x, v.y
                if v.y <= common.S_STOPLINE - reduced_center_size and v.angle < 90:
                    sv = [v.ax, v.ay, 'gray', v.id, 5]
                    packet = p.dumps(sv)
                    sock.sendall(packet)
                    v.angle += 1
                    v.ax = v.x - huge_radius * 1.1 * (1 - m.cos(m.radians(v.angle))) # Déplacement vers la gauche
                    v.ay = v.y - huge_radius * 1.1 * m.sin(m.radians(v.angle)) # Déplacement vers le haut
                    sv = [v.ax, v.ay, color, v.id, 0]
                    packet = p.dumps(sv)
                    sock.sendall(packet)
                if v.angle >= 90:
                    v.x, v.y = m.floor(v.ax), m.floor(v.ay)
                    x, y = v.x, v.y
                if v.angle >= 90 and v.x > common.E_STOPLINE - common.VEHICLE_SIZE / 2:
                    sv = [v.ax, v.ay, 'gray', v.id, 0]
                    packet = p.dumps(sv)
                    sock.sendall(packet)
                    v.ax -= 1
                    sv = [v.ax, v.ay, color, v.id, 0]
                    packet = p.dumps(sv)
                    sock.sendall(packet)
                if v.x <= common.E_STOPLINE - common.VEHICLE_SIZE / 2:
                    v.x, v.y = m.floor(v.ax), m.floor(v.ay)
                    x, y = v.x, v.y
                    v.status = 1
            elif v.status == 1:
                id = v.id
                if id[0] == 'p':
                    # Envoi du signal SIGINT pour indiquer la présence d'un véhicule prioritaire au processus lights
                    try:
                        os.kill(common.LIGHTS_PID, sg.SIGTERM)
                        if common.DEBUG:
                            print(f"\033[92m[DEBUG][coordinator] Signal SIGTERM envoyé au processus lights de PID : {common.LIGHTS_PID}\033[0m")
                        id = 't' + id
                        v.id = id
                    except ProcessLookupError:
                        print(f"\033[91m[ERREUR][coordinator] Processus de PID {common.LIGHTS_PID} non trouvé\033[0m")
                    except:
                        print("\033[91m[ERREUR][coordinator] Erreur lors de l'envoi du signal SIGTERM\033[0m")
                if v.dst == 'E':
                    sv = [v.x, v.y, 'gray', v.id, 0]
                    packet = p.dumps(sv)
                    sock.sendall(packet)
                    # Mettre à jour la position du véhicule
                    v.x -= common.NORMAL_SPEED
                    # Envoyer la nouvelle position en bleu (après le déplacement)
                    sv = [v.x, v.y, color, v.id, 0]
                    packet = p.dumps(sv)
                    sock.sendall(packet)
                    if v.x <= 0 - common.VEHICLE_SIZE / 2:
                        sq.pop(sq.index(v))
                        del v
                elif v.dst == 'W':
                    sv = [v.x, v.y, 'gray', v.id, 0]
                    packet = p.dumps(sv)
                    sock.sendall(packet)
                    # Mettre à jour la position du véhicule
                    v.x += common.NORMAL_SPEED
                    # Envoyer la nouvelle position en bleu (après le déplacement)
                    sv = [v.x, v.y, color, v.id, 0]
                    packet = p.dumps(sv)
                    sock.sendall(packet)
                    if v.x >= common.CANVAS_SIZE + common.VEHICLE_SIZE / 2:
                        sq.pop(sq.index(v))
                        del v
                elif v.dst == 'N':
                    sv = [v.x, v.y, 'gray', v.id, 0]
                    packet = p.dumps(sv)
                    sock.sendall(packet)
                    # Mettre à jour la position du véhicule
                    v.y -= common.NORMAL_SPEED
                    # Envoyer la nouvelle position en bleu (après le déplacement)
                    sv = [v.x, v.y, color, v.id, 0]
                    packet = p.dumps(sv)
                    sock.sendall(packet)
                    if v.y <= 0 - common.VEHICLE_SIZE / 2:
                        sq.pop(sq.index(v))
                        del v
        
        # Mise à jour des véhicules dans la file ouest (wq)
        for v in wq:
            if v.priority == 1: color = 'red'
            else: color = 'blue'
            # Liste des positions y des autres véhicules dans la même file
            x = [t.x for t in wq if t != v and t.x < v.x]
            if x:  # Si la liste n'est pas vide
                x_max = max(x)  # Trouver la position y maximale des véhicules devant
            else:
                x_max = 0
            # Calcul de la limite de sécurité
            limit = x_max + common.VEHICLE_SIZE + common.VEHICULE_SPACING
            # Vérifier si le véhicule peut avancer
            if v.status == 0 and v.x > limit and v.x > common.W_STOPLINE:
                # Envoyer la position actuelle en gris (avant le déplacement)
                sv = [v.x, v.y, 'gray', v.id, 0]
                packet = p.dumps(sv)
                sock.sendall(packet)
                # Mettre à jour la position du véhicule
                v.x -= common.NORMAL_SPEED
                # Envoyer la nouvelle position en bleu (après le déplacement)
                sv = [v.x, v.y, color, v.id, 0]
                packet = p.dumps(sv)
                sock.sendall(packet)
            elif v.status == 0 and v.x <= common.W_STOPLINE and v.x >= common.W_STOPLINE - common.STOPLINE_THRESHOLD and common.west_light.value == 1:
                if v.dst == 'E':
                    v.status = 2
                elif v.dst == 'N':
                    v.status = 3
                elif v.dst == 'S':
                    v.status = 4
                v.ax, v.ay = v.x, v.y
            elif v.status == 2: # Straight
                if v.x > common.E_STOPLINE - center_size:
                    sv = [v.ax, v.ay, 'gray', v.id, 0]
                    packet = p.dumps(sv)
                    sock.sendall(packet)
                    v.ax -= 1
                    sv = [v.ax, v.ay, color, v.id, 0]
                    packet = p.dumps(sv)
                    sock.sendall(packet)
                v.x, v.y = m.floor(v.ax), m.floor(v.ay)
                x, y = v.x, v.y
                if v.x <= common.E_STOPLINE - center_size:
                    v.status = 1
            elif v.status == 3: # Right
                if v.x > common.W_STOPLINE - reduced_center_size:
                    sv = [v.ax, v.ay, 'gray', v.id, 0]
                    packet = p.dumps(sv)
                    sock.sendall(packet)
                    v.ax -= 1
                    sv = [v.ax, v.ay, color, v.id, 0]
                    packet = p.dumps(sv)
                    sock.sendall(packet)
                v.x, v.y = m.floor(v.ax), m.floor(v.ay)
                x, y = v.x, v.y
                if v.x <= common.W_STOPLINE - reduced_center_size and v.y > common.N_STOPLINE - reduced_center_size:
                    sv = [v.ax, v.ay, 'gray', v.id, 4]
                    packet = p.dumps(sv)
                    sock.sendall(packet)
                    v.ay -= 1
                    sv = [v.ax, v.ay, color, v.id, 0]
                    packet = p.dumps(sv)
                    sock.sendall(packet)
                v.x, v.y = m.floor(v.ax), m.floor(v.ay)
                x, y = v.x, v.y
                if v.y <= common.N_STOPLINE - reduced_center_size:
                    v.status = 1
            elif v.status == 4: # Left
                if v.x > common.W_STOPLINE - reduced_center_size:
                    sv = [v.ax, v.ay, 'gray', v.id, 0]
                    packet = p.dumps(sv)
                    sock.sendall(packet)
                    v.ax -= 1
                    sv = [v.ax, v.ay, color, v.id, 0]
                    packet = p.dumps(sv)
                    sock.sendall(packet)
                if v.angle == 0:
                    v.x, v.y = m.floor(v.ax), m.floor(v.ay)
                    x, y = v.x, v.y
                if v.x <= common.W_STOPLINE - reduced_center_size and v.angle < 90:
                    sv = [v.ax, v.ay, 'gray', v.id, 5]
                    packet = p.dumps(sv)
                    sock.sendall(packet)
                    v.angle += 1
                    v.ax = v.x - huge_radius * 1.1 * m.sin(m.radians(v.angle))  # Déplacement vers la gauche
                    v.ay = v.y + huge_radius * 1.1 * (1 - m.cos(m.radians(v.angle)))  # Déplacement vers le haut
                    sv = [v.ax, v.ay, color, v.id, 0]
                    packet = p.dumps(sv)
                    sock.sendall(packet)
                if v.angle >= 90:
                    v.x, v.y = m.floor(v.ax), m.floor(v.ay)
                    x, y = v.x, v.y
                if v.angle >= 90 and v.y < common.S_STOPLINE + common.VEHICLE_SIZE / 2:
                    sv = [v.ax, v.ay, 'gray', v.id, 0]
                    packet = p.dumps(sv)
                    sock.sendall(packet)
                    v.ay += 1
                    sv = [v.ax, v.ay, color, v.id, 0]
                    packet = p.dumps(sv)
                    sock.sendall(packet)
                if v.y >= common.S_STOPLINE + common.VEHICLE_SIZE / 2:
                    v.x, v.y = m.floor(v.ax), m.floor(v.ay)
                    x, y = v.x, v.y
                    v.status = 1
            elif v.status == 1:
                id = v.id
                if id[0] == 'p':
                    # Envoi du signal SIGINT pour indiquer la présence d'un véhicule prioritaire au processus lights
                    try:
                        os.kill(common.LIGHTS_PID, sg.SIGTERM)
                        if common.DEBUG:
                            print(f"\033[92m[DEBUG][coordinator] Signal SIGTERM envoyé au processus lights de PID : {common.LIGHTS_PID}\033[0m")
                        id = 't' + id
                        v.id = id
                    except ProcessLookupError:
                        print(f"\033[91m[ERREUR][coordinator] Processus de PID {common.LIGHTS_PID} non trouvé\033[0m")
                    except:
                        print("\033[91m[ERREUR][coordinator] Erreur lors de l'envoi du signal SIGTERM\033[0m")
                if v.dst == 'S':
                    sv = [v.x, v.y, 'gray', v.id, 0]
                    packet = p.dumps(sv)
                    sock.sendall(packet)
                    # Mettre à jour la position du véhicule
                    v.y += common.NORMAL_SPEED
                    # Envoyer la nouvelle position en bleu (après le déplacement)
                    sv = [v.x, v.y, color, v.id, 0]
                    packet = p.dumps(sv)
                    sock.sendall(packet)
                    if v.y >= common.CANVAS_SIZE + common.VEHICLE_SIZE / 2:
                        wq.pop(wq.index(v))
                        del v
                elif v.dst == 'N':
                    sv = [v.x, v.y, 'gray', v.id, 0]
                    packet = p.dumps(sv)
                    sock.sendall(packet)
                    # Mettre à jour la position du véhicule
                    v.y -= common.NORMAL_SPEED
                    # Envoyer la nouvelle position en bleu (après le déplacement)
                    sv = [v.x, v.y, color, v.id, 0]
                    packet = p.dumps(sv)
                    sock.sendall(packet)
                    if v.y <= 0 - common.VEHICLE_SIZE / 2:
                        wq.pop(wq.index(v))
                        del v
                elif v.dst == 'E':
                    sv = [v.x, v.y, 'gray', v.id, 0]
                    packet = p.dumps(sv)
                    sock.sendall(packet)
                    # Mettre à jour la position du véhicule
                    v.x -= common.NORMAL_SPEED
                    # Envoyer la nouvelle position en bleu (après le déplacement)
                    sv = [v.x, v.y, color, v.id, 0]
                    packet = p.dumps(sv)
                    sock.sendall(packet)
                    if v.x <= 0 - common.VEHICLE_SIZE / 2:
                        wq.pop(wq.index(v))
                        del v

    # Création d'un socket persistant
    client = so.socket(so.AF_INET, so.SOCK_STREAM)
    connected = False
    while not stop.is_set() and not connected:
        try:
            client.connect((common.HOST, common.PORT))
            connected = True
            if common.DEBUG:
                print("\033[92m[DEBUG][coordinator] Connexion établie avec display\033[0m")
        except ConnectionRefusedError:
            print("\033[91m[ERREUR][coordinator] Échec de la connexion au processus display, nouvelle tentative dans 1s\033[0m")
            t.sleep(1)
        except Exception as e:
            print(f"\033[91m[ERREUR][coordinator] Exception lors de la connexion: {e}\033[0m")
            stop.set()

    # Initialisation des files d'attente locales
    nq = []
    eq = []
    sq = []
    wq = []

    while not stop.is_set():
        try:
            # Lecture des files d'attente sans blocage
            try:
                nsv, _ = common.north_queue.receive(block=False)
                nv = p.loads(nsv)
                nq.append(nv)
                if common.DEBUG:
                    print(f"\033[92m[DEBUG][coordinator] Ajout dans north_queue : {nv.get_info()}\033[0m")
            except ipc.BusyError:
                pass

            try:
                esv, _ = common.east_queue.receive(block=False)
                ev = p.loads(esv)
                eq.append(ev)
                if common.DEBUG:
                    print(f"\033[92m[DEBUG][coordinator] Ajout dans east_queue : {ev.get_info()}\033[0m")
            except ipc.BusyError:
                pass

            try:
                ssv, _ = common.south_queue.receive(block=False)
                sv = p.loads(ssv)
                sq.append(sv)
                if common.DEBUG:
                    print(f"\033[92m[DEBUG][coordinator] Ajout dans south_queue : {sv.get_info()}\033[0m")
            except ipc.BusyError:
                pass

            try:
                wsv, _ = common.west_queue.receive(block=False)
                wv = p.loads(wsv)
                wq.append(wv)
                if common.DEBUG:
                    print(f"\033[92m[DEBUG][coordinator] Ajout dans west_queue : {wv.get_info()}\033[0m")
            except ipc.BusyError:
                pass

            # Mettre à jour les positions des véhicules et envoyer les données à display
            update_coords(client, nq, eq, sq, wq)
            t.sleep(common.COORDINATOR_DELAY)

        except Exception as e:
            print(f"\033[91m[ERREUR][coordinator] Exception : {e}\033[0m")
            t.sleep(0.5)

    try:
        client.shutdown(so.SHUT_RDWR)
        client.close()
    except Exception as e:
        print(f"\033[91m[ERREUR][coordinator] Échec de la fermeture du socket: {e}\033[0m")
    print("[coordinator] Processus terminé")