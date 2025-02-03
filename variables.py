import common
import tkinter as tk
import threading as th
import time as t

def variables(stop):

    root = tk.Tk()
    root.title("[DEBUG] Observateur de variables")

    # Labels
    label_north_light = tk.Label(root, text="north_light")
    label_north_light.grid(row=0, column=0)
    label_east_light = tk.Label(root, text="east_light")
    label_east_light.grid(row=1, column=0)
    label_south_light = tk.Label(root, text="south_light")
    label_south_light.grid(row=2, column=0)
    label_west_light = tk.Label(root, text="west_light")
    label_west_light.grid(row=3, column=0)

    label_queue_north = tk.Label(root, text="north_queue")
    label_queue_north.grid(row=4, column=0)
    label_queue_east = tk.Label(root, text="east_queue")
    label_queue_east.grid(row=5, column=0)
    label_queue_south = tk.Label(root, text="south_queue")
    label_queue_south.grid(row=6, column=0)
    label_queue_west = tk.Label(root, text="west_queue")
    label_queue_west.grid(row=7, column=0)

    # Variables
    var_north_light = tk.StringVar()
    var_east_light = tk.StringVar()
    var_south_light = tk.StringVar()
    var_west_light = tk.StringVar()

    var_queue_north = tk.StringVar()
    var_queue_east = tk.StringVar()
    var_queue_south = tk.StringVar()
    var_queue_west = tk.StringVar()

    # Fonction de mise à jour des variables
    def update_variables():
        var_north_light.set(common.north_light.value)
        var_east_light.set(common.east_light.value)
        var_south_light.set(common.south_light.value)
        var_west_light.set(common.west_light.value)

        var_queue_north.set(common.north_queue.get())
        var_queue_east.set(common.east_queue.get())
        var_queue_south.set(common.south_queue.get())
        var_queue_west.set(common.west_queue.get())

        # Appeler à nouveau cette fonction après 100 ms
        root.after(100, update_variables)

    # Affichage des variables
    entry_north_light = tk.Entry(root, textvariable=var_north_light)
    entry_north_light.grid(row=0, column=1)
    entry_east_light = tk.Entry(root, textvariable=var_east_light)
    entry_east_light.grid(row=1, column=1)
    entry_south_light = tk.Entry(root, textvariable=var_south_light)
    entry_south_light.grid(row=2, column=1)
    entry_west_light = tk.Entry(root, textvariable=var_west_light)
    entry_west_light.grid(row=3, column=1)

    entry_queue_north = tk.Entry(root, textvariable=var_queue_north)
    entry_queue_north.grid(row=4, column=1)
    entry_queue_east = tk.Entry(root, textvariable=var_queue_east)
    entry_queue_east.grid(row=5, column=1)
    entry_queue_south = tk.Entry(root, textvariable=var_queue_south)
    entry_queue_south.grid(row=6, column=1)
    entry_queue_west = tk.Entry(root, textvariable=var_queue_west)
    entry_queue_west.grid(row=7, column=1)

    # Démarrer la mise à jour en temps réel
    update_variables()

    root.mainloop()