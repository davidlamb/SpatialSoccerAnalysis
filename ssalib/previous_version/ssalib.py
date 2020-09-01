import json
import math
import geopandas as gpd
import pandas as pd
from shapely.geometry.point import Point
from shapely.geometry import LineString
from shapely.geometry import Polygon
from dateutil.parser import parse
from datetime import datetime
from datetime import timedelta

class SpatialSoccer(object):
    __version__ = 0
    GREEN_PITCH_COLOR = "#538032"
    WHITE_LINE_COLOR = "#ffffff"
    ELEVEN_COLORS = ["#808080","#C71585","#FFA07A","#5F9EA0","#6A5ACD","#708090",
                    "#FDF5E6","#228B22","#8B4513","#FFFF00","#000000"]
    POSITION_NUMBER = {1:'Goalkeeper',2:'Right Back',3:'Right Center Back',4:'Center Back',
                    5:'Left Center Back',6:'Left Back',7:'Right Wing Back',8:'Left Wing Back',
                    9:'Right Defensive Midfield',10:'Center Defensive Midfield',11:'Left Defensive Midfield',
                    12:'Right Midfield',13:'Right Center Midfield',14:'Center Midfield',15:'Left Center Midfield',
                    16:'Left Midfield',17:'Right Wing',18:'Right Attacking Midfield',19:'Center Attacking Midfield',
                    20:'Left Attacking Midfield',21:'Left Wing',22:'Right Center Forward',23:'Striker',
                    24:'Left Center Forward',25:'Secondary Striker'}
    POSITION_LOCATION = {1:(10,40),2:(20,14),3:(20,28),4:(20,44),
                        5:(20,60),6:(20,76),7:(40,14),8:(40,76),
                        9:(40,28),10:(40,44),11:(40,60),12:(60,14),
                        13:(60,28),14:(60,44),15:(60,60),16:(60,76),
                        17:(80,14),18:(80,28),19:(80,44),20:(80,60),
                        21:(80,76),22:(100,28),23:(100,44),24:(100,60),25:(90,44)}
    def __init__(self):
        self.parse_time = True
        self.add_type = True
        self.find_goals = True
        self.find_team_name = True
        self.correct_location = True
        self.return_geopandas = True
        self.path_to_events = "open-data-master/data/events"
        self.path_to_matches = "open-data-master/data/matches"
        self.path_to_current_match = ""
        self.current_match = {}
        self.current_match_id = 0
        self.path_to_current_match_events = ""
        self.current_match_datetime_str = ""
        self.current_match_datetime_dt = datetime.now()
        self.matches = []
        self.events = []
        self.current_match_events_df = None
        self.current_match_events_gdf = None
        self.half_time_length = 15
        self.overtime_break_length = 5

    def load_single_match(self,path_to_matches,matchid = None, matchindex=0):
        """Loads a single match's events from a match. Provide either the matchid, or the index.
        path_to_matches: string path to match json.
        matchid: id for the match. default is None. If None then matchindex is used.
        matchind: integer indicating which match to load.
        returns the dataframe of match events. returns geodataframe if return_geopandas property of class is set to true (default).
        """
        # TODO: Add exception handling.

        with open(path_to_matches, "r",encoding='utf-8') as read_file:
            self.matches = json.load(read_file)
        
        if matchid:
            for m in self.matches:
                if m['match_id'] == matchid:
                    self.current_match = m
                    break
        else:
            self.current_match = self.matches[matchindex]

        self.current_match_id = self.current_match['match_id']
        self.path_to_current_match_events = self.path_to_events + '/' + str(self.current_match_id) + '.json'
        match_day = self.current_match['match_date']
        match_start_time = self.current_match['kick_off']
        self.current_match_datetime_str = "{0} {1}".format(match_day,match_start_time)
        self.current_match_datetime_dt = parse(self.current_match_datetime_str)
        with open(self.path_to_current_match_events, "r",encoding='utf-8') as read_file:
            self.events = json.load(read_file)
        if self.events:
            self.current_match_events_df = pd.DataFrame(self.events)
            if self.parse_time:
                self.parse_time_by_period(self.current_match_events_df, self.current_match_datetime_dt)
            if self.find_goals:
                self.current_match_events_df['goal'] = self.current_match_events_df['shot'].apply(lambda x: self.get_goals_bin(x))
            if self.add_type:
                self.get_type(self.current_match_events_df)
            if self.correct_location:
                geometry = self.get_location_coords(self.current_match_events_df)
            if self.find_team_name:
                self.current_match_events_df['team_name'] = self.current_match_events_df['team'].apply(lambda x: x.get('name'))
            if self.return_geopandas:
                if len(geometry) > 0:
                    self.current_match_events_gdf = gpd.GeoDataFrame(self.current_match_events_df,geometry=geometry)
                    return self.current_match_events_gdf
            else:
                return self.current_match_events_df
        else:
            return None                



    def parse_time_by_period(self,df,match_datetime_dt=None):
        """Parse the timestamp of events using the base match kick_off time
        df: dataframe that contains the event information
        match_datetime_dt: match start time, if None, the current_match_datetime_dt is used.
        """
        # TODO: Add exception handling.

        df['event_time'] = self.convert_timestamp(df['timestamp'].values,match_datetime_dt)

        periods = [(2,1,self.half_time_length),(3,2,self.overtime_break_length ),(4,3,self.overtime_break_length ),(5,3,self.overtime_break_length )]
        for cp,pp,it in periods:
            if len(df.loc[df['period']==cp])>0:
                ts_end = df[df['period']==pp].sort_values(by="event_time",ascending=False)['event_time'].iloc[0]
                ts_start = df[df['period']==pp].sort_values(by="event_time",ascending=False)['event_time'].iloc[-1]
                df.loc[df['period']==cp,['event_time']]=df.loc[df['period']==cp,['event_time']]+(ts_end - ts_start)+timedelta(seconds=it*60)
    
    def convert_timestamp(self,timestamps,base_datetime):
        """Converts a list of timestamps to datetime using the base_datetime.
        timestamps: list of strings HH:MM:SS:MS
        base_datetime: the base kickofftime to add to the timestamps
        returns: list of datetimes. should be the same length as input list. None for values that failed.
        """
        output_list = []
        for ts in timestamps:
            try:
                t = datetime.strptime(ts,"%H:%M:%S.%f")
                delta = timedelta(hours=t.hour, minutes=t.minute, seconds=t.second, microseconds=t.microsecond)
                output_list.append(base_datetime + delta)
            except:
                output_list.append(None)
        return output_list

    def get_type(self,df):
        """Adds a column to the dataframe for the type of event.
        df: dataframe to apply this step to."""
        # TODO: Add exception handling.
        df['event_type'] = df['type'].apply(lambda x: x.get('name'))

    def get_goals_bin(self,x):
        """Used to identify a goal was scored from a shot."""
        try:
            if x['outcome']['id'] == 97:
                return 1
            else:
                return 0
        except:
            return 0
        
    def get_location_coords(self,df,mn=0,mx=80,geometry_bool=True,location_name='location',out_x_name='x_coord',out_y_name='y_coord'):
        """Adds x and y coordinates to the dataframe, corrects for the origin in lower left, and optionally returns a list of geometry from
        df: dataframe to add corrected coordinates to
        mn: minimum for correction
        mx: maximum for correction
        geometry_bool: return Point geometry of location.
        location_name: name of the field containing the location. Presumed coordinate tuple of some kind.
        out_x_name: name of the x_coordinate field.
        out_y_name: name of the y_coordinate field.
        """
        df[out_x_name] = None
        df[out_y_name] = None
        df.loc[df[location_name].notnull(),[out_x_name]] = df.loc[df[location_name].notnull()][location_name].apply(lambda x: x[0])
        df.loc[df[location_name].notnull(),[out_y_name]] = df.loc[df[location_name].notnull()][location_name].apply(lambda x: SpatialSoccer.flip_coordinate_min_max(x[1],mn,mx))
        if geometry_bool:
            geometry = [Point(a) if a[0] is not None else None for a in df[[out_x_name,out_y_name]].values]
            #print(geometry)
            return geometry


    @staticmethod
    def flip_coordinates(list_of_values,mx=None,mn=None):
        """Takes a list of numeric values and flips them based on the max and min
        list_of_values: a list of numbers
        returns a list of numbers of the same length
        """
        if mx is None:
            mx = max(list_of_values)
        if mn is None:
            mn = min(list_of_values)
        return [(mx+mn)-x for x in list_of_values]

    @staticmethod
    def flip_coordinate_min_max(value,mx=80,mn=0):
        """Takes a value and flips it based on the max and min. If the maximum is 80 and minimum is 0, then a value of 0 becomes 80.
        value: number to be changed
        mx: maximum value default is 80
        mn: minimum value default is 0
        returns the flipped number
        """
        return (mx+mn)-value
    
    @staticmethod
    def build_polygon_pitch_statsbomb():
        """Builds a pitch based on statsbomb's defined. The coordinates are flipped so the origin is in the lower left corner.
        returns a geopandas dataframe."""
        #polygons
        outside_line_pairs = [(0,0),(120,0),(120,80),(0,80),(0,0)]
        left_penalty_box = [(0,18),(18,18),(18,62),(0,62),(0,18)]
        right_penalty_box = [(120,18),(102,18),(102,62),(120,62),(120,18)]
        left_goal_box = [(0,30),(6,30),(6,50),(0,50),(0,30)]
        right_goal_box = [(120,30),(114,30),(114,50),(120,50),(120,30)]

        #circle
        center = [(60,40)]

        #linestring
        halfway_line = [(60,0),(60,80)]

        #Y Correction

        outside_line_pairs = [(v[0],SpatialSoccer.flip_coordinate_min_max(v[1],80,0)) for v in outside_line_pairs]
        left_penalty_box = [(v[0],SpatialSoccer.flip_coordinate_min_max(v[1],80,0)) for v in left_penalty_box]
        right_penalty_box = [(v[0],SpatialSoccer.flip_coordinate_min_max(v[1],80,0)) for v in right_penalty_box]
        left_goal_box = [(v[0],SpatialSoccer.flip_coordinate_min_max(v[1],80,0)) for v in left_goal_box]
        right_goal_box = [(v[0],SpatialSoccer.flip_coordinate_min_max(v[1],80,0)) for v in right_goal_box]
        center = [(v[0],SpatialSoccer.flip_coordinate_min_max(v[1],80,0)) for v in center]
        halfway_line = [(v[0],SpatialSoccer.flip_coordinate_min_max(v[1],80,0)) for v in halfway_line]
        #DataFrame
        df_dict = {"Description":['Outside Boundary Line','Left Side Penalty Box','Right Side Penalty Box',
                          'Left Goal Box', 'Right Goal Box','Center Circle Point', 'Center Circle','Halfway Line']}
        geometry = [Polygon(outside_line_pairs),Polygon(left_penalty_box),
                Polygon(right_penalty_box),Polygon(left_goal_box),Polygon(right_goal_box),Point(center),
                Point(center).buffer(5),LineString(halfway_line)]
        pitchgdf = gpd.GeoDataFrame(df_dict,geometry=geometry)
        return pitchgdf

    @staticmethod
    def build_polygon_halfpitch_statsbomb():
        """Builds a pitch based on statsbomb's defined. The coordinates are flipped so the origin is in the lower left corner.
        returns a geopandas dataframe."""
        #polygons
        outside_line_pairs = [(0,0),(60,0),(60,80),(0,80),(0,0)]
        left_penalty_box = [(0,18),(18,18),(18,62),(0,62),(0,18)]
        left_goal_box = [(0,30),(6,30),(6,50),(0,50),(0,30)]


        #Y Correction

        outside_line_pairs = [(v[0],SpatialSoccer.flip_coordinate_min_max(v[1],80,0)) for v in outside_line_pairs]
        left_penalty_box = [(v[0],SpatialSoccer.flip_coordinate_min_max(v[1],80,0)) for v in left_penalty_box]
        left_goal_box = [(v[0],SpatialSoccer.flip_coordinate_min_max(v[1],80,0)) for v in left_goal_box]
        #DataFrame
        df_dict = {"Description":['Outside Boundary Line','Left Side Penalty Box', 'Left Goal Box', 'Center Circle Point']}
        geometry = [Polygon(outside_line_pairs),Polygon(left_penalty_box),
               Polygon(left_goal_box),Point(center)]
        pitchgdf = gpd.GeoDataFrame(df_dict,geometry=geometry)
        return pitchgdf

    @staticmethod
    def bearing(pt1,pt2):
        """Returns the direction\angle of a line between two points.
        pt1: Point (shapely class) one.
        pt2: Point (shapely class) two.
        returns angle in degrees.
        """
        x_diff = pt2[0] - pt1[0]
        y_diff = pt2[1] - pt1[1]
        return math.degrees(math.atan2(y_diff, x_diff))

    @staticmethod
    def build_grid(d,llx=0,lly=0,maxX=120,maxY=80):
        """Create a grid of polygons for analysis. 
        d: widht and height of grid cell
        llx: lower left x coordinate
        lly: lower left y coordinate
        maxX: maximum x value
        maxY: maximum y value
        returns geodataframe of grid
        """
        xrng = int((maxX-llx)/d)
        yrng = int((maxY-lly)/d)
        ids = []
        geom = []
        cent = []
        xcoord = llx
        ycoord = lly
        for x in range(0,xrng):
            for y in range(0,yrng):
                ids.append("r{0}c{1}".format(y,x))
                p = SpatialSoccer.build_square_polygon(xcoord,ycoord,d)
                geom.append(p)
                cent.append(p.centroid)
                ycoord += d
            xcoord +=d
            ycoord = lly
        gdf = gpd.GeoDataFrame({"cell":ids,"centroid":cent},geometry=geom)
        return gdf

    @staticmethod
    def build_square_polygon(x,y,d):
        """Creates a square polygon from the x and y coordinates and dimension.
        x: x coordinate
        y: y coordinate
        d: dimension
        """
        lst = [(x,y),(x+d,y),(x+d,y+d),(x,y+d),(x,y)]
        return Polygon(lst)

    @staticmethod
    def find_end_point(angle,length):
        endy = length * math.sin(math.radians(angle))
        endx = length * math.cos(math.radians(angle))
        return (endx,endy)