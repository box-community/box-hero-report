# app.py

import os
import logging
from flask import Flask, request, Response, render_template, json
from flask.ext.sqlalchemy import SQLAlchemy
from config import BaseConfig

app = Flask(__name__)
app.config.from_object(BaseConfig)
db = SQLAlchemy(app)

from tasks import BackgroundTasks
from models import *


@app.route('/', methods=['GET'])
def index():
	return render_template('index.html')

@app.route('/velocity/file', methods=['GET'])
def velocity_file():
	return render_template('velocity-file.html')

@app.route('/velocity/engagement', methods=['GET'])
def velocity_engagement():
	return render_template('velocity-engagement.html')

@app.route('/velocity/stat', methods=['GET'])
def velocity():
	result = []
	epoch = datetime.datetime.utcfromtimestamp(0)

	event_types = request.args.get('event_type').split(',')
	for event_type in event_types:
		series = [] 
		stats = Stat.query.filter(Stat.measure == event_type).order_by(Stat.starting.asc()).all()
		for stat in stats:
			series.append([(stat.starting - epoch).total_seconds() * 1000, stat.value])
		result.append(series)
	return Response(json.dumps(result),  mimetype='application/json')


@app.before_first_request
def init():
	app.logger.debug("Init pid {}".format(os.getpid()))
	statrec = BackgroundTasks(db, app.logger, app.config['ACCESS_TOKEN'], app.config['REFRESH_TOKEN'])
	statrec.schedule()

if __name__ == '__main__':
	app.run(debug=False, use_reloader=False)