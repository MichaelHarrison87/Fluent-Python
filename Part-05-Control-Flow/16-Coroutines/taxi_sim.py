"""
DES Simulation of 3 taxis
Appedix A-6 [p696]
"""
import argparse
import collections
import queue
import random
import time

DEFAULT_NUM_TAXIS = 3
DEFAULT_END_TIME = 180
SEARCH_DURATION = 5
TRIP_DURATION = 20
DEPARTURE_INTERVAL = 5

Event = collections.namedtuple('Event', 'time proc action')

### TAXI PROCESS
def taxi_process(ident, num_trips, start_time = 0):
    """
    Yields to the simulator, issuing an event at each state change.
    This will be the subgenerator - managing events, called by the simulator (delegating generator),
    which itself is handled in a main() (i.e. client code)
    """
    time = yield Event(start_time, ident, 'START SHIFT')
    for i in range(num_trips):
        time = yield Event(time, ident, 'pick up passenger')
        time = yield Event(time, ident, 'drop off passenger')
    yield Event(time, ident, 'END SHIFT')
### END TAXI PROCESS
    

### SIMULATOR
class Simulator:
    
    def __init__(self, procs_map):
        """procs_map is a dict taxi_id: taxi_process pairs"""
        self.events = queue.PriorityQueue()   # this queue will hold taxi_processes
        self.procs = dict(procs_map)
        
    def run(self, end_time):
        """Schedule and display events until the time is up"""
        # First event for each cab
        for _, proc in sorted(self.procs.items()):
            first_event = next(proc)
            self.events.put(first_event)
        
        # Main simulation loop
        sim_time = 0
        while sim_time < end_time:
            if self.events.empty():
                print('END OF EVENTS')
                break
            
            current_event = self.events.get()
            sim_time, proc_id, previous_action = current_event
            print(f'Taxi {proc_id}:', proc_id * '....', current_event)
            active_proc = self.procs[proc_id]
            next_time = sim_time + compute_duration(previous_action)
            try:
                next_event = active_proc.send(next_time)   # sending to the subgenerator, taxi_process
            except StopIteration:
                del self.procs[proc_id]
            else:
                self.events.put(next_event)
        else:
            # Only reached if while runs to completion
            print(f'***END OF SIMUALTION TIME: {self.events.qsize()} EVENTS REMAINING')
### END SIMULATOR


def compute_duration(previous_action):
    """
    Action duration follows an exponential distribution, with param L - where  1/L is mean wait time
    "Action" is a text field, from the actions in taxi_process
    """
    if previous_action in ['START SHIFT', 'drop off passenger']:
        # Now prowling
        interval = SEARCH_DURATION
    elif previous_action == 'pick up passenger':
        # Now making the trip
        interval = TRIP_DURATION
    elif previous_action == 'END SHIFT':
        # Going home...
        interval = 1
    else: 
        raise ValueError(f'Unknown previous action: \'{previous_action}\'')
    
    return int(random.expovariate(1/interval)) + 1


def main(end_time = DEFAULT_END_TIME, num_taxis = DEFAULT_NUM_TAXIS, seed = None):
    if seed is not None:
        random.seed(seed)
    
    taxis = {i: taxi_process(i, (i+1)*2, i*DEPARTURE_INTERVAL) for i in range(num_taxis)}
    sim = Simulator(taxis)
    sim.run(end_time) 
    
if __name__ == '__main__':
    
    parser = argparse.ArgumentParser(description = 'Taxi Fleet Simulator')
    parser.add_argument('-e', '--end-time', type = int, default = DEFAULT_END_TIME)
    parser.add_argument('-t', '--taxis', type = int, default = DEFAULT_NUM_TAXIS)
    parser.add_argument('-s', '--seed', type = int, default = None)
    
    args = parser.parse_args()
    main(args.end_time, args.taxis, args.seed)