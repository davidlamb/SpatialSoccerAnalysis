import json
import math
import geopandas as gpd
import pandas as pd
import numpy as np
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
    STATS_BOMB_DATA = 1
    WYSCOUT_DATA = 2
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
        self.half_time_length = 15
        self.overtime_break_length = 5




 
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



    #Added to abstract for different types of events and matches

    def get_match_list_from_source(self,path_to_matches,data_source,team_name=None):
        """get's list of match ids.
        path_to_matches: string path to match json.
        data_source: specify     STATS_BOMB_DATA  or WYSCOUT_DATA = 2
        team_name: matches only involving this team. Team id is expected if using WYscout data.
        returns list of matches for a given team or all match ids if team_name == None
        """

        if data_source ==self.STATS_BOMB_DATA:
            return self.get_matches_statsbomb(path_to_matches,team_name)
        if data_source ==self.WYSCOUT_DATA:
            return self.get_matches_wyscout(path_to_matches,team_name)
        return None
    
    def get_matches_statsbomb(self,path_to_matches,team_name=None):
        matches = []
        with open(path_to_matches, "r",encoding='utf-8') as read_file:
            in_matches = json.load(read_file)
            
            for m in in_matches:
                mt = match(m['match_id'])
                mt.home_team_id = m['home_team']['home_team_id']
                mt.home_team_name = m['home_team']['home_team_name']
                mt.home_team_score = m['home_score']
                mt.away_team_id = m['away_team']['away_team_id']
                mt.away_team_name = m['away_team']['away_team_name']
                mt.away_team_score = m['away_score']
                mt.kick_off = m['kick_off']
                mt.match_date = m['match_date']
                dtstr = "{0} {1}".format(mt.kick_off,mt.match_date)
                mt.match_date_time = parse(dtstr)
                if team_name:
                    if mt.home_team_name == team_name:
                        matches.append(mt)
                    elif mt.away_team_name == team_name:
                        matches.append(mt)
                    else:
                        pass
                else:
                    if m['match_id']:
                        matches.append(mt)
        return matches

    def get_matches_wyscout(self,path_to_matches,team_name=None):
        matches = []
        with open(path_to_matches, "r",encoding='utf-8') as read_file:
            in_matches = json.load(read_file)
        
        for m in in_matches:
            mt = match(int(m['wyId']))
            mt.match_date = m['date']
            mt.match_date_time = parse(m['date'])
            mt.season_id = m['seasonId']
            for k,v in m['teamsData'].items():
                if v['side'] == 'home' or v['side']=='none':
                    mt.home_team_id = int(k)
                    mt.home_team_name = k
                    mt.home_team_score = int(v['score'])
                else:
                    mt.away_team_id = int(k)
                    mt.away_team_name = k
                    mt.away_team_score = v['score']
            
            if team_name:
                if mt.home_team_name == team_name:
                    matches.append(mt)
                elif mt.away_team_name == team_name:
                    matches.append(mt)
                else:
                    pass
            else:
                if mt.match_id:
                    matches.append(mt)
        return matches

    def load_events_from_match(self,path_to_events,data_source,match_obj):
        """Loads a single match's events from a match. Provide either the matchid, or the index.
        path_to_events: string path to event json or folder containing match or event json files
        data_source: statsbomb or wyscout
        returns the dataframe of match events. returns geodataframe if return_geopandas property of class is set to true (default).
        """
        if data_source == self.STATS_BOMB_DATA:
            return self.load_events_statsbomb(path_to_events,match_obj)
        if data_source == self.WYSCOUT_DATA:
            return self.load_events_wyscout(path_to_events,match_obj)

    def load_events_statsbomb(self,path_to_events,match_obj):
        """Loads a single match's events from a match. Provide either the matchid, or the index.
        path_to_events: path to folder containing events for matches
        match_obj: match object that contains information about the match
        returns the geodataframe of match events. 
        """
        # TODO: Add exception handling.

        
        path_to_events = path_to_events + '/' + str(match_obj.match_id) + '.json'

        with open(path_to_events, "r",encoding='utf-8') as read_file:
            current_events = json.load(read_file)
            
        if current_events:
            for e in current_events:
                event_obj = event(e["id"])
                event_obj.period = e["period"]
                event_obj.possession_id = e["possession"]
                event_obj.possession_team_name = e['possession_team']['name']
                event_obj.event_team_name = e['team']['name']
                event_obj.match_id = match_obj.match_id
                try:
                    event_obj.event_player = e['player']['name']
                except:
                    pass
                
                event_obj.event_name = e['type']['name']
                try:
                    obj = SpatialSoccer.gen_dict_extract(event_obj.event_name,e)[0]
                    event_obj.subevent_name = obj['type']['name']
                except:
                    pass
                try:
                    obj = SpatialSoccer.gen_dict_extract(str.lower(event_obj.event_name),e)[0]
                    event_obj.body_part = obj['body_part']['name']
                except:
                    pass

                if event_obj.event_name == "Shot":
                    #print(e)
                    try:
                        event_obj.xg = e['shot']['statsbomb_xg']
                    except:
                        pass
                    if e['shot']['outcome']['id'] == 97:
                        event_obj.is_goal = 1
                    else:
                        event_obj.is_goal = 0
                else:
                    event_obj.is_goal = 0
                start_locations = [x for x in SpatialSoccer.gen_dict_extract("location",e)]
                if len(start_locations)>0:
                    event_obj.start_x = float(start_locations[0][0])
                    if self.correct_location:
                        event_obj.start_y = SpatialSoccer.flip_coordinate_min_max(float(start_locations[0][1]))
                    else:
                        event_obj.start_y = float(start_locations[0][1])
                else:
                    event_obj.start_x = None
                    event_obj.start_y = None
                
                end_locations = [x for x in SpatialSoccer.gen_dict_extract("end_location",e)]
                if len(end_locations)>0:
                    event_obj.end_x = float(end_locations[0][0])
                    if self.correct_location:
                        event_obj.end_y = SpatialSoccer.flip_coordinate_min_max(float(end_locations[0][1]))
                    else:
                        event_obj.end_y = float(end_locations[0][1])
                    
                else:
                    event_obj.end_x = None
                    event_obj.end_y = None
                event_obj.build_points()
                event_obj.timestamp = e["timestamp"]
                event_obj.event_time = self.convert_timestamp([event_obj.timestamp],match_obj.match_date_time)[0]
                event_obj.original_json = json.dumps(e)
                match_obj.events.append(event_obj)
            match_df = pd.DataFrame(match_obj.build_dictionary_from_events())
            match_gdf = gpd.GeoDataFrame(match_df,geometry=match_obj.build_point_geometry_list())
            self.parse_time_by_period(match_gdf)
            del match_df
            return match_gdf
            
        return None     

    def load_events_wyscout(self,path_to_events,match_obj):
        """Loads a single match's events from a match. Provide either the matchid, or the index.
        path_to_events: path to folder containing events for matches
        match_obj: match object that contains information about the match
        returns the geodataframe of match events.
        """
        # TODO: Add exception handling.
        # TODO: Match id numbers to text

        mps = {"1H":1,"2H":2,"E1":3,"E2":4,"P":5}
       

        with open(path_to_events, "r",encoding='utf-8') as read_file:
            current_events = json.load(read_file)
            
        if current_events:
            for e in current_events:
                if e["matchId"] == match_obj.match_id:
                    event_obj = event(e["id"])
                    event_obj.match_id = e["matchId"]
                    event_obj.period = mps[e["matchPeriod"]]
                    event_obj.possession_id = None
                    event_obj.possession_team_name = None
                    event_obj.event_team_name = e['teamId']
                    try:
                        event_obj.event_player = e['playerId']
                    except:
                        pass
                    event_obj.event_name = e['eventName']
                    event_obj.subevent_name = e['subEventName']
                    if event_obj.event_name == "Shot":
                        event_obj.is_goal = 0
                        for t in e['tags']:
                            if t['id'] == 101:
                                event_obj.is_goal = 1
                                break
                    else:
                        event_obj.is_goal = 0
                    event_obj.tags = "|".join([str(t["id"]) for t in e["tags"]])
                    locations = e["positions"]
                
                    if len(locations)>0:
                        event_obj.start_x, event_obj.start_y = SpatialSoccer.percent_coordinates_to_statsbomb(float(locations[0]['x']),float(locations[0]['y']))

                        if len(locations)>1:
                            event_obj.end_x, event_obj.end_y = SpatialSoccer.percent_coordinates_to_statsbomb(float(locations[1]['x']),float(locations[1]['y']))
                        else:
                            event_obj.end_x = None
                            event_obj.end_y = None
                    else:
                        event_obj.start_x = None
                        event_obj.start_y = None
                    

                    event_obj.build_points()
                    event_obj.timestamp = e["eventSec"]
                    event_obj.event_time = self.convert_eventseconds(event_obj.timestamp,match_obj.match_date_time)
                    event_obj.original_json = json.dumps(e)
                    match_obj.events.append(event_obj)
            match_df = pd.DataFrame(match_obj.build_dictionary_from_events())
            match_gdf = gpd.GeoDataFrame(match_df,geometry=match_obj.build_point_geometry_list())
            self.parse_time_by_period(match_gdf)
            del match_df
            self.detect_wyscout_basic_possession(match_gdf)
            return match_gdf
            
        return None     

    def detect_wyscout_basic_possession(self,gdf):
        """Identify unique possession segments"""
        # TODO: review this
        p_id = 0
        prev_team = None
        prev_period = None
        for indx,row in gdf.sort_values("event_time").iterrows():
            #print(indx)
            if prev_team == None:
                prev_team = row["event_team_name"]
                prev_period = row["period"]
                gdf.loc[[indx],['possession_id']] = p_id
            elif prev_team == row["event_team_name"]:
                if prev_period == row["period"]:
                    gdf.loc[[indx],['possession_id']] = p_id
                else:
                    prev_period = row["period"]
                    p_id += 1
                    prev_team = row["event_team_name"]
                    gdf.loc[[indx],['possession_id']] = p_id
            elif prev_team != row["event_team_name"]:
                if row['event_name'] not in ["Others on the ball", "Duel"]:
                    p_id += 1
                    prev_team = row["event_team_name"]
                    gdf.loc[[indx],['possession_id']] = p_id
                else:
                    gdf.loc[[indx],['possession_id']] = p_id

        return None



    def parse_time_by_period(self,df):
        """Parse the timestamp of events using the base match kick_off time
        df: dataframe that contains the event information
        match_datetime_dt: match start time, if None, the current_match_datetime_dt is used.
        """
        # TODO: Add exception handling.

        #df['event_time'] = self.convert_timestamp(df['timestamp'].values,match_datetime_dt)

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

    def convert_eventseconds(self, seconds, base_datetime):
        return base_datetime + timedelta(seconds=seconds)

    @staticmethod
    def percent_coordinates_to_statsbomb(percent_x,percent_y, mnx=0,mxx=120,mny=0,mxy=80,flip_y = True):
        """WYSCOUT uses the position as the percentage from the left corner of the attacking team"""
        x_coord = (mxx - mnx) * (percent_x/100.0)
        y_coord = (mxy - mny) * (percent_y/100.0)
        y_coord = SpatialSoccer.flip_coordinate_min_max(y_coord,mny,mxy)
        return (x_coord,y_coord)
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
        center = [(60,40)]
        

        #Y Correction

        outside_line_pairs = [(v[0],SpatialSoccer.flip_coordinate_min_max(v[1],80,0)) for v in outside_line_pairs]
        left_penalty_box = [(v[0],SpatialSoccer.flip_coordinate_min_max(v[1],80,0)) for v in left_penalty_box]
        left_goal_box = [(v[0],SpatialSoccer.flip_coordinate_min_max(v[1],80,0)) for v in left_goal_box]
        center = [(v[0],SpatialSoccer.flip_coordinate_min_max(v[1],80,0)) for v in center]
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
    def build_st_grid(delta,tdelta,mint=0,maxt=7200,llx=0,lly=0,maxX=120,maxY=80):
        """Create a grid of polygons for analysis. 
        delta: width and height of grid cell
        tdelta: time spacing interval
        mint: starting time in seconds
        maxt: ending time in seconds
        llx: lower left x coordinate
        lly: lower left y coordinate
        maxX: maximum x value
        maxY: maximum y value
        returns geodataframe of grid
        """
        xrng = int((maxX-llx)/delta)
        yrng = int((maxY-lly)/delta)
        trng = int((maxt-mint)/tdelta)
        ids = []
        geom = []
        cent = []
        xcoords = []
        ycoords = []
        zcoords = []
        xcoord = llx
        ycoord = lly
        t = mint
        for z in range(0,trng):
            for x in range(0,xrng):
                for y in range(0,yrng):
                    ids.append("r{0}c{1}t{2}".format(y,x,t))
                    p = SpatialSoccer.build_square_polygon(xcoord,ycoord,delta)
                    geom.append(p)
                    cent.append(p.centroid)
                    xcoords.append(p.centroid.x)
                    ycoords.append(p.centroid.y)
                    zcoords.append(t + (tdelta/2.0))
                    ycoord += delta
                xcoord +=delta
                ycoord = lly
            xcoord =llx
            ycoord=lly
            t += tdelta
                
        gdf = gpd.GeoDataFrame({"cell":ids,"centroid":cent,"x_coord":xcoords,"y_coord":ycoords,"time":zcoords},geometry=geom)
        return gdf

    @staticmethod
    def adhoc_bandwidth(event_points):
        """event dataframe"""
        xmean = np.mean(event_points[:,0])
        ymean = np.mean(event_points[:,1])
        sdx = np.sum(np.square(event_points[:,0]-xmean))/len(event_points) #standard distance 
        sdy = np.sum(np.square(event_points[:,1]-ymean))/len(event_points)
        rho = 0.5 * np.sqrt(sdx+sdy)
        bandwidth = rho * np.exp(-((1.0/6.0)*np.log(len(event_points))))
        return bandwidth

    @staticmethod
    def two_d_kernel(cell_pnts,event_pnts,bandwidth):
        densities = []
        for x,y in cell_pnts:
            dist = np.sqrt(np.square(x - event_pnts[:,0])+np.square(y - event_pnts[:,1]))
            if len(dist[dist<bandwidth]) > 0:
                u = dist[dist<bandwidth] / bandwidth
                den = np.sum(np.piecewise(u, [u <= 1.0,u > 1.0],[lambda u:(15.0/16.0) * (np.power((1-np.power(u,2)),2)),lambda u: 0.0]))
                den = 1/(len(event_pnts)*bandwidth)*den
                densities.append(den)
            else:
                densities.append(0)
        return densities

    @staticmethod
    def space_time_kernel_density(st_cell_points,event_points, bandwidth, bandwidth_time):
        """Returns the space-time densities
        st_cell_points: numpy array of cell points x,y,z (z is time in seconds)
        event_points: numpy array of event points x,y,z (z is time in seconds)
        bandwidth: for the spatial bandwidth
        bandwidth_time: for the temporal bandwidth
        return densities
        """
        densities = []
        for x,y,z in cell_pnts:
            dist = np.sqrt(np.square(x - event_points[:,0])+np.square(y - event_points[:,1]))
            dist_t = z - event_points[:,2]
            if len(dist[dist<bandwidth]) > 0 and len(dist_t[dist_t<bandwidth_time]) > 0:
                u = dist[dist<bandwidth] / bandwidth
                u_t = dist_t[dist_t<bandwidth_time] / bandwidth_time
                den_s = np.piecewise(u, [u <= 1.0,u > 1.0],[lambda u:(15.0/16.0) * (np.power((1-np.power(u,2)),2)),lambda u: 0.0])
                den_t = np.piecewise(u, [u_t <= 1.0,u_t > 1.0],[lambda u:(15.0/16.0) * (np.power((1-np.power(u,2)),2)),lambda u: 0.0])
                den = np.sum(den_s*den_t)
                den = 1/(len(event_points)*bandwidth*bandwidth*bandwidth_time)*den
                densities.append(den)
            else:
                densities.append(0)


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

    @staticmethod
    def pname(x):
        try:
            return x['name']
        except:
            return None
    
    @staticmethod
    def gen_dict_extract(key, var):
        """see discussion here: https://stackoverflow.com/questions/9807634/find-all-occurrences-of-a-key-in-nested-dictionaries-and-lists"""
        if hasattr(var,'items'):
            for k, v in var.items():
                if k == key:
                    yield v
                if isinstance(v, dict):
                    for result in SpatialSoccer.gen_dict_extract(key, v):
                        yield result
                elif isinstance(v, list):
                    for d in v:
                        for result in SpatialSoccer.gen_dict_extract(key, d):
                            yield result
    
    @staticmethod
    def shots_from_trajectories(trajectories,place_index = -1):
        shot_place = {"trajectory_id":[],"point":[],"scored":[],"period":[],'x_coord':[],'y_coord':[]}
        for p_id in list(trajectories['trajectory_id'].unique()):
            traj = trajectories[trajectories['trajectory_id']==p_id].sort_values("temporal_distance").copy()
            try:
                p = Point(traj.iloc[place_index][['start_x','start_y']].values)
                shot_place["trajectory_id"].append(p_id)
                shot_place["point"].append(p)
                shot_place["period"].append(traj['period'].mean())
                shot_place["x_coord"].append(p.x)
                shot_place["y_coord"].append(p.y)
                if traj[['is_goal']].sum().iloc[0] >0:
                    shot_place["scored"].append(1)
                else:
                    shot_place["scored"].append(0)
            except:
                pass
            del traj
        shot_place_gdf = gpd.GeoDataFrame(shot_place,geometry=shot_place['point'])
        del shot_place
        return shot_place_gdf

