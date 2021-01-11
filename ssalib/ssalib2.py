import json
import math
import geopandas as gpd
import pandas as pd
import numpy as np
from shapely.geometry.point import Point
from shapely.geometry import LineString
from shapely.geometry import Polygon
from shapely import affinity
from dateutil.parser import parse
from datetime import datetime
from datetime import timedelta
import csv
import string

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
    METRICA_DATA = 3
    SKILLCORNER_DATA = 4
    NFL_DATA = 5
    TEAM_AWAY = "Away Team"
    TEAM_HOME = "Home Team"
    TYPE_PLAYER = "Player"
    TYPE_REF = "Referee"
    TYPE_BALL = "Ball"
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
        if data_source == self.METRICA_DATA:
            return self.get_matches_metrica(path_to_matches,team_name)
        if data_source == self.SKILLCORNER_DATA:
            return self.get_matches_skillcorner(path_to_matches,team_name)
        if data_source == self.NFL_DATA:
            return self.get_matches_nfl(path_to_matches,team_name)
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

    def get_matches_metrica(self,path_to_matches,team_name=None):
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
                mt.match_date_time = parse(m['match_date_str'])
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

    def get_matches_nfl(self,path_to_matches,team_name=None):
        matches = []
        in_matches = pd.read_csv(path_to_matches, encoding ='utf-8')
        for idx,m in in_matches.iterrows():
            mt = match(m['gameId'])
            mt.home_team_id = m['homeTeamAbbr']
            mt.home_team_name = m['homeTeamAbbr']
            mt.home_team_score = 0
            mt.away_team_id = m['visitorTeamAbbr']
            mt.away_team_name = m['visitorTeamAbbr']
            mt.away_team_score = 0
            datetimestr = "{0} {1}".format(m['gameDate'],m['gameTimeEastern'])
            mt.match_date_time = parse(datetimestr)
            mt.week = m['week']
            if team_name:
                if mt.home_team_name == team_name:
                    matches.append(mt)
                elif mt.away_team_name == team_name:
                    matches.append(mt)
                else:
                    pass
            else:
                if m['gameId']:
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
                for vj in v['formation']['bench']:
                    hp = player()
                    hp.player_id = vj['playerId']
                    hp.own_goals = vj['ownGoals']
                    hp.red_cards = vj['redCards']
                    hp.yellow_cards = vj['yellowCards']
                    hp.goals = vj['goals']
                    if v['side'] == 'home' or v['side']=='none':
                        mt.home_players.append(hp)
                    else:
                        mt.away_players.append(hp)
                for vj in v['formation']['lineup']:
                    hp = player()
                    hp.lineup = 1
                    hp.player_id = vj['playerId']
                    hp.own_goals = vj['ownGoals']
                    hp.red_cards = vj['redCards']
                    hp.yellow_cards = vj['yellowCards']
                    hp.goals = vj['goals']
                    if v['side'] == 'home' or v['side']=='none':
                        mt.home_players.append(hp)
                    else:
                        mt.away_players.append(hp)                       
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

    def get_matches_skillcorner(self,path_to_matches,team_name=None):
        matches = []
        with open(path_to_matches, "r",encoding='utf-8') as read_file:
            in_matches = json.load(read_file)
            
            for m in in_matches:
                mt = match(m['id'])
                mt.home_team_id = m['home_team']['short_name']
                mt.home_team_name = m['home_team']['short_name']
                mt.home_team_score = -1
                mt.away_team_id = m['away_team']['short_name']
                mt.away_team_name = m['away_team']['short_name']
                mt.away_team_score = -1
                mt.match_date_time = parse(m['date_time'])
                if team_name:
                    if mt.home_team_name == team_name:
                        matches.append(mt)
                    elif mt.away_team_name == team_name:
                        matches.append(mt)
                    else:
                        pass
                else:
                    if m['id']:
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
        if data_source == self.METRICA_DATA:
            return self.load_events_metrica(path_to_events,match_obj)
        if data_source == self.NFL_DATA:
            return self.load_events_nfl(path_to_events,match_obj)

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
            match_obj.events = []
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
            match_obj.events = []
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
    
    def load_events_metrica(self,path_to_events,match_obj):
        """Loads a single match's events from a match. Provide either the matchid, or the index.
        path_to_events: path to folder containing events for matches
        match_obj: match object that contains information about the match
        returns the geodataframe of match events.
        """
        # TODO: Add exception handling.
        # TODO: Match id numbers to text

        c_i = {"Team":0,"Type":1,"Subtype":2,"Period":3,"Start Frame":4,"Start Time [s]":5,"End Frame":6,
                        "End Time [s]":7,"From":8,"To":9,"Start X":10,"Start Y":11,"End X":12,"End Y":13}
       
        path_to_events = path_to_events + "\\" + match_obj.match_id + ".csv"
        print(path_to_events)
        with open(path_to_events, "r",encoding='utf-8',newline='') as read_file:
            reader = csv.reader(read_file)
            idx = 1000
            init = 0
            match_obj.events = []
            for e in reader:
                if init == 0:
                    init+=1
                    pass
                else:
                    event_obj = event(idx)
                    event_obj.match_id = match_obj.match_id
                    event_obj.period = e[c_i['Period']]
                    event_obj.possession_id = None
                    event_obj.possession_team_name = None
                    event_obj.event_team_name = e[c_i['Team']]
                    #EVENT_NUMERIC_PROPERTY_LIST = ["start_x","start_y","end_x","end_y","is_goal","period","match_id","xg"]
                    event_obj.add_numeric_attributes(["end_time","start_frame","end_frame"])
                    try:
                        event_obj.event_player = e[c_i['From']]
                    except:
                        pass
                    event_obj.event_name = e[c_i['Type']]
                    event_obj.subevent_name = e[c_i['Subtype']]
                    event_obj.is_goal = None
                    #if event_obj.event_name == "Shot":
                    #    event_obj.is_goal = 0
                    #    for t in e['tags']:
                    #        if t['id'] == 101:
                    #            event_obj.is_goal = 1
                    #            break
                    #else:
                    #    event_obj.is_goal = 0
                    event_obj.tags = None #"|".join([str(t["id"]) for t in e["tags"]])
                    locations = [[e[c_i['Start X']],e[c_i['Start Y']]], [e[c_i['End X']],e[c_i['End Y']]]]
                
                    if len(locations)>0:
                        try:
                            event_obj.start_x, event_obj.start_y = SpatialSoccer.proportion_coordinates_to_statsbomb(float(locations[0][0]),float(locations[0][1]))
                        except:
                            event_obj.start_x = None
                            event_obj.start_y = None

                        if len(locations)>1:
                            try:
                                event_obj.end_x, event_obj.end_y = SpatialSoccer.proportion_coordinates_to_statsbomb(float(locations[1][0]),float(locations[1][1]))
                            except:
                                event_obj.end_x = None
                                event_obj.end_y = None
                        else:
                            event_obj.end_x = None
                            event_obj.end_y = None
                    else:
                        event_obj.start_x = None
                        event_obj.start_y = None
                    

                    event_obj.build_points()
                    event_obj.timestamp = float(e[c_i["Start Time [s]"]])
                    event_obj.event_time = self.convert_eventseconds(event_obj.timestamp,match_obj.match_date_time)
                    event_obj.end_time = float(e[c_i["End Time [s]"]])
                    event_obj.start_frame = int(e[c_i["Start Frame"]])
                    event_obj.end_frame = int(e[c_i["End Frame"]])
                    event_obj.original_json = ",".join(e)
                    match_obj.events.append(event_obj)
                    idx +=1
            print(len(match_obj.events))
            match_df = pd.DataFrame(match_obj.build_dictionary_from_events())
            print(len(match_df))
            match_gdf = gpd.GeoDataFrame(match_df,geometry=match_obj.build_point_geometry_list())
            print(len(match_gdf))
            self.parse_time_by_period(match_gdf)
            del match_df
            #self.detect_wyscout_basic_possession(match_gdf)
            return match_gdf
            
        return None  

    def load_events_nfl(self,path_to_events,match_obj):
        """Loads a single match's events from a match. Provide either the matchid, or the index.
        path_to_events: path to folder containing events for matches
        match_obj: match object that contains information about the match
        returns the geodataframe of match events. 
        """
        # TODO: Add exception handling.

        
        #path_to_events = path_to_events + '/week' + str(match_obj.week) + '.csv'
        current_events = pd.read_csv(path_to_events,encoding='utf-8')

        match_obj.events = []
        for idx,e in current_events.iterrows():
            if e["gameId"] == match_obj.match_id:
                event_obj = event(e["playId"])
                try:
                    event_obj.period = e["quarter"]
                except:
                    event_obj.period = -1
                try:
                    event_obj.possession_id = e['down']
                except:
                    event_obj.possession_id = -1

                try:
                    event_obj.possession_team_name = e['possessionTeam']
                except:
                    event_obj.possession_team_name = -1
                try:
                    event_obj.event_team_name = e['possessionTeam']
                except:
                    event_obj.event_team_name = -1
                try:
                    event_obj.match_id = match_obj.match_id
                except:
                    event_obj.match_id = -1
                try:
                    event_obj.event_player = ""
                except:
                    pass
                try:
                    event_obj.event_name = e['playType']
                except:
                    event_obj.event_name = - 1
                

                event_obj.start_x = float(e['absoluteYardlineNumber'])+10.0
                event_obj.start_y = 0.0
                event_obj.end_x = float(e['absoluteYardlineNumber'])+10.0+float(e['playResult'])
                event_obj.end_y = 0.0

                    

                event_obj.build_points()
                event_obj.original_json = e.to_dict()
                match_obj.events.append(event_obj)
        match_df = pd.DataFrame(match_obj.build_dictionary_from_events())
        match_gdf = gpd.GeoDataFrame(match_df,geometry=match_obj.build_point_geometry_list())
        return match_gdf
    
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

    def load_metrica_tracking(self,path_to_tracks,ignore_ball = False):
        """Loads csv file of tracking data
        returns geodataframe
        """
        
        outdata = []
        outcolumns = ["team","period","frame","x_coord","y_coord","time","point","playerid"]
        
        with open(path_to_tracks, "r",encoding='utf-8',newline='') as read_file:
            reader = csv.reader(read_file)
            init = 0
            current_team = ""
            player_jerseys = []
            column_names = ["Period","Frame","Time [s]"]
            player_columns = []

            for t in reader:
                if init == 0:
                    #row 1
                    for x in t:
                        if x != "":
                            current_team = x
                            break
                    init+= 1
                elif init == 1:
                    #row 2
                    #print(t)
                    for x in t:
                        if x != "":
                            player_jerseys.append(x)
                    #print(player_jerseys)
                    for jn in player_jerseys:
                        player_columns.append("Player_{0}_x".format(jn))
                        player_columns.append("Player_{0}_y".format(jn))
                    if ignore_ball == False:
                        player_columns.append("Ball_x")
                        player_columns.append("Ball_y")
                    #print(player_columns)
                    init+= 1
                elif init == 2:
                    #row 3
                    init+= 1
                else:
                    #rest of data
                    #outvector [period,frame,x,y,z,point,playerid]
                    period = int(t[0])
                    frame = int(t[1])
                    z = float(t[2])
                    
                    for i in range(3,len(player_columns)+3,2):
                        
                        try:
                            x,y = SpatialSoccer.proportion_coordinates_to_statsbomb(float(t[i]),float(t[i+1]))
                            p = Point(x,y,z)
                        except:
                            x = None
                            y = None
                            p = None
                        outdata.append([current_team,period,frame,x,y,z,p,player_columns[i-3].replace("_x","")])
        df = pd.DataFrame(outdata,columns=outcolumns)
        gdf = gpd.GeoDataFrame(df,geometry=df["point"])
        del df
        return gdf

    def load_skillcorner_tracking(self,path_to_tracks,path_to_match_info,ignore_ball = False):
        """Loads json file of tracking data
        returns geodataframe
        """
        match_info = {}
        home_away_info = {}
        with open(path_to_match_info,"r",encoding='utf-8') as read_file:
            match_json = json.load(read_file)
            home_away_info[match_json['away_team']['id']] = {"Type":self.TEAM_AWAY,"short_name":match_json['away_team']['short_name']}
            home_away_info[match_json['home_team']['id']] = {"Type":self.TEAM_HOME,"short_name":match_json['home_team']['short_name']}
            for r in match_json["referees"]:
                match_info[r['trackable_object']] = {"Name":r['last_name'],"Type":self.TYPE_REF,"Team":None,"ID":r['id'],"Position":None,"TeamName":"Referee"}
            for p in match_json['players']:
                if home_away_info[p['team_id']]["Type"] == self.TEAM_HOME:
                    home = True
                else:
                    home = False
                match_info[p['trackable_object']] = {"Name":p['last_name'],"Type":self.TYPE_PLAYER,"TeamID":p['team_id'],"TeamPlayerID":p['team_player_id'],
                                                    "HomeTeam":home,"TeamName":home_away_info[p['team_id']]["short_name"],"ID":p['id'],"Position":None}
                match_info[p['trackable_object']]['Position'] = p['player_role']['acronym']
            match_info[match_json['ball']['trackable_object']] = {"Name":"Ball","Type":self.TYPE_BALL,"TeamName":"Ball","Position":None}
        outdata = []
        outcolumns = ["group","team","period","frame","x_coord","y_coord","z_coord","time","point","objectid","trackid","playername","position","type"]
        
        with open(path_to_tracks, "r",encoding='utf-8',newline='') as read_file:
            print("Processing tracks...")
            tracks_json = json.load(read_file)
            for t in tracks_json:
                cg = t['possession']['group']
                cp = t['period']
                cf = t['frame']
                ct = t['time']
                for d in t['data']:
                    track_obj = {x:None for x in outcolumns}
                    track_obj['group'] = cg
                    track_obj['period'] = cp
                    track_obj['frame'] = cf
                    track_obj['time'] = ct
                    coords = SpatialSoccer.skillcorner_coordinates_to_statsbomb(d['x'],d['y'])
                    track_obj['x_coord'] = coords[0]
                    track_obj['y_coord'] = coords[1]
                    track_obj['point'] = Point(coords)
                    try:
                        track_obj['z_coord'] = d['z']
                    except:
                        track_obj['z_coord'] = 0
                    track_obj["trackid"] = d["track_id"]
                    try:
                        track_obj['objectid'] = d["trackable_object"]
                    except:
                        track_obj['objectid'] = -9999
                    try:
                        track_obj['playername'] = match_info[d["trackable_object"]]["Name"]
                    except:
                        track_obj['playername'] = ""
                    try:
                        track_obj['position'] = match_info[d["trackable_object"]]["Position"]
                    except:
                        track_obj['position'] = ""
                    try:
                        track_obj['type'] = match_info[d["trackable_object"]]["Type"]
                    except:
                        track_obj['type'] = ""
                    try:
                        track_obj['team'] = match_info[d["trackable_object"]]["TeamName"]
                    except:
                        track_obj['team'] = ""
                    outdata.append([track_obj[k] for k in outcolumns])
                    del track_obj
        df = pd.DataFrame(outdata,columns=outcolumns)
        gdf = gpd.GeoDataFrame(df,geometry=df["point"])
        print("Completed!")
        del df
        return gdf

    def load_nfl_tracking(self,path_to_tracks,match_obj,normalize_to_same_direction = False):
        """Loads csv file of tracking data
        path_to_tracks should be the root folder containing the week*.csv files
        match_obj can be loaded as above
        normalize_to_same_direction Not Implemented Yet, meant to be a place holder to take the change in direction of play after each quarter
        returns geodataframe
        """
        
        outdata = []
        path_to_tracks = path_to_tracks + '/week' + str(match_obj.week) + '.csv'
        df = pd.read_csv(path_to_tracks,encoding='utf-8')
        df = df[df['gameId'] == match_obj.match_id].copy()
        #players = pd.read_csv(path_to_players,encoding='utf-8')
        geometry = [Point(x,y) for x,y in df[['x','y']].values]


        #for playerid in df['nflid'].values:
            #position = players[players['nflid']]==playerid]
        
        gdf = gpd.GeoDataFrame(df,geometry=geometry)
        gdf.loc[pd.isnull(gdf['position']),"position"]="Ball"
        gdf['fulldatetime'] = [parse(tstr) for tstr in gdf['time'].values]
        mindttime = np.min(gdf['fulldatetime'].values)
        tds = [fdt-mindttime for fdt in gdf['fulldatetime'].values]
        gdf['nsec'] = tds
        gdf['total_seconds'] = gdf['nsec'].dt.total_seconds()
        del df
        return gdf

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
        if flip_y:
            y_coord = SpatialSoccer.flip_coordinate_min_max(y_coord,mny,mxy)
        return (x_coord,y_coord)
    
    @staticmethod
    def proportion_coordinates_to_statsbomb(prop_x,prop_y, mnx=0,mxx=120,mny=0,mxy=80,flip_y = True):
        """WYSCOUT uses the position as the percentage from the left corner of the attacking team"""
        x_coord = (mxx - mnx) * (prop_x)
        y_coord = (mxy - mny) * (prop_y)
        if flip_y:
            y_coord = SpatialSoccer.flip_coordinate_min_max(y_coord,mny,mxy)
        return (x_coord,y_coord)

    @staticmethod
    def skillcorner_coordinates_to_statsbomb(raw_x,raw_y, mnx=0,mxx=120,mny=0,mxy=80,flip_y = False):
        """WYSCOUT uses the position as the percentage from the left corner of the attacking team"""
        prop_x = (raw_x + 52.5)/105.0
        prop_y = (raw_y + 34) / 68
        
        x_coord = (mxx - mnx) * (prop_x)
        y_coord = (mxy - mny) * (prop_y)
        if flip_y:
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
    def build_polygon_field_nfl():
        """Builds a pitch based on nfl's defined."""
        #polygons
        outside_line_pairs = [(0,0),(120,0),(120,53.3),(0,53.3),(0,0)]
        left_end_zone = [(0,0),(10,0),(10,53.3),(0,53.3),(0,0)]
        right_end_zone = [(110,0),(120,0),(120,53.3),(110,53.3),(110,0)]
        geometry = [Polygon(outside_line_pairs),Polygon(left_end_zone),
                Polygon(right_end_zone)]
        #DataFrame
        df_dict = {"Description":['Outside Boundary Line','Home Endzone','Visitor Endzone']}
        for i in range(0,60,10):
            if i == 0:
                label = "Goal Line"
                ln = LineString([(i,0),(i,53.3)])
                ln1 = LineString([(100,0),(100,53.3)])
                df_dict['Description'].append(label)
                df_dict['Description'].append(label)
                geometry.append(ln)
                geometry.append(ln1)
            elif i == 50:
                label = "50 yard line"
                ln = LineString([(i+10,0),(i+10,53.3)])
                df_dict['Description'].append(label)
                geometry.append(ln)
            else:
                label = "{0} yard line".format(i)
                ln = LineString([(i+10,0),(i+10,53.3)])
                ln1 = LineString([(100-i+10,0),(100-i+10,53.3)])
                df_dict['Description'].append(label)
                df_dict['Description'].append(label)
                geometry.append(ln)
                geometry.append(ln1)

        pitchgdf = gpd.GeoDataFrame(df_dict,geometry=geometry)
        return pitchgdf
    
    @staticmethod
    def build_plot_field_nfl(ax):
        """Builds a plot for the nfl field."""
        field = SpatialSoccer.build_polygon_field_nfl()
        field[field['Description'] == "Outside Boundary Line"].plot(ax=ax,facecolor=SpatialSoccer.GREEN_PITCH_COLOR,edgecolor ="black")
        field[field['Description'] == "Home Endzone"].plot(ax=ax,facecolor="red",edgecolor ="black",alpha=.6)
        field[field['Description'] == "Visitor Endzone"].plot(ax=ax,facecolor="blue",edgecolor ="black",alpha=.6)
        for yard in field['Description'].unique():
            if 'yard line' in yard:
                field[field['Description'] == yard].plot(ax=ax,color=SpatialSoccer.WHITE_LINE_COLOR)
                ls = field[field['Description'] == yard]['geometry'].values[0]


    @staticmethod
    def build_18zones_statsbomb_dim():
        alpha = list(string.ascii_lowercase)
        x_gap = 20
        zones = {"zone":[],"zone_lbl":[],"zone_geometry":[]}
        zone_i = 1
        for i in range(0,120,20):
            for j in range(0,3):
                if j == 0:
                    zn = Polygon([(i,80),(i+20,80),(i+20,80-18),(i,80-18),(i,80)])
                    zones['zone'].append(zone_i)
                    zones['zone_lbl'].append(alpha[zone_i-1])
                    zones['zone_geometry'].append(zn)
                    zone_i+=1
                if j == 1:
                    zn = Polygon([(i,80-18),(i+20,80-18),(i+20,80-62),(i,80-62),(i,80-18)])
                    zones['zone'].append(zone_i)
                    zones['zone_lbl'].append(alpha[zone_i-1])
                    zones['zone_geometry'].append(zn)
                    zone_i+=1
                if j == 2:
                    zn = Polygon([(i,80-62),(i+20,80-62),(i+20,0),(i,0),(i,80-62)])
                    zones['zone'].append(zone_i)
                    zones['zone_lbl'].append(alpha[zone_i-1])
                    zones['zone_geometry'].append(zn)
                    zone_i+=1
        zngdf = gpd.GeoDataFrame(zones,geometry=zones['zone_geometry'])
        return zngdf

    @staticmethod
    def angle_to_goal(pt,goallength=20,returnradians=True):
        """Calculate the angle to the goal from the pt
        pt: Point (shapely class)
        goallength: length of the goal, default is the statsbomb dimension
        returnradians: radians are returned if true, degrees if false
        returns angle (theta)
        see: https://github.com/Friends-of-Tracking-Data-FoTD/SoccermaticsForPython/blob/master/3xGModel.py
        """
        glh = (goallength/2)
        a = np.arctan(goallength*pt.x / (pt.x*pt.x + pt.y*pt.y - (glh*glh)))
        if a <0:
            a = np.pi + a
        if returnradians:
            return a
        else:
            return np.degrees(a)

    @staticmethod
    def bearing(pt1,pt2):
        """Returns the direction\angle of a line between two points.
        pt1: Point (shapely class) one.
        pt2: Point (shapely class) two.
        returns angle in degrees.
        """
        if type(pt1) == Point:
            x_diff = pt2.x - pt1.x
            y_diff = pt2.y - pt1.y
        else:
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
    def player_velocities(gdf,player_id_field,point_field,time_field,maxspeed=12,smooth=True,window=7):
        unique_players = gdf[player_id_field].unique()
        gdf['vx'] = np.zeros(len(gdf))
        gdf['vy'] = np.zeros(len(gdf))
        gdf['xc'] = gdf[point_field].apply(lambda x: x.x)
        gdf['yc'] = gdf[point_field].apply(lambda x: x.y)
        gdf['dt'] = gdf[time_field].diff()
        gdf['velocity'] = np.zeros(len(gdf))
        for p in unique_players:
            gdf.loc[gdf[player_id_field]==p,'dt'] = gdf[gdf[player_id_field]==p][time_field].diff()
            gdf.loc[gdf[player_id_field]==p,'vx'] = gdf[gdf[player_id_field]==p]['xc'].diff()/ gdf[gdf[player_id_field]==p]['dt']
            gdf.loc[gdf[player_id_field]==p,'vy'] = gdf[gdf[player_id_field]==p]['yc'].diff()/ gdf[gdf[player_id_field]==p]['dt']
            if maxspeed>0:
                # remove unsmoothed data points that exceed the maximum speed (these are most likely position errors)
                raw_speed = np.sqrt( gdf['vx']*gdf['vx'] + gdf['vy']*gdf['vy'] )
                try:
                    gdf.loc[raw_speed>maxspeed,'vx'] = np.nan
                    gdf.loc[raw_speed>maxspeed,'vy'] = np.nan
                except:
                    pass
            if smooth:
                gdf.loc[gdf[player_id_field]==p,'vx'] = gdf[gdf[player_id_field]==p]['vx'].rolling(7,min_periods=1).mean()
                gdf.loc[gdf[player_id_field]==p,'vy'] = gdf[gdf[player_id_field]==p]['vy'].rolling(7,min_periods=1).mean()
            gdf.loc[gdf[player_id_field]==p,'velocity'] = np.sqrt(np.square(gdf[gdf[player_id_field]==p]['vx']) + np.square(gdf[gdf[player_id_field]==p]['vy']))
        gdf['vx'].fillna(0,inplace=True)
        gdf['vy'].fillna(0,inplace=True)
        gdf['velocity'].fillna(0,inplace=True)
        gdf['dt'].fillna(0,inplace=True)
    
    @staticmethod
    def pitch_control_at_target(target_point,ball_point,player_attack_df,player_defense_df, point_field, velocity_field, reaction_field, ball_velocity=15):

        source = "https://github.com/Friends-of-Tracking-Data-FoTD/LaurieOnTracking"
        #reaction_point_a = player_attack_df[[point_field, velocity_field, reaction_field]].apply(lambda x: x.interpolate)
        #reaction_point_d = player_defense_df[[point_field, velocity_field, reaction_field]].apply(lambda x: Point(x[0].x + x[1]*x[2],x[0].y+ x[1]*x[2]))
        kappa_def =  1. # kappa parameter in Spearman 2018 (=1.72 in the paper) that gives the advantage defending players to control ball, I have set to 1 so that home & away players have same ball control probability
        lambda_att = 4.3 # ball control parameter for attacking team
        lambda_def = 4.3 * kappa_def # ball control parameter for defending team
        time_to_control_veto = 3
        int_dt = 0.04
        tti_sigma = .45
        max_int_time = 10 
        model_converge_tol = 0.01
        time_to_control_a = time_to_control_veto*np.log(10) * (np.sqrt(3)*tti_sigma/np.pi + 1/lambda_att)
        time_to_control_d = time_to_control_veto*np.log(10) * (np.sqrt(3)*tti_sigma/np.pi + 1/lambda_def)

        time_to_intercept_a = player_attack_df[[point_field, velocity_field, reaction_field]].apply(lambda x: x[2] + x[0].distance(target_point) / x[1], axis=1)
        time_to_intercept_d = player_defense_df[[point_field, velocity_field, reaction_field]].apply(lambda x: x[2] + x[0].distance(target_point) / x[1], axis=1)
        ball_travel_time = target_point.distance(ball_point) / ball_velocity
        tau_min_a = np.nanmin(time_to_intercept_a)
        tau_min_d = np.nanmin(time_to_intercept_d)
        
        if tau_min_a-max(ball_travel_time,tau_min_d) >= time_to_control_d:
            # if defending team can arrive significantly before attacking team, no need to solve pitch control model
            return 0., 1.
        elif tau_min_d-max(ball_travel_time,tau_min_a) >= time_to_control_a:
            # if attacking team can arrive significantly before defending team, no need to solve pitch control model
            return 1., 0.
        else: 
            attacking_players = time_to_intercept_a[(time_to_intercept_a-tau_min_a)<time_to_control_a]
            defending_players = time_to_intercept_d[(time_to_intercept_d-tau_min_d)<time_to_control_d]
            attack_ppcf = np.zeros(len(attacking_players))
            defend_ppcf = np.zeros(len(defending_players))
            # set up integration arrays
            dT_array = np.arange(ball_travel_time-int_dt,ball_travel_time+max_int_time,int_dt) 
            PPCFatt = np.zeros_like( dT_array )
            PPCFdef = np.zeros_like( dT_array )
            # integration equation 3 of Spearman 2018 until convergence or tolerance limit hit (see 'params')
            ptot = 0.0
            i = 1
            while 1-ptot>model_converge_tol and i<dT_array.size: 
                T = dT_array[i]
                #f = 1/(1. + np.exp( -np.pi/np.sqrt(3.0)/self.tti_sigma * (T-self.time_to_intercept) ) )
                prob_a = 1/(1. + np.exp( -np.pi/np.sqrt(3.0)/tti_sigma * (T-attacking_players) ) )
                dPPCFdT = (1-PPCFatt[i-1]-PPCFdef[i-1])*prob_a * lambda_att
                attack_ppcf+=(dPPCFdT * int_dt)
                PPCFatt[i] += attack_ppcf.sum()
                prob_d = 1/(1. + np.exp( -np.pi/np.sqrt(3.0)/tti_sigma * (T-defending_players) ) )
                dPPCFdT = (1-PPCFatt[i-1]-PPCFdef[i-1])*prob_d * lambda_def
                defend_ppcf+=(dPPCFdT * int_dt)
                PPCFdef[i] += defend_ppcf.sum()
                
                ptot = PPCFdef[i]+PPCFatt[i] # total pitch control probability 
                i += 1
        if i>=dT_array.size:
            print("Integration failed to converge: %1.3f" % (ptot) )
        return PPCFatt[i-1], PPCFdef[i-1]
        
                        



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
    def space_time_kernel_density(cell_pnts,event_points, bandwidth, bandwidth_time):
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
                den_t = np.piecewise(u_t, [u_t <= 1.0,u_t > 1.0],[lambda u:(15.0/16.0) * (np.power((1-np.power(u,2)),2)),lambda u: 0.0])
                den = np.sum(den_s*den_t)
                den = 1/(len(event_points)*bandwidth*bandwidth*bandwidth_time)*den
                densities.append(den)
            else:
                densities.append(0)
        return densities

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
        shot_place = {"trajectory_id":[],"point":[],"scored":[],"period":[],'x_coord':[],'y_coord':[],'original_json':[]}
        for p_id in list(trajectories['trajectory_id'].unique()):
            traj = trajectories[trajectories['trajectory_id']==p_id].sort_values("temporal_distance").copy()
            try:
                p = Point(traj.iloc[place_index][['start_x','start_y']].values)
                shot_place["trajectory_id"].append(p_id)
                shot_place["point"].append(p)
                shot_place["period"].append(traj['period'].mean())
                shot_place["x_coord"].append(p.x)
                shot_place["y_coord"].append(p.y)
                shot_place["original_json"].append(traj['original_json'])
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
        self.home_players = []
        self.away_players = []
        self.week = ""

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

class player(object):
    def __init__(self):
        self.player_id = -1
        self.own_goals = 0
        self.red_cards = 0
        self.yellow_cards = 0
        self.goals = 0
        self.position = ""
        self.last_name = ""
        self.first_name = ""
        self.full_name = ""
        self.lineup = 0



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
    
    def add_numeric_attributes(self,attributes=None):
        if attributes:
            for a in attributes:
                setattr(self, a, None)
                self.EVENT_NUMERIC_PROPERTY_LIST.append(a)
