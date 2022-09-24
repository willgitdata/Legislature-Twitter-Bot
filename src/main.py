import requests
# import tweepy
from dataclasses import dataclass
from dacite import from_dict
from datetime import date
from typing import Optional


@dataclass
class Bill:
    title: Optional[str]
    latest_action: Optional[str]


@dataclass
class VoteBreakdown:
    yes: int
    no: int


@dataclass
class Vote:
    chamber: str
    bill: Bill
    description: str
    result: str
    democratic: VoteBreakdown
    republican: VoteBreakdown
    total: VoteBreakdown
    date: str


def main():
    # Set all static variables
    # Create variables for each key, secret, token
    consumer_key = ''
    consumer_secret = ''
    access_token = ''
    access_token_secret = ''

    # Set up OAuth and integrate with API
    # auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
    # auth.set_access_token(access_token, access_token_secret)
    # api = tweepy.API(auth)

    votes = _get_votes(date(2022, 9, 22))

    for v in votes:
        # construct tweet from data

        # send tweet

        # wait
        pass


def _get_votes(for_date: Optional[date] = None):
    response = requests.get(
        "https://api.propublica.org/congress/v1/both/votes/recent.json",
        headers={"X-API-Key": "LqW2bJv0Rt5C441mv8rQJtVqCVTDPAEdKoUNMgaI"}
    )

    votes = [
        from_dict(data_class=Vote, data=v)
        for v in response.json()["results"]["votes"]
    ]

    return [
        v
        for v in votes
        if date.fromisoformat(v.date) == for_date
    ]
