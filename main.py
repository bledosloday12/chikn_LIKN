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
        ("ADDRESS_B hint", DEPLOY_HINT_B),
        ("ADDRESS_C hint", DEPLOY_HINT_C),
        ("Oracle shadow", ORACLE_SHADOW),
        ("Relay ghost", RELAY_GHOST),
    ]
    return "\n".join(f"{k}: {v} ({short_addr(v)})" for k, v in rows)


def replay_entropy(samples: int) -> List[int]:
    return [secrets.randbits(64) % 9973 for _ in range(samples)]


def roster_table(state: TrainerState) -> str:
    if not state.roster:
        return "(empty roster)"
    rows = []
    for c in state.roster:
        g = species_gene(c.species_id)
        rows.append(
            f"{c.chick_id:4d}  {c.nickname:12s}  {g['name']:12s}  L{c.level:2d}  "
            f"pwr={c.power_score():4d}  grain={c.grain:3d}"
        )
    return "\n".join(rows)


def export_team_json(state: TrainerState) -> str:
    return json.dumps([asdict(c) for c in state.roster], indent=2)


def import_team_json(state: TrainerState, text: str) -> int:
    blob = json.loads(text)
    count = 0
    for entry in blob:
        chick = ChickRecord(**entry)
        state.roster.append(chick)
        count += 1
    return count


def stress_sim(rounds: int) -> Dict[str, float]:
    t0 = time.perf_counter()
    wins = 0
    for r in range(rounds):
        a = ChickRecord(
            chick_id=1,
            species_id=(r % 49) + 1,
            level=10,
            xp=2000,
            grain=50,
            vitality=80,
            might=12,
            guard=11,
            tempo=11,
            element=1,
            nickname="A",
            evolved=True,
            streak=0,
            moves=[1, 2, 3, 4],
        )
        b = ChickRecord(
            chick_id=2,
            species_id=((r + 7) % 49) + 1,
            level=10,
            xp=2000,
            grain=50,
            vitality=80,
            might=11,
            guard=12,
            tempo=10,
            element=2,
            nickname="B",
            evolved=False,
            streak=0,
            moves=[5, 6, 7, 8],
        )
        w, _, _ = resolve_spar(a, b, r, secrets.randbits(256))
        if w == 1:
            wins += 1
    dt = time.perf_counter() - t0
    return {"rounds": float(rounds), "wins_a": float(wins), "seconds": dt}


