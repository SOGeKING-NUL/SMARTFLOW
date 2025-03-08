import pygame
import sys
import os
import math
import random
import time
import threading
from collections import defaultdict
import numpy as np

# Configuration
defaultRed = 150
defaultYellow = 5
defaultGreen = 20
simTime = 3000
timeElapsed = 0
currentGreen = 0
currentYellow = 0
noOfSignals = 4

# RL Parameters
alpha = 0.1  # Learning rate
gamma = 0.6  # Discount factor
epsilon = 0.1  # Exploration rate
min_phase_duration = 10
max_phase_duration = 60

# Vehicle parameters
speeds = {'car':2.25,
            'bus':1.8, 
            'truck':1.8, 
            'rickshaw':2, 
            'bike':2.5, 
            'ambulance':2.5, 
            'fireVan':2, 
            'police':2.25
        }  # average speeds of vehicles

vehicleTypes = {
    0:'car', 
    1:'bus', 
    2:'truck', 
    3:'rickshaw', 
    4:'bike',
    5:'ambulance',    
    6:'fireVan',      
    7:'police'
}
directionNumbers = {0: 'right', 1: 'down', 2: 'left', 3: 'up'}

# Coordinates
x = {'right': [0, 0, 0], 'down': [755, 727, 697], 'left': [1400, 1400, 1400], 'up': [602, 627, 657]}
y = {'right': [348, 370, 398], 'down': [0, 0, 0], 'left': [498, 466, 436], 'up': [800, 800, 800]}
vehicles = {'right': {0: [], 1: [], 2: [], 'crossed': 0},
            'down': {0: [], 1: [], 2: [], 'crossed': 0},
            'left': {0: [], 1: [], 2: [], 'crossed': 0},
            'up': {0: [], 1: [], 2: [], 'crossed': 0}}
stopLines = {'right': 590, 'down': 330, 'left': 800, 'up': 535}
defaultStop = {'right': 580, 'down': 320, 'left': 810, 'up': 545}
mid = {'right': {'x': 705, 'y': 445}, 'down': {'x': 695, 'y': 450}, 
        'left': {'x': 695, 'y': 425}, 'up': {'x': 695, 'y': 400}}

# Display coordinates
signalCoods = [(530, 230), (810, 230), (810, 570), (530, 570)]
signalTimerCoods = [(530, 210), (810, 210), (810, 550), (530, 550)]
vehicleCountCoods = [(480, 210), (880, 210), (880, 550), (480, 550)]

class QLearningAgent:

    def __init__(self):
        self.q_table = defaultdict(float)
        self.alpha = alpha  # Learning rate
        self.gamma = gamma  # Discount factor
        self.epsilon = epsilon  # Exploration rate

    def state_to_tuple(self, state):
        """
        Convert the complex state dictionary to a hashable tuple
        
        Args:
        state (list): Complex state representation
        
        Returns:
        tuple: Simplified, hashable state representation
        """
        # Extract key information from the state
        simplified_state = []
        for direction in state:
            # Add total vehicles and emergency vehicles for each direction
            simplified_state.extend([
                direction['total_vehicles'], 
                direction['emergency_vehicles']
            ])
        return tuple(simplified_state)

    def get_action(self, state):
        # Flatten state for action selection
        flat_state = [
            item 
            for direction in state 
            for lane in direction['lanes'] 
            for item in [lane['count'], lane['emergency_count']]
        ]
        
        if random.uniform(0, 1) < self.epsilon:
            return random.choice(range(4))
        
        return max(range(4), key=lambda a: self.q_table.get((tuple(flat_state), a), 0))
    
    def update_q_table(self, old_state, action, reward, new_state):
        # Flatten states
        old_flat_state = [
            item 
            for direction in old_state 
            for lane in direction['lanes'] 
            for item in [lane['count'], lane['emergency_count']]
        ]
        new_flat_state = [
            item 
            for direction in new_state 
            for lane in direction['lanes'] 
            for item in [lane['count'], lane['emergency_count']]
        ]
        
        # Existing Q-learning update logic
        max_next = max([self.q_table.get((tuple(new_flat_state), a), 0) for a in range(4)])
        self.q_table[(tuple(old_flat_state), action)] += self.alpha * (
            reward + self.gamma * max_next - self.q_table.get((tuple(old_flat_state), action), 0)
        )

