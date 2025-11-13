import random


class Passenger:
    def __init__(self, dest_floor: int):
        self.dest_floor = dest_floor
        self.wait_time = 0

class Elevator:
    def __init__(self, 
                n_floors, 
                cur_floor, 
                capacity, 
                door_open,
                arrival_prob,
                max_steps = 100):
        self.n_floors = n_floors
        self.cur_floor = cur_floor
        self.arrival_prob = arrival_prob
        self.capacity = capacity
        self.door_open = door_open
        self.max_steps = max_steps

        self.t = 0

        self.waiting_passengers = [[] for _ in range(n_floors)]
        self.onboard_passengers = []

    def reset(self):
        self.cur_floor = 0
        self.door_open = False
        self.t = 0
        self.waiting_passengers = [[] for _ in range(self.n_floors)]
        self.onboard_passengers = []
        return self.get_observation()

    def take_action(self, action):
        # a_0 = move up
        if action == 0 and not self.door_open:
            self.cur_floor = min(self.n_floors - 1, self.cur_floor + 1)
        # a_1 = move down
        elif action == 1 and not self.door_open:
            self.cur_floor = max(0, self.cur_floor - 1)
        # a_2 = open door
        elif action == 2:
            self.door_open = True
        # a_3 = close door
        elif action == 3:
            self.door_open = False

    def handle_passengers(self):
        # passengers can't move if door is closed
        if not self.door_open:
            return
        
        # handle passengers getting off
        remaining_onboard = []
        for p in self.onboard_passengers:
            if p.dest_floor == self.cur_floor:
                continue
            remaining_onboard.append(p)
        self.onboard_passengers = remaining_onboard

        # handle passengers getting on
        available_space = max(0, self.capacity - len(self.onboard_passengers))
        passengers_boarding = self.waiting_passengers[self.cur_floor][:available_space]
        passengers_staying = self.waiting_passengers[self.cur_floor][available_space:]
        self.onboard_passengers.extend(passengers_boarding)
        self.waiting_passengers[self.cur_floor] = passengers_staying
    
    def increment_wait_times(self):
        for floor_passengers in self.waiting_passengers:
            for p in floor_passengers:
                p.wait_time += 1

    def sample_arrivals(self):
        for floor in range(self.n_floors):
            if random.random() < self.arrival_prob[floor]:
                dest_floor = random.choice([f for f in range(self.n_floors) if f != floor])
                new_passenger = Passenger(dest_floor)
                self.waiting_passengers[floor].append(new_passenger)

    def get_reward(self, action):
        tot_wait_time = 0
        for floor_passengers in self.waiting_passengers:
            for p in floor_passengers:
                tot_wait_time += p.wait_time

        return -tot_wait_time
        
    def get_observation(self):
        obs = {
            'cur_floor': self.cur_floor,
            'door_open': self.door_open,
            'call_buttons': [1 if len(self.waiting_passengers[floor]) > 0 else 0 for floor in range(self.n_floors)],
            'dest_buttons': [1 if any(p.dest_floor == floor for p in self.onboard_passengers) else 0 for floor in range(self.n_floors)]
        }
        return obs

    def step(self, action):
        self.take_action(action)

        self.handle_passengers()
        self.sample_arrivals()
        self.increment_wait_times()


        obs = self.get_observation()
        reward = self.get_reward(action)

        self.t += 1

        return obs, reward, self.t >= self.max_steps
