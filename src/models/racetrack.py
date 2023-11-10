class RaceTrack:
    def __init__(self) -> None:
        """
        clone from Catalunya Race Track
        """
        
        # static property
        self.distance_km=4.657
        self.racetrack_temperature_celcius=25
        # assume equal distance between stopwatch
        self.num_stopwatch=28
        self.list_sector_start_stopwatch=[0,10,19]
        self.list_sector_end_stopwatch=[10,19,0]
        self.start_end_pitlane_stopwatch=[25,3]