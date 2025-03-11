# Import the dependencies.
import numpy as np
import pandas as pd
import datetime as dt
from flask import Flask, jsonify
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func


#################################################
# Database Setup
#################################################

# Create engine using the `hawaii.sqlite` database file
engine = create_engine("sqlite:///Resources/hawaii.sqlite")
# Declare a Base using `automap_base()`
Base = automap_base()


# Use the Base class to reflect the database tables
Base.prepare(engine, reflect=True)


# Assign the measurement class to a variable called `Measurement` and
# the station class to a variable called `Station`

Measurement = Base.classes.measurement
Station = Base.classes.station

# Create a session

#################################################
# Flask Setup

app = Flask(__name__)

#################################################


#################################################
# Flask Routes
@app.route("/")
def home():
    return (
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/&lt;start&gt;<br/>"
        f"/api/v1.0/&lt;start&gt;/&lt;end&gt;"
    )

# Route to get precipitation data for the last 12 months
@app.route("/api/v1.0/precipitation")
def precipitation():
    session = Session(engine)
    most_recent_date = session.query(func.max(Measurement.date)).scalar()
    most_recent_date = dt.datetime.strptime(most_recent_date, "%Y-%m-%d")
    one_year_ago = most_recent_date - dt.timedelta(days=365)

    results = session.query(Measurement.date, Measurement.prcp)\
                     .filter(Measurement.date >= one_year_ago).all()
    session.close()

    return jsonify({date: prcp for date, prcp in results})

# Route to get a list of stations
@app.route("/api/v1.0/stations")
def stations():
    session = Session(engine)
    results = session.query(Station.station).all()
    session.close()
    return jsonify([station[0] for station in results])

# Route to get temperature observations of the most active station for the last year
@app.route("/api/v1.0/tobs")
def tobs():
    session = Session(engine)
    most_active_station = session.query(Measurement.station)\
                                 .group_by(Measurement.station)\
                                 .order_by(func.count(Measurement.station).desc())\
                                 .first()[0]
    
    most_recent_date = session.query(func.max(Measurement.date))\
                              .filter(Measurement.station == most_active_station).scalar()
    most_recent_date = dt.datetime.strptime(most_recent_date, "%Y-%m-%d")
    one_year_ago = most_recent_date - dt.timedelta(days=365)

    results = session.query(Measurement.date, Measurement.tobs)\
                     .filter(Measurement.station == most_active_station)\
                     .filter(Measurement.date >= one_year_ago).all()
    session.close()

    return jsonify([{date: tobs} for date, tobs in results])

# Route to get temperature stats from a start date onward
@app.route("/api/v1.0/<start>")
def temp_stats_start(start):
    session = Session(engine)
    results = session.query(func.min(Measurement.tobs),
                            func.avg(Measurement.tobs),
                            func.max(Measurement.tobs))\
                     .filter(Measurement.date >= start).all()
    session.close()
    
    return jsonify({
        "Min Temperature": results[0][0],
        "Avg Temperature": results[0][1],
        "Max Temperature": results[0][2]
    })

# Route to get temperature stats between a start and end date
@app.route("/api/v1.0/<start>/<end>")
def temp_stats_range(start, end):
    session = Session(engine)
    results = session.query(func.min(Measurement.tobs),
                            func.avg(Measurement.tobs),
                            func.max(Measurement.tobs))\
                     .filter(Measurement.date >= start)\
                     .filter(Measurement.date <= end).all()
    session.close()

    return jsonify({
        "Min Temperature": results[0][0],
        "Avg Temperature": results[0][1],
        "Max Temperature": results[0][2]
    })

# Run the Flask app
if __name__ == "__main__":
    app.run(debug=True)


#################################################
