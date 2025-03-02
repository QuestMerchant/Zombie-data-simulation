import numpy as np
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
from matplotlib.animation import FuncAnimation


def main():
    print("Population density:")
    while True:
        try:
            population = int(input("Please enter a valid integer between 10 & 1000: "))
            if 10 <= population <= 1000:
                break
        except ValueError:
            pass

    simulation = ZombieOutbreakSimulation(population)
    simulation.run_simulation()


class ZombieOutbreakSimulation:
    def __init__(self, n):
        # Parameters
        self.n = n
        self.grid_size = 100
        self.zombie_sense = 15.0  # Radius of zombie detecting uninfected
        self.zombie_speed = 1.0
        self.uninfected_sense = 12.0
        self.uninfected_speed = 0.8
        self.initial_infected = 1
        self.encounter_distance = 1.0
        self.deaths = 0  # Human deaths to realize zombies are a life or death situation
        self.attacked = 0  # If no deaths but this reaches a high volume of attacks, people would realize.
        self.threat = False

        """States of infection. 0 = uninfected, 1 = infected, 2 = zombie, 3 = dead"""

        # Initialize states
        self.states = np.zeros(self.n, dtype=int)  # Default all to uninfected (0)
        # Select random uninfected to be patient zero
        p_zero = np.random.choice(self.n, self.initial_infected, replace=False)
        self.states[p_zero] = 2

        # Initialize fight (1) or flight (0)
        self.strategies = np.zeros(self.n, dtype=int)  # Default to flee
        # 20% chance to choose fight
        for i in self.strategies:
            if np.random.rand() < 0.2:
                self.strategies[i] = 1

        # Initialize infection timer
        self.infected = np.zeros(self.n)
        self.infection_limit = 60

        # Initialize positions
        self.positions = np.random.rand(self.n, 2) * self.grid_size

        # Initialize target locations
        self.target_locations = np.random.rand(self.n, 2) * self.grid_size

        # Color map: 0 = green (uninfected), 1 = orange (infected), 2 = red (zombie), 3 = black (dead)
        self.colors = ['green', 'orange', 'red', 'black']
        self.custom_cmap = mcolors.ListedColormap(self.colors)
        self.norm = mcolors.BoundaryNorm([0, 1, 2, 3, 4], len(self.colors))

        # Setup plot
        self.fig, self.ax = plt.subplots()
        self.scat = self.ax.scatter(self.positions[:, 0], self.positions[:, 1], c=self.states, cmap=self.custom_cmap,
                                    norm=self.norm, s=10)  # Test size
        self.ax.set_xlim(0, self.grid_size)
        self.ax.set_ylim(0, self.grid_size)
        self.ax.set_title('Zombie Outbreak Simulation')

    def update(self, frame):
        """Update positions, states, and decisions"""
        # Determine threat
        if self.deaths > 1 or self.attacked >= 5:
            self.threat = True
        # Move each individual based on its state
        for i in range(self.n):
            if self.states[i] == 0:  # Uninfected
                # Identify zombies and positions
                zombies = np.where(self.states == 2)[0]
                zombie_positions = self.positions[zombies]
                # Calculate distance from zombies
                distances = np.linalg.norm(zombie_positions - self.positions[i], axis=1)
                # Filter to nearby zombies
                zombies_nearby = zombies[distances <= self.uninfected_sense]

                # Check for nearby zombies
                if len(zombies_nearby) >= 1 and self.threat:
                    # Check strategy
                    if self.strategies[i] == 0:  # Flight
                        # Flee zombies
                        self.flee(i, zombies_nearby)
                    else:
                        # Check if within encounter range
                        encounter = zombies[distances <= self.encounter_distance]
                        if len(encounter) > 0:
                            target = encounter[0]
                            self.resolve_encounter(i, target)
                        else:
                            # Move toward first zombie
                            target = zombies_nearby[0]
                            # Create vector pointing towards zombie
                            direction = self.positions[target] - self.positions[i]
                            try:
                                movement = direction / np.linalg.norm(direction) * self.uninfected_speed
                                self.positions[i] += movement
                            except ZeroDivisionError:
                                self.resolve_encounter(i, zombies_nearby[0])
                            # Check for encounter with targeted zombie
                            distance = np.linalg.norm(self.positions[target] - self.positions[i])
                            if distance <= self.encounter_distance:
                                self.resolve_encounter(i, zombies_nearby[0])
                else:
                    if self.check_destination(i):
                        self.update_target_location(i)
                    else:
                        self.advance(i)

            elif self.states[i] == 1:  # Infected
                # Check for nearby uninfected
                uninfected = np.where(self.states == 0)[0]
                distances = np.linalg.norm(self.positions[uninfected] - self.positions[i], axis=1)
                uninfected_nearby = uninfected[distances <= self.encounter_distance]
                if len(uninfected_nearby) > 0:
                    # Group decision
                    kill_votes = np.random.choice([0, 1], size=len(uninfected_nearby))  # 0 to spare, 1 to kill
                    # Majority wins
                    if np.sum(kill_votes) > len(uninfected_nearby) // 2:
                        self.states[i] = 3  # Dead
                    else:
                        # Check infection state
                        if self.infected[i] >= self.infection_limit:
                            self.states[i] = 2
                        else:
                            self.infected[i] += 1
                # Check infection state
                elif self.infected[i] >= self.infection_limit:
                    self.states[i] = 2
                else:
                    self.infected[i] += 1

            elif self.states[i] == 2:  # Zombie
                # Identify uninfected and positions
                uninfected = np.where(self.states == 0)[0]  # Array of states indices (int)
                uninfected_positions = self.positions[uninfected]  # 2D Array of x,y coord pairs
                # Check if any are within zombie sense radius
                distances = np.linalg.norm(uninfected_positions - self.positions[i], axis=1)  # Array of floats for each position.
                nearby = uninfected[distances <= self.zombie_sense]  # Array of states indices
                if len(nearby) == 0:
                    # Move randomly if none are sensed
                    movement = (np.random.rand(2) - 0.5) * (self.zombie_speed / 2)  # Roam at half pace
                    self.positions[i] += movement
                else:
                    # Check if within encounter range
                    encounter = uninfected[distances <= self.encounter_distance]  # Array of indices for nearby
                    if len(encounter) > 0:
                        # Pick first target
                        target = encounter[0]
                        self.resolve_encounter(target, i)
                    else:
                        # Chase nearest uninfected
                        # Get nearby distances
                        nearby_distances = distances[distances <= self.zombie_sense]  # Array of distances of only nearby
                        """or nearby_distances = np.linalg.norm(self.positions[nearby] - self.positions[i], axis=1)"""
                        closest_distance_index = np.argmin(nearby_distances)  # Index to nearby distance of shortest distance.
                        closest_uninfected_index = nearby[closest_distance_index]  # Mapping back to nearby index
                        closest_uninfected = self.positions[closest_uninfected_index]
                        # Create vector pointing towards the closest position
                        direction = closest_uninfected - self.positions[i]
                        # Work out max distance required
                        target_distance = nearby_distances[closest_distance_index]
                        if target_distance > (self.zombie_speed - 0.5):  # Checks if the max movement is less than the target encounter distance
                            # Move full speed
                            movement = direction / target_distance * self.zombie_speed
                            # Update position
                            self.positions[i] += movement
                        else:
                            movement = direction / target_distance * (target_distance - self.encounter_distance)
                            # Update position
                            self.positions[i] += movement
                            self.resolve_encounter(closest_uninfected, i)

        # Update plot
        self.positions = np.clip(self.positions, 0, self.grid_size)  # Creates a boundary
        self.scat.set_offsets(self.positions)
        self.scat.set_array(self.states)
        return [self.scat]

    def flee(self, person, nearby):
        # Collect all zombie positions and get an average position
        nearby_positions = self.positions[nearby]
        avg_position = np.mean(nearby_positions, axis=0)  # Collects a 1D array of a single (x, y) coord pair
        direction = self.positions[person] - avg_position
        norm = np.linalg.norm(direction)
        if norm > 1e-6: # Threshold to avoid division by 0.0
            movement = direction / norm * self.uninfected_speed
        else:
            movement = (np.random.rand(2) - 0.5) * self.uninfected_speed
        self.positions[person] += movement

    def update_target_location(self, person):
        self.target_locations[person] = np.random.rand(2) * self.grid_size

    def check_destination(self, person):
        distance = np.linalg.norm(self.positions[person] - self.target_locations[person])
        if distance < 0.5:
            return True

    # Move towards target location
    def advance(self, person):
        direction = self.target_locations[person] - self.positions[person]
        movement = direction / np.linalg.norm(direction) * (self.uninfected_speed / 2)
        self.positions[person] += movement

    def resolve_encounter(self, uninfected_id, zombie_id):
        # If uninfected was fleeing, either infected or dead
        if self.strategies[uninfected_id] == 0:
            if np.random.rand() < 0.5:
                self.states[uninfected_id] = 1  # Infected
                self.attacked += 1
                # 30 % chance of killing the zombie
                if np.random.rand() < 0.3:
                    self.states[zombie_id] = 3  # dead
            else:
                self.states[uninfected_id] = 3  # dead
                self.deaths += 1
        else:
            if self.deaths == 0:
                # Unexpected attack results 50/50 chance
                if np.random.rand() <0.5:
                    self.states[zombie_id] = 3  # dead
                    # 75% chance of uninfected getting infected during the encounter
                    if np.random.rand() < 0.75:
                        # Change state to infected
                        self.states[uninfected_id] = 1
                        self.attacked += 1
            # 70% chance of winning using weapons
            elif np.random.rand() < 0.7:
                # Uninfected wins
                self.states[zombie_id] = 3  # Change zombies state to dead
                # 30% chance of uninfected getting infected during the encounter
                if np.random.rand() < 0.3:
                    # Change state to infected
                    self.states[uninfected_id] = 1
                    self.attacked += 1
            else:
                # Zombie wins, 30% chance of uninfected dying.
                if np.random.rand() < 0.3:
                    self.states[uninfected_id] = 3  # Change state to dead
                    self.deaths += 1
                else:
                    self.states[uninfected_id] = 1  # Change state to infected
                    self.attacked += 1

    def run_simulation(self, save_as=None):
        animation = FuncAnimation(self.fig, self.update, frames=10, interval=100, blit=True)  # Test interval
        if save_as:
            from matplotlib.animation import FFMpegWriter
            writer = FFMpegWriter(fps=10, metadata=dict(artist='Zombie Outbreak Simulation'))
            animation.save(save_as, writer=writer)
            print(f"Animation saved as {save_as}")

        plt.show()
        return animation


if __name__ == "__main__":
    main()
