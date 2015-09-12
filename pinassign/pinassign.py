import itertools as it

class Machine:
    def __init__(self, name, expected_time):
        self.name = name
        self.expected_time = expected_time
        self.ready = True
    
    def __eq__(self, other):
        return other is not None and self.name == other.name
    
    def __str__(self):
        return 'Machine {}'.format(self.name)
    
    def __repr__(self):
        return 'Machine({}, {})'.format(self.name, self.expected_time)

class Player:
    def __init__(self, name):
        self.name = name
        self.expected_time_spent = 0
        self.ready = True
    
    def __eq__(self, other):
        return other is not None and self.name == other.name
    
    def __str__(self):
        return 'Player {}'.format(self.name)
    
    def __repr__(self):
        return 'Player({})'.format(self.name)

class Score:
    def __init__(self, machine, player):
        self.machine = machine
        self.player = player
    
    def __eq__(self, other):
        return other is not None and self.machine == other.machine and self.player == other.player
    
    def __str__(self):
        return '{} played {}'.format(self.player, self.machine)
    
    def __repr__(self):
        return 'Score({}, {})'.format(repr(self.machine), repr(self.player))

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
    all_available = (p for p in players if p.ready and not has_played_machine(machine, p, scores))
    q = sorted(all_available, key=lambda p: p.expected_time_spent)
    if not q:
        return ()
    return it.takewhile(lambda p: p.expected_time_spent == q[0].expected_time_spent, q)

def filter_available_machines(machines):
    return (m for m in machines if m.ready)

def register_score(machine, player, scores):
    score = Score(machine, player)
    if score in scores:
        raise ValueError('{} has already been registered on {}'.format(player, machine))
    machine.ready = True
    player.ready = True
    player.expected_time_spent += machine.expected_time
    scores.append(score)

def assign_player(machine, player):
    machine.ready = False
    player.ready = False

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