def interactive_loop(state: TrainerState, path: Path) -> None:
    print(banner())
    print(f"Trainer {state.name} — save at {path}")
    print("Type HELP for commands.\n")
    while True:
        try:
            cmd = input("chikn> ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nBye.")
            return
        if not cmd:
            continue
        parts = cmd.split()
        head = parts[0].upper()
        if head in {"Q", "QUIT", "EXIT"}:
            persist(state, path)
            print("Saved. Bye.")
            return
        if head == "HELP":
            print(
                "\n".join(
                    (
                        "HELP | Q",
                        "ROSTER | SPECIES | ADDRS",
                        "MINT <speciesId> <nickname>",
                        "SHOW <chickId>",
                        "FEED <chickId> <grain>",
                        "TRAIN <chickId>",
                        "FORAGE <chickId>",
                        "EVOLVE <chickId>",
                        "MOVE <chickId> <slot0-3> <moveCode>",
                        "SPAR <attackerId> <defenderId>",
                        "CUP (tournament)",
                        "DRILL <chickId>",
                        "SAVE",
                    )
                )
            )
            continue
        if head == "SAVE":
            persist(state, path)
            print("OK")
            continue
        if head == "ROSTER":
            print(roster_table(state))
            continue
        if head == "SPECIES":
            print(list_species())
            continue
        if head == "ADDRS":
            print(audit_addresses())
            continue
        if head == "MINT" and len(parts) >= 3:
            sid = int(parts[1])
            nick = " ".join(parts[2:])
            chick = mint_chick(state, sid, nick)
            print(f"Minted #{chick.chick_id} {chick.nickname}")
            continue
        if head == "SHOW" and len(parts) == 2:
            cid = int(parts[1])
            match = next((c for c in state.roster if c.chick_id == cid), None)
            print(describe_chick(match) if match else "not found")
            continue
        if head == "FEED" and len(parts) == 3:
            cid = int(parts[1])
            spend = int(parts[2])
            chick = next((c for c in state.roster if c.chick_id == cid), None)
            if not chick:
                print("not found")
                continue
            try:
                for line in feed_chick(chick, spend, time.time()):
                    print(line)
            except ValueError as exc:
                print(f"err: {exc}")
            continue
        if head == "TRAIN" and len(parts) == 2:
            cid = int(parts[1])
            chick = next((c for c in state.roster if c.chick_id == cid), None)
            if not chick:
                print("not found")
                continue
            try:
                for line in train_chick(chick, secrets.randbits(32)):
                    print(line)
            except ValueError as exc:
                print(f"err: {exc}")
            continue
        if head == "FORAGE" and len(parts) == 2:
            cid = int(parts[1])
            chick = next((c for c in state.roster if c.chick_id == cid), None)
            if not chick:
                print("not found")
                continue
            g = forage_grain(chick, secrets.randbits(32))
            print(f"+{g} grain")
            continue
        if head == "EVOLVE" and len(parts) == 2:
            cid = int(parts[1])
            chick = next((c for c in state.roster if c.chick_id == cid), None)
            if not chick:
                print("not found")
                continue
            try:
                for line in evolve_chick(chick):
                    print(line)
            except ValueError as exc:
                print(f"err: {exc}")
            continue
        if head == "MOVE" and len(parts) == 4:
            cid = int(parts[1])
            slot = int(parts[2])
            code = int(parts[3])
            chick = next((c for c in state.roster if c.chick_id == cid), None)
            if not chick:
                print("not found")
                continue
            try:
                slot_move(chick, slot, code)
                print("slotted")
            except ValueError as exc:
                print(f"err: {exc}")
            continue
        if head == "SPAR" and len(parts) == 3:
            a_id = int(parts[1])
            b_id = int(parts[2])
            a = next((c for c in state.roster if c.chick_id == a_id), None)
            b = next((c for c in state.roster if c.chick_id == b_id), None)
            if not a or not b:
                print("need two roster ids")
                continue
            w, l, xp = resolve_spar(a, b, secrets.randbits(64), secrets.randbits(256))
            win = next(c for c in (a, b) if c.chick_id == w)
            lose = next(c for c in (a, b) if c.chick_id == l)
            win.xp += xp
            win.streak += 1
            lose.streak = 0
            apply_level_sync(win)
            print(f"Winner #{w} (+{xp} xp) loser #{l}")
            continue
        if head == "CUP":
            for line in run_tournament(state):
                print(line)
            continue
        if head == "DRILL" and len(parts) == 2:
            cid = int(parts[1])
            chick = next((c for c in state.roster if c.chick_id == cid), None)
            if not chick:
                print("not found")
                continue
            for line in coaching_drill(chick):
                print(line)
            continue
        print("Unknown command — type HELP")


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description="chikn_LIKN battle lab")
    p.add_argument("--trainer", default="Coach", help="trainer name")
    p.add_argument("--save", type=Path, default=None, help="custom save path")
    p.add_argument("--bench", action="store_true", help="run micro bench")
    p.add_argument("--entropy", type=int, default=32, help="entropy sample count")
    p.add_argument("--export-roster", action="store_true", help="print roster json")
    p.add_argument("--import-roster", type=Path, help="merge roster json file")
    return p


def main(argv: Optional[Sequence[str]] = None) -> int:
    args = build_parser().parse_args(list(argv) if argv is not None else None)
    path = args.save or save_path()
    if path.exists():
        try:
            state = restore(path)
        except (json.JSONDecodeError, KeyError, ValueError):
            state = TrainerState(name=args.trainer, roster=[])
    else:
        state = TrainerState(name=args.trainer, roster=[])
    if args.import_roster:
        text = args.import_roster.read_text(encoding="utf-8")
        added = import_team_json(state, text)
        print(f"imported {added} chicks")
        persist(state, path)
    if args.export_roster:
        print(export_team_json(state))
        return 0
    if args.bench:
        stats = stress_sim(4000)
        print(json.dumps(stats, indent=2))
        return 0
    if args.entropy:
        samples = replay_entropy(max(1, min(args.entropy, 4096)))
        print("entropy:", samples[:8], "...")
    interactive_loop(state, path)
    return 0


# --- Expanded league toolkit (intentionally verbose for local coaching UX) ---


def league_checksum(payload: Dict[str, Any]) -> int:
    raw = json.dumps(payload, sort_keys=True, separators=(",", ":")).encode()
    return zlib.crc32(raw) & 0xFFFFFFFF


