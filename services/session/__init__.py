# Copyright (C) 2023 Authors of the MCDA project - All Rights Reserved

"""Service for session storage across requests.
"""

from .state import SessionStorage, get_state, init_state, Session