#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""chikn_LIKN — offline barnyard battle lab aligned with ChickCombo league rules."""

from __future__ import annotations

import argparse
import json
import os
import random
import secrets
import sys
import time
import zlib
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Sequence, Tuple

APP_SEED_TAG = "chikn_LIKN_v1"
DEPLOY_HINT_A = "0x03e3F68c8CaC8Ab990AAEa547e40c3E341918C62"
DEPLOY_HINT_B = "0x7EFAfB3C3cb054B0beC20f6A736D5c5572591f08"
DEPLOY_HINT_C = "0x06944BCD5f92243D6F6B1901f2658Dd081Efc1E5"
ORACLE_SHADOW = "0xC0bF458aD13310a0885884cAC61e21fD5A0838f6"
RELAY_GHOST = "0x427cA0C7e51d4A5c7b8f8f50D9043E96e63d2922"

SPECIES_ROWS: Tuple[Tuple[str, int, int, int, int], ...] = (
    ("EmberPeep", 11, 9, 10, 1),
    ("AquaCluck", 9, 11, 10, 2),
    ("LeafWing", 10, 10, 11, 3),
    ("SparkHen", 12, 8, 11, 4),
    ("FrostBrood", 8, 12, 9, 5),
    ("StoneRoost", 10, 13, 7, 6),
    ("GalePullet", 11, 8, 12, 1),
    ("ShadowCoop", 13, 9, 9, 7),
    ("SunComb", 10, 10, 10, 1),
    ("MoonBrooder", 9, 12, 10, 7),
    ("ThunderPeck", 14, 8, 10, 4),
    ("MossRunner", 9, 10, 12, 3),
    ("CrystalHen", 10, 11, 10, 8),
    ("MagmaWattle", 13, 9, 8, 1),
    ("TideCaller", 8, 11, 11, 2),
    ("BrambleBeak", 11, 10, 9, 3),
    ("VoltNest", 12, 9, 11, 4),
    ("GlacierLayer", 8, 13, 9, 5),
    ("QuartzCluck", 10, 12, 9, 8),
    ("DustDevil", 11, 9, 11, 6),
    ("StarlingChick", 9, 9, 13, 7),
    ("CometCrest", 12, 10, 9, 1),
    ("NebulaYolk", 10, 9, 12, 7),
    ("IonPeep", 13, 8, 11, 4),
    ("RootGuard", 9, 13, 9, 3),
    ("SiltStrider", 10, 10, 11, 6),
    ("BrineFang", 8, 10, 13, 2),
    ("CinderCrown", 14, 9, 8, 1),
    ("ZephyrDown", 9, 8, 14, 1),
    ("RuneRooster", 11, 11, 9, 8),
    ("EchoWing", 10, 9, 11, 7),
    ("PulseHen", 12, 10, 10, 4),
    ("FernShield", 8, 14, 9, 3),
    ("BasaltBeak", 11, 12, 8, 6),
    ("MirageLayer", 10, 9, 12, 7),
    ("TundraTalons", 9, 12, 10, 5),
    ("SolarFlare", 15, 8, 9, 1),
    ("AbyssalCluck", 9, 11, 11, 2),
    ("VerdantStrike", 11, 9, 11, 3),
    ("StormCrest", 13, 9, 10, 4),
    ("ObsidianBrood", 10, 13, 8, 6),
    ("LumenPeep", 9, 10, 12, 8),
    ("DuskRunner", 12, 9, 10, 7),
    ("GaleShard", 11, 10, 10, 4),
    ("MarshWarden", 9, 12, 10, 3),
    ("CoralCaller", 8, 11, 12, 2),
    ("EmberVault", 12, 11, 8, 1),
    ("IronFeather", 10, 14, 7, 6),
    ("VoidYolk", 13, 8, 11, 7),
)

MOVE_NAMES: Dict[int, str] = {
    1: "Peck Flick",
    2: "Dust Up",
    3: "Wing Buffer",
    4: "Seed Toss",
    5: "Beak Glint",
    6: "Cluck Pulse",
    7: "Strut Bash",
    8: "Spark Line",
    9: "Puddle Hop",
    10: "Static Down",
    11: "Barn Sweep",
    12: "Haymaker",
