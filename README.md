# PinAssign

An implementation of an algorithm that assigns players to machines during a pinball tournament.

## Purpose

The purpose of this project is to provide an algorithm for automatically assigning players to machines during a pinball tournament. The following requirements must be met:

1. All players must play all machines.
2. No player must play the same machine more than once.

This algorithm tries to minimize the overall time spent by tracking the progress of each individual player. Instead of counting every machine equally, it accounts for the fact that different machines usually take different amounts of time to play. Easier machines generally last longer.

The algorithm will also generally prevent players from waiting for long periods between each time they play, but this is not a explicit goal of the algorithm. Only the overall time is considered important.

## Description

### Terminology:

- M = Machine
- P = Player
- S = Score (combination of machine and player)
- ET = Expected Time for a machine
- ETS = Expected Time Spent for a player (sum of ET for finished machines)

Machines and players have a boolean Ready state. If a machine is not ready, it's because some player is currently playing it. If a player is not ready, it's because that player is currently playing some machine. Optionally, a machine or player may also be marked as not ready if they're otherwise unavailable, for instance if a machine requires maintenance or a player has temporarily left.

### Overall algorithm:

1. Let S = An empty list of scores
2. Let RM = All machines M where M.Ready = true
3. Let RP = All players P where P.Ready = true
4. For each M in RM:
    1. Let RPM = All players P in RP such that (M, P) is not in S
    2. Randomly choose a P from RPM with the lowest possible P.ETS
    3. Set M.Ready = false
    4. Set P.Ready = false
5. Wait until a player finishes a machine. When P finishes M:
    1. Add (M, P) to S.
    2. Set M.Ready = true
    3. Set P.Ready = true
    4. Increment P.ETS by M.ET
6. If for every (M, P), (M, P) is in S, the algorithm is finished; otherwise go to (2)

## Improvements

The algorithm is all about trying to get machines out of the way as soon as possible. There are many possible ways to improve this.

1. The expected time of each machine could be adaptive.
2. We could account for the average playing time of each individual player. Some people take much longer than others, and should therefore be assigned machines earlier.
3. We could even track players' performance on particular machines. If a player is not very good overall but is an expert at a particular machine, they should play that one as soon as possible.
4. When multiple machines become available at roughly the same time, we could ensure that players with little progress are assigned the slowest machines first.

This algorithm is undoubtedly an instance of some more general problem that has already been solved.