import common

import pickle as p

import threading as th
import multiprocessing as mp
import socket as so
import time as t
import random as r
import tkinter as tk
import math as m

# PROCESSUS DISPLAY
# Le processus display est responsable de l'affichage de l'interface graphique
# Il crée également un thread display_manager chargé de la mise à jour des feux et véhicules présents sur le canvas

def display(stop):

    # Récupération de la taille de la fenêtre
    size = common.CANVAS_SIZE

    ron = common.RED_ON
    gon = common.GREEN_ON
    yoff = common.YELLOW_OFF
    
    # Création de la fenêtre Tkinter
    root = tk.Tk()
    root.title("🚦 Simulation d'intersection 🚦")

    # Création du canvas d'affichage principal
    canvas = tk.Canvas(root, width=size, height=size, bg='lightgray')
    canvas.pack()

    # FOND INTERFACE GRAPHIQUE
    # Routes
    canvas.create_rectangle(m.floor(size/2 - size*0.05), 0, m.floor(size/2 + size*0.05), size, fill='gray', outline='') # axe nord-sud
    canvas.create_rectangle(0, m.floor(size/2 - size*0.05), size, m.floor(size/2 + size*0.05), fill='gray', outline='') # axe est-ouest
    # Marquages au sol
    canvas.create_rectangle(m.floor(size/2 - size*0.005), 0, m.floor(size/2 + size*0.005), size, fill='white', outline='') # axe nord-sud
    canvas.create_rectangle(0, m.floor(size/2 - size*0.005), size, m.floor(size/2 + size*0.005), fill='white', outline='') # axe est-ouest
    canvas.create_rectangle(m.floor(size/2 - size*0.05), m.floor(size/2 - size*0.05), m.floor(size/2 + size*0.05), m.floor(size/2 + size*0.05), fill='gray', outline='') # carré central

    global tlnr, tlny, tlng, tler, tley, tleg, tlsr, tlsy, tlsg, tlwr, tlwy, tlwg

    # FEUX
    # Feu nord
    tln = canvas.create_rectangle(m.floor(size/2 - size*0.1), m.floor(size/2 - size*0.16), m.floor(size/2 - size*0.06), m.floor(size/2 - size*0.06), fill='black', outline='')
    tlnr = canvas.create_oval(m.floor(size/2 - size*0.09), m.floor(size/2 - size*0.09), m.floor(size/2 - size*0.07), m.floor(size/2 - size*0.07), fill=ron, outline='')
    tlny = canvas.create_oval(m.floor(size/2 - size*0.09), m.floor(size/2 - size*0.12), m.floor(size/2 - size*0.07), m.floor(size/2 - size*0.1), fill=yoff, outline='')
    tlng = canvas.create_oval(m.floor(size/2 - size*0.09), m.floor(size/2 - size*0.15), m.floor(size/2 - size*0.07), m.floor(size/2 - size*0.13), fill=gon, outline='')
    # Feu est
    tle = canvas.create_rectangle(m.floor(size/2 - size*0.16), m.floor(size/2 + size*0.06), m.floor(size/2 - size*0.06), m.floor(size/2 + size*0.1), fill='black', outline='')
    tler = canvas.create_oval(m.floor(size/2 - size*0.09), m.floor(size/2 + size*0.07), m.floor(size/2 - size*0.07), m.floor(size/2 + size*0.09), fill=ron, outline='')
    tley = canvas.create_oval(m.floor(size/2 - size*0.12), m.floor(size/2 + size*0.07), m.floor(size/2 - size*0.1), m.floor(size/2 + size*0.09), fill=yoff, outline='')
    tleg = canvas.create_oval(m.floor(size/2 - size*0.15), m.floor(size/2 + size*0.07), m.floor(size/2 - size*0.13), m.floor(size/2 + size*0.09), fill=gon, outline='')
    # Feu sud
    tls = canvas.create_rectangle(m.floor(size/2 + size*0.06), m.floor(size/2 + size*0.06), m.floor(size/2 + size*0.1), m.floor(size/2 + size*0.16), fill='black', outline='')
    tlsr = canvas.create_oval(m.floor(size/2 + size*0.07), m.floor(size/2 + size*0.07), m.floor(size/2 + size*0.09), m.floor(size/2 + size*0.09), fill=ron, outline='')
    tlsy = canvas.create_oval(m.floor(size/2 + size*0.07), m.floor(size/2 + size*0.1), m.floor(size/2 + size*0.09), m.floor(size/2 + size*0.12), fill=yoff, outline='')
    tlsg = canvas.create_oval(m.floor(size/2 + size*0.07), m.floor(size/2 + size*0.13), m.floor(size/2 + size*0.09), m.floor(size/2 + size*0.15), fill=gon, outline='')
    # Feu ouest
    tlw = canvas.create_rectangle(m.floor(size/2 + size*0.06), m.floor(size/2 - size*0.1), m.floor(size/2 + size*0.16), m.floor(size/2 - size*0.06), fill='black', outline='')
    tlwr = canvas.create_oval(m.floor(size/2 + size*0.07), m.floor(size/2 - size*0.09), m.floor(size/2 + size*0.09), m.floor(size/2 - size*0.07), fill=ron, outline='')
    tlwy = canvas.create_oval(m.floor(size/2 + size*0.1), m.floor(size/2 - size*0.09), m.floor(size/2 + size*0.12), m.floor(size/2 - size*0.07), fill=yoff, outline='')
    tlwg = canvas.create_oval(m.floor(size/2 + size*0.13), m.floor(size/2 - size*0.09), m.floor(size/2 + size*0.15), m.floor(size/2 - size*0.07), fill=gon, outline='')

    # Bouton de sortie du programme
    def exit():
        stop.set()
        root.destroy()
        print("[display] Processus terminé")

    exit_button = tk.Button(root, text="Quitter le programme", command=exit)
    exit_button.pack(pady=10, padx=10)

    # Lance le thread display_manager en charge de l'affichage des feux et des véhicules
    # On choisi ici thread plutôt que de lancer un processus supplémentaire car multiprocessing ne fonctionne pas bien avec Tkinter
    # Le paramètre daemon=True permet de terminer automatiquement le thread lorsque le processus principal se termine (en l'occurence le processus display)
    t_display_manager = th.Thread(target=display_manager, args=(stop, canvas,), daemon=True)
    t_display_manager.start()

    root.mainloop()

