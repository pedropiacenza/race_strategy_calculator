from dataclasses import dataclass
import datetime as dt
from typing import List

@dataclass
class RaceRules:
    num_pitstops: int = 15
    num_kart_swaps: int = 2
    race_duration: dt.timedelta = dt.timedelta(hours=6)
    race_start: dt.time = dt.time(hour=11, minute=30)
    pit_duration: dt.timedelta = dt.timedelta(seconds = 20)
    swap_duration: dt.timedelta = dt.timedelta(minutes = 3)
    stop_time_loss: dt.timedelta = dt.timedelta(seconds = 20)
    max_kart_runtime: dt.timedelta = dt.timedelta(hours = 2, minutes = 15)


@dataclass
class Stint:
    driver: str
    duration: dt.timedelta 
    swap: bool   

class RaceStrat:
    def __init__(self, drivers: List[str], racerules: RaceRules) -> None:
        self.drivers = drivers
        self.racecfg = racerules
        self.num_stops = 0
        self.num_swaps = 0
        self.stints = []

    def get_race_strat(self, current_stint_start: dt.time, current_driver: str) -> List[Stint]:
        """
        Should return a list of stints that alternates drivers and balances the amount
        of time that driver gets
        """
        #Create an alternating driver order and then create stops with minimum duration for all drivers 
        driver_order = self.get_stint_driver_order(current_driver)
        print(f"Driver order is: \n{driver_order}")
        next_stints = self.create_min_stints(driver_order, current_stint_start, current_driver, min_duration = dt.timedelta(minutes=2))
        #Start assigning driving time for the stints based on who has driven less (brute force, 1 min at a time)
        drive_time_left = self.get_driving_time_left(self.stints) 
        while drive_time_left >= dt.timedelta(minutes=0):
            low_t_driver = self.get_lowest_driver_time(self.stints+next_stints)
            # Alocate this driver with more time on his shortest stint
            idx = self.get_shortest_stint_idx(next_stints, low_t_driver)
            if idx:
                next_stints[idx].duration += dt.timedelta(minutes=1)
                drive_time_left = self.get_driving_time_left(self.stints+next_stints) 
            else: 
                #This shouldn't happen... fix this bug
                print("get shortest stint idx returned None")
                print(f"lowest_t_driver was {low_t_driver}")
                print("next stints passed was \n")
                self.print_stints(next_stints)
                break
        return next_stints

    def get_shortest_stint_idx(self, stint_list: List[Stint], driver: str) -> int:
        """
        Returns the index of the stint with the lowest duration
        """
        min_stint = dt.timedelta(hours=2)
        min_idx = None
        print("[get_shortest_stint_idx]")
        self.print_stints(stint_list)
        for idx, s in enumerate(stint_list):
            if s.duration < min_stint and s.driver == driver:
                min_stint = s.duration
                min_idx = idx
        return min_idx

    def get_lowest_driver_time(self, stint_list: List[Stint] = None) -> str:
        """
        Looks at a full list of stints and returns the driver who's driven the least
        """
        if stint_list is None:
            stint_list = self.stints
        drive_times = dict(zip(self.drivers, [self.get_drive_time(x, stint_list) for x in self.drivers]))
        return min(drive_times, key=drive_times.get)
        

    def get_stint_driver_order(self, current_driver: str):
        """
        Looks at past stints and returns a list of drivers such that 
        we alternate as much as possible. The current driver information is used to determine the order
        but it should NOT be included in the future order
        """
        driver_order = []
        #Driver order so far, including the current stint driver
        past_drivers = [s.driver for s in self.stints]
        past_drivers.append(current_driver)
        #Compute how many stints are left
        num_stints_left = self.racecfg.num_pitstops - len(past_drivers) + 1
        #and how many stints each driver has done
        num_stints_per_driver = {}
        for d in self.drivers:
            num_stints_per_driver[d] = past_drivers.count(d)
        while num_stints_left > 0:
            #If two drivers have the same amount, it just gives the first one! 
            next_driver = min(num_stints_per_driver, key=num_stints_per_driver.get) 
            driver_order.append(next_driver)
            num_stints_left -= 1
            num_stints_per_driver[next_driver] += 1
        return driver_order

    def create_min_stints(self, 
        driver_order: List[str], 
        current_stint_start: dt.time, 
        current_driver: str,
        min_duration: dt.timedelta = dt.timedelta(minutes=1)
    ) -> List[Stint]:
        """
        Based on a driver order list, create a list of stints with minimum duration
        for those drivers
        """
        min_stints = []
        #First add the current stint to the list with its current running time
        current_stint_duration = dt.datetime.now() - dt.datetime.combine(dt.date.today(), current_stint_start) 
        min_stints.append(Stint(current_driver, current_stint_duration, False))
        #Now add the minimum duration stints
        for d in driver_order:
            min_stints.append(Stint(d, min_duration, False))
        return min_stints
        

    def add_stint(self, stint: Stint) -> None:
        self.stints.append(stint)
        if stint.swap:
            self.num_swaps += 1
        self.num_stops += 1

    def get_drive_time(self, driver: str, stint_list: List[Stint] = None) -> dt.timedelta:
        """
        Returns the total time driven by a driver from a list of stints
        """
        total = dt.timedelta()
        for s in stint_list:
            if s.driver == driver:
                total += s.duration
        return total

    def get_time_left(self) -> dt.timedelta:
        """
        Uses the PC local time to compute the amount of time left in the race
        """
        race_end = self._get_race_end_time()
        return dt.datetime.combine(dt.date.today(), race_end) - dt.datetime.now()

    def get_driving_time_left(self, stint_list: List[Stint]) -> dt.timedelta:
        """
        Returns the total amount of drivable time in the race (we subtract
        the time lost during stops and swaps)
        """
        stops_left = self.racecfg.num_pitstops - self.num_stops
        swaps_left = self.racecfg.num_kart_swaps - self.num_swaps
        raw_time_left = self.get_time_left()
        drive_time = raw_time_left - stops_left*(self.racecfg.pit_duration + self.racecfg.stop_time_loss) - swaps_left*(self.racecfg.swap_duration + self.racecfg.stop_time_loss)
        return drive_time
        
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

    def print_stints(self, stint_list: List[Stint] = None):
        """
        Prints a list of Stints in a nice readable format
        """
        if stint_list is None:
            stint_list = self.stints
        print("\n================ STINTS DESCRIPTION ==========================\n")
        for idx, stint in enumerate(stint_list):
            print(f"\tStint #{idx}  |  {stint.driver}\t|  {stint.duration}\t")
        print("==============================================================")
        for d in self.drivers:
            print(f"{d} has been on track for\t{self.get_drive_time(d, stint_list)}")
        print("==============================================================\n\n")


if __name__ == "__main__":
    strat = RaceStrat(
        drivers = ["Pedro", "Karim", "Joe"],
        racerules = RaceRules()
        )
    strat.add_stint(Stint("Pedro", dt.timedelta(minutes=21), swap=False))
    strat.add_stint(Stint("Karim", dt.timedelta(minutes=26), swap=False))
    # strat.add_stint(Stint("Joe", dt.timedelta(minutes=25), swap=False))
    # strat.print_stints()
    # print(f"Based on PC time, there are {strat.get_time_left()} left in the race")
    # print(f"{strat.get_lowest_driver_time()} drove the least amount")
    strat.get_race_strat(dt.time(hour=10, minute=15),"Joe")