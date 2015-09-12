import itertools as it
import random

"""
5 players (1, 2, 3, 4, 5)
2 machines (A, B)

Players (P):
Name    Free    ExpectedTimeSpent (ETS)
1       true    0
2       true    0
3       true    0
4       true    0
5       true    0

Machines (M):
Name    Free    ExpectedTime (ET)
A       true    5                
B       true    10               

Scores (S):
Player  Machine
(initially empty)

Algorithm:

1. For every machine in M where M.Free=true, randomly choose a player P where P.ETS is minimal, P.Free=true and (P, M) is not in S, and assign P to M.
2. When P finishes M:
    2.1: Add (P, M) to S.
    2.2: Mark M as free.
    2.3: Mark P as free.
    2.4: Increment P.ETS by M.ET.
    2.5: Go to (1).
"""

def default_machines():
    return [
        Machine('A', 5),
        Machine('B', 10),
    ]

def default_players():
    return [
        Player('1'),
        Player('2'),
        Player('3'),
        Player('4'),
        Player('5'),
    ]

class Machine:
    def __init__(self, name, expectedTime):
        self.name = name
        self.expectedTime = expectedTime
        self.free = True
    
    def __eq__(self, other):
        return other is not None and self.name == other.name
    
    def __str__(self):
        return 'Machine {}'.format(self.name)

class Player:
    def __init__(self, name):
        self.name = name
        self.expectedTimeSpent = 0
        self.free = True
    
    def __eq__(self, other):
        return other is not None and self.name == other.name
    
    def __str__(self):
        return 'Player {}'.format(self.name)

class Score:
    def __init__(self, machine, player):
        self.machine = machine
        self.player = player
    
    def __eq__(self, other):
        return other is not None and self.machine == other.machine and self.player == other.player
    
    def __str__(self):
        return '{} played {}'.format(self.player, self.machine)

def pick_player(players, r):
    l = list(players)
    if not l:
        return None
    return r.choice(l)

def has_played_machine(machine, player, scores):
    return any(s for s in scores if s.machine == machine and s.player == player)

def is_everyone_finished(machines, players, scores):
    return all(has_played_machine(m, p, scores) for m in machines for p in players)

def filter_available_players(machine, players, scores):
    all_available = (p for p in players if p.free and not has_played_machine(machine, p, scores))
    q = sorted(all_available, key=lambda p: p.expectedTimeSpent)
    if not q:
        return ()
    return it.takewhile(lambda p: p.expectedTimeSpent == q[0].expectedTimeSpent, q)

def filter_available_machines(machines):
    return (m for m in machines if m.free)

def register_score(machine, player, scores):
    machine.free = True
    player.free = True
    player.expectedTimeSpent += machine.expectedTime
    scores.append(Score(machine, player))

def assign_player(machine, player):
    machine.free = False
    player.free = False

def assign_players(machines, players, scores, r):
    for m in filter_available_machines(machines):
        available_players = filter_available_players(m, players, scores)
        p = pick_player(available_players, r)
        if p:
            assign_player(m, p)
            yield (m, p)

def player_finished_machine(machine, player, machines, players, scores, r):
    register_score(machine, player, scores)
    return assign_players(machines, players, scores, r)
