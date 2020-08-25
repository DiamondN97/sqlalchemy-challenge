from flask import Flask, jsonify, request
# from matplotlib import style
# style.use('fivethirtyeight')
# import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import datetime as dt
from datetime import timedelta
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func


engine = create_engine("sqlite:///Resources/hawaii.sqlite")
Base = automap_base()
Base.prepare(engine, reflect = True)
Tables = Base.classes.keys()
measurement = Base.classes.measurement
station = Base.classes.station

session = Session(engine)
#Find last 12 months of precipitation data to store on appropriate flask app page
## Start with finding last date in dataset
last = session.query(func.max(measurement.date))
##Initialize list to store last date object when we find it
last_date = []
##Add last date to its list
for l in last:
    last_date.append(l)
begin = dt.date(2017, 8, 23)
##Find date 12 months before the last date to retrieve last 12 months of precip data & plot results
year_range = begin - dt.timedelta(days = 365)
# print(year_range)
date = session.query(measurement.date, measurement.prcp).filter(measurement.date >= year_range).all()
rain = pd.DataFrame(date, columns=['date', 'precipitation'])
rain_dict = rain.to_dict('records')
# print(Tables)
# print(rain_dict)
# print(station)


stations=session.query(measurement.station, func.count(measurement.station)).group_by(measurement.station).order_by(measurement.station.desc())
# print(stations)
stations_df = pd.DataFrame(stations, columns=['station', 'count'])
stations_df = stations_df.sort_values(by = ['count'], ascending = False)
# print(stations_df)

stations_dict = stations_df.to_dict('records')
# print(active_station_dict)
temperatures = session.query(measurement.date, measurement.tobs).filter(measurement.date >= year_range).all()
temperatures_df = pd.DataFrame(temperatures, columns = ['date', 'temperature'])
temperature_dict = temperatures_df.to_dict('records')
# print(temperature_dict)


app = Flask(__name__)
@app.route("/")
def home():
	print("Server received request for homepage")
	return   """<html><head></head><body><h1>Climate App Home Page</h1>
	<p><em>Available URL routes:</em></p><ul></body><br/><li><u>/api/v1.0/precipitation</u> --  Rainfall data over the past 12 months.<br/><br/> 
	<li><u>/api/v1.0/stations</u> -- Weather station information. <br/><br/> 
	<li><u>/api/v1.0/tobs</u> -- Temperature observations from the most active station. <br/><br/> 
	<li><u>/api/v1.0/start</u> -- The minimum, maximum and average temperatures for a specific date. <br/><br/> 
	<li><u>/api/v1.0/start/end</u> -- The minimum, maximum and average temperatures for a range of dates. </html></ul>"""


@app.route("/api/v1.0/precipitation")
def precipitation():
    print("Server received request for rainfall data.")
    return jsonify(rain_dict)

@app.route("/api/v1.0/stations")
def stations():
	print("Server received request for weather station data")
	return jsonify(stations_dict)

@app.route("/api/v1.0/tobs")
def tobs():
	print("Server received request for temperature data")
	return jsonify(temperature_dict)

@app.route("/api/v1.0/start")
def datesa():
    return """
        <html><body>
            <h2>Weather data for a specific date</h2>
            <form action="/date">
                Enter a specific date between 2010/01/01 and 2017/08/23</br>
                Must be in <em>YYYYMMDD</em> format </br>
                <input type = 'text' name = 'startdate'></br>
                <input type = 'submit' value = 'Continue'>
            </form>
        </body></html>
        """
@app.route("/date")
def temps():
    startdate = request.args['startdate']
    start = pd.to_datetime(str(startdate), format = '%Y%m%d').date()
    engine = create_engine("sqlite:///Resources/hawaii.sqlite")
    Base = automap_base()
    Base.prepare(engine, reflect = True)
    Tables = Base.classes.keys()
    measurement = Base.classes.measurement
    station = Base.classes.station
    session = Session(engine)
    temps = session.query(measurement.date, func.min(measurement.tobs), func.max(measurement.tobs), func.avg(measurement.tobs)).group_by(measurement.date).filter(measurement.date >= start).all()
    temps_df = pd.DataFrame(temps, columns = ['date', 'min_temp', 'max_temp', 'avg_temp']).head(1)
    temps_dict = temps_df.to_dict('records')
    return jsonify(temps_dict)

@app.route("/api/v1.0/start/end")
def daterange():
	return """
        <html><body>
            <h2>Weather data for a range of dates</h2>
            <form action="/date2">
                Enter a range of dates between 2010/01/01 and 2017/08/23</br>
                Must be in <em>YYYYMMDD</em> format </br>
                <input type = 'text' name = 'startdate'></br>
                <input type = 'text' name = 'enddate'</br>
                <input type = 'submit' value = 'Continue'>
            </form>
        </body></html>
        """
@app.route("/date2")
def temprange():
    startdate = request.args['startdate']
    enddate = request.args['enddate']
    start = pd.to_datetime(str(startdate), format = '%Y%m%d').date()
    end = pd.to_datetime(str(enddate), format = '%Y%m%d').date()
    engine = create_engine("sqlite:///Resources/hawaii.sqlite")
    Base = automap_base()
    Base.prepare(engine, reflect = True)
    Tables = Base.classes.keys()
    measurement = Base.classes.measurement
    station = Base.classes.station
    session = Session(engine)
    rangetemps = session.query(measurement.date, func.min(measurement.tobs), func.max(measurement.tobs), func.avg(measurement.tobs)).group_by(measurement.date).filter(measurement.date >= start).filter(measurement.date <= end).all()
    rangetemps_df = pd.DataFrame(rangetemps, columns = ['date', 'min_temp', 'max_temp', 'avg_temp'])
    rangetemps_dict = rangetemps_df.to_dict('records')
    return jsonify(rangetemps_dict)

if __name__ == "__main__":
    app.run(debug = True)