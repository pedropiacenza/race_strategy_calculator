import numpy as np
from dataclasses import dataclass
import datetime as dt
from typing import List

@dataclass
class RaceRules:
    num_pitstops: int = 15
    num_kart_swaps: int = 2
    race_duration: dt.timedelta = dt.timedelta(hours=6)
    race_start: dt.time = dt.time(hour=11, minute=30)
    pit_duration: dt.timedelta = dt.timedelta(seconds = 30)
    swap_duration: dt.timedelta = dt.timedelta(minutes=3)


@dataclass
class Stint:
    driver: str
    duration: dt.timedelta 
    swap: bool
    start_time: dt.time = None #Useful for current stint info?
   

class RaceStrat:
    def __init__(self, drivers: List[str], racerules: RaceRules) -> None:
        self.drivers = drivers
        self.racecfg = racerules
        self.num_stops = 0
        self.num_swaps = 0
        self.stints = []

    def get_race_strat(self, current_stint: Stint, use_pc_time=False) -> List[Stint]:
        #First get current race status (timeleft, stops left, swaps left, each driver time)
        #Create stints for each driver to balance driving time and comply with 
        #number of pit stops and kart swaps (not sure what algorithm to use here yet)
        pass

    def add_stint(self, stint: Stint) -> None:
        self.stints.append(stint)
        if stint.swap:
            self.num_swaps += 1
        self.num_stops += 1

    def get_drive_time(self, driver: str) -> dt.timedelta:
        total = dt.timedelta()
        for stint in self.stints:
            if stint.driver == driver:
                total += stint.duration
        return total

    def get_time_left(self) -> dt.timedelta:
        """
        Uses the PC local time to compute the amount of time left in the race
        """
        race_end = self._get_race_end_time()
        return dt.datetime.combine(dt.date.today(), race_end) - dt.datetime.now()
        
    def _get_race_end_time(self):
        return self._add(self.racecfg.race_start, self.racecfg.race_duration)
        
    def _add(self, a: dt.time, b: dt.timedelta) -> dt.time:
        a_datetime = dt.datetime.combine(dt.date.today(), a)
        new_datetime = a_datetime + b
        return new_datetime.time()
    
    def _subtract(self, a: dt.time, b: dt.timedelta) -> dt.time:
        a_datetime = dt.datetime.combine(dt.date.today(), a)
        new_datetime = a_datetime - b
        return new_datetime.time()


if __name__ == "__main__":
    strat = RaceStrat(
        drivers = ["Pedro", "Karim", "Joe"],
        racerules = RaceRules()
        )
    strat.add_stint(Stint("Pedro", dt.timedelta(minutes=21), swap=False))
    strat.add_stint(Stint("Pedro", dt.timedelta(minutes=31), swap=False))
    print(f"Pedro has driven {strat.get_drive_time('Pedro')} so far")
    print(f"Based on PC time, there are {strat.get_time_left()} left in the race")
    