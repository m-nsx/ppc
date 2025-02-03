# Génère un véhicule et l'ajoute à la liste des véhicules en circulation
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
        status = 0
        turn = common.turn(src, dst)
        
        vehicles.append = [id, priority, src, dst, x, y, color, status, turn]
        # 0=id, 1=priority, 2=src, 3=dst, 4=x, 5=y, 6=color, 7=status, 8=turn