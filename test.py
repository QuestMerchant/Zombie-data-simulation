import numpy as np
from app import ZombieOutbreakSimulation

def test_movement():
    sim = ZombieOutbreakSimulation(n=10)
    initial_positions = sim.positions.copy()
    sim.update(frame=0)
    assert not np.array_equal(initial_positions, sim.positions)  # Movement occurred


def test_movement_bounds():
    sim = ZombieOutbreakSimulation(n=10)
    initial_positions = sim.positions.copy()
    sim.update(frame=0)
    assert all(0 <= pos[0] <= sim.grid_size for pos in sim.positions)  # Check x-axis
    assert all(0 <= pos[1] <= sim.grid_size for pos in sim.positions)  # Check y-axis


def test_state_change():
    sim = ZombieOutbreakSimulation(n=10)
    sim.states[0] = 0
    sim.states[1] = 2
    sim.positions[0] = sim.positions[1]
    sim.resolve_encounter(0, 1)
    assert sim.states[0] in [0,1,3]
    assert sim.states[1] in [2,3]



