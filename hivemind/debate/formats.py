"""Debate format definitions — Oxford, Lincoln-Douglas, Free-form."""

from dataclasses import dataclass
from typing import List


@dataclass
class DebateFormat:
    name: str
    description: str
    rounds: int
    time_per_round: str
    structure: List[str]


OXFORD = DebateFormat(
    name="Oxford",
    description="Classic formal debate with structured rounds",
    rounds=4,
    time_per_round="5 min",
    structure=[
        "Opening Statement (each agent)",
        "Rebuttal Round (counter opponents)",
        "Cross-examination (challenge specific claims)",
        "Closing Statement (summarize + final appeal)"
    ]
)

LINCOLN_DOUGLAS = DebateFormat(
    name="Lincoln-Douglas",
    description="Value-based debate focusing on moral/ethical dimensions",
    rounds=3,
    time_per_round="7 min",
    structure=[
        "Affirmative presents value framework",
        "Negative challenges framework + presents alternative",
        "Final rebuttals + crystallization"
    ]
)

FREE_FORM = DebateFormat(
    name="Free Form",
    description="Flexible debate — agents argue naturally",
    rounds=3,
    time_per_round="unlimited",
    structure=[
        "Opening arguments",
        "Response and counter-arguments",
        "Final positions"
    ]
)

ALL_FORMATS = {
    "oxford": OXFORD,
    "lincoln_douglas": LINCOLN_DOUGLAS,
    "free_form": FREE_FORM,
}
