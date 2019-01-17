#!/usr/bin/env python
# -*- coding: utf-8 -*-

import json
import re

from flask import Flask, render_template
import requests


app = Flask(__name__)

@app.route('/')
def main_page():
	#Get from ThingSpeak
	thingspeak_req = requests.get('https://thingspeak.com/channels/1417/feed.json')
	
	#Parse JSON
	thingspeak_data = json.loads(thingspeak_req.text)
	
	#Get latest color
	latest_color = thingspeak_data['feeds'][-1]['field2']
	
	#Sanitize data from the Internet
	safe_color = '#FFFFFF'
	color_exp = re.compile('([#][ABCDEFabcdef0123456789]{6})')
	color_match = color_exp.match(latest_color)
	if color_match is not None:
		safe_color = color_match.group(1)
	
	#Render template
	return render_template('webpage_template.html', b_color=safe_color)


if __name__ == "__main__":
	app.run(host='0.0.0.0')
