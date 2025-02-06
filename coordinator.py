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

    def send_msg(sock, msg):
        """
        Envoie un message par le socket en préfixant par 4 octets indiquant la taille du message.
        """
        msg_len = len(msg)
        header = msg_len.to_bytes(4, byteorder='big')
        sock.sendall(header + msg)


    def update_coords(sock, nq, eq, sq, wq):
        # On définit une fonction utilitaire pour vérifier la priorité à droite.
        # Pour un véhicule v, si ce n'est pas un virage à droite (v.status != 3),
        # et s'il existe dans la file "à droite" un véhicule qui effectue un virage à droite,
        # alors on renvoie False (le véhicule ne peut pas encore passer).
        def can_process(v, right_lane, right_light_value, expected_right_dst):
            if v.status != 3:  # seuls les véhicules qui ne tournent pas à droite doivent céder
                for rv in right_lane:
                    # Si un véhicule est déjà en train de tourner à droite
                    if rv.status == 3:
                        print(f"[DEBUG] {v.id} cède à {rv.id} (déjà en droit)")
                        return False
                    # Si un véhicule est à l'arrêt mais prêt à tourner à droite (feu vert et destination attendue)
                    if (rv.status == 0 and 
                        right_light_value == 1 and 
                        rv.dst == expected_right_dst):
                        print(f"[DEBUG] {v.id} cède à {rv.id} (en attente de droit)")
                        return False
            return True
        
        # --- Mise à jour des véhicules dans la file nord (nq) ---
        for v in nq:
            null_id = 'null'
            if v.priority == 1: 
                color = 'red'
            else: 
                color = 'blue'
            y = [t.y for t in nq if t != v and t.y > v.y]
            if y:
                y_min = min(y)
            else:
                y_min = common.CANVAS_SIZE
            limit = y_min - common.VEHICLE_SIZE - common.VEHICULE_SPACING
            if v.status == 0 and v.y < limit and v.y < common.N_STOPLINE:
                sv = [v.x, v.y, 'gray', v.id, 0]
                packet = p.dumps(sv)
                send_msg(sock, packet)
                v.y += common.NORMAL_SPEED
                sv = [v.x, v.y, color, v.id, 0]
                packet = p.dumps(sv)
                send_msg(sock, packet)
            elif v.status == 0 and v.y >= common.N_STOPLINE and v.y <= common.N_STOPLINE + common.STOPLINE_THRESHOLD and common.north_light.value == 1:
                if v.dst == 'S':
                    v.status = 2
                elif v.dst == 'E':
                    v.status = 3
                elif v.dst == 'W':
                    v.status = 4
                v.ax, v.ay = v.x, v.y
            elif v.status == 2:  # Passage tout droit depuis le Nord
                # Pour le véhicule allant tout droit du Nord, il doit céder à ceux venant de l'Est tournant à droite.
                if not can_process(v, eq, common.east_light.value, 'S'):
                    continue  # On attend tant que le véhicule à droite ne s'est pas engagé
                # (le reste de la mise à jour de position reste inchangé)
                if v.y < common.N_STOPLINE + center_size:
                    sv = [v.ax, v.ay, 'gray', v.id, 0]
                    packet = p.dumps(sv)
                    send_msg(sock, packet)

                    v.ay += common.NORMAL_SPEED
                    sv = [v.ax, v.ay, color, v.id, 0]
                    packet = p.dumps(sv)
                    send_msg(sock, packet)

                v.x, v.y = m.floor(v.ax), m.floor(v.ay)
                if v.y >= common.N_STOPLINE + center_size:
                    v.status = 1
            elif v.status == 3:  # Virage à droite (pour le Nord, vers l'Est)
                # Les véhicules qui tournent à droite ont la priorité, pas de vérif.
                if v.y < common.N_STOPLINE + reduced_center_size:
                    sv = [v.ax, v.ay, 'gray', v.id, 0]
                    packet = p.dumps(sv)
                    send_msg(sock, packet)
                    v.ay += common.NORMAL_SPEED
                    sv = [v.ax, v.ay, color, v.id, 0]
                    packet = p.dumps(sv)
                    send_msg(sock, packet)
                v.x, v.y = m.floor(v.ax), m.floor(v.ay)
                if v.y >= common.N_STOPLINE + reduced_center_size and v.x > common.E_STOPLINE + reduced_center_size:
                    sv = [v.ax, v.ay, 'gray', v.id, 4]
                    packet = p.dumps(sv)
                    send_msg(sock, packet)
                    v.ax -= common.NORMAL_SPEED
                    sv = [v.ax, v.ay, color, v.id, 0]
                    packet = p.dumps(sv)
                    send_msg(sock, packet)
                v.x, v.y = m.floor(v.ax), m.floor(v.ay)
                if v.x <= common.E_STOPLINE + reduced_center_size:
                    v.status = 1
            elif v.status == 4:  # Virage à gauche depuis le Nord
                # Pour le virage à gauche, le véhicule doit également céder aux véhicules venant de l'Est en virage droit.
                if not can_process(v, eq, common.east_light.value, 'S'):
                    print(f"[DEBUG][Nord] {v.id} attend pour céder à priorité à droite.")
                    continue
                # (poursuite de l'animation pour le virage à gauche)
                if v.y < common.N_STOPLINE + reduced_center_size:
                    sv = [v.ax, v.ay, 'gray', v.id, 0]
                    packet = p.dumps(sv)
                    send_msg(sock, packet)
                    v.ay += common.NORMAL_SPEED
                    sv = [v.ax, v.ay, color, v.id, 0]
                    packet = p.dumps(sv)
                    send_msg(sock, packet)
                if v.angle == 0:
                    v.x, v.y = m.floor(v.ax), m.floor(v.ay)
                if v.y >= common.N_STOPLINE + reduced_center_size and v.angle < 90:
                    sv = [v.ax, v.ay, 'gray', v.id, 5]
                    packet = p.dumps(sv)
                    send_msg(sock, packet)
                    # Calcul de l'incrément d'angle en degrés pour un déplacement constant sur l'arc
                    effective_radius = huge_radius * 1.1
                    delta_angle = (common.NORMAL_SPEED / effective_radius) * (180 / m.pi)
                    v.angle += delta_angle
                    v.ax = v.x + effective_radius * (1 - m.cos(m.radians(v.angle)))
                    v.ay = v.y + effective_radius * m.sin(m.radians(v.angle))
                    sv = [v.ax, v.ay, color, v.id, 0]
                    packet = p.dumps(sv)
                    send_msg(sock, packet)
                if v.angle >= 90:
                    v.x, v.y = m.floor(v.ax), m.floor(v.ay)
                if v.angle >= 90 and v.x < common.W_STOPLINE + common.VEHICLE_SIZE / 2:
                    sv = [v.ax, v.ay, 'gray', v.id, 0]
                    packet = p.dumps(sv)
                    send_msg(sock, packet)
                    v.ax += common.NORMAL_SPEED
                    sv = [v.ax, v.ay, color, v.id, 0]
                    packet = p.dumps(sv)
                    send_msg(sock, packet)
                if v.x >= common.W_STOPLINE + common.VEHICLE_SIZE / 2:
                    v.x, v.y = m.floor(v.ax), m.floor(v.ay)
                    v.status = 1
            elif v.status == 1:
                # Passage de l'intersection (hors de l'intersection)
                id = v.id
                if id[0] == 'p':
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
                    send_msg(sock, packet)
                    v.x -= common.NORMAL_SPEED
                    sv = [v.x, v.y, color, v.id, 0]
                    packet = p.dumps(sv)
                    send_msg(sock, packet)
                    if v.x <= 0 - common.VEHICLE_SIZE / 2:
                        print(f"[DEBUG][coordinator] {v.id} a quitté l'aire d'affichage et est supprimé.")
                        nq.pop(nq.index(v))
                        del v
                elif v.dst == 'W':
                    sv = [v.x, v.y, 'gray', v.id, 0]
                    packet = p.dumps(sv)
                    send_msg(sock, packet)
                    v.x += common.NORMAL_SPEED
                    sv = [v.x, v.y, color, v.id, 0]
                    packet = p.dumps(sv)
                    send_msg(sock, packet)
                    if v.x >= common.CANVAS_SIZE + common.VEHICLE_SIZE / 2:
                        print(f"[DEBUG][coordinator] {v.id} a quitté l'aire d'affichage et est supprimé.")
                        nq.pop(nq.index(v))
                        del v
                elif v.dst == 'S':
                    sv = [v.x, v.y, 'gray', v.id, 0]
                    packet = p.dumps(sv)
                    send_msg(sock, packet)
                    v.y += common.NORMAL_SPEED
                    sv = [v.x, v.y, color, v.id, 0]
                    packet = p.dumps(sv)
                    send_msg(sock, packet)
                    if v.y >= common.CANVAS_SIZE + common.VEHICLE_SIZE / 2:
                        print(f"[DEBUG][coordinator] {v.id} a quitté l'aire d'affichage et est supprimé.")
                        nq.pop(nq.index(v))
                        del v

        # --- Mêmes modifications pour la file EST ---
        for v in eq:
            if v.priority == 1: 
                color = 'red'
            else: 
                color = 'blue'
            x = [t.x for t in eq if t != v and t.x > v.x]
            if x:
                x_min = min(x)
            else:
                x_min = common.CANVAS_SIZE
            limit = x_min - common.VEHICLE_SIZE - common.VEHICULE_SPACING
            if v.status == 0 and v.x < limit and v.x < common.E_STOPLINE:
                sv = [v.x, v.y, 'gray', v.id, 0]
                packet = p.dumps(sv)
                send_msg(sock, packet)
                v.x += common.NORMAL_SPEED
                sv = [v.x, v.y, color, v.id, 0]
                packet = p.dumps(sv)
                send_msg(sock, packet)
            elif v.status == 0 and v.x >= common.E_STOPLINE and v.x <= common.E_STOPLINE + common.STOPLINE_THRESHOLD and common.east_light.value == 1:
                if v.dst == 'W':
                    v.status = 2
                elif v.dst == 'S':
                    v.status = 3
                elif v.dst == 'N':
                    v.status = 4
                v.ax, v.ay = v.x, v.y
            elif v.status == 2:  # Passage tout droit depuis l'Est
                if not can_process(v, sq, common.south_light.value, 'W'):
                    continue
                if v.x < common.E_STOPLINE + center_size:
                    sv = [v.ax, v.ay, 'gray', v.id, 0]
                    packet = p.dumps(sv)
                    send_msg(sock, packet)
                    v.ax += common.NORMAL_SPEED
                    sv = [v.ax, v.ay, color, v.id, 0]
                    packet = p.dumps(sv)
                    send_msg(sock, packet)
                v.x, v.y = m.floor(v.ax), m.floor(v.ay)
                if v.x >= common.E_STOPLINE + center_size:
                    v.status = 1
            elif v.status == 3:  # Virage à droite (pour l'Est, vers le Sud)
                # Les véhicules tournant à droite passent sans attendre
                if v.x < common.E_STOPLINE + reduced_center_size:
                    sv = [v.ax, v.ay, 'gray', v.id, 0]
                    packet = p.dumps(sv)
                    send_msg(sock, packet)
                    v.ax += common.NORMAL_SPEED
                    sv = [v.ax, v.ay, color, v.id, 0]
                    packet = p.dumps(sv)
                    send_msg(sock, packet)
                v.x, v.y = m.floor(v.ax), m.floor(v.ay)
                if v.x >= common.E_STOPLINE + reduced_center_size and v.y < common.S_STOPLINE + reduced_center_size:
                    sv = [v.ax, v.ay, 'gray', v.id, 4]
                    packet = p.dumps(sv)
                    send_msg(sock, packet)
                    v.ay += common.NORMAL_SPEED
                    sv = [v.ax, v.ay, color, v.id, 0]
                    packet = p.dumps(sv)
                    send_msg(sock, packet)
                v.x, v.y = m.floor(v.ax), m.floor(v.ay)
                if v.y >= common.S_STOPLINE + reduced_center_size:
                    v.status = 1
            elif v.status == 4:  # Virage à gauche depuis l'Est
                if not can_process(v, sq, common.south_light.value, 'W'):
                    continue

                if v.x < common.E_STOPLINE + reduced_center_size:
                    sv = [v.ax, v.ay, 'gray', v.id, 0]
                    packet = p.dumps(sv)
                    send_msg(sock, packet)
                    v.ax += common.NORMAL_SPEED
                    sv = [v.ax, v.ay, color, v.id, 0]
                    packet = p.dumps(sv)
                    send_msg(sock, packet)
                if v.angle == 0:
                    v.x, v.y = m.floor(v.ax), m.floor(v.ay)
                if v.x >= common.E_STOPLINE + reduced_center_size and v.angle < 90:
                    sv = [v.ax, v.ay, 'gray', v.id, 5]
                    packet = p.dumps(sv)
                    send_msg(sock, packet)
                    effective_radius = huge_radius * 1.1
                    delta_angle = (common.NORMAL_SPEED / effective_radius) * (180 / m.pi)
                    v.angle += delta_angle
                    v.ax = v.x + effective_radius * 1.1 * m.sin(m.radians(v.angle))
                    v.ay = v.y - effective_radius * 1.1 * (1 - m.cos(m.radians(v.angle)))
                    sv = [v.ax, v.ay, color, v.id, 0]
                    packet = p.dumps(sv)
                    send_msg(sock, packet)
                if v.angle >= 90:
                    v.x, v.y = m.floor(v.ax), m.floor(v.ay)
                if v.angle >= 90 and v.y > common.N_STOPLINE - common.VEHICLE_SIZE / 2:
                    sv = [v.ax, v.ay, 'gray', v.id, 0]
                    packet = p.dumps(sv)
                    send_msg(sock, packet)
                    v.ay -= common.NORMAL_SPEED
                    sv = [v.ax, v.ay, color, v.id, 0]
                    packet = p.dumps(sv)
                    send_msg(sock, packet)
                if v.y <= common.N_STOPLINE - common.VEHICLE_SIZE / 2:
                    v.x, v.y = m.floor(v.ax), m.floor(v.ay)
                    v.status = 1
            elif v.status == 1:
                id = v.id
                if id[0] == 'p':
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
                    send_msg(sock, packet)
                    v.y += common.NORMAL_SPEED
                    sv = [v.x, v.y, color, v.id, 0]
                    packet = p.dumps(sv)
                    send_msg(sock, packet)
                    if v.y >= common.CANVAS_SIZE + common.VEHICLE_SIZE / 2:
                        print(f"[DEBUG][coordinator] {v.id} a quitté l'aire d'affichage et est supprimé.")
                        eq.pop(eq.index(v))
                        del v
                elif v.dst == 'N':
                    sv = [v.x, v.y, 'gray', v.id, 0]
                    packet = p.dumps(sv)
                    send_msg(sock, packet)
                    v.y -= common.NORMAL_SPEED
                    sv = [v.x, v.y, color, v.id, 0]
                    packet = p.dumps(sv)
                    send_msg(sock, packet)
                    if v.y <= 0 - common.VEHICLE_SIZE / 2:
                        print(f"[DEBUG][coordinator] {v.id} a quitté l'aire d'affichage et est supprimé.")
                        eq.pop(eq.index(v))
                        del v
                elif v.dst == 'W':
                    sv = [v.x, v.y, 'gray', v.id, 0]
                    packet = p.dumps(sv)
                    send_msg(sock, packet)
                    v.x += common.NORMAL_SPEED
                    sv = [v.x, v.y, color, v.id, 0]
                    packet = p.dumps(sv)
                    send_msg(sock, packet)
                    if v.x >= common.CANVAS_SIZE + common.VEHICLE_SIZE / 2:
                        print(f"[DEBUG][coordinator] {v.id} a quitté l'aire d'affichage et est supprimé.")
                        eq.pop(eq.index(v))
                        del v

        # --- Traitement similaire pour la file Sud (sq) ---
        # Pour la file Sud, la file à droite sera wq (ouest).
        for v in sq:
            if v.priority == 1: 
                color = 'red'
            else: 
                color = 'blue'
            y = [t.y for t in sq if t != v and t.y < v.y]
            if y:
                y_max = max(y)
            else:
                y_max = 0
            limit = y_max + common.VEHICLE_SIZE + common.VEHICULE_SPACING
            if v.status == 0 and v.y > limit and v.y > common.S_STOPLINE:
                sv = [v.x, v.y, 'gray', v.id, 0]
                packet = p.dumps(sv)
                send_msg(sock, packet)
                v.y -= common.NORMAL_SPEED
                sv = [v.x, v.y, color, v.id, 0]
                packet = p.dumps(sv)
                send_msg(sock, packet)
            elif v.status == 0 and v.y <= common.S_STOPLINE and v.y >= common.S_STOPLINE - common.STOPLINE_THRESHOLD and common.south_light.value == 1:
                if v.dst == 'N':
                    v.status = 2
                elif v.dst == 'W':
                    v.status = 3
                elif v.dst == 'E':
                    v.status = 4
                v.ax, v.ay = v.x, v.y
            elif v.status == 2:  # Tout droit depuis le Sud
                if not can_process(v, wq, common.west_light.value, 'N'):
                    continue
                if v.y > common.S_STOPLINE - center_size:
                    sv = [v.ax, v.ay, 'gray', v.id, 0]
                    packet = p.dumps(sv)
                    send_msg(sock, packet)
                    v.ay -= common.NORMAL_SPEED
                    sv = [v.ax, v.ay, color, v.id, 0]
                    packet = p.dumps(sv)
                    send_msg(sock, packet)
                v.x, v.y = m.floor(v.ax), m.floor(v.ay)
                if v.y <= common.S_STOPLINE - center_size:
                    v.status = 1
            elif v.status == 3:  # Virage à droite depuis le Sud (vers l'Ouest)
                if v.y > common.S_STOPLINE - reduced_center_size:
                    sv = [v.ax, v.ay, 'gray', v.id, 0]
                    packet = p.dumps(sv)
                    send_msg(sock, packet)
                    v.ay -= common.NORMAL_SPEED
                    sv = [v.ax, v.ay, color, v.id, 0]
                    packet = p.dumps(sv)
                    send_msg(sock, packet)
                v.x, v.y = m.floor(v.ax), m.floor(v.ay)
                if v.y <= common.S_STOPLINE - reduced_center_size and v.x < common.W_STOPLINE + reduced_center_size:
                    sv = [v.ax, v.ay, 'gray', v.id, 4]
                    packet = p.dumps(sv)
                    send_msg(sock, packet)
                    v.ax += common.NORMAL_SPEED
                    sv = [v.ax, v.ay, color, v.id, 0]
                    packet = p.dumps(sv)
                    send_msg(sock, packet)
                v.x, v.y = m.floor(v.ax), m.floor(v.ay)
                if v.x >= common.W_STOPLINE + reduced_center_size:
                    v.status = 1
            elif v.status == 4:  # Virage à gauche depuis le Sud
                if not can_process(v, wq, common.west_light.value, 'N'):
                    continue
                if v.y > common.S_STOPLINE - reduced_center_size:
                    sv = [v.ax, v.ay, 'gray', v.id, 0]
                    packet = p.dumps(sv)
                    send_msg(sock, packet)
                    v.ay -= common.NORMAL_SPEED
                    sv = [v.ax, v.ay, color, v.id, 0]
                    packet = p.dumps(sv)
                    send_msg(sock, packet)
                if v.angle == 0:
                    v.x, v.y = m.floor(v.ax), m.floor(v.ay)
                if v.y <= common.S_STOPLINE - reduced_center_size and v.angle < 90:
                    sv = [v.ax, v.ay, 'gray', v.id, 5]
                    packet = p.dumps(sv)
                    send_msg(sock, packet)
                    effective_radius = huge_radius * 1.1
                    delta_angle = (common.NORMAL_SPEED / effective_radius) * (180 / m.pi)
                    v.angle += delta_angle
                    v.ax = v.x - effective_radius * 1.1 * (1 - m.cos(m.radians(v.angle)))
                    v.ay = v.y - effective_radius * 1.1 * m.sin(m.radians(v.angle))
                    sv = [v.ax, v.ay, color, v.id, 0]
                    packet = p.dumps(sv)
                    send_msg(sock, packet)
                if v.angle >= 90:
                    v.x, v.y = m.floor(v.ax), m.floor(v.ay)
                if v.angle >= 90 and v.x > common.E_STOPLINE - common.VEHICLE_SIZE / 2:
                    sv = [v.ax, v.ay, 'gray', v.id, 0]
                    packet = p.dumps(sv)
                    send_msg(sock, packet)
                    v.ax -= common.NORMAL_SPEED
                    sv = [v.ax, v.ay, color, v.id, 0]
                    packet = p.dumps(sv)
                    send_msg(sock, packet)
                if v.x <= common.E_STOPLINE - common.VEHICLE_SIZE / 2:
                    v.x, v.y = m.floor(v.ax), m.floor(v.ay)
                    v.status = 1
            elif v.status == 1:
                id = v.id
                if id[0] == 'p':
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
                    send_msg(sock, packet)
                    v.x -= common.NORMAL_SPEED
                    sv = [v.x, v.y, color, v.id, 0]
                    packet = p.dumps(sv)
                    send_msg(sock, packet)
                    if v.x <= 0 - common.VEHICLE_SIZE / 2:
                        print(f"[DEBUG][coordinator] {v.id} a quitté l'aire d'affichage et est supprimé.")
                        sq.pop(sq.index(v))
                        del v
                elif v.dst == 'W':
                    sv = [v.x, v.y, 'gray', v.id, 0]
                    packet = p.dumps(sv)
                    send_msg(sock, packet)
                    v.x += common.NORMAL_SPEED
                    sv = [v.x, v.y, color, v.id, 0]
                    packet = p.dumps(sv)
                    send_msg(sock, packet)
                    if v.x >= common.CANVAS_SIZE + common.VEHICLE_SIZE / 2:
                        print(f"[DEBUG][coordinator] {v.id} a quitté l'aire d'affichage et est supprimé.")
                        sq.pop(sq.index(v))
                        del v
                elif v.dst == 'N':
                    sv = [v.x, v.y, 'gray', v.id, 0]
                    packet = p.dumps(sv)
                    send_msg(sock, packet)
                    v.y -= common.NORMAL_SPEED
                    sv = [v.x, v.y, color, v.id, 0]
                    packet = p.dumps(sv)
                    send_msg(sock, packet)
                    if v.y <= 0 - common.VEHICLE_SIZE / 2:
                        print(f"[DEBUG][coordinator] {v.id} a quitté l'aire d'affichage et est supprimé.")
                        sq.pop(sq.index(v))
                        del v

        # --- Traitement pour la file Ouest (wq) ---
        for v in wq:
            if v.priority == 1: 
                color = 'red'
            else: 
                color = 'blue'
            x = [t.x for t in wq if t != v and t.x < v.x]
            if x:
                x_max = max(x)
            else:
                x_max = 0
            limit = x_max + common.VEHICLE_SIZE + common.VEHICULE_SPACING
            if v.status == 0 and v.x > limit and v.x > common.W_STOPLINE:
                sv = [v.x, v.y, 'gray', v.id, 0]
                packet = p.dumps(sv)
                send_msg(sock, packet)
                v.x -= common.NORMAL_SPEED
                sv = [v.x, v.y, color, v.id, 0]
                packet = p.dumps(sv)
                send_msg(sock, packet)
            elif v.status == 0 and v.x <= common.W_STOPLINE and v.x >= common.W_STOPLINE - common.STOPLINE_THRESHOLD and common.west_light.value == 1:
                if v.dst == 'E':
                    v.status = 2
                elif v.dst == 'N':
                    v.status = 3
                elif v.dst == 'S':
                    v.status = 4
                v.ax, v.ay = v.x, v.y
            elif v.status == 2:  # Tout droit depuis l'Ouest
                if not can_process(v, nq, common.north_light.value, 'E'):
                    continue
                if v.x > common.E_STOPLINE - center_size:
                    sv = [v.ax, v.ay, 'gray', v.id, 0]
                    packet = p.dumps(sv)
                    send_msg(sock, packet)
                    v.ax -= common.NORMAL_SPEED
                    sv = [v.ax, v.ay, color, v.id, 0]
                    packet = p.dumps(sv)
                    send_msg(sock, packet)
                v.x, v.y = m.floor(v.ax), m.floor(v.ay)
                if v.x <= common.E_STOPLINE - center_size:
                    v.status = 1
            elif v.status == 3:  # Virage à droite depuis l'Ouest (vers le Nord)
                if v.x > common.W_STOPLINE - reduced_center_size:
                    sv = [v.ax, v.ay, 'gray', v.id, 0]
                    packet = p.dumps(sv)
                    send_msg(sock, packet)
                    v.ax -= common.NORMAL_SPEED
                    sv = [v.ax, v.ay, color, v.id, 0]
                    packet = p.dumps(sv)
                    send_msg(sock, packet)
                v.x, v.y = m.floor(v.ax), m.floor(v.ay)
                if v.x <= common.W_STOPLINE - reduced_center_size and v.y > common.N_STOPLINE - reduced_center_size:
                    sv = [v.ax, v.ay, 'gray', v.id, 4]
                    packet = p.dumps(sv)
                    send_msg(sock, packet)
                    v.ay -= common.NORMAL_SPEED
                    sv = [v.ax, v.ay, color, v.id, 0]
                    packet = p.dumps(sv)
                    send_msg(sock, packet)
                v.x, v.y = m.floor(v.ax), m.floor(v.ay)
                if v.y <= common.N_STOPLINE - reduced_center_size:
                    v.status = 1
            elif v.status == 4:  
                if not can_process(v, nq, common.north_light.value, 'E'):
                    continue
                if v.x > common.W_STOPLINE - reduced_center_size:
                    sv = [v.ax, v.ay, 'gray', v.id, 0]
                    packet = p.dumps(sv)
                    send_msg(sock, packet)
                    v.ax -= common.NORMAL_SPEED
                    sv = [v.ax, v.ay, color, v.id, 0]
                    packet = p.dumps(sv)
                    send_msg(sock, packet)
                if v.angle == 0:
                    v.x, v.y = m.floor(v.ax), m.floor(v.ay)
                if v.x <= common.W_STOPLINE - reduced_center_size and v.angle < 90:
                    sv = [v.ax, v.ay, 'gray', v.id, 5]
                    packet = p.dumps(sv)
                    send_msg(sock, packet)
                    effective_radius = huge_radius * 1.1
                    delta_angle = (common.NORMAL_SPEED / effective_radius) * (180 / m.pi)
                    v.angle += delta_angle
                    v.ax = v.x - effective_radius * 1.1 * m.sin(m.radians(v.angle))
                    v.ay = v.y + effective_radius * 1.1 * (1 - m.cos(m.radians(v.angle)))
                    sv = [v.ax, v.ay, color, v.id, 0]
                    packet = p.dumps(sv)
                    send_msg(sock, packet)
                if v.angle >= 90:
                    v.x, v.y = m.floor(v.ax), m.floor(v.ay)
                if v.angle >= 90 and v.y < common.S_STOPLINE + common.VEHICLE_SIZE / 2:
                    sv = [v.ax, v.ay, 'gray', v.id, 0]
                    packet = p.dumps(sv)
                    send_msg(sock, packet)
                    v.ay += common.NORMAL_SPEED
                    sv = [v.ax, v.ay, color, v.id, 0]
                    packet = p.dumps(sv)
                    send_msg(sock, packet)
                if v.y >= common.S_STOPLINE + common.VEHICLE_SIZE / 2:
                    v.x, v.y = m.floor(v.ax), m.floor(v.ay)
                    v.status = 1
            elif v.status == 1:
                id = v.id
                if id[0] == 'p':
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
                    send_msg(sock, packet)
                    v.y += common.NORMAL_SPEED
                    sv = [v.x, v.y, color, v.id, 0]
                    packet = p.dumps(sv)
                    send_msg(sock, packet)
                    if v.y <= 0 - common.VEHICLE_SIZE / 2:
                        print(f"[DEBUG][coordinator] {v.id} a quitté l'aire d'affichage et est supprimé.")
                        wq.pop(wq.index(v))
                        del v
                elif v.dst == 'N':
                    sv = [v.x, v.y, 'gray', v.id, 0]
                    packet = p.dumps(sv)
                    send_msg(sock, packet)
                    v.y -= common.NORMAL_SPEED
                    sv = [v.x, v.y, color, v.id, 0]
                    packet = p.dumps(sv)
                    send_msg(sock, packet)
                    if v.y >= common.CANVAS_SIZE + common.VEHICLE_SIZE / 2:
                        print(f"[DEBUG][coordinator] {v.id} a quitté l'aire d'affichage et est supprimé.")
                        wq.pop(wq.index(v))
                        del v
                elif v.dst == 'E':
                    sv = [v.x, v.y, 'gray', v.id, 0]
                    packet = p.dumps(sv)
                    send_msg(sock, packet)
                    v.x -= common.NORMAL_SPEED
                    sv = [v.x, v.y, color, v.id, 0]
                    packet = p.dumps(sv)
                    send_msg(sock, packet)
                    if v.x <= 0 - common.VEHICLE_SIZE / 2:
                        print(f"[DEBUG][coordinator] {v.id} a quitté l'aire d'affichage et est supprimé.")
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