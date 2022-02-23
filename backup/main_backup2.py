"""
8INF846-01 - Intelligence artificielle - Hiver 2022

Travail Pratique #1 - Résolution par l’exploration (description)

Groupe 01 : Marcelo Vasconcellos / Gabriel Shenouda / Matthis Villeneuve / Yann Reynaud
"""

import codecs
import json
import random
import threading
import webbrowser
from time import sleep


def save_json():
    global room
    global robot

    data = {
        'robot': robot.get_dict_for_json(),
        'room': room.get_dict_for_json(),
    }
    file = codecs.open('data.json', "w", 'utf-8')
    file.write(json.dumps(data, indent=4))
    file.close()


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

    def __eq__(self, other):
        return self.position == other.position

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

    def get_f(self):
        global robot
        self.g = robot.current_g + 1  # \
        # - robot.state_bdi[self.position].get("quantity_dirty") \
        # + robot.state_bdi[self.position].get("quantity_jewels")
        self.h = ((self.x - robot.end_node.x) ** 2
                  + (self.y - robot.end_node.y) ** 2) ** 0.5
        self.f = self.g + self.h
        return self.f

    def clean(self):
        self.quantity_dirty = 0
        self.quantity_jewel = 0


class Room:

    def __init__(self):
        self.quant_y = 5
        self.quant_x = 5
        self.matrix = {}
        self.tree = {}
        self.dict = {}
        self.create_tree()

    def create_room(self):
        for y in range(self.quant_y):
            for x in range(self.quant_x):
                self.matrix[tuple([x, y])] = Node(tuple([x, y]))

    def create_tree(self):
        for y in range(self.quant_y):
            for x in range(self.quant_x):
                positions = []
                if x != 4:
                    positions.append(tuple([x + 1, y]))
                if x != 0:
                    positions.append(tuple([x - 1, y]))
                if y != 4:
                    positions.append(tuple([x, y + 1]))
                if y != 0:
                    positions.append(tuple([x, y - 1]))
                self.tree[tuple([x, y])] = positions

    def get_dict_for_json(self):
        self.dict = {}
        if self.matrix:
            for y in range(self.quant_y):
                for x in range(self.quant_x):
                    self.dict[f'X{x}Y{y}'] = self.matrix[tuple([x, y])].get_dict_for_json()
        return self.dict

    def get_room(self):
        return self.matrix

    def generate_dirty(self):
        import random
        x = random.choice(list(range(self.quant_x)))
        y = random.choice(list(range(self.quant_y)))
        self.matrix[tuple([x, y])].quantity_dirty += 1

    def generate_jewel(self):
        import random
        x = random.choice(list(range(self.quant_x)))
        y = random.choice(list(range(self.quant_y)))
        self.matrix[tuple([x, y])].quantity_jewel += 1


class Environment(threading.Thread):

    def __init__(self):
        super(Environment, self).__init__()
        global room
        self.room = room

    def start(self):
        super().start()

    def run(self):
        import random

        """
        while thread_is_running:
            if should_generate_dirty:
                generate_dirty()
            if should_generate_jewel:
                generate_jewel()
        """

        while True:
            sleep(random.choice(list(range(5))))
            if random.choice([True, False, False]):
                self.room.generate_jewel()
            if random.choice([True, True, False]):
                self.room.generate_dirty()


class EnergyConsumption:

    def __init__(self):
        import random
        self.per_jewel = 40 + random.choice(range(10))
        self.per_dirty = 30 + random.choice(range(15))
        self.per_step = 10 + random.choice(range(5))
        self.per_turn = 5 + random.choice(range(3))


