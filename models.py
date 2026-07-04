from datetime import datetime
from pydantic import BaseModel


class FlightChangeModel(BaseModel):
    flight_id:int|str
    parameter:str
    old_value:str
    new_value:str
    modified_at:str|datetime

# TOPICS
ADD_SUBSCRIPTION='subscriptions'
FLIGHT_CHANGES='flight-changes'
SENT_NOTIFICATIONS='sent-notifications'

#KAFKA CONSUMER CONFIG
CONSUMER_OF = [FLIGHT_CHANGES, ADD_SUBSCRIPTION]
PRODUCE_TO = [SENT_NOTIFICATIONS]
