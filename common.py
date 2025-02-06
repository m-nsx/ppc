import sysv_ipc as ipc
import multiprocessing as mp
import math as m

##################################################
#                                                #
#              PARAMÈTRES GÉNÉRAUX               #
#                                                #
##################################################

# DEBUG MODE
DEBUG = True

# SCRIPTS À ACTIVER
lights = 1
normal_traffic_gen = 1
priority_traffic_gen = 1
coordinator = 1
display = 1

##################################################
#                                                #
#          PARAMÈTRES DE LA SIMULATION           #
#                                                #
##################################################

# Défintion des constantes d'affichage
CANVAS_SIZE = 800
RED_ON = '#FF0000'
RED_OFF = '#440000'
GREEN_ON = '#00FF00'
GREEN_OFF = '#004400'
YELLOW_ON = '#FFFF00'
YELLOW_OFF = '#444400'

# Définition des constantes globales
DEFAULT_LIGHT_DURATION = 8
NORMAL_SPAWN_INTERVAL = 3
PRIORITY_SPAWN_INTERVAL = 20
AFTER_PRIORITY_DURATION = 3
DURATION_BETWEEN_SWITCH = 2
NORMAL_SPEED = 1 # attention ne doit pas être trop élevé (>5 = mauvaise idée !!!)
DIRECTIONS = ['N', 'E', 'S', 'W']

# Table de calcul des priorités ! NE PAS MODIFIER !
ORDER = ['right', 'straight', 'left']

# Constante d'initialisation des feux (0 = NS_GREEN, 1 = EW_GREEN)
INIT_LIGHTS_STATE = 0

# Variable globale pour le signalement d'un véhicule prioritaire (SIGUSR1)
PRIORITY_REQUEST = False
# Variable globale pour la fin du passage d'un véhicule prioritaire (SIGUSR2)
PASS_COMPLETE = False

# Décalage ligne d'arrêt
STOPLINE_OFFSET = 60 # valeur par défaut recommandée : 60

# Espacement des véhicules
VEHICULE_SPACING = 10

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

# Délai avant première tentative de connexion de coordinator à display
TIME_BEFORE_CONNECTION_ATTEMPT = 1

##################################################
#                                                #
#               PARAMÈTRES DE TEST               #
#                                                #
##################################################

# OBSERVATEUR DE VARIABLES
DEBUG_VARIABLES = False
# /!\ NE FONCTIONNE PAS POUR LE MOMENT /!\
# Ne pas passer à True

# MAX TOTAL VEHICLES
# Nombre total de véhicules pouvant être générés
MAX_TOTAL_VEHICLES = 1000

# ALWAYS GREEN
# Force tous les feux à rester au vert
ALWAYS_GREEN = False

##################################################
#                                                #
#     ! NE PAS MODIFIER LA PARTIE SUIVANTE !     #
#                                                #
##################################################

# Délai avant nouveau calcul de positions ! NE PAS MODIFIER !
COORDINATOR_DELAY = 0.01

# Stopline threshold
STOPLINE_THRESHOLD = 10

# Choix des processus à activer
PROCESS = [lights, normal_traffic_gen, priority_traffic_gen, coordinator, display]

# Définition de la taille des véhicules sur l'interface graphique
VEHICLE_SIZE = m.floor(CANVAS_SIZE * 0.03)

# Gestionnaire d'objets partagés
manager = mp.Manager()

# Lignes d'arrêt pour les véhicules
N_STOPLINE = CANVAS_SIZE / 2 - STOPLINE_OFFSET
E_STOPLINE = CANVAS_SIZE / 2 - STOPLINE_OFFSET
S_STOPLINE = CANVAS_SIZE / 2 + STOPLINE_OFFSET
W_STOPLINE = CANVAS_SIZE / 2 + STOPLINE_OFFSET

# Suppression d'éventuelles files résiduelles
for key in [NORTH_KEY, EAST_KEY, SOUTH_KEY, WEST_KEY, PRIORITY_KEY]:
    try:
        mq = ipc.MessageQueue(key)
        mq.remove()
        if DEBUG:
            print(f"[DEBUG][common] File de message avec la clé {key} supprimée")
    except ipc.ExistentialError:
        # La file n'existe pas, pas besoin de la supprimer
        pass

# Création de "message queues" (stockage de l'état des files d'attente)
try:
    north_queue = ipc.MessageQueue(NORTH_KEY, ipc.IPC_CREAT)
    east_queue = ipc.MessageQueue(EAST_KEY, ipc.IPC_CREAT)
    south_queue = ipc.MessageQueue(SOUTH_KEY, ipc.IPC_CREAT)
    west_queue = ipc.MessageQueue(WEST_KEY, ipc.IPC_CREAT)
    priority_queue = ipc.MessageQueue(PRIORITY_KEY, ipc.IPC_CREAT)
    if DEBUG:
        print("\033[92m[DEBUG][common] Les files 'message queue' ont été créées avec succès\033[0m")
except Exception as e:
    print(f"\033[91m[ERREUR][common] Erreur lors de la création des files 'message queue': {e}\033[0m")

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
    north_light = manager.Value('i', 1) # 1 = vert / 0 = rouge / 2 = orange
    east_light = manager.Value('i', 0)
    south_light = manager.Value('i', 1)
    west_light = manager.Value('i', 0)
    if DEBUG:
        print("\033[92m[DEBUG][common] Initialisation des feux dans l'état NS_GREEN\033[0m")
elif INIT_LIGHTS_STATE == 1:
    north_light = manager.Value('i', 0)
    east_light = manager.Value('i', 1)
    south_light = manager.Value('i', 0)
    west_light = manager.Value('i', 1)
    if DEBUG:
        print("\033[92m[DEBUG][common] Initialisation des feux dans l'état EW_GREEN\033[0m")
else:
    print("\033[91m[ERREUR][common] Erreur lors de l'initialisation de l'état des feux\033[0m")

# Définition de la classe Vehicle
class Vehicle(object):
    def __init__(self, id, priority, src, dst, x, y, turn):
        self.id = id
        self.priority = priority
        self.src = src
        self.dst = dst
        self.x = x
        self.y = y
        self.ax = x
        self.ay = y
        self.angle = 0
        self.turn = turn
        self.status = 0
    # NOMENCLATURE ATTRIBUT status
    # 0 = en attente de passage à l'intersection
    # 1 = en cours de passage (virage à droite)
    # 2 = en cours de passage (tout droit)
    # 3 = en cours de passage (virage à gauche)
    # 4 = passage terminé

    def __delete__(self):
        del self

    def get_info(self):
        return f"ID:{self.id},PRIORITY:{self.priority},ROUTE:{self.src}→{self.dst},CURRENT_POS:({self.x};{self.y},TURN:{self.turn},STATUS:{self.status})"