class Robot:

    def __init__(self):
        self.current_angle = random.choice([0, 90, 180, 270])
        self.current_node = None
        self.y = random.choice(range(5))
        self.x = random.choice(range(5))
        self.quantity_jewels = 0
        self.quantity_dirty = 0
        self.distance = 0
        self.cycle = 0
        self.energy_consumption = 0
        self.dict = {}
        self.history = []
        self.state_bdi = {}
        self.sensors = {}
        self.open_list = []
        self.closed_list = []
        self.action_plan = []
        self.current_g = 0
        self.end_node = Node(tuple([self.x, self.y]))
        self.action_plan_position = 0
        self.exploration = 'Exploration not-informed'

    def get_dict_for_json(self):
        action_plan = []
        for action, node in self.action_plan:
            action_plan.append({'action': action.__name__, 'position': str(node)})
        self.dict = {
            'exploration': self.exploration,
            'current_angle': f'{self.current_angle}deg',
            'y': self.y,
            'x': self.x,
            'quantity_jewels': f'{self.quantity_jewels} unit(s)',
            'quantity_dirty': f'{self.quantity_dirty} dm3',
            'distance': f'{self.distance} meter(s)',
            'energy_consumption': f'{self.energy_consumption} Watt(s)',
            'position': f"#X{self.x}Y{self.y}-robot",
            'position_clean': f"#X{self.x}Y{self.y}-jewel-dirty",
            'action_plan': action_plan[
                           self.action_plan_position:self.action_plan_position + 10],
            'action_plan_len': len(action_plan[
                                   self.action_plan_position:self.action_plan_position + 10]),
        }
        if self.end_node:
            self.dict['end_node'] = f"X{self.end_node.x}Y{self.end_node.y}"
        return self.dict

    def collect_jewel(self, position):
        global room
        quantity_jewel = room.matrix[position].quantity_jewel
        self.quantity_jewels += quantity_jewel
        self.energy_consumption += quantity_jewel * EnergyConsumption().per_jewel
        room.matrix[position].quantity_jewel = 0

    def vacuum_dirty(self, position):
        global room
        quantity_dirty = room.matrix[position].quantity_dirty
        self.quantity_dirty += quantity_dirty
        self.energy_consumption += quantity_dirty * EnergyConsumption().per_dirty
        room.matrix[position].quantity_dirty = 0
        room.matrix[position].quantity_jewel = 0

    def move(self, node):
        node = Node(node)
        self.y = node.y
        self.x = node.x
        self.distance += 1
        self.energy_consumption += EnergyConsumption().per_step
        self.history.append(node)
        self.history = self.history[-30:]

    def rotate(self, node):
        node = Node(node)
        if self.x < node.x and self.current_angle != 0:
            self.current_angle = 0
            self.energy_consumption += EnergyConsumption().per_turn
        elif self.x > node.x and self.current_angle != 180:
            self.current_angle = 180
            self.energy_consumption += EnergyConsumption().per_turn
        elif self.y < node.y and self.current_angle != 90:
            self.current_angle = 90
            self.energy_consumption += EnergyConsumption().per_turn
        elif self.y > node.y and self.current_angle != 270:
            self.current_angle = 270
            self.energy_consumption += EnergyConsumption().per_turn

    @staticmethod
    def intersection(lst1, lst2):
        return list(set(lst1) & set(lst2))

    def process_node(self, node):
        self.action_plan.append([self.rotate, node])
        self.action_plan.append([self.move, node])

        if room.matrix[node.position].quantity_dirty and \
                room.matrix[node.position].quantity_jewel:
            self.action_plan.append([self.vacuum_dirty, node])
            room.matrix[node.position].quantity_jewel = 0

        elif room.matrix[node.position].quantity_dirty and \
                not room.matrix[node.position].quantity_jewel:
            self.action_plan.append([self.vacuum_dirty, node])

        elif not room.matrix[node.position].quantity_dirty and \
                room.matrix[node.position].quantity_jewel:
            self.action_plan.append([self.collect_jewel, node])

    def get_node_exploration_non_informed(self, position):
        global room
        metric = 0
        next_node = None
        tree = [node for node in room.tree[position] if node not in self.history]
        for node in tree:
            metric_node = room.matrix[node].quantity_dirty \
                          + room.matrix[node].quantity_jewel
            if metric_node > metric:
                metric = metric_node
                next_node = node
        if tree and not next_node:
            next_node = random.choice(tree)
        if next_node:
            self.history.append(next_node)
        return next_node

    def exploration_non_informed(self, position):
        global room
        next = self.get_node_exploration_non_informed(position)
        if next:
            node = Node(next)
            self.end_node = node
            self.process_node(node)
            self.exploration_non_informed(next)
        else:
            return None

    def execute_exploration_non_informed(self):
        global room
        next = self.get_node_exploration_non_informed(tuple([self.x, self.y]))
        if next:
            node = Node(next)
            self.process_node(node)
            self.exploration_non_informed(next)
        else:
            return None

    def most_dirty_node(self):
        """
        It returns the node with the most dust and jewelry,
        if it finds more than one node with the same amount
        of dirt and jewelry it will look for the closest one among them.
        """
        global room
        counter = 0
        distance = 25
        self.end_node = None
        for new_node in room.tree:
            dirt = self.sensors[new_node].get("quantity_dirty")
            jewel = self.sensors[new_node].get("quantity_jewels")
            new_counter = dirt + jewel
            new_node = Node(new_node)
            new_distance = ((self.x - new_node.x) ** 2
                            + (self.y - new_node.y) ** 2) ** 0.5
            if new_counter > counter and new_distance < distance:
                counter = new_counter
                distance = new_distance
                self.end_node = new_node

    def recursive_a_star(self, current_node):
        if current_node.position == self.end_node.position:
            return None
        else:
            paths = [Node(nd).get_f() for nd in room.tree[current_node.position]
                     if Node(nd) not in self.open_list]
            for new_node in room.tree[current_node.position]:
                new_node = Node(new_node)
                if new_node not in self.open_list and (paths and new_node.get_f() == min(paths)):
                    self.current_g += 1
                    self.open_list.append(new_node)
                    return self.recursive_a_star(new_node)

    def a_star(self):
        global room
        self.open_list = []

        if self.current_node == self.end_node:
            return None
        else:
            paths = [Node(nd).get_f() for nd in room.tree[self.current_node.position]
                     if Node(nd) not in self.open_list]
            for new_node in room.tree[self.current_node.position]:
                new_node = Node(new_node)
                if new_node not in self.open_list and (paths and new_node.get_f() == min(paths)):
                    self.current_g += 1
                    self.open_list.append(new_node)
                    return self.recursive_a_star(new_node)

    def execute_exploration_informed(self):
        # Do explication informed
        global room
        self.current_node = Node(tuple([self.x, self.y]))
        self.most_dirty_node()
        if self.end_node:
            self.a_star()

            for node in self.open_list:
                self.process_node(node)

            self.current_g = 0
            self.open_list = []

    def observe_environment_with_my_sensors(self):
        global room

        self.sensors = {}
        for node in room.tree:
            """
            The sensor is only picking up the amount of jewelry and 
            dust in the space, but it can add up the amount of row 
            or column depending on the angle it is at.
            """
            self.sensors[node] = {'quantity_jewels': room.matrix[node].quantity_jewel,
                                  'quantity_dirty': room.matrix[node].quantity_dirty, }

    def update_my_state_bdi(self):
        self.state_bdi = self.sensors.copy()

    def execute_exploration(self):
        if self.cycle < 2:
            self.exploration = 'Exploration not-informed'
            self.execute_exploration_non_informed()
        else:
            self.exploration = 'Exploration informed'
            self.execute_exploration_informed()

    def execute_action_plan(self):
        for action, node in self.action_plan:
            sleep(0.5)
            action(node.position)
            self.action_plan_position += 1
            save_json()
        self.end_node = None
        self.open_list = None
        self.history = []
        self.action_plan = []
        self.action_plan_position = 0


class Agent(threading.Thread):

    def __init__(self):
        super(Agent, self).__init__()
        global robot
        self.robot = robot

    def start(self):
        super().start()

    def run(self):
        """
        while am_I_alive: # This is the analysis cycle
            environment = observe_environment_with_my_sensors()
            state_bdi = update_my_state_bdi(environment, metric)
            plan_action = execute_exploration(state_bdi, algo-informed or algo-not-informed)
            metric = execute_action_plan(plan_action)
        """

        while True:
            self.robot.observe_environment_with_my_sensors()
            self.robot.update_my_state_bdi()
            self.robot.execute_exploration()
            self.robot.execute_action_plan()
            self.robot.cycle += 1


room = Room()
room.create_room()
robot = Robot()

if __name__ == '__main__':
    environment = Environment()
    environment.start()
    agent = Agent()
    agent.start()

    import http.server
    import socketserver

    webbrowser.open("http://localhost:8000/")
    handler = http.server.SimpleHTTPRequestHandler
    with socketserver.TCPServer(("", 8000), handler) as httpd:
        httpd.serve_forever()