class TrafficSignal:
    def __init__(self, red, yellow, green):
        self.red = red
        self.yellow = yellow
        self.green = green
        self.signalText = ""
        self.totalGreenTime = 0

class Vehicle(pygame.sprite.Sprite):
    def __init__(self, lane, vehicleClass, direction_number, direction, will_turn):
        pygame.sprite.Sprite.__init__(self)
        self.lane = lane
        self.vehicleClass = vehicleClass
        self.speed = speeds[vehicleClass]
        self.direction_number = direction_number
        self.direction = direction
        self.x = x[direction][lane]
        self.y = y[direction][lane]
        self.crossed = 0
        self.willTurn = will_turn
        self.turned = 0
        self.rotateAngle = 0
        self.waiting_time = 0
        vehicles[direction][lane].append(self)
        self.index = len(vehicles[direction][lane]) - 1
        path = f"images/{direction}/{vehicleClass}.png"
        self.originalImage = pygame.image.load(path).convert_alpha()
        self.image = self.originalImage.copy()  # Renamed from currentImage to image
        self.rect = self.image.get_rect(topleft=(self.x, self.y))  # Added rect attribute
        self.update_stop_position()
        simulation.add(self)

    def update_stop_position(self):
        direction, lane = self.direction, self.lane
        if len(vehicles[direction][lane]) > 1 and vehicles[direction][lane][self.index - 1].crossed == 0:
            prev_vehicle = vehicles[direction][lane][self.index - 1]
            if direction == 'right':
                self.stop = prev_vehicle.stop - prev_vehicle.image.get_width() - 15
            elif direction == 'left':
                self.stop = prev_vehicle.stop + prev_vehicle.image.get_width() + 15
            elif direction == 'down':
                self.stop = prev_vehicle.stop - prev_vehicle.image.get_height() - 15
            elif direction == 'up':
                self.stop = prev_vehicle.stop + prev_vehicle.image.get_height() + 15
        else:
            self.stop = defaultStop[direction]

    def move(self):
        if self.crossed == 0:
            if (self.direction == 'right' and self.x + self.rect.width > stopLines['right']) or \
               (self.direction == 'down' and self.y + self.rect.height > stopLines['down']) or \
               (self.direction == 'left' and self.x < stopLines['left']) or \
               (self.direction == 'up' and self.y < stopLines['up']):
                self.crossed = 1
                vehicles[self.direction]['crossed'] += 1

        if (currentGreen == self.direction_number and currentYellow == 0) or self.crossed == 1:
            if self.willTurn and not self.turned:
                self.handle_turn()
            else:
                self.proceed()
        else:
            self.waiting_time += 1

        # Update rect position after movement
        self.rect.topleft = (self.x, self.y)

    def handle_turn(self):
        mid_point = mid[self.direction]
        if (self.direction == 'right' and self.x < mid_point['x']) or \
           (self.direction == 'down' and self.y < mid_point['y']) or \
           (self.direction == 'left' and self.x > mid_point['x']) or \
           (self.direction == 'up' and self.y > mid_point['y']):
            self.proceed()
        else:
            if self.rotateAngle < 90:
                self.rotateAngle += 3
                self.image = pygame.transform.rotate(self.originalImage, -self.rotateAngle)
                if self.direction == 'right':
                    self.x += 2
                    self.y += 1.8
                elif self.direction == 'down':
                    self.x -= 2.5
                    self.y += 2
                elif self.direction == 'left':
                    self.x -= 1.8
                    self.y -= 2.5
                elif self.direction == 'up':
                    self.x += 1
                    self.y -= 1
            else:
                self.turned = 1
                self.proceed()

    def proceed(self):
        if self.index > 0:
            prev_vehicle = vehicles[self.direction][self.lane][self.index - 1]
            prev_rect = prev_vehicle.rect
            if self.direction == 'right' and self.x + self.rect.width >= prev_vehicle.x - 15:
                return
            elif self.direction == 'left' and self.x <= prev_vehicle.x + prev_rect.width + 15:
                return
            elif self.direction == 'down' and self.y + self.rect.height >= prev_vehicle.y - 15:
                return
            elif self.direction == 'up' and self.y <= prev_vehicle.y + prev_rect.height + 15:
                return

        if self.direction == 'right' and self.x + self.rect.width < 1400:
            self.x += self.speed
        elif self.direction == 'down' and self.y + self.rect.height < 800:
            self.y += self.speed
        elif self.direction == 'left' and self.x > 0:
            self.x -= self.speed
        elif self.direction == 'up' and self.y > 0:
            self.y -= self.speed

    def update(self):
        self.move()  # Called by sprite group update

