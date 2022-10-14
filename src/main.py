import json
import requests
from tweepy import API, OAuthHandler
from tweepy.models import Status
import time
from dacite.core import from_dict
from datetime import datetime, timedelta
from flask import Flask, make_response
import settings
from typing import Optional, List
from src.data import Vote


app = Flask(__name__)


@app.route("/")
def main():
    """Pulls Congress votes for the previous day and tweets out the results."""
    api = _initialize_tweepy()

    curr_time = datetime.now()

    votes = _get_votes(curr_time)

    print(
        f"{len(votes)} votes to tweet for f{curr_time.date().isoformat} "
        f"{(curr_time.hour - 4) % 24} to {curr_time.hour}."
    )

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

        api.update_status(tweet)

        time.sleep(5)  # Avoid rate-limiting

    return make_response("200")


def _get_votes(for_datetime: Optional[datetime] = None) -> List[Vote]:
    """Returns recent Congress votes.

    Args:
        for_date:
            If provided, only return votes that happened on the date provided.
    """
    last_hour_date_time = (
        for_datetime - timedelta(hours=1)
        if for_datetime
        else None
    )

    assert settings.PROPUBLICA_API_KEY

    response = requests.get(
        "https://api.propublica.org/congress/v1/both/votes/recent.json",
        headers={"X-API-Key": settings.PROPUBLICA_API_KEY}
    )

    votes = [
        from_dict(data_class=Vote, data=v)
        for v in response.json()["results"]["votes"]
    ]

    return [
        v
        for v in votes
        if (
            last_hour_date_time is None
            or datetime.fromisoformat(v.date + "T" + v.time) >= last_hour_date_time
        )
    ]


def _initialize_tweepy() -> API:
    """Initialize the Twitter API client."""
    auth = OAuthHandler(settings.TWEEPY_CONSUMER_KEY, settings.TWEEPY_CONSUMER_SECRET)
    auth.set_access_token(settings.TWEEPY_ACCESS_TOKEN, settings.TWEEPY_ACCESS_TOKEN_SECRET)
    return API(auth)
