import common

import time as t
import signal as sg
import random as rd

# Création du gestionnaire de signaux pour SIGINT (véhicule prioritaire)
def priority_handler(sig, frame):
    if sig == sg.SIGINT:
        common.PRIORITY_REQUEST = True
# Initialisation du gestionnaire de signaux SIGINT
sg.signal(sg.SIGINT, priority_handler)

# Création du gestionnaire de signaux pour SIGTERM (fin de passage)
def pass_handler(sig, frame):
    if sig == sg.SIGTERM:
        common.PASS_COMPLETE = True
# Initialisation du gestionnaire de signaux SIGTERM
sg.signal(sg.SIGTERM, pass_handler)

# PROCESSUS LIGHTS
# Le processus lights est responsable de la gestion des feux de circulation
# En mode normal il alterne à intervalles réguliers entre les deux états possibles, vert pour l'axe nord-sud ou pour l'axe est-ouest
# Ce processus est également capable de passer en mode prioritaire lorsqu'il reçoit un signal de priority_traffic_gen
# Dans ce cas, tous les feux passent au rouge sauf celui correspondant à la source du véhicule prioritaire
# Une fois le véhicule prioritaire passé, le processus lights retourne en mode normal

def lights(stop):

    light_state = common.INIT_LIGHTS_STATE
    ltime = t.time()

    if common.ALWAYS_GREEN:
        while True:
            common.north_light.value = 1
            common.east_light.value = 1
            common.south_light.value = 1
            common.west_light.value = 1

    while not stop.is_set():
        # Si un signal de véhicule prioritaire est reçu passer en mode prioritaire
        if common.PRIORITY_REQUEST:
            # Faire passer tous les feux au rouge
            common.north_light.value = 0
            common.east_light.value = 0
            common.south_light.value = 0
            common.west_light.value = 0
            # Récupérer la source du véhicule prioritaire
            rsrc, _ = common.priority_queue.receive()
            src = rsrc.decode()
            if common.DEBUG:
                    print(f"\033[92m[DEBUG][lights] Signal du véhicule prioritaire reçu, priorité à donner à {src}\033[0m")
            # Passer au vert le feu correspondant à la source du véhicule prioritaire
            if src == 'N':
                common.north_light.value = 1
            elif src == 'E':
                common.east_light.value = 1
            elif src == 'S':
                common.south_light.value = 1
            elif src == 'W':
                common.west_light.value = 1

            # On attend un signal de fin de passage du véhicule prioritaire pour reprendre le cycle normal
            while common.PASS_COMPLETE is False:
                t.sleep(0.01)
            common.PASS_COMPLETE = False
            if common.DEBUG:
                    print(f"\033[92m[DEBUG][lights] Le véhicule prioritaire a franchi l'intersection\033[0m")

            # On attend un certain temps après le passage du véhicule prioritaire
            t.sleep(common.AFTER_PRIORITY_DURATION/2)

            # On retourne au mode normal
            common.PRIORITY_REQUEST = False
            ltime = t.time()

            alea = rd.randint(0, 1)

            if src == 'N' and alea == 1:
                common.north_light.value = 2
            elif src == 'E' and alea == 0:
                common.east_light.value = 2
            elif src == 'S' and alea == 1:
                common.south_light.value = 2
            elif src == 'W' and alea == 0:
                common.west_light.value = 2

            if alea == 0:
                t.sleep(common.AFTER_PRIORITY_DURATION/2)
                light_state = 0
                common.north_light.value = 1
                common.east_light.value = 0
                common.south_light.value = 1
                common.west_light.value = 0
            elif alea == 1:
                t.sleep(common.AFTER_PRIORITY_DURATION/2)
                light_state = 1
                common.north_light.value = 0
                common.east_light.value = 1
                common.south_light.value = 0
                common.west_light.value = 1

            continue

        ctime = t.time()
        if (ctime - ltime) >= common.DEFAULT_LIGHT_DURATION:
            ltime = t.time()
            # On fait passer les feux de vert à orange
            if light_state == 0:
                common.north_light.value = 2
                common.east_light.value = 0
                common.south_light.value = 2
                common.west_light.value = 0
            elif light_state == 1:
                common.north_light.value = 0
                common.east_light.value = 2
                common.south_light.value = 0
                common.west_light.value = 2
            t.sleep(common.DURATION_BETWEEN_SWITCH/2)
            # On fait passer tous les feux au rouge
            common.north_light.value = 0
            common.east_light.value = 0
            common.south_light.value = 0
            common.west_light.value = 0
            t.sleep(common.DURATION_BETWEEN_SWITCH/2)


            # On fait passer les feux au vert en alternance
            if light_state == 0:
                # Inverser l'état des feux
                common.north_light.value = 0
                common.east_light.value = 1
                common.south_light.value = 0
                common.west_light.value = 1
                light_state = 1
                if common.DEBUG:
                    print(f"\033[92m[DEBUG][lights] État des feux inversé\033[0m")
                    print(f"\033[92m[DEBUG][lights] État des feux récupéré, N={common.north_light.value} E={common.east_light.value} S={common.south_light.value} W={common.west_light.value}\033[0m")
            elif light_state == 1:
                # Inverser l'état des feux
                common.north_light.value = 1
                common.east_light.value = 0
                common.south_light.value = 1
                common.west_light.value = 0
                light_state = 0
                if common.DEBUG:
                    print(f"\033[92m[DEBUG][lights] État des feux inversé\033[0m")
                    print(f"\033[92m[DEBUG][lights] État des feux récupéré, N={common.north_light.value} E={common.east_light.value} S={common.south_light.value} W={common.west_light.value}\033[0m")

            t.sleep(0.1)

    print("[lights] Processus terminé")