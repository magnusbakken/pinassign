import cmd
import random

import pinassign
import simulation

INTRO = """Welcome to the PinAssign command line interface.

Before you can start assigning, you need to add machines and players.
Machines and players can also be added using text files passed as input to this script.

To add a machine, type "addmachine NAME EXPECTEDTIME".
To add a player, type "addplayer NAME".

Player names must not contain spaces (use tags).

Once you've added all machines and at least one player, type "start".
"""

GAME_STARTED = """The game has started!

Here are the initial machine assignments:"""

GAME_FINISHED = """All players have finished all machines!

Use the reset command to start over from scratch, or resetscores to restart with the same machines and players."""

GAME_RESET = """The game has been reset. New machines and players must be added."""

SCORES_RESET = """The game scores have been reset.

The game is still running with the same machines and players as before, but no scores are registered anymore."""

class GameError(Exception):
    pass

class MachineError(GameError):
    pass

class InvalidMachineError(MachineError):
    pass

class DuplicateMachineError(MachineError):
    pass

class UnknownMachineError(MachineError):
    pass

class PlayerError(GameError):
    pass

class InvalidPlayerError(PlayerError):
    pass

class DuplicatePlayerError(PlayerError):
    pass

class UnknownPlayerError(PlayerError):
    pass

class DuplicateScoreError(GameError):
    pass

class Game:
    def __init__(self, r=random.Random()):
        self.r = r
        self._machines = []
        self._players = []
        self._scores = []
        self._machine_dict = {}
        self._player_dict = {}
        self._is_running = False
    
    @property
    def machines(self):
        return self._machines
    
    @property
    def players(self):
        return self._machines
    
    def add_machine(self, name, expected_time):
        self._fail_if_running()
        if not name:
            raise InvalidMachineError('The machine must have a name')
        elif expected_time <= 0:
            raise InvalidMachineError('The expected time of the machine cannot be zero or negative')
        elif self._get_machine(name) is not None:
            raise DuplicateMachineError('The machine {} already exists'.format(name))
        machine = pinassign.Machine(name, expected_time)
        self._machines.append(machine)
        self._machine_dict[name] = machine
    
    def add_player(self, name):
        if not name:
            raise InvalidPlayerError('The player must have a name')
        elif ' ' in name:
            raise InvalidPlayerError('Player names must not contain spaces')
        elif self._get_player(name) is not None:
            raise DuplicatePlayerError('The player {} already exists'.format(name))
        player = pinassign.Player(name)
        self._players.append(player)
        self._player_dict[name] = player
    
    def start(self):
        self._fail_if_running()
        if not self._machines:
            raise GameError('There must be at least one machine')
        elif not self._players:
            raise GameError('There must be at least one player')
        self._is_running = True
        return self._assign_all()
    
    def register_score(self, machine_name, player_name):
        self._fail_if_not_running()
        if not machine_name:
            raise InvalidMachineError('No machine name given')
        elif not player_name:
            raise InvalidPlayerError('No player name given')
        
        machine = self._get_machine(machine_name)
        if not machine:
            raise UnknownMachineError('Machine {} not recognized'.format(machine_name))
        player = self._get_player(player_name)
        if not player:
            raise UnknownPlayerError('Player {} not recognized'.format(player_name))
        try:
            return pinassign.player_finished_machine(
                machine, player, self._machines, self._players, self._scores, self.r)
        except ValueError as e:
            msg = 'Score for {} on {} already registered'.format(player_name, machine_name)
            raise DuplicateScoreError(msg) from e
    
    def is_finished(self):
        self._fail_if_not_running()
        return pinassign.is_everyone_finished(self._machines, self._players, self._scores)
    
    def reset_scores(self):
        self._fail_if_not_running()
        self._scores = []
    
    def _fail_if_running(self):
        if self._is_running:
            raise GameError('The game has already been started')
    
    def _fail_if_not_running(self):
        if not self._is_running:
            raise GameError('The game has not been started')
    
    def _assign_all(self):
        assert self._is_running
        return pinassign.assign_players(self._machines, self._players, self._scores, self.r)
    
    def _get_machine(self, name):
        return self._machine_dict.get(name, None)
    
    def _get_player(self, name):
        return self._player_dict.get(name, None)

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
        except GameError as e:
            print('Cannot add machine: {}'.format(e))
    
    def do_addplayer(self, s):
        try:
            self.game.add_player(s)
            print('Player {} added'.format(s))
        except PlayerError as e:
            print('Invalid addplayer command: {}'.format(e))
        except GameError as e:
            print('Cannot add player: {}'.format(e))
    
    def do_start(self, s):
        try:
            initial_assignments = self.game.start()
        except GameError as e:
            print('Cannot start game: {}'.format(e))
        else:
            print(GAME_STARTED)
            self._print_assignments(initial_assignments)
    
    def do_register(self, s):
        first_space_idx = s.find(' ')
        if first_space_idx == -1:
            print('Invalid register syntax. Example: register MGB Firepower')
            return
        player_name = s[:first_space_idx]
        machine_name = s[first_space_idx+1:]
        try:
            new_assignments = self.game.register_score(machine_name, player_name)
        except (GameError, InvalidMachineError, InvalidPlayerError) as e:
            print('Cannot register score: {}'.format(e))
        except UnknownMachineError as e:
            print(e)
            print('Use the machines command to see a list of machines')
        except UnknownPlayerError as e:
            print(e)
            print('Use the players command to see a list of players')
        except DuplicateScoreError as e:
            print(e)
            print('Use the scores command to see a list of scores')
        else:
            self._print_assignments(new_assignments)
            if self.game.is_finished():
                print(GAME_FINISHED)
    
    def do_reset(self, s):
        print(GAME_RESET)
        self.game = Game()
    
    def do_resetscores(self, s):
        print(SCORES_RESET)
        try:
            self.game.reset_scores()
        except GameError as e:
            print('Cannot reset scores: {}'.format(e))
    
    def _print_assignments(self, assignments):
        for idx, (machine, player) in enumerate(assignments):
            print('{}. {} plays {}'.format(idx+1, player.name, machine.name))

def run_cli():
    PinAssignCmd().cmdloop()

if __name__ == '__main__':
    run_cli()
