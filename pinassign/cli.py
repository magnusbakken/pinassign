import cmd
from distutils.util import strtobool

import tabulate

from .game import *

INTRO = """Welcome to the PinAssign command line interface.

Before you can start assigning, you need to add machines and players.

To add a machine, type "addmachine NAME EXPECTEDTIME".
To add a player, type "addplayer NAME".

Player names must not contain spaces (use tags).

Once you've added all machines and at least one player, type "start". After the game has been started you can no longer add or remove machines.

Then use addscore PLAYERNAME MACHINENAME whenever a player has finished a machine.
"""

GAME_STARTED = """The game has started!

Here are the initial machine assignments:"""

GAME_FINISHED = """All players have finished all machines!

Use the reset command to start over from scratch, or resetscores to restart with the same machines and players."""

GAME_RESET = """The game has been reset. New machines and players must be added."""

SCORES_RESET = """The game scores have been reset.

The game is still set up with the same machines and players as before, but no scores are registered anymore.

You may now add or remove machines. You will have to use the start command again to start assigning players to machines."""


class PinAssignCmd(cmd.Cmd):

    def __init__(self):
        super().__init__()
        self.prompt = 'Command (? for help): '
        self.intro = INTRO
        self.game = Game()

    def do_machines(self, s):
        """Display a list of machines. This command may be used at any time."""
        machines = self.game.machines
        if not machines:
            print(
                'No machines have been added. Use the addmachine command to add machines.')
        else:
            print('Machines:')
            sorted_machines = sorted(machines, key=lambda m: m.name)
            table = [['Name', 'Ready', 'Expected Time']] + \
                [[m.name, m.ready, m.expected_time] for m in sorted_machines]
            print(tabulate.tabulate(table))

    def do_players(self, s):
        """Display a list of players. This command may be used at any time."""
        players = self.game.players
        if not players:
            print('No players have been added. Use the addplayer command to add players.')
        else:
            print('Players:')
            sorted_players = sorted(players, key=lambda p: p.name)
            table = [['Name', 'Ready', 'Expected Time Spent']] + \
                [[p.name, p.ready, p.expected_time_spent]
                    for p in sorted_players]
            print(tabulate.tabulate(table))

    def do_scores(self, s):
        """Display a list of scores.

This command may be used at any time, but will never give any results if the game hasn't been started yet."""
        scores = self.game.scores
        if not scores:
            print('No scores have been registered. Use the addscore command to add a score (after starting the game).')
        else:
            print('Scores:')
            sorted_scores = sorted(
                scores, key=lambda s: (s.machine.name, s.player.name))
            table = [['Machine', 'Player']] + \
                [[s.machine.name, s.player.name] for s in sorted_scores]
            print(tabulate.tabulate(table))

    def do_addmachine(self, s):
        """Adds a machine to the game. Syntax: addmachine MACHINENAME EXPECTEDTIME.

The MACHINENAME may contain any symbols. The EXPECTEDTIME must be an integer greater than zero.

Each machine name must be unique.

Machines may not be added after the game has been started with the start command."""
        last_space_idx = s.rfind(' ')
        if last_space_idx == -1:
            print('Invalid addmachine syntax. Example: "addmachine Medieval Madness 5"')
            return
        name = s[:last_space_idx]
        try:
            expected_time = int(s[last_space_idx + 1:])
        except ValueError:
            value = s[last_space_idx + 1:]
            print('Invalid expected time: {} (must be integer)'.format(value))
            return
        try:
            self.game.add_machine(name, expected_time)
        except MachineError as e:
            print('Invalid addmachine command: {}'.format(e))
        except GameError as e:
            print('Cannot add machine: {}'.format(e))
        else:
            print('Machine {} added with expected time {}'.format(
                name, expected_time))

    def do_addplayer(self, s):
        """Adds a player to the game. Syntax: addplayer PLAYERNAME.

The player name may not contain spaces. Use player tags or first names.

Each player name must be unique."""
        try:
            self.game.add_player(s)
        except PlayerError as e:
            print('Invalid addplayer command: {}'.format(e))
        except GameError as e:
            print('Cannot add player: {}'.format(e))
        else:
            print('Player {} added'.format(s))

    def do_removemachine(self, s):
        """Removes a machine from the game. Syntax: removemachine MACHINENAME.

The MACHINENAME must match a machine that was previously added.

Machines may not be removed after the game has been started with the start command."""
        try:
            self.game.remove_machine(s)
        except MachineError as e:
            print('Invalid removemachine command: {}'.format(e))
        except GameError as e:
            print('Cannot remove machine: {}'.format(e))
        else:
            print('Machine {} removed'.format(s))

    def do_removeplayer(self, s):
        """Removes a player from the game. Syntax: removeplayer PLAYERNAME.

The PLAYERNAME must match a player that was previously added.

Players may be removed while the game is ongoing, but if the removed player was previously assigned to a machine you will have to fix the Ready state of that machine with the machineready command."""
        if self.game.is_running and not self._get_confirmation(
                'The game has started. Are you sure you want to remove a player?'):
            return
        try:
            self.game.remove_player(s)
        except PlayerError as e:
            print('Invalid removeplayer command: {}'.format(e))
        except GameError as e:
            print('Cannot remove player: {}'.format(e))
        else:
            print('Player {} removed'.format(s))

    def do_addscore(self, s):
        """Registers a score. Syntax: addscore PLAYERNAME MACHINENAME.

The player must not already have a registered score on the machine.

There is no verification that the player/machine combination matches the one recommended by the algorithm, nor that the player and the machine are currently marked as unready.

If a player has not played the recommended machine, you may need to manually fix the ready state of the player and/or machine with the commands playerready, playerbusy, machineready, machinebusy."""
        player_name, machine_name = self._parse_player_and_machine(s)
        if not player_name or not machine_name:
            print('Invalid addscore syntax. Example: addscore MGB Firepower')
        try:
            new_assignments = self.game.add_score(machine_name, player_name)
        except (GameError, InvalidMachineError, InvalidPlayerError) as e:
            print('Cannot add score: {}'.format(e))
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
            print('Score for player {} added for game {}'.format(
                player_name, machine_name))
            self._print_assignments(new_assignments)
            if self.game.is_finished():
                print(GAME_FINISHED)

    def do_removescore(self, s):
        """Removes a score for a player/machine. Syntax: removescore PLAYERNAME MACHINENAME.

The PLAYERNAME must match a player that has been added, the MACHINENAME must match a machine that has been added, and the player must have been registered as having played that machine.

This will not set the player or the machine to be ready if they're currently busy."""
        if self.game.is_running and not self._get_confirmation(
                'Are you sure you want to remove a score?'):
            return
        player_name, machine_name = self._parse_player_and_machine(s)
        if not player_name or not machine_name:
            print('Invalid removescore syntax. Example: removescore MGB Firepower')
        try:
            self.game.remove_score(machine_name, player_name)
        except MachineError as e:
            print('Invalid machine: {}'.format(e))
        except PlayerError as e:
            print('Invalid player: {}'.format(e))
        except GameError as e:
            print('Cannot remove score: {}'.format(e))
        else:
            print('Score for player {} on machine {} removed'.format(
                player_name, machine_name))

    def do_start(self, s):
        """Starts the game. This is necessary for scores to be added, and for the algorithm to start running.

At least one machine and at least one player must be added before starting the game.

Once this command has been run, machines may no longer be added. Players can still be added, however.

To reset a running game completely, use the reset command. This will remove all machines and players. To reset the scores only, use the resetscores command."""
        try:
            initial_assignments = self.game.start()
        except GameError as e:
            print('Cannot start game: {}'.format(e))
        else:
            print(GAME_STARTED)
            self._print_assignments(initial_assignments)

    def do_reset(self, s):
        """Resets a game completely.

This will remove all machines, players and scores from the running game.

To reset only the scores, use the resetscores command instead."""
        if self._get_confirmation('Are you sure you want to reset the game?'):
            self.game = Game()
            print(GAME_RESET)

    def do_resetscores(self, s):
        """Resets the scores of a running game.

This will remove all registered scores for the game, but machines and players will be kept.

After running this command, machines may be added. The start command must be used again before new scores may be added."""
        if self._get_confirmation(
                'Are you sure you want to reset the scores?'):
            try:
                self.game.reset_scores()
            except GameError as e:
                print('Cannot reset scores: {}'.format(e))
            else:
                print(SCORES_RESET)

    def do_assignments(self, s):
        """Gets current assignments.

This is only necessary when the playerready/machineready commands have been used manually. In other cases the assignments are given when a score is registered.

This will only give current assignments. It will not repeat the previous ones."""
        try:
            assignments = list(self.game.assign())
        except GameError as e:
            print('Cannot get assignments: {}'.format(e))
        else:
            if assignments:
                self._print_assignments(assignments)
            else:
                print('No new assignments available')

    def do_playerready(self, s):
        """Marks a player as ready.

Use this command when players have played machines in a different way than recommended by the algorithm.

For instance if, the algorithm recommended that Player1 play MachineA, but Player2 started playing it instead, execute playerready Player1 and playerbusy Player2.

You can also use this command if the player was marked as temporarily unable to play with the playerbusy command, and is now back in business."""
        try:
            self.game.set_player_ready(s, True)
        except GameError as e:
            print('Cannot mark player as ready: {}'.format(e))
        else:
            print('Player {} has been marked as ready'.format(s))

    def do_playerbusy(self, s):
        """Marks a player as busy.

Use this command when players have played machines in a different way than recommended by the algorithm.

For instance if, the algorithm recommended that Player1 play MachineA, but Player2 started playing it instead, execute playerready Player1 and playerbusy Player2.

You can also use this command if the player is temporarily unable to play."""
        try:
            self.game.set_player_ready(s, False)
        except GameError as e:
            print('Cannot mark player as busy: {}'.format(e))
        else:
            print('Player {} has been marked as busy'.format(s))

    def do_machineready(self, s):
        """Marks a machine as ready.

Use this command when players have played machines in a different way than recommended by the algorithm.

For instance if, the algorithm recommended that Player1 play MachineA, but he or she started MachineB instead, execute machineready MachineA and machinebusy MachineB.

You can also use this command if the machine was marked as temporarily out of order with the machinebusy command, and is now back in business."""
        try:
            self.game.set_machine_ready(s, True)
        except GameError as e:
            print('Cannot mark machine as ready: {}'.format(e))
        else:
            print('Machine {} has been marked as ready'.format(s))

    def do_machinebusy(self, s):
        """Marks a machine as busy.

Use this command when players have played machines in a different way than recommended by the algorithm.

For instance if, the algorithm recommended that Player1 play MachineA, but he or she started MachineB instead, execute machineready MachineA and machinebusy MachineB.

You can also use this command if the machine is temporarily out of order."""
        try:
            self.game.set_machine_ready(s, False)
        except GameError as e:
            print('Cannot mark machine as busy: {}'.format(e))
        else:
            print('Machine {} has been marked as busy'.format(s))

    def do_exit(self, s):
        """Exits the program."""
        return self._get_confirmation('Are you sure you want to exit?')

    def do_quit(self, s):
        """Exits the program."""
        return self.do_exit(s)

    def _print_assignments(self, assignments):
        for idx, (machine, player) in enumerate(assignments):
            print('{}. {} should now play {}'.format(
                idx + 1, player.name, machine.name))

    def _get_confirmation(self, msg):
        return strtobool(input('{} (y/n): '.format(msg)))

    def _parse_player_and_machine(self, s):
        first_space_idx = s.find(' ')
        if first_space_idx == -1:
            return (None, None)
        player_name = s[:first_space_idx]
        machine_name = s[first_space_idx + 1:]
        return (player_name, machine_name)


def run_cli():
    PinAssignCmd().cmdloop()

if __name__ == '__main__':
    run_cli()
