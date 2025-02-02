import sysv_ipc as ipc
import multiprocessing as mp
import math as m

##################################################
#                                                #
#          PARAMÈTRES DE LA SIMULATION           #
#                                                #
##################################################

# DEBUG MODE
DEBUG = True

# Défintion des constantes d'affichage
CANVAS_SIZE = 800
RED_ON = '#FF0000'
RED_OFF = '#440000'
GREEN_ON = '#00FF00'
GREEN_OFF = '#004400'
YELLOW_ON = '#FFFF00'
YELLOW_OFF = '#444400'

# Définition des constantes globales
DEFAULT_LIGHT_DURATION = 3
NORMAL_SPAWN_INTERVAL = 2
PRIORITY_SPAWN_INTERVAL = 8
AFTER_PRIORITY_DURATION = 1
DURATION_BETWEEN_SWITCH = 1
NORMAL_SPEED = 1
PRIORITY_SPEED = 3
DIRECTIONS = ['N', 'E', 'S', 'W']

# Constante d'initialisation des feux (0 = NS_GREEN, 1 = EW_GREEN)
INIT_LIGHTS_STATE = 0

# Variable globale pour le signalement d'un véhicule prioritaire (SIGUSR1)
PRIORITY_REQUEST = False
# Variable globale pour la fin du passage d'un véhicule prioritaire (SIGUSR2)
PASS_COMPLETE = False

# Initialisation des PID des processus pour l'envoi de signaux
LIGHTS_PID = 0

# CLÉ POUR CHAQUE QUEUE MESSAGE PASSING
NORTH_KEY = 1
EAST_KEY = 2
SOUTH_KEY = 3
WEST_KEY = 4
PRIORITY_KEY = 5

# Adresse et port pour l'utilisation du processus display
HOST = '127.0.0.1'
PORT = 9999

##################################################
#                                                #
#     ! NE PAS MODIFIER LA PARTIE SUIVANTE !     #
#                                                #
##################################################

# Définition de la taille des véhicules sur l'interface graphique
VEHICLE_SIZE = m.floor(CANVAS_SIZE * 0.03)

# Création de "message queues" (stockage de l'état des files d'attente)
try:
    north_queue = ipc.MessageQueue(NORTH_KEY, ipc.IPC_CREAT)
    east_queue = ipc.MessageQueue(EAST_KEY, ipc.IPC_CREAT)
    south_queue = ipc.MessageQueue(SOUTH_KEY, ipc.IPC_CREAT)
    west_queue = ipc.MessageQueue(WEST_KEY, ipc.IPC_CREAT)
    priority_queue = ipc.MessageQueue(PRIORITY_KEY, ipc.IPC_CREAT)
    if DEBUG:
        print("\033[92m[DEBUG][common] Les files 'message queue' ont été créées avec succès\033[0m")
except:
    print("\033[91m[ERREUR][common] Erreur lors de la création des files 'message queue'\033[0m")

# Retourne le type de virage en fonction des directions source et destination
def turn(src, dst):
    if src == 'N':
        if dst == 'E':
            return 'right'
        elif dst == 'W':
            return 'left'
        elif dst == 'S':
            return 'straight'
    elif src == 'E':
        if dst == 'S':
            return 'right'
        elif dst == 'N':
            return 'left'
        elif dst == 'W':
            return 'straight'
    elif src == 'S':
        if dst == 'W':
            return 'right'
        elif dst == 'E':
            return 'left'
        elif dst == 'N':
            return 'straight'
    elif src == 'W':
        if dst == 'N':
            return 'right'
        elif dst == 'S':
            return 'left'
        elif dst == 'E':
            return 'straight'

# Création et initialisation de variables "shared memory" (stockage de l'état des feux)
if INIT_LIGHTS_STATE == 0:
    north_light = mp.Value('i', 1) # 1 = vert / 0 = rouge / 2 = orange
    east_light = mp.Value('i', 0)
    south_light = mp.Value('i', 1)
    west_light = mp.Value('i', 0)
    if DEBUG:
        print("\033[92m[DEBUG][common] Initialisation des feux dans l'état NS_GREEN\033[0m")
elif INIT_LIGHTS_STATE == 1:
    north_light = mp.Value('i', 0)
    east_light = mp.Value('i', 1)
    south_light = mp.Value('i', 0)
    west_light = mp.Value('i', 1)
    if DEBUG:
        print("\033[92m[DEBUG][common] Initialisation des feux dans l'état EW_GREEN\033[0m")
else:
    print("\033[91m[ERREUR][common] Erreur lors de l'initialisation de l'état des feux\033[0m")

# Définition de la classe Vehicle
class Vehicle(object):
    def __init__(self, id, priority, src, dst, x, y):
        self.id = id
        self.priority = priority
        self.src = src
        self.dst = dst
        self.x = x
        self.y = y

    def get_info(self):
        return f"ID:{self.id},PRIORITY:{self.priority},ROUTE:{self.src}→{self.dst},CURRENT_POS:({self.x};{self.y})"