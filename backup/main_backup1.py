"""
8INF846-01 - Intelligence artificielle - Hiver 2022

Travail Pratique #1 - Résolution par l’exploration (description)

Groupe 01 : Marcelo Vasconcellos / Gabriel Shenouda / Matthis Villeneuve / Yann Reynaud
"""

import threading
from time import sleep
import random


def save_json():
    import codecs
    import json
    global room
    global robot
    data = {
        'robot': robot.get_dict_for_json(),
        'room': room.get_dict_for_json(),
    }
    file = codecs.open('data.json', "w", 'utf-8')
    file.write(json.dumps(data, indent=4))
    file.close()


class Position:

    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.quantity_dirty = 0
        self.quantity_jewel = 0
        self.dict = {}

    def __str__(self):
        return f'{self.x}, {self.y}'

    def __repr__(self):
        return f'Position(X{self.x}, Y{self.y}, D{self.quantity_dirty}, J{self.quantity_jewel, })'

    def get_dict_for_json(self):
        self.dict = {'x': self.x,
                     'y': self.y,
                     'quantity_dirty': self.quantity_dirty,
                     'quantity_jewel': self.quantity_jewel, }
        return self.dict

    def clean(self):
        self.quantity_dirty = 0
        self.quantity_jewel = 0


class Room:

    def __init__(self):
        self.num_lines = 5
        self.num_columns = 5
        self.matrix = {}
        self.tree = {}
        self.dict = {}
        self.create_tree()

    def create_room(self):
        for y in range(self.num_lines):
            for x in range(self.num_columns):
                self.matrix[tuple([x, y])] = Position(x, y)

    def create_tree(self):
        for y in range(self.num_lines):
            for x in range(self.num_columns):
                positions = []
                if x != 4:
                    positions.append(tuple([x+1, y]))
                if x != 0:
                    positions.append(tuple([x-1, y]))
                if y != 4:
                    positions.append(tuple([x, y+1]))
                if y != 0:
                    positions.append(tuple([x, y-1]))
                self.tree[tuple([x, y])] = positions


    def get_dict_for_json(self):
        self.dict = {}
        if self.matrix:
            for y in range(self.num_lines):
                for x in range(self.num_columns):
                    self.dict[f'X{x}Y{y}'] = self.matrix[tuple([x, y])].get_dict_for_json()
        return self.dict

    def get_room(self):
        return self.matrix

    def generate_dirty(self):
        import random
        line_positions_valids = list(range(self.num_lines))
        columns_positions_valids = list(range(self.num_columns))
        x = random.choice(columns_positions_valids)
        y = random.choice(line_positions_valids)
        self.matrix[tuple([x, y])].quantity_dirty += 1

    def generate_jewel(self):
        import random
        line_positions_valids = list(range(self.num_lines))
        columns_positions_valids = list(range(self.num_columns))
        x = random.choice(columns_positions_valids)
        y = random.choice(line_positions_valids)
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
        self.current_row = random.choice(range(5))
        self.current_col = random.choice(range(5))
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
        self.end_node = None
        self.action_plan_position = 0
        self.exploration = 'Exploration not-informed'

    def get_dict_for_json(self):
        action_plan = []
        for act in self.action_plan:
            action_plan.append({'action': act[0].__name__, 'position': '(%s, %s)' % act[1]})
        self.dict = {
            'exploration': self.exploration,
            'current_angle': f'{self.current_angle}deg',
            'current_row': self.current_row,
            'current_col': self.current_col,
            'quantity_jewels': f'{self.quantity_jewels} unit(s)',
            'quantity_dirty': f'{self.quantity_dirty} dm3',
            'distance': f'{self.distance} meter(s)',
            'energy_consumption': f'{self.energy_consumption} Watt(s)',
            'position': f"#X{self.current_col}Y{self.current_row}-robot",
            'position_clean': f"#X{self.current_col}Y{self.current_row}-jewel-dirty",
            'action_plan': action_plan[
                           self.action_plan_position:self.action_plan_position+10],
            'action_plan_len': len(action_plan[
                                   self.action_plan_position:self.action_plan_position+10]),
        }
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

    def move(self, position):
        self.current_row = position[1]
        self.current_col = position[0]
        self.distance += 1
        self.energy_consumption += EnergyConsumption().per_step
        self.history.append(position)
        self.history = self.history[-30:]

    def rotate(self, position):
        if self.current_col < position[0] and self.current_angle != 0:
            self.current_angle = 0
            self.energy_consumption += EnergyConsumption().per_turn
        elif self.current_col > position[0] and self.current_angle != 180:
            self.current_angle = 180
            self.energy_consumption += EnergyConsumption().per_turn
        elif self.current_row < position[1] and self.current_angle != 90:
            self.current_angle = 90
            self.energy_consumption += EnergyConsumption().per_turn
        elif self.current_row > position[1] and self.current_angle != 270:
            self.current_angle = 270
            self.energy_consumption += EnergyConsumption().per_turn

    @staticmethod
    def intersection(lst1, lst2):
        return list(set(lst1) & set(lst2))

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
        self.action_plan.append([self.move, position])
        next = self.get_node_exploration_non_informed(position)
        if next:
            self.action_plan.append([self.rotate, next])
            self.action_plan.append([self.move, next])
            if room.matrix[next].quantity_dirty and \
                    room.matrix[next].quantity_jewel:
                self.action_plan.append([self.vacuum_dirty, next])
                room.matrix[next].quantity_jewel = 0
            elif room.matrix[next].quantity_dirty and \
                    not room.matrix[next].quantity_jewel:
                self.action_plan.append([self.vacuum_dirty, next])
            elif not room.matrix[next].quantity_dirty and \
                    room.matrix[next].quantity_jewel:
                self.action_plan.append([self.collect_jewel, next])
            self.exploration_non_informed(next)
        else:
            return None

    def execute_exploration_non_informed(self):
        global room
        next = self.get_node_exploration_non_informed(tuple([self.current_col, self.current_row]))
        if next:
            self.action_plan.append([self.rotate, next])
            self.action_plan.append([self.move, next])
            if room.matrix[next].quantity_dirty and \
                    room.matrix[next].quantity_jewel:
                self.action_plan.append([self.vacuum_dirty, next])
                room.matrix[next].quantity_jewel = 0
            elif room.matrix[next].quantity_dirty and \
                    not room.matrix[next].quantity_jewel:
                self.action_plan.append([self.vacuum_dirty, next])
            elif not room.matrix[next].quantity_dirty and \
                    room.matrix[next].quantity_jewel:
                self.action_plan.append([self.collect_jewel, next])
            self.exploration_non_informed(next)
        else:
            return None

    def mostDirtyRoom(self):
        global room
        counter=0
        a,b=-1,-1
        for y in range(room.num_lines) :
            for x in range(room.num_columns) :
                dirt = self.state_bdi[tuple([x, y])].get("quantity_dirty")
                jewel = self.state_bdi[tuple([x, y])].get("quantity_jewels")
                if dirt+jewel>counter :
                    counter=dirt+jewel
                    a,b=x,y
                elif dirt+jewel==counter :
                    if ((((self.current_col-x)**2+(self.current_row-y)**2)**0.5)<=(((self.current_col-a)**2+(self.current_row-b)**2)**0.5)):
                        a,b=x,y
        return (a,b)


    def execute_exploration_informed(self):
        # Do explication informed
        global room
        start = (self.current_col, self.current_row)
        end = self.mostDirtyRoom()
        steps = self.astar(start, end)
        for step_position in range(1, len(steps)):
            self.action_plan.append([self.rotate, steps[step_position]])
            self.action_plan.append([self.move, steps[step_position]])
            if room.matrix[steps[step_position]].quantity_dirty and \
                    room.matrix[steps[step_position]].quantity_jewel:
                self.action_plan.append([self.vacuum_dirty, steps[step_position]])
                room.matrix[steps[step_position]].quantity_jewel = 0
            elif room.matrix[steps[step_position]].quantity_dirty and \
                    not room.matrix[steps[step_position]].quantity_jewel:
                self.action_plan.append([self.vacuum_dirty, steps[step_position]])
            elif not room.matrix[steps[step_position]].quantity_dirty and \
                    room.matrix[steps[step_position]].quantity_jewel:
                self.action_plan.append([self.collect_jewel, steps[step_position]])
        #print(self.action_plan)




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
        # Necessary to correct the mental state of the robot
        self.state_bdi = self.sensors.copy()


    def execute_exploration(self):
        if self.cycle < 2:
            self.exploration = 'Exploration not-informed'
            self.execute_exploration_non_informed()
        else:
            self.exploration = 'Exploration informed'
            # Change function to execute_exploration_informed
            self.execute_exploration_informed()

    def execute_action_plan(self):
        for action, position in self.action_plan:
            sleep(0.5)
            action(position)
            self.action_plan_position += 1
            save_json()
        self.history = []
        self.action_plan = []
        self.action_plan_position = 0

    def return_path(self,current_node):
        path = []
        current = current_node
        while current is not None:
            path.append(current.position)
            current = current.parent
        return path[::-1]  # Return reversed path


    def recursive_astar(self, current_node):
        if current_node == self.end_node:
            return None

        for new_position in room.tree[tuple([current_node.position[1], current_node.position[0]])]:
            # # Get node position
            new_node = Node(current_node, tuple([new_position[1], new_position[0]]))
            # Child is on the closed list
            # if len([closed_child for closed_child in self.closed_list if closed_child == new_node]) > 0:
            #     continue
            # Create the f, g, and h values
            new_node.g = current_node.g + 1 - self.state_bdi[new_node.position].get("quantity_dirty") + self.state_bdi[
                new_node.position].get("quantity_jewels")
            new_node.h = ((new_node.position[0] - self.end_node.position[0]) ** 2 + (
                        new_node.position[1] - self.end_node.position[1]) ** 2) ** 0.5
            new_node.f = new_node.g + new_node.h
            # Child is already in the open list
            if len([open_node for open_node in self.open_list if new_node == open_node and new_node.g > open_node.g]) > 0:
                continue
            # Add the child to the open list
            self.open_list.append(new_node)
            self.recursive_astar(new_node)


    def astar(self, start, end):
        global room
        # Create start and end node
        start_node = Node(None, start)
        start_node.g = start_node.h = start_node.f = 0
        self.end_node = Node(None, end)
        self.end_node.g = self.end_node.h = self.end_node.f = 0
        # Initializing open and closed list
        self.open_list = []
        self.closed_list = []
        # Add the start node
        self.open_list.append(start_node)
        # Loop until you find the end
        while len(self.open_list) > 0:
            # Get the current node
            current_node = self.open_list[0]
            current_index = 0
            for index, item in enumerate(self.open_list):
                if item.f < current_node.f:
                    current_node = item
                    current_index = index
            # Pop current off open list, add to closed list
            self.open_list.pop(current_index)
            self.closed_list.append(current_node)
            # Found the goal
            if current_node == self.end_node:
                return self.return_path(current_node)
                #self.action_plan = self.return_path(current_node)
            # Generate children
            # children = []
            for new_position in room.tree[tuple([current_node.position[1], current_node.position[0]])]:

                # Create new node
                new_node = Node(current_node, tuple([new_position[1], new_position[0]]))
                # Child is on the closed list
                if len([closed_child for closed_child in self.closed_list if closed_child == new_node]) > 0:
                    continue
                # Create the f, g, and h values
                new_node.g = current_node.g + 1 - self.state_bdi[new_node.position].get("quantity_dirty") + self.state_bdi[
                    new_node.position].get("quantity_jewels")
                new_node.h = ((new_node.position[0] - self.end_node.position[0]) ** 2 + (
                        new_node.position[1] - self.end_node.position[1]) ** 2) ** 0.5
                new_node.f = new_node.g + new_node.h
                # Child is already in the open list
                if len([open_node for open_node in self.open_list if
                        new_node == open_node and new_node.g > open_node.g]) > 0:
                    continue
                # Add the child to the open list
                self.open_list.append(new_node)
                self.recursive_astar(new_node)



class Node:

    def __init__(self, parent=None, position=None):
        self.parent = parent
        self.position = position
        self.g = 0
        self.h = 0
        self.f = 0

    def __eq__(self, other):
        return self.position == other.position




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


class Webserver(threading.Thread):

    def __init__(self):
        super(Webserver, self).__init__()

    def start(self):
        super().start()

    def run(self):
        import http.server
        import socketserver
        handler = http.server.SimpleHTTPRequestHandler
        with socketserver.TCPServer(("", 8000), handler) as httpd:
            httpd.serve_forever()

room = Room()
room.create_room()
robot = Robot()

if __name__ == '__main__':
    import webbrowser
    webserver = Webserver()
    webserver.start()
    environment = Environment()
    environment.start()
    agent = Agent()
    agent.start()
    webbrowser.open("http://localhost:8000/")
