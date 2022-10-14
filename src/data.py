from dataclasses import dataclass


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
