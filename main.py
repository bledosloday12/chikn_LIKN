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
    13: "Drift Peck",
    14: "Gust Turn",
    15: "Stone Stomp",
    16: "Frost Ruffle",
    17: "Moss Wrap",
    18: "Tide Slap",
    19: "Shadow Dart",
    20: "Sun Flare",
    21: "Moon Hook",
    22: "Combo Rush",
    23: "Guarded Peck",
    24: "Tempo Swap",
    25: "Counter Coop",
    26: "League Finale",
    27: "Yolk Surge",
    28: "Crest Spin",
    29: "Brood Wall",
    30: "Arena Echo",
    31: "Vault Strike",
    32: "Void Tap",
}


def type_advantage(atk_elem: int, def_elem: int) -> int:
    if atk_elem == def_elem:
        return 0
    rings = (
        (1, 3, 2),
        (4, 2, 5),
        (6, 4, 7),
        (8, 7, 1),
    )
    for a, b, c in rings:
        if atk_elem == a and def_elem == b:
            return 1
        if atk_elem == b and def_elem == c:
            return 1
        if atk_elem == c and def_elem == a:
            return 1
        if def_elem == a and atk_elem == b:
            return -1
        if def_elem == b and atk_elem == c:
            return -1
        if def_elem == c and atk_elem == a:
            return -1
    return 0


def species_gene(species_id: int) -> Dict[str, Any]:
    if species_id < 1 or species_id > len(SPECIES_ROWS):
        raise ValueError("species range")
    name, might, guard, tempo, elem = SPECIES_ROWS[species_id - 1]
    return {
        "id": species_id,
        "name": name,
        "might": might,
        "guard": guard,
        "tempo": tempo,
        "element": elem,
    }


@dataclass
class ChickRecord:
    chick_id: int
    species_id: int
    level: int
    xp: int
    grain: int
    vitality: int
    might: int
    guard: int
    tempo: int
    element: int
    nickname: str
    evolved: bool
    streak: int
    moves: List[int] = field(default_factory=list)

    def power_score(self) -> int:
        return self.might * 2 + self.guard + self.tempo


@dataclass
class TrainerState:
    name: str
    roster: List[ChickRecord]
    bits: int = 0
    coins: int = 0

    def next_id(self) -> int:
        return max((c.chick_id for c in self.roster), default=0) + 1


def level_from_xp(xp: int) -> int:
    base = 1 + xp // 220
    return min(72, max(1, base))


def apply_level_sync(chick: ChickRecord) -> List[str]:
    logs: List[str] = []
    target = level_from_xp(chick.xp)
    if target > chick.level:
        delta = target - chick.level
        chick.level = target
        chick.vitality += delta * 3
        chick.grain += delta * 2
        logs.append(f"Level up x{delta} → {chick.level}")
    return logs


def mint_chick(state: TrainerState, species_id: int, nickname: str) -> ChickRecord:
    g = species_gene(species_id)
    cid = state.next_id()
    base_v = g["might"] + g["guard"] + g["tempo"]
    elem = int(g["element"])
    moves = [1 + (elem % 7), 8 + (elem % 5), 15 + (elem % 4), 22 + (elem % 6)]
    chick = ChickRecord(
        chick_id=cid,
        species_id=species_id,
        level=1,
        xp=0,
        grain=48,
        vitality=base_v,
        might=int(g["might"]),
        guard=int(g["guard"]),
        tempo=int(g["tempo"]),
        element=elem,
        nickname=nickname.strip() or g["name"],
        evolved=False,
        streak=0,
        moves=moves,
    )
    state.roster.append(chick)
    return chick


def feed_chick(chick: ChickRecord, spend: int, now: float) -> List[str]:
    logs: List[str] = []
    if chick.grain < spend:
        raise ValueError("not enough grain")
    chick.grain -= spend
    bump = spend // 3 + 2
    chick.vitality += bump
    logs.append(f"Fed −{spend} grain, +{bump} vitality")
    return logs


def train_chick(chick: ChickRecord, entropy: int) -> List[str]:
    logs: List[str] = []
    if chick.grain < 6:
        raise ValueError("train needs 6 grain")
    chick.grain -= 6
    pick = entropy % 3
    if pick == 0:
        chick.might += 1
        logs.append("Might +1")
    elif pick == 1:
        chick.guard += 1
        logs.append("Guard +1")
    else:
        chick.tempo += 1
        logs.append("Tempo +1")
    chick.xp += 14
    logs.extend(apply_level_sync(chick))
    return logs


def forage_grain(chick: ChickRecord, mix: int) -> int:
    gain = 6 + (mix % 11)
    chick.grain += gain
    return gain


def evolve_chick(chick: ChickRecord) -> List[str]:
    logs: List[str] = []
    if chick.level < 18 or chick.evolved:
        raise ValueError("not ready to evolve")
    if chick.xp < 900:
        raise ValueError("need 900 xp")
