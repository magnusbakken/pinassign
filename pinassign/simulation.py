import random

from .pinassign import *

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

def simulate(machines=default_machines(), players=default_players(), r=random.Random()):
    scores = []
    current_pairings = []
    time_taken = 0
    assigned = assign_players(machines, players, scores, r)
    for pairing in assigned:
        current_pairings.append((pairing, time_taken))
    while not is_everyone_finished(machines, players, scores):
        print('Time passed: {}'.format(time_taken))
        if time_taken % 10 == 0:
            print('Status at {}:'.format(time_taken))
            print('  Finished machines:')
            for score in sorted(scores, key=lambda s: (s.machine.name, s.player.name)):
                print('  - {} has finished {}'.format(score.player, score.machine))
            print('  Current pairings:')
            for ((m, p), t) in current_pairings:
                print('  - {} is playing {} (started at {})'.format(p, m, t))
        time_taken += 1
        next_pairings = [((m, p), t) for (m, p), t in current_pairings if m.expected_time > time_taken - t]
        for (m, p), t in (((m, p), t) for (m, p), t in current_pairings if m.expected_time <= time_taken - t):
            print('{} finished {} at {} (started at {})'.format(p, m, time_taken, t))
            new_pairings = player_finished_machine(m, p, machines, players, scores, r)
            for new_m, new_p in new_pairings:
                print('{} assigned to {} at {}'.format(new_p, new_m, time_taken))
                next_pairings.append(((new_m, new_p), time_taken))
        current_pairings = next_pairings
