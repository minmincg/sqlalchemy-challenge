import numpy as np

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine,func
import datetime as dt


from flask import Flask, jsonify

#######################################################
#Database Setup
#######################################################
engine = create_engine("sqlite:///../Resources/hawaii.sqlite")

#Reflect an existing database into a model
Base = automap_base()
#reflect the tables
Base.prepare(autoload_with=engine)

#Save reference to the table
Measurement = Base.classes.measurement
Station = Base.classes.station

#######################################################
#Flask setup
#######################################################
app = Flask(__name__)

@app.route("/")
def welcome():
    return(
        f"Available Routes:<br>"
        f"/api/v1.0/precipitation<br>"
        f"/api/v1.0/stations<br>"
        f"/api/v1.0/tobs<br>"
        f"/api/v1.0/date/&lt;start&gt;<br>"
        f"/api/v1.0/date/&lt;start&gt;/&lt;end&gt;<br>"
        f"start and end date in format yyyy-mm-dd"
    )



@app.route("/api/v1.0/precipitation")
def precipitation():
    session=Session(engine)

    # last_date = session.query(Measurement.date).order_by(Measurement.date.desc()).first()
    # Calculate the date one year from the last date in data set.
    last_year = dt.date(2017,8,23) - dt.timedelta(days=365)
    # Perform a query to retrieve the data and precipitation scores
    sel=[Measurement.date,
     Measurement.prcp
    ]
    results = session.query(*sel).filter(Measurement.date>=last_year).order_by(Measurement.date).all()

    session.close()

    dictionary={}

    for date, prcp in results:
        dictionary[date]=prcp
    return jsonify(dictionary)

@app.route("/api/v1.0/stations")
def stations():
    session = Session(engine)
    results = session.query(Station.station).all()
    session.close()

    stations=list(np.ravel(results))
    return jsonify(stations)

@app.route("/api/v1.0/tobs")
def temperatures():
    session = Session(engine)

    last_year = dt.date(2017,8,18) - dt.timedelta(days=365)

    sel2=[Measurement.date,
    Measurement.tobs]

    results = session.query(*sel2).filter(Measurement.date>=last_year).\
        filter(Measurement.station=='USC00519281').\
        group_by(Measurement.date).\
        order_by(Measurement.date.desc()).all()
    session.close()

    tobs=list(np.ravel(results))


    ##tried this for reference and though it looked nicer.
    # temperatures=[]
    # for date, tobs in results:
    #     dict={}
    #     dict["date"]=date
    #     dict["tobs"]=tobs
    #     temperatures.append(dict)
    return jsonify(tobs)
@app.route("/api/v1.0/date/<start>")
def beggining(start=None):
    
    session = Session(engine)

    sel = [func.min(Measurement.tobs),
        func.max(Measurement.tobs),
        func.avg(Measurement.tobs)
       ]
    results=session.query(*sel).filter(Measurement.date>=start).all()

    session.close()
    temps=list(np.ravel(results))
    return jsonify(temps)

@app.route("/api/v1.0/date/<start>/<end>")
def range(start=None,end=None):
    
    session = Session(engine)

    sel = [func.min(Measurement.tobs),
        func.max(Measurement.tobs),
        func.avg(Measurement.tobs)
       ]
    # if "<end>"=="":
        # results=session.query(*sel).filter(Measurement.date>=start).all()
    # else:
    results=session.query(*sel).filter(Measurement.date>=start).filter(Measurement.date<=end).all()
    session.close()
    temperatures=list(np.ravel(results))
    return jsonify(temperatures)

if __name__ == '__main__':
    app.run(debug=True)