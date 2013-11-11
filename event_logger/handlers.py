__author__ = 'dominum'

import os
import webapp2
import json
import jinja2
from collections import Counter
from event_logger.fresh_meat import ApplicationEvent, EventCounter, log_event
from event_logger.model import EventModel
from google.appengine.api import memcache

JINJA_ENVIRONMENT = jinja2.Environment(
    loader=jinja2.FileSystemLoader(os.path.dirname(__file__) + "/../templates"),
    extensions=['jinja2.ext.autoescape'],
    autoescape=True)


class GlobalStatisticsHandler(webapp2.RequestHandler):

    def get(self):
        self.c = Counter()
        #result = EventModel.query().map(self.count)
        #esult = self.c
        result = self.get_data()
        template = JINJA_ENVIRONMENT.get_template('index.html')
        self.response.write(template.render(template_values=result))

    def count(self, x):
       self.c[x.event] += 1

    def get_data(self):
        all_in_cache = True
        result = {}
        for e in ApplicationEvent.observers.keys():
            data = memcache.get(e)
            if data is not None:
                result[e] = data
            else:
                all_in_cache = False
                break
        if not all_in_cache:
            EventModel.query().map(self.count)
            result = self.c
            # should use batch if goes bigger
            for k, v in result.items():
                memcache.add(k, v, 3600)
        return result


class EventListHandler(webapp2.RequestHandler):

    def get(self):
        event_name = self.request.get('event_name')
        query = EventModel.query(EventModel.event == event_name)
        template = JINJA_ENVIRONMENT.get_template('events.html')

        #self.response.write(self._sum_by_countries(query.iter()))

        self.response.write(template.render(event_name = event_name, template_values=query.iter(), countries=self._sum_by_countries(query.iter())))

    def _sum_by_countries(self, data):
        """Sum events by countries to show on map"""
        result = {}
        for d in data:
            if d.country is not None and d.country not in ['', 'zz', 'ZZ']:
                result[d.country] = result.get(d.country, 0) + 1
        return json.dumps(result)


class WonHandler(webapp2.RequestHandler):

    @log_event('game-won')
    def get(self):
        country = self.request.headers.get('X-appengine-country')
        self.response.write('Event game-won has been triggered from ' + country)


class RegisteredHandler(webapp2.RequestHandler):

    @log_event('user-registered')
    def get(self):
        country = self.request.headers.get('X-appengine-country')
        self.response.write('Event user-registered has been triggered from ' + country)