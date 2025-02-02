# Importe le module common pour avoir accès aux constantes globales
import common
# Importe le module pickle pour la sérialisation des objets
import pickle as p

import sysv_ipc as ipc
import multiprocessing as mp
import socket as so
import time as t

def coordinator(stop):
    sock = so.socket(so.AF_INET, so.SOCK_STREAM)
    sock_status = False

    # Tentative de connexion au processus display
    while not stop.is_set() and not sock_status:
        try:
            sock.connect((common.HOST, common.PORT))
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
            except:
                print("\033[91m[ERREUR][coordinator] Échec de la désérialisation des objets\033[0m")

            # Détection des véhicules en approche de l'intersection
            # try: