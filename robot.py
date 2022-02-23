"""
8INF846-01 - Intelligence artificielle - Hiver 2022

Travail Pratique #1 - Résolution par l’exploration (description)

Groupe 01 : Marcelo Vasconcellos / Gabriel Shenouda / Matthis Villeneuve / Yann Reynaud
"""

import codecs
import json
import random
from time import sleep

from energy import EnergyConsumption
from node import Node


class StateBDI:

    def __init__(self):
        self.tree = {}
        self.cycles = 0
        self.quantity_dirty = 0
        self.quantity_jewels = 0
        self.distance = 0
        self.energy_consumption = 0
        self.cycle = 0
        self.history = []
        self.sensors = {}
        self.open_list = []
        self.closed_list = []
        self.action_plan = []
        self.current_g = 0
        self.end_node = None
        self.action_plan_position = 0
        self.exploration = 'Exploration not-informed'


class Sensors:

    def __init__(self):
        self.tree = {}
        self.quantity_dirty = 0
        self.quantity_jewels = 0


class Robot:

    def __init__(self):
        self.current_angle = random.choice([0, 90, 180, 270])
        #random position in the room when we create the robot
        self.y = random.choice(range(5))
        self.x = random.choice(range(5))
        self.current_node = Node(tuple([self.x, self.y]))
        self.state_bdi = StateBDI()

    def get_dict_for_json(self):
        action_plan = []
        for action, node in self.state_bdi.action_plan:
            action_plan.append({'action': action.__name__, 'position': str(node)})
        data = {
            'exploration': self.state_bdi.exploration,
            'current_angle': f'{self.current_angle}deg',
            'y': self.y,
            'x': self.x,
            'quantity_jewels': f'{self.state_bdi.quantity_jewels} unit(s)',
            'quantity_dirty': f'{self.state_bdi.quantity_dirty} dm3',
            'distance': f'{self.state_bdi.distance} meter(s)',
            'energy_consumption': f'{self.state_bdi.energy_consumption} Watt(s)',
            'position': f"#X{self.x}Y{self.y}-robot",
            'position_clean': f"#X{self.x}Y{self.y}-jewel-dirty",
            'action_plan': action_plan[
                           self.state_bdi.action_plan_position:
                           self.state_bdi.action_plan_position + 10],
            'action_plan_len': len(action_plan[
                                   self.state_bdi.action_plan_position:
                                   self.state_bdi.action_plan_position + 10]),
        }
        if self.state_bdi.end_node:
            data['end_node'] = f"X{self.state_bdi.end_node.x}Y{self.state_bdi.end_node.y}"
        return data


    #function to save the information in a JSON file
    def save_state(self, room):
        data = {
            'robot': self.get_dict_for_json(),
            'room': room.get_dict_for_json(),
        }
        file = codecs.open('data.json', "w", 'utf-8')
        file.write(json.dumps(data, indent=4))
        file.close()


    #action of the robot : collect a jewel in a piece of the room
    def collect_jewel(self, room, node):
        quantity_jewel = room.matrix[node.position].quantity_jewel
        # update the quantity jewel of the robot
        self.state_bdi.quantity_jewels += quantity_jewel
        #energy consumption of the robot depends on the quantity of jewel it collects
        self.state_bdi.energy_consumption += quantity_jewel * \
                                             EnergyConsumption().per_jewel
        #put to 0 the number of jewel in the piece after collecting them
        room.matrix[node.position].quantity_jewel = 0


    #action of the robot : vacuum dirty in a piece of the room
    def vacuum_dirty(self, room, node):
        quantity_dirty = room.matrix[node.position].quantity_dirty
        self.state_bdi.quantity_dirty += quantity_dirty
        # energy consumption of the robot depends on the quantity of dirty it vacuums
        self.state_bdi.energy_consumption += quantity_dirty \
                                             * EnergyConsumption().per_dirty
        #we put both to 0 because when there are both jewel and dirty in the same room,\
                                                            # the robot vacuums both but don't collect the jewel
        room.matrix[node.position].quantity_dirty = 0
        room.matrix[node.position].quantity_jewel = 0


    #permit to a robot to move in different pieces, identified by a node
    def move(self, _, node):
        self.y = node.y
        self.x = node.x
        #for each move, distance  increases by one
        self.state_bdi.distance += 1
        #robot consumes energy when it moves
        self.state_bdi.energy_consumption += EnergyConsumption().per_step
        #We put the concerned node in the history
        self.state_bdi.history.append(node)
        self.state_bdi.history = self.state_bdi.history[-30:]


    #permit to the robot to rotate itself to the next node's direction
    #Energy consumption in,creases when robot rotates
    def rotate(self, _, node):
        if self.x < node.x and self.current_angle != 0:
            self.current_angle = 0
            self.state_bdi.energy_consumption += EnergyConsumption().per_turn
        elif self.x > node.x and self.current_angle != 180:
            self.current_angle = 180
            self.state_bdi.energy_consumption += EnergyConsumption().per_turn
        elif self.y < node.y and self.current_angle != 90:
            self.current_angle = 90
            self.state_bdi.energy_consumption += EnergyConsumption().per_turn
        elif self.y > node.y and self.current_angle != 270:
            self.current_angle = 270
            self.state_bdi.energy_consumption += EnergyConsumption().per_turn

    #associates an action to a node depending of its jewel and dirty quantities. It helps to create the action plan
    def process_node(self, node):
        #the robot begin by rotating and then moving to the next node
        self.state_bdi.action_plan.append([self.rotate, node])
        self.state_bdi.action_plan.append([self.move, node])

        if self.state_bdi.sensors[node.position].quantity_dirty and \
                self.state_bdi.sensors[node.position].quantity_jewels:
            #if there is jewel and dirty, robot associates the node to the action vacuum dirty
            self.state_bdi.action_plan.append([self.vacuum_dirty, node])

        elif self.state_bdi.sensors[node.position].quantity_dirty and \
                not self.state_bdi.sensors[node.position].quantity_jewels:
            # if there is only dirty, robot associates the node to the action vacuum dirty
            self.state_bdi.action_plan.append([self.vacuum_dirty, node])

        elif not self.state_bdi.sensors[node.position].quantity_dirty and \
                self.state_bdi.sensors[node.position].quantity_jewels:
            # if there is only jewel, robot associates the node to the action collect jewel
            self.state_bdi.action_plan.append([self.collect_jewel, node])
    #return the next node in the non informed exploration
    def get_node_exploration_non_informed(self, position):
        metric = 0
        next_node = None #initialiazing node
        tree = [node for node in self.state_bdi.sensors[position].tree
                if node not in self.state_bdi.history]
        for node in tree:
            metric_node = self.state_bdi.sensors[node].quantity_dirty \
                          + self.state_bdi.sensors[node].quantity_jewels
            if metric_node > metric:
                metric = metric_node
                next_node = node
        if tree and not next_node:
            next_node = random.choice(tree)
        if next_node:
            self.state_bdi.history.append(next_node)
        return next_node

    def exploration_non_informed(self, position):
        next = self.get_node_exploration_non_informed(position)
        if next:
            node = Node(next)
            self.state_bdi.end_node = node
            self.process_node(node)
            self.exploration_non_informed(next)
        else:
            return None

    def execute_exploration_non_informed(self):
        next = self.get_node_exploration_non_informed(tuple([self.x, self.y]))
        if next:
            node = Node(next)
            self.process_node(node)
            self.exploration_non_informed(next)
        else:
            return None

    def get_f_score(self, node):
        """
        Calculates the value of f for a specific node.

        :param node: Node class object
        :return: Node class object
        """
        node.g = self.state_bdi.current_g + 1 \
                 - self.state_bdi.sensors[node.position].quantity_jewels \
                 - self.state_bdi.sensors[node.position].quantity_dirty
        node.h = ((node.x - self.state_bdi.end_node.x) ** 2
                  + (node.y - self.state_bdi.end_node.y) ** 2) ** 0.5
        node.f = node.g + node.h
        return node.f

    def decision_test(self, current_node):
        """
        This function returns the node that has the smallest f
        If it finds any node not yet visited, it returns the minimum f
        among the already visited neighbors, if it is surrounded by
        already visited nodes, it returns the minimum among
        all neighbors, without considering the visit.

        :param current_node: Node class object
        :return: Object of class node with smallest f-value among neighbors.
        """
        f_values_out_open_list = {}
        f_values = {}
        for node in self.state_bdi.sensors[current_node.position].tree:
            node = Node(node)
            if node not in self.state_bdi.open_list:
                f_values_out_open_list[self.get_f_score(node)] = node
            f_values[self.get_f_score(node)] = node
        print('-'*20)
        print('DECISION TEST')
        print('current_node', current_node)
        print('f_values_out_open_list', f_values_out_open_list)
        print('f_values', f_values)
        if f_values_out_open_list:
            return f_values_out_open_list[min(list(f_values_out_open_list))]
        else:
            return f_values[min(list(f_values))]

    # Used for the A* Algorithm
    def most_dirty_node(self):
        """
        It returns the node with the most dust and jewelry,
        if it finds more than one node with the same amount
        of dirt and jewelry it will look for the closest one among them.
        """
        counter = 0
        distance = 25
        selected_node = None
        self.state_bdi.end_node = None
        print('-'*20)
        print('GET MOST DIRTY NODE:')
        for new_node in self.state_bdi.sensors:
            dirt = self.state_bdi.sensors[new_node].quantity_dirty
            jewel = self.state_bdi.sensors[new_node].quantity_jewels
            new_counter = dirt + jewel
            new_node = Node(new_node)
            new_distance = ((self.x - new_node.x) ** 2
                            + (self.y - new_node.y) ** 2) ** 0.5
            print(new_node, dirt, jewel, new_distance, '<', distance,
                  (new_counter > counter and new_distance < distance))
            if new_counter > counter and new_distance < distance:
                counter = new_counter
                distance = new_distance
                selected_node = new_node
        self.state_bdi.end_node = selected_node
        print('selected node', self.state_bdi.end_node)

    # Recursive implementation of A*
    def recursive_a_star(self, current_node):
        if current_node.position == self.state_bdi.end_node.position:
            return None
        else:
            new_node = self.decision_test(current_node)
            self.state_bdi.current_g += 1
            self.state_bdi.open_list.append(new_node)
            return self.recursive_a_star(new_node)

    # Used to launch A*
    def a_star(self):
        new_node = self.decision_test(self.current_node)
        self.state_bdi.open_list.append(self.current_node)
        self.state_bdi.current_g += 1
        self.state_bdi.open_list.append(new_node) # The open list are the nodes which have been examinated
        return self.recursive_a_star(new_node) # Here is the call for the recursive A*

    # launches the A* algorithm
    def execute_exploration_informed(self):
        self.current_node = Node(tuple([self.x, self.y]))
        self.most_dirty_node()
        if self.state_bdi.end_node:
            self.state_bdi.open_list = []
            self.a_star()
            for node in self.state_bdi.open_list:
                if(node != self.state_bdi.open_list[0]):
                    self.process_node(node)

            self.state_bdi.current_g = 0
            self.state_bdi.open_list = []

    def observe_environment_with_my_sensors(self, room):
        environment = {}
        tree = room.tree
        for node in room.tree:
            """
            The sensor is only picking up the amount of jewelry and 
            dust in the space, but it can add up the amount of row 
            or column depending on the angle it is at.
            """
            environment[node] = {
                'tree': room.tree[node],
                'quantity_jewels': room.matrix[node].quantity_jewel,
                'quantity_dirty': room.matrix[node].quantity_dirty, }
        return tree, environment

    # Used to update the BDI values and allows us to display it on the web interface
    def update_my_state_bdi(self, environment):
        tree, sensors = environment
        self.state_bdi.tree = tree
        for node in sensors:
            sensor = Sensors()
            sensor.tree = sensors[node]['tree']
            sensor.quantity_jewels = sensors[node]['quantity_jewels']
            sensor.quantity_dirty = sensors[node]['quantity_dirty']
            self.state_bdi.sensors[node] = sensor

    # define how the not informed and informed exploration are launched
    # actually, there are 2 cycles of not informed exploration and then the informed exploration is launched
    def execute_exploration(self):
        if self.state_bdi.cycle < 2:
            self.state_bdi.exploration = 'Exploration not-informed'
            self.execute_exploration_non_informed()
        else:
            self.state_bdi.exploration = 'Exploration informed'
            self.execute_exploration_informed()

    # executes the action plan created by the informed or non informed algorithm
    def execute_action_plan(self, room):
        for action, node in self.state_bdi.action_plan:
            sleep(1)
            action(room, node)
            self.state_bdi.action_plan_position += 1
            self.save_state(room)
        self.state_bdi.end_node = None
        self.state_bdi.open_list = None
        self.state_bdi.history = []
        self.state_bdi.action_plan = []
        self.state_bdi.action_plan_position = 0
        self.state_bdi.cycle += 1


