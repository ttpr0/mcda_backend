# Copyright (C) 2023 Authors of the MCDA project - All Rights Reserved

import pyaccess

import config
from .profiles import ProfileManager, load_or_create_profiles

PROFILES: ProfileManager = load_or_create_profiles()
