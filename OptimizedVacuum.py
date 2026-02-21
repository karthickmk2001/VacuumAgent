from __future__ import annotations
from dataclasses import dataclass
from typing import Tuple
import random
import statistics

Pos = Tuple[int, int]  #(row, col)


@dataclass
class Room:
    rows: int
    cols: int
    dirt_prob: float = 0.25
    seed: int = 0

    def __post_init__(self):
        rnd = random.Random(self.seed)
        # True = dirty, False = clean
        self.grid = [
            [(rnd.random() < self.dirt_prob) for _ in range(self.cols)]
            for _ in range(self.rows)
        ]

    def is_dirty(self, p: Pos) -> bool:
        r, c = p
        return self.grid[r][c]

    def clean(self, p: Pos) -> None:
        r, c = p
        self.grid[r][c] = False

    def dirt_count(self) -> int:
        return sum(
            1 for r in range(self.rows)
            for c in range(self.cols)
            if self.grid[r][c]
        )


@dataclass
class Percept:
    pos: Pos
    dirty_here: bool
    #Boundary sensors (agent knows if a move would hit a wall)
    wall_up: bool
    wall_down: bool
    wall_left: bool
    wall_right: bool


#OPTIMIZED SWEEP AGENT
class OptimizedVacuumAgent:
    """
    Zig-Zag Sweep Agent - Here the agent moves right across the first row, then down one row, then left across the second row, then down, and so on.
    Covers the grid row by row systematically, like scans first one row left to right, then the next row right to left, minimizing unnecessary movements.

    """

    def __init__(self):
        self.direction = 1  #1 : moving right

    def choose_action(self, percept: Percept) -> str:

        #Clean if it is dirty
        if percept.dirty_here:
            return "SUCK"

        #RIGHT
        if self.direction == 1:  #1 : moving right
            if not percept.wall_right:
                return "RIGHT"
            elif not percept.wall_down:
                self.direction = -1   #-1 : moving left
                return "DOWN"

        #LEFT
        else:
            if not percept.wall_left:
                return "LEFT"
            elif not percept.wall_down:
                self.direction = 1  #1 : moving right
                return "DOWN"

        return "NOOP"


def get_percept(room: Room, pos: Pos) -> Percept:
    r, c = pos
    return Percept(
        pos=pos,
        dirty_here=room.is_dirty(pos),
        wall_up=(r == 0),
        wall_down=(r == room.rows - 1),
        wall_left=(c == 0),
        wall_right=(c == room.cols - 1),
    )


def step(room: Room, pos: Pos, action: str) -> Pos:
    r, c = pos

    if action == "SUCK":
        room.clean(pos)
        return pos

    if action == "UP":
        return (r - 1, c) if r > 0 else pos

    if action == "DOWN":
        return (r + 1, c) if r < room.rows - 1 else pos

    if action == "LEFT":
        return (r, c - 1) if c > 0 else pos

    if action == "RIGHT":
        return (r, c + 1) if c < room.cols - 1 else pos

    return pos


def run_episode(
    rows: int = 6,
    cols: int = 6,
    dirt_prob: float = 0.25,
    room_seed: int = 1,
    #agent_seed: int = 1,  # Not used for deterministic agent but kept for consistency
    max_steps: int = 500,
    start: Pos = (0, 0),
) -> dict:

    room = Room(rows, cols, dirt_prob, seed=room_seed)
    agent = OptimizedVacuumAgent()

    pos = start
    initial_dirt = room.dirt_count()
    steps_taken = 0

    while steps_taken < max_steps and room.dirt_count() > 0:
        percept = get_percept(room, pos)
        action = agent.choose_action(percept)
        pos = step(room, pos, action)
        steps_taken += 1

    return {
        "rows": rows,
        "cols": cols,
        "initial_dirt": initial_dirt,
        "steps_taken": steps_taken,
        "dirt_remaining": room.dirt_count(),
        "cleaned_all": room.dirt_count() == 0,
    }


def benchmark(trials: int = 30, rows: int = 8, cols: int = 8, dirt_prob: float = 0.30):
    results = []

    for t in range(trials):
        res = run_episode(
            rows=rows,
            cols=cols,
            dirt_prob=dirt_prob,
            room_seed=1000 + t,
            max_steps=2000,
        )
        results.append(res)

    steps = [r["steps_taken"] for r in results]
    success = sum(1 for r in results if r["cleaned_all"])

    print("=== Optimized Systematic Sweep Vacuum Agent ===")
    print(f"Trials: {trials}, Grid: {rows}x{cols}, DirtProb: {dirt_prob}")
    print(f"Success: {success}/{trials}")
    print(
        f"Avg steps: {statistics.mean(steps):.1f} | "
        f"Median: {statistics.median(steps):.1f} | "
        f"Min/Max: {min(steps)}/{max(steps)}"
    )


if __name__ == "__main__":
    benchmark()