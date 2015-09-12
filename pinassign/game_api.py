import random

import .pinassign


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
        return self._players

    @property
    def scores(self):
        return self._scores

    @property
    def is_running(self):
        return self._is_running

    def add_machine(self, name, expected_time):
        self._fail_if_running()
        if not name:
            raise InvalidMachineError('The machine must have a name')
        elif expected_time <= 0:
            raise InvalidMachineError(
                'The expected time of the machine cannot be zero or negative')
        elif self._get_machine(name) is not None:
            raise DuplicateMachineError(
                'The machine {} already exists'.format(name))
        machine = pinassign.Machine(name, expected_time)
        self._machines.append(machine)
        self._machine_dict[name] = machine

    def remove_machine(self, name):
        self._fail_if_running()
        if not name:
            raise InvalidMachineError('The machine must have a name')
        machine = self._get_machine(name)
        if not machine:
            raise UnknownMachineError('Machine {} not recognized'.format(name))
        self._machines.remove(machine)
        del self._machine_dict[name]

    def add_player(self, name):
        if not name:
            raise InvalidPlayerError('The player must have a name')
        elif ' ' in name:
            raise InvalidPlayerError('Player names must not contain spaces')
        elif self._get_player(name) is not None:
            raise DuplicatePlayerError(
                'The player {} already exists'.format(name))
        player = pinassign.Player(name)
        self._players.append(player)
        self._player_dict[name] = player

    def remove_player(self, name):
        if not name:
            raise InvalidPlayerError('The player must have a name')
        player = self._get_player(name)
        if not player:
            raise UnknownPlayerError('Player {} not recognized'.format(name))
        self._players.remove(player)
        del self._player_dict[name]

    def add_score(self, machine_name, player_name):
        self._fail_if_not_running()
        if not machine_name:
            raise InvalidMachineError('No machine name given')
        elif not player_name:
            raise InvalidPlayerError('No player name given')
        machine = self._get_machine(machine_name)
        if not machine:
            raise UnknownMachineError(
                'Machine {} not recognized'.format(machine_name))
        player = self._get_player(player_name)
        if not player:
            raise UnknownPlayerError(
                'Player {} not recognized'.format(player_name))
        try:
            return pinassign.player_finished_machine(
                machine, player, self._machines, self._players, self._scores, self.r)
        except ValueError as e:
            msg = 'Score for {} on {} already exists'.format(
                player_name, machine_name)
            raise DuplicateScoreError(msg) from e

    def remove_score(self, machine_name, player_name):
        self._fail_if_not_running()
        if not machine_name:
            raise InvalidMachineError('No machine name given')
        elif not player_name:
            raise InvalidPlayerError('No player name given')
        machine = self._get_machine(machine_name)
        if not machine:
            raise UnknownMachineError(
                'Machine {} not recognized'.format(machine_name))
        player = self._get_player(player_name)
        if not player:
            raise UnknownPlayerError(
                'Player {} not recognized'.format(player_name))
        score = pinassign.Score(machine, player)
        self._scores.remove(score)

    def start(self):
        self._fail_if_running()
        if not self._machines:
            raise GameError('There must be at least one machine')
        elif not self._players:
            raise GameError('There must be at least one player')
        self._is_running = True
        return self._assign_all()

    def is_finished(self):
        self._fail_if_not_running()
        return pinassign.is_everyone_finished(
            self._machines, self._players, self._scores)

    def reset_scores(self):
        self._fail_if_not_running()
        self._scores = []
        self._is_running = False

    def assign(self):
        self._fail_if_not_running()
        return self._assign_all()

    def set_machine_ready(self, machine_name, ready):
        self._fail_if_not_running()
        if not machine_name:
            raise InvalidMachineError('No machine name given')
        machine = self._get_machine(machine_name)
        if not machine:
            raise UnknownMachineError(
                'Machine {} not recognized'.format(machine_name))
        elif machine.ready == ready:
            desc = 'ready' if ready else 'busy'
            raise GameError(
                'Machine {} is already {}'.format(
                    machine_name, desc))
        machine.ready = ready

    def set_player_ready(self, player_name, ready):
        self._fail_if_not_running()
        if not player_name:
            raise InvalidPlayerError('No player name given')
        player = self._get_player(player_name)
        if not player:
            raise UnknownPlayerError(
                'Player {} not recognized'.format(player_name))
        elif player.ready == ready:
            desc = 'ready' if ready else 'busy'
            raise GameError(
                'Player {} is already {}'.format(
                    player_name, desc))
        player.ready = ready

    def _fail_if_running(self):
        if self._is_running:
            raise GameError('The game has already been started')

    def _fail_if_not_running(self):
        if not self._is_running:
            raise GameError('The game has not been started')

    def _assign_all(self):
        assert self._is_running
        return pinassign.assign_players(
            self._machines, self._players, self._scores, self.r)

    def _get_machine(self, name):
        return self._machine_dict.get(name, None)

    def _get_player(self, name):
        return self._player_dict.get(name, None)
