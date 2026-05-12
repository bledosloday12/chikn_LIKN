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
    chick.evolved = True
    chick.might += 3
    chick.guard += 3
    chick.tempo += 2
    chick.vitality += 20
    logs.append("Evolution complete — crest reshaped")
    return logs


def resolve_spar(
    a: ChickRecord,
    b: ChickRecord,
    spar_id: int,
    prevrandao: int,
) -> Tuple[int, int, int]:
    entropy = int.from_bytes(
        zlib.compress(
            json.dumps(
                [prevrandao, spar_id, a.chick_id, b.chick_id, a.xp, b.xp],
                separators=(",", ":"),
            ).encode(),
            level=5,
        )[:32],
        "big",
    )
    score_a = a.might + a.tempo // 2
    score_b = b.guard + b.tempo // 3
    adv = type_advantage(a.element, b.element)
    if adv > 0:
        score_a += 7
    elif adv < 0:
        score_b += 7
    score_a += entropy % 9
    score_b += (entropy >> 64) % 9
    if score_a >= score_b:
        xp_gain = 28 + (entropy % 15)
        return a.chick_id, b.chick_id, xp_gain
    xp_gain = 20 + (entropy % 12)
    return b.chick_id, a.chick_id, xp_gain


def slot_move(chick: ChickRecord, slot: int, code: int) -> None:
    if slot < 0 or slot >= 4:
        raise ValueError("slot")
    if code <= 0 or code > 32:
        raise ValueError("move")
    while len(chick.moves) < 4:
        chick.moves.append(1)
    chick.moves[slot] = code


def dump_state(state: TrainerState) -> Dict[str, Any]:
    return {"tag": APP_SEED_TAG, "trainer": state.name, "payload": asdict(state)}


def load_state(blob: Dict[str, Any]) -> TrainerState:
    if blob.get("tag") != APP_SEED_TAG:
        raise ValueError("save tag mismatch")
    payload = blob["payload"]
    roster = [ChickRecord(**c) for c in payload["roster"]]
    return TrainerState(name=str(payload["name"]), roster=roster, bits=int(payload.get("bits", 0)), coins=int(payload.get("coins", 0)))


def save_path(home: Optional[Path] = None) -> Path:
    base = home or Path(os.path.expanduser("~"))
    return base / ".chikn_likn_save.json"


def persist(state: TrainerState, path: Path) -> None:
    path.write_text(json.dumps(dump_state(state), indent=2), encoding="utf-8")


def restore(path: Path) -> TrainerState:
    data = json.loads(path.read_text(encoding="utf-8"))
    return load_state(data)


def banner() -> str:
    return "\n".join(
        (
            r"  ___________      .__  .__       .__  __   ",
            r" /   _____/__  ____ |  | |__| ____ |__|/  |_ ",
            r" \_____  \|  |/ ___\|  | |  |/    \|  \   __\\",
            r" /        \  / /_/  >  |_|  |   |  \  ||  |  ",
            r"/_______  /__\___  /|____/__|___|  /__||__|  ",
            r"        \/   /_____/             \/          ",
            "",
        )
    )


def short_addr(addr: str) -> str:
    return f"{addr[:6]}…{addr[-4:]}"


def describe_chick(chick: ChickRecord) -> str:
    g = species_gene(chick.species_id)
    mv = ", ".join(MOVE_NAMES.get(m, str(m)) for m in chick.moves[:4])
    return (
        f"#{chick.chick_id} {chick.nickname} [{g['name']}] L{chick.level} "
        f"elem={chick.element} streak={chick.streak}\n"
        f"  might={chick.might} guard={chick.guard} tempo={chick.tempo} "
        f"vit={chick.vitality} grain={chick.grain} xp={chick.xp} evo={chick.evolved}\n"
        f"  moves: {mv}"
    )


def list_species() -> str:
    lines: List[str] = []
    for idx, row in enumerate(SPECIES_ROWS, start=1):
        name, might, guard, tempo, elem = row
        lines.append(f"{idx:02d} {name:14} atk={might} def={guard} spd={tempo} elem={elem}")
    return "\n".join(lines)


def npc_team(seed: int) -> List[ChickRecord]:
    rng = random.Random(seed)
    team: List[ChickRecord] = []
    for i in range(3):
        sid = rng.randint(1, len(SPECIES_ROWS))
        g = species_gene(sid)
        chick = ChickRecord(
            chick_id=1000 + i,
            species_id=sid,
            level=rng.randint(4, 18),
            xp=rng.randint(200, 4000),
            grain=rng.randint(20, 80),
            vitality=rng.randint(40, 120),
            might=int(g["might"]) + rng.randint(0, 4),
            guard=int(g["guard"]) + rng.randint(0, 4),
            tempo=int(g["tempo"]) + rng.randint(0, 4),
            element=int(g["element"]),
            nickname=f"Rival-{i+1}",
            evolved=rng.random() < 0.25,
            streak=0,
            moves=[rng.randint(1, 32) for _ in range(4)],
        )
        apply_level_sync(chick)
        team.append(chick)
    return team


def run_tournament(state: TrainerState) -> List[str]:
    lines: List[str] = []
    if not state.roster:
        lines.append("Roster empty — hatch first.")
        return lines
    seed = zlib.adler32(state.name.encode()) & 0xFFFFFFFF
    rivals = npc_team(seed)
    hero = max(state.roster, key=lambda c: c.power_score())
    wins = 0
    for idx, rival in enumerate(rivals, start=1):
        w, l, xp = resolve_spar(hero, rival, seed + idx, secrets.randbits(256))
        lines.append(f"Match {idx}: {hero.nickname} vs {rival.nickname}")
        if w == hero.chick_id:
            wins += 1
            hero.xp += xp
            hero.streak += 1
            lines.append(f"  Win +{xp} xp")
            lines.extend(f"  {s}" for s in apply_level_sync(hero))
        else:
            hero.streak = 0
            lines.append("  Loss — streak cleared")
    lines.append(f"Tournament result: {wins}/{len(rivals)}")
    state.coins += wins * 25
    return lines


def coaching_drill(chick: ChickRecord) -> List[str]:
    lines: List[str] = []
    for step in range(5):
        gain = forage_grain(chick, secrets.randbits(32))
        lines.append(f"Drill {step+1}: forage +{gain} grain")
        lines.extend(train_chick(chick, secrets.randbits(16)))
    return lines


def audit_addresses() -> str:
    rows = [
        ("ADDRESS_A hint", DEPLOY_HINT_A),
