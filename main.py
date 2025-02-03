# Importe le module common afin de pouvoir utiliser la classe Vehicle
import common
# Importe le module multiprocessing pour utiliser les threads et méthodes de partage de données
import multiprocessing as mp
# Importe le module sysv_ipc pour utiliser les méthodes IPC
import sysv_ipc as ipc

process = common.PROCESS

# Importe les différents modules nécessaires ainsi que leurs processus en fonction de la variable process
if process[0] == 1:
    import lights as l
if process[1] == 1:
    import normal_traffic_gen as ntg
if process[2] == 1:
    import priority_traffic_gen as ptg
if process[3] == 1:
    import coordinator as c
if process[4] == 1:
    import display as d
if common.DEBUG_VARIABLES:
    import variables as v
# Importe les modules time, random et math
import time as t
import random as r
import math as m

def main():

    # Création d'un évènement déclenchable pour arrêter les processus
    stop = mp.Event()

    # Création et lancement des cinq processus

    # 1. Processus de gestion des feux
    if process[0] == 1:
        try:
            p_lights = mp.Process(target=l.lights, args=(stop,), name="lights")
            p_lights.start()
            try:
                common.LIGHTS_PID = p_lights.pid
            except:
                print("\033[91m[ERREUR][main] Échec de la récupération du PID du processus lights\033[0m")
        except:
            print("\033[91m[ERREUR][main] Échec de la création du processus lights\033[0m")

    # 2. Procesus de génération de trafic normal
    if process[1] == 1:
        try:
            p_ntg = mp.Process(target=ntg.normal_traffic_gen, args=(stop,), name="normal_traffic_gen")
            p_ntg.start()
        except:
            print("\033[91m[ERREUR][main] Échec de la création du processus normal_traffic_gen\033[0m")

    # 3. Procesus de génération de trafic prioritaire
    if process[2] == 1:
        try:
            p_ptg = mp.Process(target=ptg.priority_traffic_gen, args=(stop,), name="priority_traffic_gen")
            p_ptg.start()
        except:
            print("\033[91m[ERREUR][main] Échec de la création du processus priority_traffic_gen\033[0m")

    # 4. Processus de calcul des priorités et de l'ordre de passage
    if process[3] == 1:
        try:
            p_coordinator = mp.Process(target=c.coordinator, args=(stop,), name="coordinator")
            p_coordinator.start()
        except:
            print("\033[91m[ERREUR][main] Échec de la création du processus coordinator\033[0m")

    # 5. Processus d'affichage
    if process[4] == 1:
        try:
            p_display = mp.Process(target=d.display, args=(stop,), name="display")
            p_display.start()
        except:
            print("\033[91m[ERREUR][main] Échec de la création du processus display\033[0m")

    # Observateur de variables
    if common.DEBUG_VARIABLES:
        try:
            p_variables = mp.Process(target=v.variables, args=(stop,), name="variables")
            p_variables.start()
        except:
            print("\033[91m[ERREUR][main] Échec de la création du processus variables\033[0m")

    try:
        while True:
            if stop.is_set():
                break
            t.sleep(1)
    except KeyboardInterrupt:
        print("[main] Programme interrompu")
    finally:
        # On supprime les message queues
        common.north_queue.remove()
        common.east_queue.remove()
        common.south_queue.remove()
        common.west_queue.remove()
        common.priority_queue.remove()
        # On arrête tous les processus
        stop.set()
        print("[main] Arrêt du programme")

if __name__ == "__main__":
    main()