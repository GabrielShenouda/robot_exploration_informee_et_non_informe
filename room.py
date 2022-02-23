"""
8INF846-01 - Intelligence artificielle - Hiver 2022

Travail Pratique #1 - Résolution par l’exploration (description)

Groupe 01 : Marcelo Vasconcellos / Gabriel Shenouda / Matthis Villeneuve / Yann Reynaud
"""

from node import Node


class Room:

    def __init__(self):
        self.quant_y = 5
        self.quant_x = 5
        self.matrix = {}
        self.dict = {}
        self.tree = {}
        self.create_tree()


    # Création de la salle de taille définie dans __init__ comme quant_x et quant_y
    def create_room(self):
        for y in range(self.quant_y):
            for x in range(self.quant_x):
                self.matrix[tuple([x, y])] = Node(tuple([x, y]))

    #creation of a tree in which we can access the different possible nodes for each pieces of the room
    def create_tree(self):
        for y in range(self.quant_y):
            for x in range(self.quant_x):
                positions = []
                #We look if we are in an extremity of the room
                if x != 4:
                    positions.append(tuple([x + 1, y]))
                if x != 0:
                    positions.append(tuple([x - 1, y]))
                if y != 4:
                    positions.append(tuple([x, y + 1]))
                if y != 0:
                    positions.append(tuple([x, y - 1]))
                self.tree[tuple([x, y])] = positions

    # permet de retourner l'état de la salle sous format json pour l'affichage web
    def get_dict_for_json(self):
        self.dict = {}
        if self.matrix:
            for y in range(self.quant_y):
                for x in range(self.quant_x):
                    self.dict[f'X{x}Y{y}'] = self.matrix[tuple([x, y])].get_dict_for_json()
        return self.dict


    # Retourne la matrice sous forme de dictionnaire de tuple (coordonnées)
    def get_room(self):
        return self.matrix

    #getter to access the information of the room
    def get_room(self):
        return self.matrix

    # Ces deux fonctions permettent de générer de manière aléatoire un emplacement dans la salle pour y 
    # ajouter une poussière ou un diamant
    #random generation of dirty in the room
    def generate_dirty(self):
        import random
        x = random.choice(list(range(self.quant_x)))
        y = random.choice(list(range(self.quant_y)))
        self.matrix[tuple([x, y])].quantity_dirty += 1

    #random generation of jewels in the room
    def generate_jewel(self):
        import random
        x = random.choice(list(range(self.quant_x)))
        y = random.choice(list(range(self.quant_y)))
        self.matrix[tuple([x, y])].quantity_jewel += 1