class match(object):
    def __init__(self,match_id):
        self.match_id = match_id
        self.home_team_id = 0
        self.home_team_name = ""
        self.home_team_score = 0
        self.away_team_id = 0
        self.away_team_name = ""
        self.away_team_score = 0
        self.season_id = 0
        self.season_name = ""
        self.kick_off = ""
        self.match_date = ""
        self.match_date_time = datetime.now()
        self.events = []


    def build_dictionary_from_events(self):
        result = {}
        for p in event.EVENT_NUMERIC_PROPERTY_LIST:
            result[p] = []
        for p in event.EVENT_STRING_PROPERTY_LIST:
            result[p] = []
        for p in event.EVENT_DATETIME_PROPERTY_LIST:
            result[p] = []
        for p in event.EVENT_GEOMETRY_PROPERTY_LIST:
            result[p] = []
        for e in self.events:
            for k in result.keys():
                result[k].append(getattr(e, k))
        return result
    
    def build_point_geometry_list(self,start=True):
        geometry = []
        if start:
            for e in self.events:
                geometry.append(getattr(e,"start_point"))
            return geometry
        else:
            if start:
                for e in self.events:
                    geometry.append(getattr(e,"end_point"))
            return geometry

    def build_match_trajectories(self,team_name,only_goals=True,for_team=True):
        """Builds a dataframe of trajectories for either shots (only_goals == false) or goals (only_goals == true)
        team_name: team from the match to build the trajectories
        only_goals: only if you want to use goals, returns none if there were no goals for the team
        for_team: goals for == True, goals against == False
        """
        home = True
        goal_count = 0
        trajectories = None

        if for_team == False:
            if self.home_team_name == team_name:
                team_name = self.away_team_name
            else:
                team_name = self.home_team_name

        if self.home_team_name != team_name:
            home = False
        if home:
            goal_count = self.home_team_score
        else:
            goal_count = self.away_team_score
        

        gdf = gpd.GeoDataFrame(self.build_dictionary_from_events(),geometry=self.build_point_geometry_list())
        if only_goals == True:
            if goal_count > 0:
                possessions = list(gdf.loc[(gdf['is_goal']==1)&(gdf['event_team_name']==team_name)]['possession_id'].values)
            else:
                return None
        else:
            possessions = list(gdf.loc[(gdf['event_name']=='Shot')&(gdf['event_team_name']==team_name)]['possession_id'].values)
        
        for p in possessions:
            possession_id = "{0}_{1}".format(self.match_id,p)
            traj = gdf.loc[gdf['possession_id']==p,].copy()
            traj['trajectory_id'] = possession_id
            drop_rows = list(traj[traj['event_team_name']!=team_name].index)
            traj.drop(drop_rows,inplace=True)
            traj['temporal_distance'] = traj['event_time'].apply(lambda x: (x-self.match_date_time).total_seconds())
            try:
                trajectories = trajectories.append(traj[traj['event_name'].isin(["Ball Receipt*","Pass","Carry","Shot"])],ignore_index=True,sort=False)
            except:
                trajectories = traj[traj['event_name'].isin(["Ball Receipt*","Pass","Carry","Shot"])].copy()
            del traj
        return trajectories

    

class event(object):
    EVENT_NUMERIC_PROPERTY_LIST = ["start_x","start_y","end_x","end_y","is_goal","period","match_id","xg"]
    EVENT_STRING_PROPERTY_LIST = ["event_id","event_name","subevent_name","event_team_name","possession_team_name",
    "event_player","possession_id","timestamp","body_part","tags","original_json"]
    EVENT_DATETIME_PROPERTY_LIST = ["event_time"]
    EVENT_GEOMETRY_PROPERTY_LIST = ["start_point","end_point"]
   
    def __init__(self,event_id):
        self.original_json = ""

        for p in self.EVENT_NUMERIC_PROPERTY_LIST:
            setattr(self, p, None)
        for p in self.EVENT_STRING_PROPERTY_LIST:
            setattr(self, p, None)
        for p in self.EVENT_DATETIME_PROPERTY_LIST:
            setattr(self, p, None)
        for p in self.EVENT_GEOMETRY_PROPERTY_LIST:
            setattr(self, p, None)
        self.event_id = event_id
        

    def build_points(self):
        try:
            self.start_point = Point(self.start_x,self.start_y)
        except:
            self.start_point = None
        try:
            self.end_point = Point(self.end_x,self.end_y)
        except:
            self.end_point = None