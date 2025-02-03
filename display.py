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

def display_manager(stop, canvas):

    # Change la couleur des feux dans l'interface en fonction de l'état de ces derniers
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

    def draw_vehicle(canvas, x, y, color):
        canvas.create_rectangle(m.floor(x - vradius), m.floor(y - vradius), m.floor(x + vradius), m.floor(y + vradius), fill=color, outline='')

    # Lancement du serveur pour la réception des commandes du processus coordinator
    try:
        with so.socket(so.AF_INET, so.SOCK_STREAM) as server:
            server.bind((common.HOST, common.PORT))
            server.listen(1)
            client, addr = server.accept()
            with client:
                if common.DEBUG:
                    print(f"[DEBUG][display] Connexion établie avec {addr}")
                data = client.recv(1024)

                # Récupération des couleurs des feux
                ron = common.RED_ON
                roff = common.RED_OFF
                gon = common.GREEN_ON
                goff = common.GREEN_OFF
                yon = common.YELLOW_ON
                yoff = common.YELLOW_OFF

                # Calcul de la demi-taille des vehicules
                vradius = m.floor(common.VEHICLE_SIZE/2)

                while not stop.is_set():

                    # Mise à jour de l'état des feux - AFFICHAGE
                    north_light = common.north_light.value
                    east_light = common.east_light.value
                    south_light = common.south_light.value
                    west_light = common.west_light.value
                    # print(f'FEUX=[{north_light},{east_light},{south_light},{west_light}]')
                    # t.sleep(0.2)
                    try:
                        set_lights(canvas, north_light, east_light, south_light, west_light)
                    except:
                        print(f"\033[91m[ERREUR][display] Erreur lors de la modification des feux, arrêt du programme\033[0m")
                        stop.set()
                    
                    # Mise à jour de la position des véhicules - AFFICHAGE
                    try:
                        data = client.recv(1024)  # Recevoir les données du coordinateur
                        if data:
                            try:
                                debug_message = data.decode()
                                if debug_message:
                                    print(f"\033[92m[DEBUG][display] Message reçu: {debug_message}\033[0m")
                                try:
                                    vehicle_data = p.loads(data)
                                except:
                                    print(f"\033[91m[ERREUR][display] Échec de la désérialisation des données de position\033[0m")
                                x = int(vehicle_data[0])
                                y = int(vehicle_data[1])
                                color = vehicle_data[2]
                                draw_vehicle(canvas, x, y, color)  # Dessiner le véhicule sur le canvas
                            except:
                                print(f"\033[91m[ERREUR][display] Impossible de récupérer le message de test\033[0m")
                    except BlockingIOError:
                        pass # On passe si il n'y a aucune donnée à lire
                    except:
                        print(f"\033[91m[ERREUR][display] Erreur lors de la réception des données du coordinateur, arrêt du programme\033[0m")
                        stop.set()
                

        # sock = so.socket(so.AF_INET, so.SOCK_STREAM)
        # sock.setsockopt(so.SOL_SOCKET, so.SO_REUSEADDR, 1) # je ne sais pas trop ce que ça fait, à voir ce qu'on en fait
        # sock.bind((common.HOST, common.PORT))
        # sock.listen(1)
        # sock.setblocking(False)
        print(f"[display] Serveur lancé sur {common.HOST}:{common.PORT}")
    except:
        print(f"\033[91m[ERREUR][display] Impossible de lancer le serveur sur {common.HOST}:{common.PORT}, arrêt du programme\033[0m")
        stop.set()

    # while not stop.is_set():
    #     # Mise à jour de l'état des feux - AFFICHAGE
    #     north_light = common.north_light.value
    #     east_light = common.east_light.value
    #     south_light = common.south_light.value
    #     west_light = common.west_light.value
    #     try:
    #         set_lights(north_light, east_light, south_light, west_light)
    #     except:
    #         print(f"\033[91m[ERREUR][dissplay] Erreur lors de la modification des feux, arrêt du programme\033[0m")
    #         stop.set()
        
    #     # Mise à jour de la position des véhicules - AFFICHAGE
    #     try:
    #         data = sock.recv(1024)  # Recevoir les données du coordinateur
    #         if data:
    #             vehicle_data = data.decode()
    #             x = int(vehicle_data[0])
    #             y = int(vehicle_data[1])
    #             color = vehicle_data[2]
    #             draw_vehicle(x, y, color)  # Dessiner le véhicule sur le canvas
    #     except BlockingIOError:
    #         pass # On passe si il n'y a aucune donnée à lire
    #     # except:
    #     #     print(f"\033[91m[ERREUR][display] Erreur lors de la réception des données du coordinateur, arrêt du programme\033[0m")
    #     #     stop.set()
    
    server.close()
    client.close()
    if common.DEBUG:
        print("\033[92m[DEBUG][display] Serveur arrêté avec succès\033[0m")