def build_scouting_report(state: TrainerState) -> Dict[str, Any]:
    report: Dict[str, Any] = {
        "trainer": state.name,
        "roster": len(state.roster),
        "coins": state.coins,
        "top": None,
    }
    if state.roster:
        top = max(state.roster, key=lambda c: c.power_score())
        report["top"] = {
            "id": top.chick_id,
            "nick": top.nickname,
            "species": species_gene(top.species_id)["name"],
            "power": top.power_score(),
        }
    report["checksum"] = league_checksum(report)
    return report


def mutate_daily_quest(state: TrainerState) -> List[str]:
    lines: List[str] = []
    if not state.roster:
        lines.append("Quest skipped — no roster")
        return lines
    target = random.choice(state.roster)
    gain = forage_grain(target, secrets.randbits(24))
    lines.append(f"Quest: {target.nickname} foraged +{gain}")
    state.bits += 1
    return lines


def bulk_train(state: TrainerState, rounds: int) -> List[str]:
    lines: List[str] = []
    if not state.roster:
        return ["empty roster"]
    chick = random.choice(state.roster)
    for _ in range(max(1, rounds)):
        try:
            lines.extend(train_chick(chick, secrets.randbits(48)))
        except ValueError:
            lines.append("halted — low grain")
            break
    return lines


def element_breakdown(state: TrainerState) -> Dict[int, int]:
    counts: Dict[int, int] = {}
    for c in state.roster:
        counts[c.element] = counts.get(c.element, 0) + 1
    return dict(sorted(counts.items()))


def suggest_counter(team: Sequence[ChickRecord]) -> Optional[str]:
    if not team:
        return None
    focus = max(team, key=lambda c: c.might)
    for sid in range(1, len(SPECIES_ROWS) + 1):
        g = species_gene(sid)
        adv = type_advantage(int(g["element"]), focus.element)
        if adv > 0:
            return f"Try hatching #{sid} {g['name']} to counter {focus.nickname}"
    return "No hard counter found — diversify tempo"


def simulate_season(state: TrainerState, weeks: int) -> List[str]:
    lines: List[str] = []
    for w in range(1, weeks + 1):
        events = mutate_daily_quest(state)
        lines.append(f"Week {w}: " + "; ".join(events))
        if state.roster:
            chick = state.roster[(w - 1) % len(state.roster)]
            lines.extend(coaching_drill(chick)[:2])
    return lines


def normalize_nickname(text: str) -> str:
    cleaned = "".join(ch for ch in text.strip() if ch.isprintable())
    return cleaned[:24] or "Unnamed"


def clone_chick(chick: ChickRecord, new_id: int) -> ChickRecord:
    data = asdict(chick)
    data["chick_id"] = new_id
    data["moves"] = list(chick.moves)
    return ChickRecord(**data)


def merge_rosters(a: TrainerState, b: TrainerState) -> TrainerState:
    merged = TrainerState(name=f"{a.name}+{b.name}", roster=[], bits=a.bits + b.bits, coins=a.coins + b.coins)
    next_id = 1
    for chick in a.roster + b.roster:
        c = clone_chick(chick, next_id)
        merged.roster.append(c)
        next_id += 1
    return merged


def rank_roster(state: TrainerState) -> List[ChickRecord]:
    return sorted(state.roster, key=lambda c: c.power_score(), reverse=True)


def export_scouting(path: Path, state: TrainerState) -> None:
    path.write_text(json.dumps(build_scouting_report(state), indent=2), encoding="utf-8")


def import_scouting(path: Path) -> Dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def teach_move_set(chick: ChickRecord, pattern: str) -> None:
    codes = [int(x) for x in pattern.split(",") if x.strip().isdigit()]
    for idx, val in enumerate(codes[:4]):
        slot_move(chick, idx, val)


def describe_move(code: int) -> str:
    return MOVE_NAMES.get(code, f"Unknown#{code}")


def move_lexicon() -> str:
    rows = [f"{k:02d} {v}" for k, v in sorted(MOVE_NAMES.items())]
    return "\n".join(rows)


def pokedex_blurb(sid: int) -> str:
    g = species_gene(sid)
    adv_pairs: List[str] = []
    for other in range(1, 9):
        if other == g["element"]:
            continue
        if type_advantage(int(g["element"]), other) > 0:
            adv_pairs.append(str(other))
    weak = ", ".join(adv_pairs) or "balanced"
    return f"{g['name']} presses best vs elements {weak}"


