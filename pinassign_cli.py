import cmd

from game_api import *

INTRO = """Welcome to the PinAssign command line interface.

Before you can start assigning, you need to add machines and players.
Machines and players can also be added using text files passed as input to this script.

To add a machine, type "addmachine NAME EXPECTEDTIME".
To add a player, type "addplayer NAME".

Player names must not contain spaces (use tags).

Once you've added all machines and at least one player, type "start". After the game has been started you can no longer add machines.

Then use register PLAYERNAME MACHINENAME whenever a player has finished a machine.
"""

GAME_STARTED = """The game has started!

Here are the initial machine assignments:"""

GAME_FINISHED = """All players have finished all machines!

Use the reset command to start over from scratch, or resetscores to restart with the same machines and players."""

GAME_RESET = """The game has been reset. New machines and players must be added."""

SCORES_RESET = """The game scores have been reset.

The game is still running with the same machines and players as before, but no scores are registered anymore."""

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
            print('No machines have been added. Use the addmachine command to add machines.')
        else:
            print('Machines:')
            for machine in sorted(machines, key=lambda m: m.name):
                print('- {} (expected time {})'.format(machine.name, machine.expected_time))
    
    def do_players(self, s):
        """Display a list of players. This command may be used at any time."""
        players = self.game.players
        if not players:
            print('No players have been added. Use the addplayer command to add players.')
        else:
            print('Players:')
            for player in sorted(players, key=lambda p: p.name):
                print('- {}'.format(player.name))
    
    def do_scores(self, s):
        """Display a list of scores.

This command may be used at any time, but will never give any results if the game hasn't been started yet."""
        scores = self.game.scores
        if not scores:
            print('No scores have been registered. Use the register command to add a score (after starting the game).')
        else:
            for score in sorted(scores, key=lambda s: (s.machine.name, s.player.name)):
                print('- {}: {}'.format(score.machine.name, score.player.name))
    
    def do_addmachine(self, s):
        """Adds a machine to the game. Syntax: addmachine MACHINENAME EXPECTEDTIME

The MACHINENAME may contain any symbols. The EXPECTEDTIME must be an integer greater than zero.

Each machine name must be unique.

Machines may not be added after the game has been started with the start command."""
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
        """Adds a player to the game. Syntax: addplayer PLAYERNAME.

The player name may not contain spaces. Use player tags or first names.

Each player name must be unique."""
        try:
            self.game.add_player(s)
            print('Player {} added'.format(s))
        except PlayerError as e:
            print('Invalid addplayer command: {}'.format(e))
        except GameError as e:
            print('Cannot add player: {}'.format(e))
    
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
    
    def do_register(self, s):
        """Registers a score. Syntax: register PLAYERNAME MACHINENAME.

The player must not already have a registered score on the machine.

There is no verification that the player/machine combination matches the one recommended by the algorithm, nor that the player and the machine are currently marked as unready.

If a player has not played the recommended machine, you may need to manually fix the ready state of the player and/or machine with the commands playerready, playerbusy, machineready, machinebusy."""
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
        """Resets a game completely.

This will remove all machines, players and scores from the running game.

To reset only the scores, use the resetscores command instead."""
        print(GAME_RESET)
        self.game = Game()
    
    def do_resetscores(self, s):
        """Resets the scores of a running game.

This will remove all registered scores for the game, but machines and players will be kept.

After running this command, machines may be added. The start command must be used again before new scores may be added."""
        print(SCORES_RESET)
        try:
            self.game.reset_scores()
        except GameError as e:
            print('Cannot reset scores: {}'.format(e))
    
    def do_playerready(self, s):
        """Marks a player as ready.

Use this command when players have played machines in a different way than recommended by the algorithm.

For instance if, the algorithm recommended that Player1 play MachineA, but Player2 started playing it instead, execute playerready Player1 and playerbusy Player2.

You can also use this command if the player was marked as temporarily unable to play with the playerbusy command, and is now back in business."""
        try:
            self.game.set_player_ready(True)
        except GameError as e:
            print('Cannot mark player as ready: {}'.format(e))
    
    def do_playerbusy(self, s):
        """Marks a player as busy.

Use this command when players have played machines in a different way than recommended by the algorithm.

For instance if, the algorithm recommended that Player1 play MachineA, but Player2 started playing it instead, execute playerready Player1 and playerbusy Player2.

You can also use this command if the player is temporarily unable to play."""
        try:
            self.game.set_player_ready(False)
        except GameError as e:
            print('Cannot mark player as busy: {}'.format(e))
    
    def do_machineready(self, s):
        """Marks a machine as ready.

Use this command when players have played machines in a different way than recommended by the algorithm.

For instance if, the algorithm recommended that Player1 play MachineA, but he or she started MachineB instead, execute machineready MachineA and machinebusy MachineB.

You can also use this command if the machine was marked as temporarily out of order with the machinebusy command, and is now back in business."""
        try:
            self.game.set_machine_ready(True)
        except GameError as e:
            print('Cannot mark machine as ready: {}'.format(e))
    
    def do_machinebusy(self, s):
        """Marks a machine as busy.

Use this command when players have played machines in a different way than recommended by the algorithm.

For instance if, the algorithm recommended that Player1 play MachineA, but he or she started MachineB instead, execute machineready MachineA and machinebusy MachineB.

You can also use this command if the machine is temporarily out of order."""
        try:
            self.game.set_machine_ready(False)
        except GameError as e:
            print('Cannot mark machine as busy: {}'.format(e))
    
    def _print_assignments(self, assignments):
        for idx, (machine, player) in enumerate(assignments):
            print('{}. {} should now play {}'.format(idx+1, player.name, machine.name))

def run_cli():
    PinAssignCmd().cmdloop()

if __name__ == '__main__':
    run_cli()
