import cmd

import pinassign
import simulation

INTRO = """Welcome to the PinAssign command line interface.

Before you can start assigning, you need to add machines and players.
Machines and players can also be added using text files passed as input to this script.

To add a machine, type "addmachine NAME EXPECTEDTIME".
To add a player, type "addplayer NAME".

Once you've added all machines and at least one player, type "start".
"""

class MachineError(Exception):
    pass

class InvalidMachineError(MachineError):
    pass

class DuplicateMachineError(MachineError):
    pass

class PlayerError(Exception):
    pass

class InvalidPlayerError(PlayerError):
    pass

class DuplicatePlayerError(PlayerError):
    pass

class Game:
    def __init__(self):
        self.machines = []
        self.players = []
        self.scores = []
    
    def add_machine(self, name, expected_time):
        if not name:
            raise InvalidMachineError('The machine must have a name')
        elif expected_time <= 0:
            raise InvalidMachineError('The expected time of the machine cannot be zero or negative')
        elif name in (m.name for m in self.machines):
            raise DuplicateMachineError('The machine {} already exists'.format(name))
        self.machines.append(pinassign.Machine(name, expected_time))
    
    def add_player(self, name):
        if not name:
            raise InvalidPlayerError('The player must have a name')
        elif name in (m.name for m in self.players):
            raise DuplicatePlayerError('The player {} already exists'.format(name))
        self.players.append(pinassign.Player(name))

class PinAssignCmd(cmd.Cmd):
    def __init__(self):
        super().__init__()
        self.prompt = 'Command (? for help): '
        self.intro = INTRO
        self.game = Game()
    
    def do_machines(self, s):
        machines = self.game.machines
        if not machines:
            print('No machines have been added')
        else:
            print('Machines:')
            for machine in sorted(machines, key=lambda m: m.name):
                print('- {} (expected time {})'.format(machine.name, machine.expected_time))
    
    def do_players(self, s):
        players = self.game.players
        if not players:
            print('No players have been added')
        else:
            print('Players:')
            for player in sorted(players, key=lambda p: p.name):
                print('- {}'.format(player.name))
    
    def do_addmachine(self, s):
        last_space_idx = s.rfind(' ')
        if last_space_idx == -1:
            print('Invalid addmachine syntax. Example: "addmachine Medieval Madness 5"')
            return
        name = s[:last_space_idx]
        try:
            expected_time = int(s[last_space_idx+1:])
        except ValueError:
            print('Invalid expected time: {} (must be integer)'.format(s[last_space_idx+1:]))
            return
        try:
            self.game.add_machine(name, expected_time)
            print('Machine {} added with expected time {}'.format(name, expected_time))
        except MachineError as e:
            print('Invalid addmachine command: {}'.format(e))
    
    def do_addplayer(self, s):
        try:
            self.game.add_player(s)
            print('Player {} added'.format(s))
        except PlayerError as e:
            print('Invalid addplayer command: {}'.format(e))

def run_cli():
    PinAssignCmd().cmdloop()

if __name__ == '__main__':
    run_cli()