def arena_blurb(a: ChickRecord, b: ChickRecord) -> str:
    adv = type_advantage(a.element, b.element)
    edge = "even"
    if adv > 0:
        edge = f"{a.nickname} favored"
    elif adv < 0:
        edge = f"{b.nickname} favored"
    return f"Matchup: {edge} (element {a.element} vs {b.element})"


def grain_forecast(chick: ChickRecord, days: int) -> int:
    total = chick.grain
    rng = random.Random(chick.chick_id + days)
    for _ in range(days):
        total += 6 + rng.randint(0, 10)
        total -= rng.randint(0, 4)
    return max(0, total)


def xp_curve_preview(level: int) -> int:
    return level * 220


def chick_memory_digest(chick: ChickRecord) -> str:
    raw = json.dumps(asdict(chick), sort_keys=True, separators=(",", ":")).encode()
    return f"{zlib.adler32(raw):08x}"


def trainer_digest(state: TrainerState) -> str:
    raw = json.dumps(dump_state(state), sort_keys=True, separators=(",", ":")).encode()
    return f"{zlib.crc32(raw) & 0xFFFFFFFF:08x}"


def roll_call(state: TrainerState) -> str:
    names = ", ".join(c.nickname for c in state.roster)
    return names or "(silent coop)"


def sprint_cycle(state: TrainerState) -> List[str]:
    lines: List[str] = []
    for chick in state.roster[:3]:
        lines.append(f"{chick.nickname}: power {chick.power_score()}")
        lines.extend(apply_level_sync(chick))
    return lines


def danger_zone_report(chick: ChickRecord) -> List[str]:
    issues: List[str] = []
    if chick.grain < 8:
        issues.append("low grain")
    if chick.vitality < 30:
        issues.append("low vitality")
    if chick.level < 6 and chick.xp > 800:
        issues.append("xp heavy — train")
    return issues or ["stable"]


def coach_notes(state: TrainerState) -> str:
    lines = [
        f"Trainer digest {trainer_digest(state)}",
        f"Roster {len(state.roster)} | coins {state.coins}",
        f"Elements {element_breakdown(state)}",
    ]
    tip = suggest_counter(state.roster)
    if tip:
        lines.append(tip)
    return "\n".join(lines)


def telemetry_ping() -> Dict[str, Any]:
    return {
        "ts": time.time(),
        "py": sys.version.split()[0],
        "seed": secrets.token_hex(8),
    }


def offline_rng_chain(n: int) -> List[int]:
    return [secrets.randbelow(10_000) for _ in range(n)]


def battle_commentary(w_id: int, l_id: int, xp: int) -> str:
    return f"Chick {w_id} clinches +{xp} xp while {l_id} regroups."


def roster_json_min(state: TrainerState) -> str:
    slim = [{"id": c.chick_id, "nick": c.nickname, "species": c.species_id} for c in state.roster]
    return json.dumps(slim)


def warmup_moves(chick: ChickRecord) -> List[str]:
    return [describe_move(m) for m in chick.moves[:4]]


def rehome_chick(state: TrainerState, chick_id: int) -> bool:
    before = len(state.roster)
    state.roster = [c for c in state.roster if c.chick_id != chick_id]
    return len(state.roster) < before


def nick_collision(state: TrainerState, nick: str) -> bool:
    return any(c.nickname.lower() == nick.lower() for c in state.roster)


def rename_chick(state: TrainerState, chick_id: int, nick: str) -> bool:
    chick = next((c for c in state.roster if c.chick_id == chick_id), None)
    if not chick:
        return False
    chick.nickname = normalize_nickname(nick)
    return True


def grant_bonus_grain(chick: ChickRecord, amount: int) -> None:
    chick.grain += max(0, amount)


def league_seed_mix() -> int:
    return int.from_bytes(secrets.token_bytes(8), "big")


def mock_prevrandao() -> int:
    return secrets.randbits(256)


def compare_chicks(a: ChickRecord, b: ChickRecord) -> str:
    if a.power_score() == b.power_score():
        return "tie power"
    return f"{a.nickname} wins power" if a.power_score() > b.power_score() else f"{b.nickname} wins power"


def roster_filter_element(state: TrainerState, elem: int) -> List[ChickRecord]:
    return [c for c in state.roster if c.element == elem]


def roster_total_xp(state: TrainerState) -> int:
    return sum(c.xp for c in state.roster)


def roster_total_grain(state: TrainerState) -> int:
    return sum(c.grain for c in state.roster)


