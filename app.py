import numpy as np
import datetime as dt

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func, and_

from flask import Flask, jsonify

engine = create_engine("sqlite:///Resources/hawaii.sqlite")

Base = automap_base()
Base.prepare(engine, reflect=True)

Measurement = Base.classes.measurement
Station = Base.classes.station

app = Flask(__name__)

# Flask Routes
@app.route("/")
def welcome():
    return (
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/&lt;start&gt;<br/>"
        f"/api/v1.0/&lt;start&gt;/&lt;end&gt;"
    )

@app.route("/api/v1.0/precipitation")
def precipitation():
    session = Session(engine)
    
    results =   session.query(Measurement.date, Measurement.prcp).\
                order_by(Measurement.date).all()

    prcplist = []

    for date, prcp in results:
        new_dict = {}
        new_dict[date] = prcp
        prcplist.append(new_dict)

    session.close()

    return jsonify(prcplist)

@app.route("/api/v1.0/stations")
def stations():

    session = Session(engine)

    stations = {}

    results = session.query(Station.station, Station.name).all()
    for s,name in results:
        stations[s] = name

    session.close()
 
    return jsonify(stations)

@app.route("/api/v1.0/tobs")
def tobs():
    session = Session(engine)

    lastdate = session.query(Measurement.date).order_by(Measurement.date.desc()).first()
    oneyear = (dt.datetime.strptime(lastdate[0],'%Y-%m-%d') - dt.timedelta(days=365)).strftime('%Y-%m-%d')

    results =   session.query(Measurement.date, Measurement.tobs).\
                filter(Measurement.date >= oneyear).\
                order_by(Measurement.date).all()

    tobslist = []

    for date, tobs in results:
        new_dict = {}
        new_dict[date] = tobs
        tobslist.append(new_dict)

    session.close()

    return jsonify(tobslist)

@app.route("/api/v1.0/<start>")
def temp_start(start):

    session = Session(engine)

    return_list = []

    results =   session.query(Measurement.date,func.min(Measurement.tobs),func.avg(Measurement.tobs),\
                              func.max(Measurement.tobs)).filter(Measurement.date >= start).\
                                group_by(Measurement.date).all()

    for date, min, avg, max in results:
        new_dict = {}
        new_dict["Date"] = date
        new_dict["TMIN"] = min
        new_dict["TAVG"] = avg
        new_dict["TMAX"] = max
        return_list.append(new_dict)

    session.close()    

    return jsonify(return_list)

@app.route("/api/v1.0/<start>/<end>")
def temp_start_end(start,end):

    session = Session(engine)

    return_list = []

    results =   session.query(Measurement.date, func.min(Measurement.tobs), func.avg(Measurement.tobs),\
                                func.max(Measurement.tobs)).filter(and_(Measurement.date >= start, Measurement.date <= end)).\
                                group_by(Measurement.date).all()

    for date, min, avg, max in results:
        new_dict = {}
        new_dict["Date"] = date
        new_dict["TMIN"] = min
        new_dict["TAVG"] = avg
        new_dict["TMAX"] = max
        return_list.append(new_dict)

    session.close()    

    return jsonify(return_list)

if __name__ == '__main__':
    app.run(debug=True)