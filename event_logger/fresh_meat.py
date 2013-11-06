__author__ = 'dominum'

from google.appengine.ext import ndb
from event_logger.model import EventModel, event_key, DEFAULT_EVENT

class Observer(object):

    def observe_event(self, event):
        """Override in class which inherits Observer"""
        pass


class ApplicationEvent(object):

    observers = {}

    @classmethod
    def subscribe(cls, event, observer):
        """Add new observer to list of observers"""
        if event not in cls.observers:
            cls.observers[event] = []
        cls.observers[event].append(observer)

    @classmethod
    def notify(cls, event):
        """Notify all observers for  given event"""
        if event in cls.observers:
            for o in cls.observers[event]:
                o.observe_event(event)


class EventCounter(Observer):

    def observe_event(self, e):
        event_name = e if e else DEFAULT_EVENT
        event = EventModel(parent=event_key(event_name))
        event.event = event_name
        event.content = 'Test Content'
        event.put()