def simulate_coin_flip() -> str:
    return "heads" if secrets.randbelow(2) == 0 else "tails"


def day_night_buff(chick: ChickRecord) -> str:
    return "nocturne" if chick.element in {7, 5} else "diurnal"


def hatch_plan(target_power: int) -> List[int]:
    plan: List[int] = []
    for sid in range(1, len(SPECIES_ROWS) + 1):
        g = species_gene(sid)
        if g["might"] + g["guard"] + g["tempo"] >= target_power:
            plan.append(sid)
    return plan[:8]


def explain_type_chart() -> str:
    lines = ["Type rings (sample):"]
    rings = (
        ("fire(1)", "plant(3)", "water(2)"),
        ("spark(4)", "water(2)", "frost(5)"),
        ("stone(6)", "spark(4)", "shadow(7)"),
        ("crystal(8)", "shadow(7)", "fire(1)"),
    )
    for a, b, c in rings:
        lines.append(f"  {a} > {b} > {c} > {a}")
    return "\n".join(lines)


def coach_random_tip() -> str:
    tips = (
        "Rotate tempo training on glass cannons.",
        "Bank grain before tournament week.",
        "Slot coverage moves before sparring.",
        "Evolve after level 18 with 900 xp banked.",
        "Watch element rings — advantage flips fights.",
    )
    return random.choice(tips)


def audit_roster_ids(state: TrainerState) -> bool:
    ids = [c.chick_id for c in state.roster]
    return len(ids) == len(set(ids))


def repair_roster_ids(state: TrainerState) -> None:
    for idx, chick in enumerate(sorted(state.roster, key=lambda c: c.chick_id), start=1):
        chick.chick_id = idx


def compact_save(state: TrainerState) -> str:
    return json.dumps(dump_state(state), separators=(",", ":"))


def expand_save(blob: str) -> TrainerState:
    return load_state(json.loads(blob))


def dual_spar_series(state: TrainerState, rounds: int) -> List[str]:
    lines: List[str] = []
    if len(state.roster) < 2:
        return ["need 2+ roster"]
    a, b = state.roster[0], state.roster[1]
    for r in range(rounds):
        w, l, xp = resolve_spar(a, b, r, mock_prevrandao())
        win = a if w == a.chick_id else b
        win.xp += xp
        apply_level_sync(win)
        lines.append(battle_commentary(w, l, xp))
    return lines


def champion_chain(state: TrainerState) -> Optional[ChickRecord]:
    ranked = rank_roster(state)
    return ranked[0] if ranked else None


def underdog_pick(state: TrainerState) -> Optional[ChickRecord]:
    ranked = rank_roster(state)
    return ranked[-1] if ranked else None


def schedule_reminder() -> str:
    return "Feed cadence 120s | Train cadence 240s | Spar cadence 90s (on-chain mirrors)"


def ascii_chick() -> str:
    return "\n".join(
        (
            "     .-.",
            "    (o o)",
            "    | O \\",
            "     \\   \\",
            "      `~~~`",
        )
    )


def story_seed() -> str:
    return secrets.token_urlsafe(12)


def league_banner_lines() -> List[str]:
    return [
        "ChickCombo league sync: offline safe mode",
        f"Hints {short_addr(DEPLOY_HINT_A)} / {short_addr(DEPLOY_HINT_B)} / {short_addr(DEPLOY_HINT_C)}",
    ]


def print_league_banner() -> None:
    print("\n".join(league_banner_lines()))


def debug_state(state: TrainerState) -> Dict[str, Any]:
    return {
        "trainer": state.name,
        "roster": len(state.roster),
        "audit": audit_roster_ids(state),
        "digest": trainer_digest(state),
    }


def selftest() -> None:
    st = TrainerState(name="SelfTest", roster=[])
    c = mint_chick(st, 3, "Tester")
    assert c.species_id == 3
    train_chick(c, 2)
    w, l, xp = resolve_spar(c, clone_chick(c, 99), 1, 12345)
    assert w in (c.chick_id, 99)
    assert xp > 0
    assert type_advantage(1, 3) == 1


def bench_training_path(chick: ChickRecord, steps: int) -> List[int]:
    curve: List[int] = []
    for s in range(steps):
        try:
            train_chick(chick, s * 7919)
            curve.append(chick.might + chick.guard + chick.tempo)
        except ValueError:
            curve.append(-1)
            break
    return curve


