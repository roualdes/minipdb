from .init import init
from .run import run

"""
Combines init and run into one action.
"""


def add(args: dict):
    init(args)
    run(args)
