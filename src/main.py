import requests
import os
import tweepy
import time
from dataclasses import dataclass
from dacite import from_dict
from datetime import date, timedelta
from typing import Optional, List

PROPUBLICA_API_KEY = os.environ.get("PROPUBLICA_API_KEY")
TWEEPY_CONSUMER_KEY = os.environ.get("TWEEPY_CONSUMER_KEY")
TWEEPY_CONSUMER_SECRET = os.environ.get("TWEEPY_CONSUMER_SECRET")
TWEEPY_ACCESS_TOKEN = os.environ.get("TWEEPY_ACCESS_TOKEN")
TWEEPY_ACCESS_TOKEN_SECRET = os.environ.get("TWEEPY_ACCESS_TOKEN_SECRET")


@dataclass
class VoteBreakdown:
    """The breakdown of yeas and nays on a vote."""
    yes: int
    no: int


@dataclass
class Vote:
    """A vote in Congress."""
    chamber: str
    description: str
    result: str
    democratic: VoteBreakdown
    republican: VoteBreakdown
    total: VoteBreakdown
    date: str
    time: str

def main():
    """Pulls Congress votes for the previous day and tweets out the results."""
    
    # set current time for filtering to only last hour
    curr_time = datetime.now()

    votes = _get_votes(curr_time)

    tweepy = _initialize_tweepy()

    # Construct and send the tweet for each vote for the day.
    for v in votes:
        line1 = f"New vote {curr_time.date().strftime('%-m/%-d/%Y')} in the {v.chamber.capitalize()}.\n\n"
        line2 = f"{v.description}\n\n"
        line3 = (
            f"The vote {v.result.lower()} with {v.total.yes} yea{'' if v.total.yes ==1 else 's'} "
            f"(D: {v.democratic.yes}, R: {v.republican.yes}) "
            f"and {v.total.no} nay{'' if v.total.no ==1 else 's'} "
            f"(D: {v.democratic.no}, R: {v.republican.no})."
        )

        tweet = line1 + line2 + line3

        # TODO: Uncomment this line
        # tweepy.update_status(tweet)

        # Avoid rate-limiting
        time.sleep(5)


def _get_votes(for_datetime: Optional[datetime] = None) -> List[Vote]:
    """Returns recent Congress votes.

    Args:
        for_datetime:
            If provided, only return votes that happened on the date provided.
    """
    last_hour_date_time = for_datetime - timedelta(hours = 1)
    
    response = requests.get(
        "https://api.propublica.org/congress/v1/both/votes/recent.json",
        headers={"X-API-Key": PROPUBLICA_API_KEY}
    )

    votes = [
        from_dict(data_class=Vote, data=v)
        for v in response.json()["results"]["votes"]
    ]

    return [
        v
        for v in votes
        
        if not datetime.strptime((v.date + v.time), "%Y-%m-%d %H-%M-%S") >= last_hour_date_time:
              
        if not for_datetime or date.fromisoformat(v.date) == for_datetime
    ]


def _initialize_tweepy() -> Optional[tweepy.API]:
    """Initialize the Twitter API client."""
    # TODO: Uncomment these lines
    # auth = tweepy.OAuthHandler(TWEEPY_CONSUMER_KEY, TWEEPY_CONSUMER_SECRET)
    # auth.set_access_token(TWEEPY_ACCESS_TOKEN, TWEEPY_ACCESS_TOKEN_SECRET)

    # return tweepy.API(auth)
    return None