def roster_histogram(state: TrainerState) -> Dict[str, int]:
    hist = {"low": 0, "mid": 0, "high": 0}
    for c in state.roster:
        p = c.power_score()
        if p < 45:
            hist["low"] += 1
        elif p < 60:
            hist["mid"] += 1
        else:
            hist["high"] += 1
    return hist


def mock_contract_call(label: str, payload: Dict[str, Any]) -> Dict[str, Any]:
    return {"label": label, "echo": payload, "nonce": secrets.token_hex(6)}


def serialize_chick_csv(state: TrainerState) -> str:
    rows = ["id,nick,species,level,power,grain,xp"]
    for c in state.roster:
        rows.append(
            f"{c.chick_id},{c.nickname},{c.species_id},{c.level},{c.power_score()},{c.grain},{c.xp}"
        )
    return "\n".join(rows)


def parse_chick_csv(text: str) -> List[ChickRecord]:
    lines = [ln for ln in text.splitlines() if ln.strip()]
    out: List[ChickRecord] = []
    for ln in lines[1:]:
        parts = ln.split(",")
        if len(parts) < 7:
            continue
        g = species_gene(int(parts[2]))
        out.append(
            ChickRecord(
                chick_id=int(parts[0]),
                species_id=int(parts[2]),
                level=int(parts[3]),
                xp=int(parts[6]),
                grain=int(parts[5]),
                vitality=g["might"] + g["guard"] + g["tempo"],
                might=g["might"],
                guard=g["guard"],
                tempo=g["tempo"],
                element=g["element"],
                nickname=parts[1],
                evolved=False,
                streak=0,
                moves=[1, 8, 15, 22],
            )
        )
    return out


def attach_csv_roster(state: TrainerState, text: str) -> int:
    before = len(state.roster)
    for chick in parse_chick_csv(text):
        state.roster.append(chick)
    return len(state.roster) - before


def duel_commentary(a: ChickRecord, b: ChickRecord) -> List[str]:
    return [
        arena_blurb(a, b),
        f"{a.nickname} power {a.power_score()} vs {b.nickname} {b.power_score()}",
        day_night_buff(a) + " / " + day_night_buff(b),
    ]


def league_schedule_stub() -> List[Tuple[int, str]]:
    return [(1, "Grain Cup"), (2, "Tempo Clash"), (3, "Element Open"), (4, "Brood Finals")]


def print_schedule() -> None:
    for rnd, title in league_schedule_stub():
        print(f"Round {rnd}: {title}")


def coach_profile_card(state: TrainerState) -> str:
    champ = champion_chain(state)
    dog = underdog_pick(state)
    lines = [
        f"Coach {state.name}",
        f"Coins {state.coins} | Bits {state.bits}",
    ]
    if champ:
        lines.append(f"Champion candidate: {champ.nickname} ({champ.power_score()})")
    if dog:
        lines.append(f"Bench project: {dog.nickname} ({dog.power_score()})")
    return "\n".join(lines)


def rng_weights(species_id: int) -> List[float]:
    g = species_gene(species_id)
    return [
        float(g["might"]) / 20.0,
        float(g["guard"]) / 20.0,
        float(g["tempo"]) / 20.0,
    ]


def weighted_pick(weights: Sequence[float]) -> int:
    total = sum(weights)
    r = secrets.randbelow(1_000_000) / 1_000_000 * total
    acc = 0.0
    for idx, w in enumerate(weights):
        acc += w
        if r <= acc:
            return idx
    return len(weights) - 1


def train_weighted(chick: ChickRecord) -> List[str]:
    w = rng_weights(chick.species_id)
    choice = weighted_pick(w)
    lines = train_chick(chick, choice + secrets.randbelow(256))
    lines.insert(0, f"Weighted focus {choice}")
    return lines


def mock_bridge_ping() -> str:
    return f"bridge:{secrets.token_hex(4)}"


def describe_trainer_state(state: TrainerState) -> Dict[str, Any]:
    return {
        "name": state.name,
        "roster": len(state.roster),
        "xp": roster_total_xp(state),
        "grain": roster_total_grain(state),
        "elements": element_breakdown(state),
    }


def safe_mint_flow(state: TrainerState, sid: int, nick: str) -> Tuple[ChickRecord, List[str]]:
    logs: List[str] = []
    if nick_collision(state, nick):
        logs.append("warn: nickname collision")
    chick = mint_chick(state, sid, nick)
    logs.append(f"digest {chick_memory_digest(chick)}")
    return chick, logs


def replay_spar_log(state: TrainerState, rounds: int) -> List[str]:
