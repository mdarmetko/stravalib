"""
Entity classes for representing the various Strava datatypes. 
"""
import abc

from stravalib import exc

class StravaEntity(object):
    """
    Base class holds properties/functionality that Strava entities have in common.
    """
    __metaclass__ = abc.ABCMeta
    
    id = None
    name = None
            
    def __init__(self, bind_client=None):
        """
        Base entity initializer, which accepts a client parameter that creates a "bound" entity
        which can perform additional lazy loading of content.
        
        :param bind_client: The client instance to bind to this entity.
        :type bind_client: :class:`stravalib.simple.Client`
        """
        self._bind_client = bind_client
    
        
    def hydrate(self):
        """
        Fill this object with data from the bound client.
        
        This default implementation assumes things about the names of methods in the client, so
        may need to be overridden by subclasses.
        """
        if not self._bind_client:
            raise exc.UnboundEntity("Cannot set entity attributes for unbound entity.")
        assumed_method_name = '_populate_{0}'.format(self.__class__.__name__.lower())
        method = getattr(self._bind_client, assumed_method_name)
        method(self.id, self)
    
    def __repr__(self):
        return '<{0} id={id} name={name!r}>'.format(self.__class__.__name__, id=self.id, name=self.name)
     
class Club(StravaEntity):
    """
    Class to represent Strava clubs/teams.
    """
    description = None
    location = None
    
    def __init__(self, entity_pouplator=None, members_fetcher=None):
        super(Club, self).__init__(entity_pouplator=entity_pouplator)
        self._members_fetcher = members_fetcher
        self._members = None
    
    @property
    def members(self):
        if self._members is None:
            if self._members_fetcher is None:
                raise exc.UnboundEntity("Unable to retrieve members for unbound {0} entity.".format(self.__class__))
            else:
                self._members = self._members_fetcher()  
        return self._members
    
class Athlete(StravaEntity):
    """
    Represents a Strava athlete.
    """
    username = None

class RideEffortBase(StravaEntity):
    """
    Abstract class that holds the attributes that Rides and Efforts share in common.
    """
    athlete = None
    start_date = None
    
    average_speed = None
    maximum_speed = None
    average_watts = None
    
    distance = None
    elevation_gain = None 
    
    elapsed_time = None
    moving_time = None
    
class Ride(RideEffortBase):
    """
    Represents a Strava activity.
    """
    commute = None # V1
    trainer = None # V1
    
    location = None # V1, V2
    start_latlon = None # V2
    end_latlon = None # V2
    
    _efforts = None
    
    @property
    def efforts(self):
        if self._efforts is None:
            
            if self._members_fetcher is None:
                raise exc.UnboundEntity("Unable to retrieve members for unbound {0} entity.".format(self.__class__))
            else:
                self._members = self._members_fetcher()  
        return self._members
    
# The Strava API is somewhat tailored to cycling, but we will 
# alias Activity in the expectation that the v3 API will provide a more
# generic interface.
Activity = Ride

class Effort(RideEffortBase):
    ride = None
    segment = None
    
class Segment(StravaEntity):
    distance = None
    elevation_gain = None
    elevation_high = None
    elevation_low = None
    average_grade = None
    climb_category = None
    
    # API V2 provides latlon info, but apparently must get to it via effort 
    start_latlon = None
    end_latlon = None
    
    _efforts = None
    
    @property
    def efforts(self):
        if self._efforts is None:
            if self._efforts_fetcher is None:
                raise exc.UnboundEntity("Unable to retrieve efforts for unbound {0} entity.".format(self.__class__))
            else:
                self._efforts = self._bind_client.get_segment_efforts()  
        return self._efforts
    
