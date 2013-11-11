__author__ = 'dominum'

from google.appengine.ext import ndb


class EventModel(ndb.Model):
    """Models an individual event entry with content and date."""
    event = ndb.StringProperty(indexed=True)
    country = ndb.StringProperty(indexed=False)
    content = ndb.StringProperty(indexed=False)
    date = ndb.DateTimeProperty(auto_now_add=True)


DEFAULT_EVENT = 'default_event'


def event_key(event_name=DEFAULT_EVENT):
    """Constructs a Datastore key for a EventModel entity with event_name."""
    return ndb.Key('EventModel', event_name)