class Simulation:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((1400, 800))
        pygame.display.set_caption("RL Traffic Controller")
        self.background = pygame.image.load('images/mod_int.png').convert()
        self.signals = [TrafficSignal(defaultRed if i != 0 else 0, defaultYellow, defaultGreen) for i in range(4)]
        self.agent = QLearningAgent()
        self.current_phase = 0
        self.phase_timer = 0
        self.running = True
        global simulation
        simulation = pygame.sprite.Group()
        self.font = pygame.font.Font(None, 30)
        self.signal_images = {
            'red': pygame.image.load('images/signals/red.png').convert_alpha(),
            'yellow': pygame.image.load('images/signals/yellow.png').convert_alpha(),
            'green': pygame.image.load('images/signals/green.png').convert_alpha()
        }

    def get_state(self):
        """
        Retrieve a more detailed state representation of traffic conditions
        
        Returns:
        list: A list of dictionaries representing traffic density for each direction
        """
        state = []
        for direction_num, direction in enumerate(directionNumbers.values()):
            # Detailed lane-level information
            lane_states = []
            total_vehicles = 0
            emergency_vehicles = 0
            
            for lane in range(3):
                # Get waiting vehicles in this lane
                waiting_vehicles = [v for v in vehicles[direction][lane] if v.crossed == 0]
                lane_vehicle_count = len(waiting_vehicles)
                
                # Count emergency vehicles
                lane_emergency_count = sum(1 for v in waiting_vehicles if v.vehicleClass in ['ambulance', 'police', 'fireVan'])
                
                lane_states.append({
                    'count': lane_vehicle_count,
                    'emergency_count': lane_emergency_count
                })
                
                total_vehicles += lane_vehicle_count
                emergency_vehicles += lane_emergency_count
            
            state.append({
                'lanes': lane_states,
                'total_vehicles': total_vehicles,
                'emergency_vehicles': emergency_vehicles
            })
        
        return state


    def calculate_reward(self, old_state, new_state):
        """
        Calculate reward based on changes in traffic state
        
        Args:
        old_state (list): Previous traffic state
        new_state (list): Current traffic state
        
        Returns:
        float: Calculated reward
        """
        reward = 0
        
        for direction_idx in range(len(old_state)):
            # Compare total vehicles
            old_total = old_state[direction_idx]['total_vehicles']
            new_total = new_state[direction_idx]['total_vehicles']
            
            # Reward for reducing total vehicles
            vehicle_reduction = old_total - new_total
            reward += vehicle_reduction * 5
            
            # Significant penalty for emergency vehicles waiting
            old_emergency = old_state[direction_idx]['emergency_vehicles']
            new_emergency = new_state[direction_idx]['emergency_vehicles']
            
            if old_emergency > 0 and new_emergency == 0:
                reward += 50  # Big bonus for clearing emergency vehicles
            elif new_emergency > old_emergency:
                reward -= 30  # Penalty for increasing emergency vehicle wait
        
        # Overall congestion penalty
        total_current_vehicles = sum(direction['total_vehicles'] for direction in new_state)
        reward -= total_current_vehicles * 0.1
        
        return reward


    def switch_phase(self, new_phase):
        global currentYellow, currentGreen
        
        # Set current phase to yellow
        currentYellow = 1
        self.signals[self.current_phase].yellow = defaultYellow
        
        # Track yellow phase start time
        yellow_start_time = time.time()
        
        # Non-blocking yellow phase transition
        while time.time() - yellow_start_time < defaultYellow:
            # Process pygame events to keep window responsive
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                    return
            
            # Minimal delay to prevent high CPU usage
            pygame.time.delay(10)
        
        # Reset yellow phase
        currentYellow = 0
        
        # Switch to new green phase
        currentGreen = new_phase

    def run(self):
        global timeElapsed, currentGreen, currentYellow
        clock = pygame.time.Clock()
        last_vehicle_spawn = time.time()
        old_state = None

        while self.running:
            current_time = time.time()
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
                break

            # Regenerate vehicles if needed
        if current_time - last_vehicle_spawn > random.uniform(0.5, 1.5):
            # Generate a new vehicle
            vehicle_type = random.randint(0, 7)
            lane = 0 if vehicle_type == 4 else random.randint(1, 2)
            direction = random.choice(list(directionNumbers.values()))
            will_turn = random.random() < 0.3 if lane == 2 else False
            Vehicle(lane, vehicleTypes[vehicle_type], 
                    list(directionNumbers.values()).index(direction), 
                    direction, will_turn)
            last_vehicle_spawn = current_time

        # Get current state
        current_state = self.get_state()
        
        # Intelligent phase switching logic
        if old_state is not None:
            # Calculate reward
            reward = self.calculate_reward(old_state, current_state)
            
            # Choose action using Q-learning agent
            action = self.agent.get_action(current_state)
            
            # Determine if phase should change
            phase_change_conditions = (
                action != self.current_phase and  # Different action selected
                (
                    self.phase_timer >= min_phase_duration or  # Minimum phase duration met
                    self.is_phase_change_necessary(current_state)  # Traffic density warrants change
                )
            )
            
            if phase_change_conditions:
                # Switch traffic signal phase
                self.switch_phase(action)
                self.current_phase = action
                
                # Update Q-table with new learning
                self.agent.update_q_table(old_state, action, reward, current_state)
                
                # Reset phase timer
                self.phase_timer = 0
            else:
                # Increment phase timer
                self.phase_timer += clock.get_time() / 1000.0  # Convert to seconds
        
        # Update old state for next iteration
        old_state = current_state
        
        # Render the simulation
        self.screen.blit(self.background, (0, 0))
        
        # Update and draw sprites
        simulation.update()
        simulation.draw(self.screen)
        
        # Display traffic signals and other UI elements
        # [Rest of your existing rendering code]
        
        pygame.display.flip()
        clock.tick(60)  # Limit to 60 FPS
        
        timeElapsed += 1
        
        # End simulation if time limit reached
        if timeElapsed >= simTime:
            self.running = False

    pygame.quit()


    def is_phase_change_necessary(self, state):
        """
        Determine if a phase change is necessary based on current traffic state
        
        Args:
        state (list): Current traffic state
        
        Returns:
        bool: Whether a phase change is recommended
        """
        current_direction = state[self.current_phase]
        
        # Check conditions for phase change
        conditions = [
            # High vehicle count in current direction
            current_direction['total_vehicles'] > 10,
            
            # Emergency vehicles waiting in other directions
            any(
                state[idx]['emergency_vehicles'] > 0 
                for idx in range(len(state)) 
                if idx != self.current_phase
            ),
            
            # Significant vehicle count difference between directions
            max(
                state[idx]['total_vehicles'] 
                for idx in range(len(state))
            ) > current_direction['total_vehicles'] * 1.5
        ]
        
        return any(conditions)

def generate_vehicles():
    while True:
        vehicle_type = random.randint(0, 7)
        lane = 0 if vehicle_type == 4 else random.randint(1, 2)
        direction = random.choice(list(directionNumbers.values()))
        will_turn = random.random() < 0.3 if lane == 2 else False
        Vehicle(lane, vehicleTypes[vehicle_type], list(directionNumbers.values()).index(direction), direction, will_turn)
        time.sleep(random.uniform(0.5, 1.5))

if __name__ == "__main__":
    sim = Simulation()
    vehicle_thread = threading.Thread(target=generate_vehicles, daemon=True)
    vehicle_thread.start()
    sim.run()