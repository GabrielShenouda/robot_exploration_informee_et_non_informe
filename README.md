# robot_exploration_informee_et_non_informe

UQAC – Université du Québec à Chicoutimi
8INF846-01 - Intelligence artificielle - Hiver 2022
Travail Pratique #1 - Résolution par l’exploration (description)

## Creation of a hoover agent using uninformed exploration algorithms such as A*, search tree, etc.
![map](https://user-images.githubusercontent.com/59508102/155383043-e30ba91f-723b-41bc-9046-7841284bebad.jpg)

The hoover robot evolves in an environment where dust and jewels appear randomly throughout the execution of the program. 
The goal is to clean the environment and keep it clean.

To do this we implement two search algorithms: 
- The Depth-First-Search
![dfs](https://user-images.githubusercontent.com/59508102/155383097-689d7d31-9182-4aed-9adb-f98a4a7a5a6f.jpg)

- A*
![Astar](https://user-images.githubusercontent.com/59508102/155383059-5e13c85a-f383-4cfb-be4d-ce5d41ba3150.jpg)

With the following heuristic :
![heuristique](https://user-images.githubusercontent.com/59508102/155383186-5398f746-607b-4481-b0fc-6e5636a80f0b.jpg)


The program runs on 2 threads, one that manages the environment and the other the robot and its exploration.

![Diagramme robot](https://user-images.githubusercontent.com/59508102/155383200-8a0efa6d-504e-4fb5-99b7-9ac8110602be.jpg)

### What is this repository for? ###

* Creating the Development Environment
* Running the robot

### 1. Creating the Development Environment ###

Inside the folder run the following command to create the virtualenv.

```python -m venv venv```

To activate the virtual environment run:

* On Windows

    ```.\venv\Scripts\activate```

* On Mac/Linux

    ```source venv\bin\activate```

It is advisable that we upgrade pip tool:

```python -m pip install --upgrade pip```

Install the requirements:.

```pip install -r requirements.txt```

For deactivate virtualenv:

```deactivate```

### 2. Running the robot ###

Run the comment below in the terminal, it will open the browser.

```python main.py```
