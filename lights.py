import common

import time as t
import signal as sg

light_state = common.INIT_LIGHTS_STATE

# Création du gestionnaire de signaux pour SIGUSR1 (véhicule prioritaire)
def priority_handler(sig, frame):
    if sig == sg.SIGUSR1:
        common.PRIORITY_REQUEST = True
# Initialisation du gestionnaire de signaux SIGUSR1
sg.signal(sg.SIGUSR1, priority_handler)

# Création du gestionnaire de signaux pour SIGUSR2 (fin de passage)
def pass_handler(sig, frame):
    if sig == sg.SIGUSR2:
        common.PASS_COMPLETE = True
# Initialisation du gestionnaire de signaux SIGUSR2
sg.signal(sg.SIGUSR2, pass_handler)

ltime = t.time()

def lights(stop):
    while not stop.is_set():
        # Si un signal de véhicule prioritaire est reçu passer en mode prioritaire
        if common.PRIORITY_REQUEST:
            # Faire passer tous les feux au rouge
            common.north_light = 0
            common.east_light = 0
            common.south_light = 0
            common.west_light = 0
            # Récupérer la source du véhicule prioritaire
            rsrc = common.priority_queue.receive()
            src = rsrc.decode()
            if common.DEBUG:
                    print(f"\033[92m[DEBUG][lights] Signal du véhicule prioritaire reçu\033[0m")
            # Passer au vert le feu correspondant à la source du véhicule prioritaire
            if src == 'N':
                common.north_light = 1
            elif src == 'E':
                common.east_light = 1
            elif src == 'S':
                common.south_light = 1
            elif src == 'W':
                common.west_light = 1

            # On attend un signal de fin de passage du véhicule prioritaire pour reprendre le cycle normal
            while common.PASS_COMPLETE is False:
                pass
            common.PASS_COMPLETE = False
            if common.DEBUG:
                    print(f"\033[92m[DEBUG][lights] Le véhicule prioritaire a franchi l'intersection\033[0m")

            # On attend un certain temps après le passage du véhicule prioritaire
            t.sleep(common.AFTER_PRIORITY_DURATION)

            # On retourne au mode normal
            common.PRIORITY_REQUEST = False
            ltime = t.time()

            continue

        ctime = t.time()
        if (ctime - ltime) >= common.DEFAULT_LIGHT_DURATION:
            # On fait passer tous les feux au rouge pour une durée définie
            common.north_light = 0
            common.east_light = 0
            common.south_light = 0
            common.west_light = 0
            t.sleep(common.DURATION_BETWEEN_SWITCH)

            # On fait passer les feux au vert en alternance
            if light_state == 0:
                # Inverser l'état des feux
                common.north_light = 0
                common.south_light = 0
                common.east_light = 1
                common.west_light = 1
                light_state = 1
                if common.DEBUG:
                    print(f"\033[92m[DEBUG][lights] État des feux inversé\033[0m")
            elif light_state == 1:
                # Inverser l'état des feux
                common.north_light = 1
                common.south_light = 1
                common.east_light = 0
                common.west_light = 0
                light_state = 0
                if common.DEBUG:
                    print(f"\033[92m[DEBUG][lights] État des feux inversé\033[0m")

            t.sleep(0.1)

    print("[lights] Processus terminé")