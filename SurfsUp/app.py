# Import the dependencies.
import numpy as np
import datetime as dt

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

from flask import Flask, jsonify

#################################################
# Database Setup
#################################################

engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()

# reflect the tables

Base.prepare(autoload_with=engine)

# Save references to each table

measurement = Base.classes.measurement
Station = Base.classes.station

# Create our session (link) from Python to the DB

session = Session(engine)

#################################################
# Flask Setup
#################################################

app = Flask(__name__)


#################################################
# Flask Routes
#################################################
@app.route("/")
def welcome():
   
    return (
        
        f"<h1> Climate App</h1><br/>" 
        f"<h2> Part 2 SQLalchemy challenge</h2><br/>"
        f"<br/>"
        f"<h3>Available routes</h3><br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/2014-05-01  - Please enter a date between <strong>2010-01-01  and 2017-08-23</strong> YYYY-MM-DD format <br/>"
        f"/api/v1.0/2014-05-01/2015-04-30 - please enter a <strong>start date and end date</strong> between <strong>2010-01-01 and 2017-08-23</strong> in YYYY-MM-DD format "
    )


@app.route("/api/v1.0/precipitation")
def precipitation():
 
    session = Session(engine)
    
    enddate = session.query(func.max(measurement.date)).\
                    scalar()
    dt_enddate= dt.datetime.strptime(enddate,"%Y-%m-%d").date()
    dt_startdate = dt_enddate - dt.timedelta(days=365)
    startdate = dt_startdate.strftime("%Y-%m-%d")
    results = session.query(measurement.date, measurement.prcp).\
            filter(measurement.date.between(startdate,enddate)).\
            all()
    
    session.close()
    
    precip = []
    for date, prcp in results:
            precip_dict ={}
            precip_dict['date'] = date
            precip_dict['prcp'] = prcp
            precip.append(precip_dict)
    return jsonify(precip)



@app.route("/api/v1.0/stations")
def stations():
    
    session = Session(engine)

    results = session.query(Station.name).all()

    session.close()


    all_stations = list(np.ravel(results))
    return jsonify(all_stations)


@app.route("/api/v1.0/tobs")
def tobs():
 
    session = Session(engine)

    station2 = session.query(measurement.station).\
                    group_by(measurement.station).\
                    order_by(func.count(measurement.station).desc()).\
                    subquery()

    enddate = session.query(func.max(measurement.date)).\
                    scalar()
    dt_enddate= dt.datetime.strptime(enddate,"%Y-%m-%d").date()
    dt_startdate = dt_enddate - dt.timedelta(days=365)
    startdate = dt_startdate.strftime("%Y-%m-%d")
    
    results = session.query(measurement.date, measurement.tobs).\
                filter(measurement.date.between(startdate,enddate)).\
                filter(measurement.station.in_(station2)).\
                all()
    session.close()

    topStation = []
    for date, tobs in results:
            tobs_dict ={}
            tobs_dict['date'] = date
            tobs_dict['tobs'] = tobs
            topStation.append(tobs_dict)
    return jsonify(topStation)


@app.route("/api/v1.0/<start>")
@app.route("/api/v1.0/<start>/<end>")
def rangestart(start,end=None):
 
    session=Session(engine)
    if end == None:
        enddate = session.query(func.max(measurement.date)).\
                    scalar()
    else:
        enddate = str(end)
    startdate = str(start)
    results = session.query(func.min(measurement.tobs).label('min_temp'),
                            func.avg(measurement.tobs).label('avg_temp'),
                            func.max(measurement.tobs).label('max_temp')).\
                filter(measurement.date.between(startdate,enddate)).\
                first()
    session.close()
    datapoints = list(np.ravel(results))
    return jsonify(datapoints)



if __name__ == "__main__":
    app.run(debug=False)