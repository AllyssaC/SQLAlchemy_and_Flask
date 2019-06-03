#Climate App: A Flask API based on quaries developed
#Import Dependencies
import pandas as pd     
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, inspect, func
from flask import Flask, jsonify
import datetime as dt   
import numpy as np   
##############################################
#Database Setup
##############################################
engine = create_engine("sqlite:///hawaii.sqlite")
Base = automap_base()
Base.prepare(engine, reflect=True)

Station = Base.classes.station
Measurement = Base.classes.measurement

session = Session(engine)

###############################################
#Flask
app = Flask(__name__)
###############################################
#Flask Routes
@app.route("/")
def home():
    print ("Welcome to my Hawaii Climate App")
    
#List all available api Routes
    return(   
        f"Welcome to my Hawaii Climate App<br>"
        f"Available Routes:<br>"
        f"/api/v1.0/precipitation<br>"
        f"/api/v1.0/stations<br>"
        f"/api/v1.0/tobs<br>"
        f"/api/v1.0/start<br>"
        f"/api/v1.0/temp/start/end"
        
    )

#* Convert the query results to a Dictionary using `date` as the key and `prcp` as the value.
   
@app.route("/api/v1.0/precipitation")
def precipitation():
    results = session.query(Measurement.date, Measurement.prcp).filter(Measurement.date >'2016-08-23').\
              order_by(Measurement.date).all()
    
    all_prcp = []
    for prcp_data in results:
        prcp_dict = {}
        prcp_dict["date"] = prcp_data.date
        prcp_dict["prcp"] = prcp_data.prcp
        all_prcp.append(prcp_dict)

    return jsonify(all_prcp)

#Return a JSON list of stations from the dataset
@app.route("/api/v1.0/stations")
def stations ():
    results = session.query(Station.station, Station.name).distinct(Station.station).all()
     
  #work out the tuples  
    all_results = list(np.ravel(results))
    return jsonify(all_results)
#leave until you ask TAs why this query doesn't work since it put out desired result in Jupyter
# def station():
#     results = session.query(Measurement.station, func.count(Measurement.tobs)).\
#               group_by(Measurement.station).\
#               order_by(func.count(Measurement.tobs).desc())

#     all_stations = []
#     for name, count in results:
#         station_dict = {}
#         print(station)
#         station_dict['Station'] = station{0}
#         station_dict['Station Name'] = name
#         station_dict['Latitude'] = station.latitude
#         station_dict['Longitude'] = station.longitude
#         station_dict["Elevation"] = station.Elevations
#         all_stations.append(station_dict)

#     return jsonify(all_stations)
    
#Query for the dates and temperature observations from a year from the last data point

@app.route("/api/v1.0/tobs") 
def tobs():
    results = session.query(Measurement.date, Measurement.tobs, Measurement.station).\
              group_by (Measurement.date).\
              filter(Measurement.date > '2016-08-23').all()
    temp_data = []
    for tobs_data in results:
        tobs_dict = {}
        tobs_dict['Station'] = tobs_data.station
        tobs_dict['Date'] = tobs_data.date
        tobs_dict['Temperature'] = tobs_data.tobs
        temp_data.append(tobs_dict)
    
        all_results = list(np.ravel(temp_data))
    return jsonify(all_results)   

#This was my original code and hoping someone could help me see why it wouldn't work.    
#`/api/v1.0/<start>` and `/api/v1.0/<start>/<end>`
# Return a JSON list of the minimum temperature, the average temperature, and the max temperature for a given start or start-end range.
# When given the start only, calculate `TMIN`, `TAVG`, and `TMAX` for all dates greater than and equal to the start date.

# @app.route("/api/v1.0/<start_date>")
# def start(start_date):
#     minimum = session.query(Measurement.tobs,func.min(Measurement.tobs)).filter(Measurement.date >= start_date)
#     maximum = session.query(Measurement.tobs,func.max(Measurement.tobs)).filter(Measurement.date >= start_date)   
#     average = session.query(Measurement.tobs,func.avg(Measurement.tobs)).filter(Measurement.date >= start_date)   
#     start_temp = {"TMIN": minimum[0][0], "TMAX": maximum[0][0], "TAVG": average [0][0]}

#     return jsonify(start_temp)

#When given the start and the end date, calculate the `TMIN`, `TAVG`, and `TMAX` for dates between the start and end date inclusive.
 
# @app.route("/api/v1.0/<start_date>")
# def start_end(start_date, end_date):
#     minimum = session.query(Measurement.tobs,func.min(Measurement.tobs)).filter(Measurement.date >= start_date).filter(Measurement.date <= end_date).all()
#     maximum = session.query(Measurement.tobs,func.max(Measurement.tobs)).filter(Measurement.date >= start_date).filter(Measurement.date <= end_date).all()
#     average = session.query(Measurement.tobs,func.avg(Measurement.tobs)).filter(Measurement.date >= start_date).filter(Measurement.date <= end_date).all()
#     start_end_temps = {"TMIN": minimum[0][0], "TMAX": maximum[0][0], "TAVG": average[0][0]}

#     return jsonify(start_end_temps)

###Trying another way using select#####
@app.route("/api/v1.0/temp/<start>")
@app.route("/api/v1.0/temp/<start>/<end>")
def stats(start=None, end=None):
    sel = [func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)]

    if not end:
        # calculate TMIN, TAVG, TMAX for dates greater than start
        results = session.query(*sel).filter(Measurement.date >= start).all()
        temps = list(np.ravel(results))
        return jsonify(temps)

    # with start and end dates
    results = session.query(*sel).filter(Measurement.date >= start).filter(Measurement.date <= end).all()
    temps = list(np.ravel(results))
    return jsonify(temps)


if __name__ == "__main__":
    app.run(debug=True)

