# **Projet PPC - *programmation parallèle et concurrente***

### **Bibliothèques python requises pour lancer le projet**
- **multiprocessing :** *gestion des processus*
- **sysv_ipc :** *protocoles de communication entre les différentes processus*
- **tkinter :** *affichage de l'interface utilisateur*
- **pickle :** *sérialisation des objets python*

---

### **I. Lancer le projet sur Linux**

1. Installez les bibliothèques nécessaires
```
pip install multiprocessing
pip install sysv-ipc
pip install tkinter
pip install pickle
``` 

2. Lancez le projet (depuis le dossier racine)
```
python3 main.py
```

### **II. Lancer le projet sur WSL**

1. Créez un environnement virtuel pour l'installation des bilbiothèques non disponibles sur Windows (depuis le dossier racine), remplacez `<name>` par le nom de votre environnement virtuel
```
python3 -m venv <name>
```

2. Activez votre environnement virtuel (depuis le contenant le dossier de votre environnement virtuel)
```
source <name>/bin/activate
```

3. Installez les bibliothèques nécessaires dans votre environnement virtuel
```
pip install multiprocessing
pip install sysv-ipc
pip install tkinter
pip install pickle
```

4. Lancez le projet (depuis le dossier racine)
```
python3 main.py
```

### **III. Résolution des problèmes**

**Q. Le programme ne se lance pas**
```
R. Essayez de modifier les valeurs de la liste process du fichier main.py à 1
R. Vérifiez que vous avez bien installé toutes le bibliothèques requises
```

**Q. Le programme s'arrête et je ne trouve pas la cause de cet arrêt / Le programme m'indique une erreur inattendue et s'arrête**
```
R. Passez la variable DEBUG à True dans le fichier common.py, cela forcera l'affichage d'informations utiles au debug dans la console
```

**Q. Le programme fonctionne mais l'interface ne fonctionne pas / n'est pas mise à jour**
```
R. Vérifiez que l'adresse du socket définie dans le fichier common.py est valide et que le port sélectionné n'est pas déjà en cours d'utilisation
```

**Q. Je n'arrive pas à installer sysv_ipc (ou une autre bibliothèque)**
```
R. Si vous êtes sous Windows utilisez WSL, si vous l'utilisiez déjà il est probable que vous n'ayez pas créé d'environnement virtuel (sysv_ipc n'est disponible que pour les systèmes "UNIX-like")
R. Vérifiez que vous avez installé python sur votre machine
R. Vérifiez que votre version de pip est à jour
```