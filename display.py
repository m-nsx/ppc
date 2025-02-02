import common

import multiprocessing as mp
import socket as so
import time as t
import random as r
import tkinter as tk
import math as m

def display(stop):
    # Lancement du serveur pour la réception des commandes du processus coordinator
    # sock = so.socket(so.AF_INET, so.SOCK_STREAM)
    # sock.setsockopt(so.SOL_SOCKET, so.SO_REUSEADDR, 1) # je ne sais pas trop ce que ça fait, à voir ce qu'on en fait
    # sock.bind((common.HOST, common.PORT))
    # sock.listen(1)
    # sock.setblocking(False)
    # print(f"[display] Serveur lancé sur {common.HOST}:{common.PORT}")

    # Récupération de la taille de la fenêtre
    size = common.CANVAS_SIZE
    # Calcul de la demi-taille des vehicules
    vradius = m.floor(common.VEHICLE_SIZE/2)

    # Récupération des couleurs des feux
    ron = common.RED_ON
    roff = common.RED_OFF
    gon = common.GREEN_ON
    goff = common.GREEN_OFF
    yon = common.YELLOW_ON
    yoff = common.YELLOW_OFF

    # Création d'un dictionnaire pour les véhicules
    vehicles = {}

    # Récupération de l'état des feux
    north_light = common.north_light.value
    east_light = common.east_light.value
    south_light = common.south_light.value
    west_light = common.west_light.value
    if common.DEBUG:
        print(f"\033[92m[DEBUG][display] État des feux récupéré, N={north_light} E={east_light} S={south_light} W={west_light}\033[0m")
    
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

    # Change la couleur des feux dans l'interface en fonction de l'état de ces derniers
    def set_lights(north, east, south, west):
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

    # Crée un véhicule sur le canvas
    def summon_vehicle(vehicle):
        id = vehicle.id
        priority = vehicle.priority
        src = vehicle.src
        dst = vehicle.dst
        x = vehicle.x
        y = vehicle.y
        color = 'blue'
        if priority == 1:
            color = 'red'
        
        # Crée le véhicule sur le canvas
        display_id = canvas.create_rectangle(m.floor(x - vradius), m.floor(y - vradius), m.floor(x + vradius), m.floor(y + vradius), fill=color, outline='')

        # Ajoute le véhicule au dictionnaire des véhicules présents sur le canvas
        vehicles[id] = {
            'priority': priority,
            'src': src,
            'dst': dst,
            'x': x,
            'y': y,
            'status': 0, # 0 = avant le passage de l'intersection / 1 = après le passage de l'intersection
            'display_id': display_id
        }

    # def movement_update(vehicles):
    #     # Initialisation de la liste des véhicules à retirer du canvas
    #     destroy = []

    #     # Récupération de tous les véhicules présents sur le canvas et mise à jour de leur position
    #     for id, info in vehicules.items()
        

    # initialiser les feux
    try:
        set_lights(north_light, east_light, south_light, west_light)
    except:
        print("\033[91m[ERREUR][display] Erreur lors du chargement de la configuration des feux\033[0m")

    # Bouton de sortie du programme
    def exit():
        stop.set()
        root.destroy()
        print("[display] Processus terminé")

    exit_button = tk.Button(root, text="Quitter le programme", command=exit)
    exit_button.pack(pady=10, padx=10)

    root.mainloop()