def recvall(sock, n):
    """
    Lit exactement n octets depuis le socket ou retourne None si la connexion est fermée.
    """
    data = b''
    while len(data) < n:
        packet = sock.recv(n - len(data))
        if not packet:
            return None
        data += packet
    return data

def recv_msg(sock):
    """
    Lit un message complet envoyé avec send_msg (un en‐tête de 4 octets indiquant la taille, puis le message).
    """
    header = recvall(sock, 4)
    if header is None:
        return None
    msg_len = int.from_bytes(header, byteorder='big')
    return recvall(sock, msg_len)


def display_manager(stop, canvas):

    # Fonction locale pour mettre à jour les feux dans le canvas
    def set_lights(canvas, north, east, south, west):
        if north == 1:
            canvas.itemconfig(tlnr, fill=roff)
            canvas.itemconfig(tlny, fill=yoff)
            canvas.itemconfig(tlng, fill=gon)
        if east == 1:
            canvas.itemconfig(tler, fill=roff)
            canvas.itemconfig(tley, fill=yoff)
            canvas.itemconfig(tleg, fill=gon)
        if south == 1:
            canvas.itemconfig(tlsr, fill=roff)
            canvas.itemconfig(tlsy, fill=yoff)
            canvas.itemconfig(tlsg, fill=gon)
        if west == 1:
            canvas.itemconfig(tlwr, fill=roff)
            canvas.itemconfig(tlwy, fill=yoff)
            canvas.itemconfig(tlwg, fill=gon)
        if north == 0:
            canvas.itemconfig(tlnr, fill=ron)
            canvas.itemconfig(tlny, fill=yoff)
            canvas.itemconfig(tlng, fill=goff)
        if east == 0:
            canvas.itemconfig(tler, fill=ron)
            canvas.itemconfig(tley, fill=yoff)
            canvas.itemconfig(tleg, fill=goff)
        if south == 0:
            canvas.itemconfig(tlsr, fill=ron)
            canvas.itemconfig(tlsy, fill=yoff)
            canvas.itemconfig(tlsg, fill=goff)
        if west == 0:
            canvas.itemconfig(tlwr, fill=ron)
            canvas.itemconfig(tlwy, fill=yoff)
            canvas.itemconfig(tlwg, fill=goff)
        if north == 2:
            canvas.itemconfig(tlnr, fill=roff)
            canvas.itemconfig(tlny, fill=yon)
            canvas.itemconfig(tlng, fill=goff)
        if east == 2:
            canvas.itemconfig(tler, fill=roff)
            canvas.itemconfig(tley, fill=yon)
            canvas.itemconfig(tleg, fill=goff)
        if south == 2: 
            canvas.itemconfig(tlsr, fill=roff)
            canvas.itemconfig(tlsy, fill=yon)
            canvas.itemconfig(tlsg, fill=goff)
        if west == 2:
            canvas.itemconfig(tlwr, fill=roff)
            canvas.itemconfig(tlwy, fill=yon)
            canvas.itemconfig(tlwg, fill=goff)

    # Fonction locale pour dessiner un véhicule sur le canvas
    def draw_vehicle(canvas, x, y, color, extension):
        vradius = m.floor(common.VEHICLE_SIZE/2) + extension
        canvas.create_rectangle(m.floor(x - vradius), m.floor(y - vradius),
                                m.floor(x + vradius), m.floor(y + vradius),
                                fill=color, outline='')

    # Lancement du serveur socket pour recevoir les messages du coordinator
    try:
        with so.socket(so.AF_INET, so.SOCK_STREAM) as server:
            server.setsockopt(so.SOL_SOCKET, so.SO_REUSEADDR, 1)
            server.bind((common.HOST, common.PORT))
            server.listen(1)
            client, addr = server.accept()
            with client:
                if common.DEBUG:
                    print(f"\033[92m[DEBUG][display] Connexion établie avec {addr}\033[0m")

                # Récupération des constantes de couleurs pour les feux
                ron = common.RED_ON
                roff = common.RED_OFF
                gon = common.GREEN_ON
                goff = common.GREEN_OFF
                yon = common.YELLOW_ON
                yoff = common.YELLOW_OFF

                while not stop.is_set():
                    # Mise à jour de l'état des feux à partir de la mémoire partagée
                    try:
                        north_light = common.north_light.value
                        east_light  = common.east_light.value
                        south_light = common.south_light.value
                        west_light  = common.west_light.value
                        set_lights(canvas, north_light, east_light, south_light, west_light)
                    except Exception as e:
                        print(f"\033[91m[ERREUR][display] Erreur lors de la modification des feux: {e}\033[0m")
                        stop.set()

                    # Lecture d'un message complet en provenance du coordinator
                    try:
                        vehicle_data_bytes = recv_msg(client)
                        if vehicle_data_bytes is None:
                            # La connexion a été fermée, on sort de la boucle
                            break

                        try:
                            vehicle_data = p.loads(vehicle_data_bytes)
                            # On attend un message contenant au moins 5 éléments : x, y, color, id, extension
                            if isinstance(vehicle_data, (list, tuple)) and len(vehicle_data) >= 5:
                                x, y, color, vid, extension = vehicle_data[:5]
                                draw_vehicle(canvas, x, y, color, extension)
                        except Exception as e:
                            print(f"\033[91m[ERREUR][display] Problème lors de la désérialisation : {e}\033[0m")
                    except Exception as e:
                        print(f"\033[91m[ERREUR][display] Erreur lors de la réception des données: {e}\033[0m")
                        stop.set()

                    canvas.update()
    except Exception as e:
        print(f"\033[91m[ERREUR][display] Impossible de lancer le serveur sur {common.HOST}:{common.PORT}: {e}\033[0m")
        stop.set()

    print(f"[display] Serveur arrêté")
    # Aucun shutdown ou close supplémentaire n'est nécessaire, le 'with' s'en charge.
    if common.DEBUG:
        print("\033[92m[DEBUG][display] Serveur arrêté avec succès\033[0m")
