# -*- coding: utf-8 -*-

""" Plugin models.
"""

import dataclasses
import datetime
from enum import Enum, IntEnum

class IMAGERY(Enum):
    """Project imagery types"""

    HISTORICAL = "Historical"
    NICFI = "Nicfi"