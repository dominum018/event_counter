__author__ = 'dominum'

from google.appengine.ext import ndb
from google.appengine.api import memcache
from event_logger.model import EventModel, event_key, DEFAULT_EVENT


class Observer(object):

    def observe_event(self, event, **kwargs):
        """Override in class which inherits Observer"""
        pass


class ApplicationEvent(object):
    """Subscribes and notifies listeners for some events"""
    observers = {}

    @classmethod
    def subscribe(cls, event, observer):
        """Add new observer to list of observers"""
        if event not in cls.observers:
            cls.observers[event] = []
        cls.observers[event].append(observer)

    @classmethod
    def notify(cls, event, **kwargs):
        """Notify all observers for  given event"""
        if event in cls.observers:
            for o in cls.observers[event]:
                o.observe_event(event, **kwargs)


class EventCounter(Observer):

    def observe_event(self, e, **kwargs):
        event_name = e if e else DEFAULT_EVENT
        event = EventModel(parent=event_key(event_name))
        event.event = event_name
        event.content = 'Test Content'
        event.country = kwargs.get('country', 'ZZ') if len(kwargs) else 'zz'
        event.put()

        memcache.incr(key=event_name, delta=1)


def log_event(event_name):
    """Decorator for tagging which function triggers which event"""
    def extract_country(f):
      def wrapper(self):
        country = self.request.headers.get('X-appengine-country')
        ApplicationEvent.notify(event_name, country=country)
        return f(self)
      return wrapper
    return extract_country


def init(*args):
    """Initialize app for basic events and put in memcache 0 value for each registered event"""
    event_counter = EventCounter()
    for e in args:
        ApplicationEvent.subscribe(e, event_counter)
        memcache.add(e, 0, 10)
    ApplicationEvent.notify('app-started')
