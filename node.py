"""
8INF846-01 - Intelligence artificielle - Hiver 2022

Travail Pratique #1 - Résolution par l’exploration (description)

Groupe 01 : Marcelo Vasconcellos / Gabriel Shenouda / Matthis Villeneuve / Yann Reynaud
"""

"""
La classe Node permet de définir une case sur le plateau de jeu lorsque l'on utilise nos algorithmes 
récursifs utilisant une structure d'arbre
"""

class Node:

    def __init__(self, position):
        self.position = position
        self.x = position[0]
        self.y = position[1]
        self.g = 0
        self.h = 0
        self.f = 0
        self.quantity_dirty = 0
        self.quantity_jewel = 0
        self.dict = {}

    # Permet de définir l'égalité entre 2 noeuds, 2 noeuds sont égaux si leur position est identique
    def __eq__(self, other):
        return self.position == other.position

    # Permet de définir l'affichage d'un Noeud
    def __str__(self):
        return f'X{self.x}Y{self.y}'

    def __repr__(self):
        return f'Position(X{self.x}, Y{self.y}, D{self.quantity_dirty}, J{self.quantity_jewel,})'

    def get_dict_for_json(self):
        self.dict = {'x': self.x,
                     'y': self.y,
                     'quantity_dirty': self.quantity_dirty,
                     'quantity_jewel': self.quantity_jewel, }
        return self.dict

    # Remet le compteur de poussière et de diamant à 0
    def clean(self):
        self.quantity_dirty = 0
        self.quantity_jewel = 0


