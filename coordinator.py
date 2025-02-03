# Importe le module common pour avoir accès aux constantes globales
import common
# Importe le module pickle pour la sérialisation des objets
import pickle as p

import sysv_ipc as ipc
import multiprocessing as mp
import socket as so
import time as t

# Création d'une liste pour les véhicules en circulation
vehicles = []

# PROCESSUS COORDINATOR
# Le processus coordinator est responsable de la gestion des véhicules
# Il calcule régulièrement les nouvelles coordonnées des véhicules en circulation en fonction de l'état des feux, des autres véhicules alentours et des priorités
# Les priorités sont définies par une table disponible dans common, elles sont appliquées dans l'odre suivant : right → straight → left

def coordinator(stop):

    ##########
    TEMP_COLOR = 'blue'

    # Calcule les nouvelles coordonnées des véhicules en circulation
    def update_coords(sock, nq, eq, sq, wq):
        for v in nq:
            if v.status == 0 and common.north_light.value == 1:
                v.y += common.NORMAL_SPEED
                sv = [v.x, v.y, TEMP_COLOR]
                packet = p.dumps(sv)
                sock.sendall(packet)
                if common.DEBUG():
                    print(f"\033[92m[DEBUG][coordinator] Le véhicule {v.id} a été déplacé en {v.x}, {v.y}\033")
        for v in eq:
            if v.status == 0 and common.east_light.value == 1:
                v.x += common.NORMAL_SPEED
                sv = [v.x, v.y, TEMP_COLOR]
                packet = p.dumps(sv)
                sock.sendall(packet)
                if common.DEBUG():
                    print(f"\033[92m[DEBUG][coordinator] Le véhicule {v.id} a été déplacé en {v.x}, {v.y}\033")
        for v in sq:
            if v.status == 0 and common.south_light.value == 1:
                v.y -= common.NORMAL_SPEED
                sv = [v.x, v.y, TEMP_COLOR]
                packet = p.dumps(sv)
                sock.sendall(packet)
                if common.DEBUG():
                    print(f"\033[92m[DEBUG][coordinator] Le véhicule {v.id} a été déplacé en {v.x}, {v.y}\033")
        for v in wq:
            if v.status == 0 and common.west_light.value == 1:
                v.x -= common.NORMAL_SPEED
                sv = [v.x, v.y, TEMP_COLOR]
                packet = p.dumps(sv)
                sock.sendall(packet)
                if common.DEBUG():
                    print(f"\033[92m[DEBUG][coordinator] Le véhicule {v.id} a été déplacé en {v.x}, {v.y}\033")

    sock = so.socket(so.AF_INET, so.SOCK_STREAM)
    sock_status = False

    # Tentative de connexion au processus display
    while not stop.is_set() and not sock_status:

        t.sleep(common.TIME_BEFORE_CONNECTION_ATTEMPT)

        try:
            with so.socket(so.AF_INET, so.SOCK_STREAM) as client:
                client.connect((common.HOST, common.PORT))
            sock_status = True
        # Rententer la connexion au bout de 1 seconde et indiquer un échec
        except ConnectionRefusedError:
            print("\033[91m[ERREUR][coordinator] Échec de la connexion au processus display, nouvelle tentative dans 1s\033[0m")
            t.sleep(1)
        except:
            print("\033[91m[ERREUR][coordinator] Impossible de se connecter au processus display, arrêt du programme\033[0m")
            stop.set()

        # Création des listes d'attente pour chaque direction
        try:
            nq = []
            eq = []
            sq = []
            wq = []
        except:
            print("\033[91m[ERREUR][coordinator] Échec de la création des listes d'attente\033[0m")

        directions = common.DIRECTIONS # pas sûr que ce soit utile

        while not stop.is_set():

            if common.DEBUG_MSG:
                if client.fileno() != -1:  # Le socket est ouvert
                    message = "test"
                    send = message.encode()
                    client.sendall(send)
                    print("\033[92m[DEBUG][coordinator] Message de test envoyé\033[0m")
                else:
                    print("\033[91m[ERREUR][coordinator] Le socket est fermé\033[0m")
                t.sleep(1)


            # Récupération de tous les véhicules en attente
            try:
                try:
                    nsv, _ = common.north_queue.receive(block = False)
                    nv = p.loads(nsv)
                    nq.append(nv)
                    if common.DEBUG:
                        info = nv.get_info()
                        print(f"\033[92m[DEBUG][coordinator] north_queue last append is {info}\033[0m")
                except ipc.BusyError:
                    pass
                try:
                    esv, _ = common.east_queue.receive(block = False)
                    ev = p.loads(esv)
                    eq.append(ev)
                    if common.DEBUG:
                        info = ev.get_info()
                        print(f"\033[92m[DEBUG][coordinator] east_queue last append is {info}\033[0m")
                except ipc.BusyError:
                    pass
                try:
                    ssv, _ = common.south_queue.receive(block = False)
                    sv = p.loads(ssv)
                    sq.append(sv)
                    if common.DEBUG:
                        info = sv.get_info()
                        print(f"\033[92m[DEBUG][coordinator] south_queue last append is {info}\033[0m")
                except ipc.BusyError:
                    pass
                try:
                    wsv, _ = common.west_queue.receive(block = False)
                    wv = p.loads(wsv)
                    wq.append(wv)
                    if common.DEBUG:
                        info = wv.get_info()
                        print(f"\033[92m[DEBUG][coordinator] west_queue last append is {info}\033[0m")
                except ipc.BusyError:
                    pass

                update_coords(client, nq, eq, sq, wq)
                
                t.sleep(common.COORDINATOR_DELAY)

            # Approfondissement du debug
            except Exception as e:
                print(f"\033[91m[ERREUR][coordinator] Exception : {e}\033[0m")
                t.sleep(0.5)
                pass

            except:
                print("\033[91m[ERREUR][coordinator] Échec de la désérialisation des objets\033[0m")
                pass

            # Détection des véhicules en approche de l'intersection
            # try:

    try:
        sock.close()
    except:
        print("\033[91m[ERREUR][coordinator] Échec de la fermeture du socket\033[0m")
    print("[coordinator] Processus terminé")