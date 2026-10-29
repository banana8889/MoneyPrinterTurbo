"""Original educational shorts planner and production worker for MoneyPrinterTurbo.

No paid provider, publishing, trending-data, or analytics API is used.
Run with: python kids_autonomy.py status|plan|make|watch|feedback
"""
from __future__ import annotations

import argparse
import json
import math
import os
import subprocess
import sys
import tempfile
import time
from contextlib import contextmanager
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent
DEFAULT_STATE = ROOT / "storage" / "kids_autonomy" / "state.json"
IDEAS = (
    ("shape-mystery", "The shape mystery", "shapes", (
        "What has three sides and three corners?", "It's a triangle! Count the corners: one, two, three.",
        "A square has four equal sides. Count: one, two, three, four.",
        "Find a triangle and a square around you. Great noticing!")),
    ("color-mixing", "The color mixing surprise", "science", (
        "What happens when blue and yellow paint meet?", "Look closely as we mix them together.",
        "We get green! Mixing colors is like discovering a secret.",
        "Try it with paint and a grown-up. What other colors can you make?")),
    ("space-count", "Counting stars", "numbers", (
        "Ready for a tiny trip through pretend space?", "One star, two stars, three stars. Can you count with me?",
        "Four stars, five stars. Our imaginary sky is getting bright!",
        "Now count backward: five, four, three, two, one!")),
    ("rain-journey", "Where rain comes from", "science", (
        "Have you ever wondered where rain begins?", "The sun warms water and some of it turns into invisible water vapor.",
        "High in the sky, the vapor cools and forms tiny drops inside clouds.",
        "When drops grow heavy, rain falls. The water journey begins again!")),
    ("kindness-chain", "The kindness chain", "kindness", (
        "A small kind act can make a big difference.", "Maya helped a friend pick up some pencils.",
        "The friend smiled and helped someone else tidy the books.",
        "What's one kind thing you can do today?")),
    ("animal-homes", "Who lives where?", "animals", (
        "Let's discover some amazing animal homes.", "A bird can build a nest to keep its eggs safe.",
        "A rabbit may live in a burrow under the ground.",
        "Animals find different ways to stay safe. Which home surprised you?")),
    ("moon-phases", "Why the moon changes shape", "space", (
        "Does the Moon really change its shape?", "No! The Moon stays round as it moves around Earth.",
        "The Sun lights part of the Moon, and we see different amounts of that light.",
        "Look for the Moon tonight with a grown-up. What shape do you see?")),
    ("pattern-detective", "Become a pattern detective", "numbers", (
        "Can you guess what comes next?", "Circle, square, circle, square... What comes next?",
        "A circle! That's a repeating pattern.", "Try making your own pattern with toys or colored blocks.")),
)
COLORS = ((34, 75, 161), (22, 139, 120), (144, 69, 170), (190, 96, 33))


def now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


@contextmanager
def locked(state_path: Path):
    state_path.parent.mkdir(parents=True, exist_ok=True)
    handle = open(str(state_path) + ".lock", "a+b")
    try:
        handle.seek(0)
        handle.write(b"0")
        handle.flush()
        handle.seek(0)
        if os.name == "nt":
            import msvcrt
            msvcrt.locking(handle.fileno(), msvcrt.LK_LOCK, 1)
        else:
            import fcntl
            fcntl.flock(handle.fileno(), fcntl.LOCK_EX)
        yield
    finally:
        if os.name == "nt":
            import msvcrt
            handle.seek(0)
            msvcrt.locking(handle.fileno(), msvcrt.LK_UNLCK, 1)
        else:
            import fcntl
            fcntl.flock(handle.fileno(), fcntl.LOCK_UN)
        handle.close()


def load(state_path: Path) -> dict:
    if state_path.exists():
        obj = json.loads(state_path.read_text(encoding="utf-8"))
        if obj.get("version") != 1 or not isinstance(obj.get("items"), dict):
            raise ValueError("Unsupported state format")
        return obj
    return {"version": 1, "updated": now(), "heartbeat": None,
            "items": {idea[0]: {"status": "ready", "views": 0, "completed": 0,
                                "replays": 0, "video_paths": []} for idea in IDEAS}}


def save(state_path: Path, state: dict) -> None:
    state_path.parent.mkdir(parents=True, exist_ok=True)
    state["updated"] = now()
    fd, temporary = tempfile.mkstemp(prefix=".state-", suffix=".tmp", dir=state_path.parent)
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as handle:
            json.dump(state, handle, ensure_ascii=False, indent=2)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temporary, state_path)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)


def confidence(item: dict) -> float:
    return item["views"] / (item["views"] + 200)


def score(item: dict) -> float:
    views = item["views"]
    if not views:
        return 0.0
    completion_rate = (item["completed"] + 20) / (views + 40)
    replay_rate = (min(item["replays"], views) + 4) / (views + 40)
    return confidence(item) * (0.8 * completion_rate + 0.2 * replay_rate)


def category_priority(state: dict, category: str) -> tuple[float, int]:
    peers = [state["items"][idea[0]] for idea in IDEAS if idea[2] == category]
    views = sum(peer["views"] for peer in peers)
    completed = sum(peer["completed"] for peer in peers)
    replays = sum(min(peer["replays"], peer["views"]) for peer in peers)
    explored = sum(peer["status"] == "created" for peer in peers)
    weight = views / (views + 200)
    performance = 0.8 * ((completed + 20) / (views + 40)) + 0.2 * ((replays + 4) / (views + 40))
    return (1 - weight) * 0.5 + weight * performance + 0.08 / (1 + explored), views


def ranked(state: dict) -> list[dict]:
    rows = []
    for order, (idea_id, title, category, scenes) in enumerate(IDEAS):
        item = state["items"][idea_id]
        priority, category_views = category_priority(state, category)
        rows.append({"id": idea_id, "title": title, "category": category,
                     "priority": round(priority, 4), "category_evidence_views": category_views,
                     "status": item["status"], "views": item["views"],
                     "completion_rate": round(item["completed"] / item["views"], 4) if item["views"] else None,
                     "replays": item["replays"], "evidence_weight": round(confidence(item), 4),
                     "evidence_score": round(score(item), 4) if item["views"] else None,
                     "_order": order})
    rows.sort(key=lambda x: (x["status"] != "ready", -x["priority"], x["_order"]))
    for row in rows:
        del row["_order"]
    return rows


def draw_cards(idea_id: str, target: Path) -> list[Path]:
    try:
        from PIL import Image, ImageDraw, ImageFont
    except ImportError as exc:
        raise RuntimeError("Pillow is required to create original local artwork") from exc
    item = next((idea for idea in IDEAS if idea[0] == idea_id), None)
    if item is None:
        raise ValueError("Unknown video idea")
    target.mkdir(parents=True, exist_ok=True)
    files = []
    for index, scene in enumerate(item[3]):
        background = COLORS[index]
        image = Image.new("RGB", (720, 1280), background)
        draw = ImageDraw.Draw(image)
        draw.ellipse((130, 155, 590, 615), fill=(255, 227, 101))
        if index % 2:
            draw.rectangle((245, 310, 475, 530), fill=(255, 255, 255))
        else:
            draw.polygon(((360, 240), (210, 520), (510, 520)), fill=(255, 255, 255))
        try:
            font = ImageFont.truetype("DejaVuSans.ttf", 43)
            small = ImageFont.truetype("DejaVuSans.ttf", 32)
        except OSError:
            font = ImageFont.load_default()
            small = font
        words = scene.split()
        lines, line = [], ""
        for word in words:
            probe = (line + " " + word).strip()
            if draw.textbbox((0, 0), probe, font=font)[2] > 615 and line:
                lines.append(line)
                line = word
            else:
                line = probe
        if line:
            lines.append(line)
        y = 715
        for segment in lines[:6]:
            draw.text((360, y), segment, fill="white", anchor="mt", font=font,
                      stroke_width=2, stroke_fill=(25, 35, 55))
            y += 85
        draw.text((360, 1170), f"{index + 1} / 4   |   Learn & Discover", font=small,
                  fill="white", anchor="mm")
        output = target / f"scene_{index + 1:02}.png"
        image.save(output, optimize=True)
        files.append(output)
    return files


def produce(idea_id: str, state_path: Path, no_voice: bool = False) -> dict:
    idea = next((idea for idea in IDEAS if idea[0] == idea_id), None)
    if idea is None:
        raise ValueError(f"Unknown idea: {idea_id}")
    with locked(state_path):
        state = load(state_path)
        item = state["items"][idea_id]
        if item["status"] != "ready":
            raise ValueError(f"Idea is already {item['status']}; no duplicate generation")
        item["status"] = "running"
        item["started"] = now()
        save(state_path, state)
    try:
        images = draw_cards(idea_id, state_path.parent / "assets" / idea_id)
        # A fresh child process overrides the runtime auto-upload switch before
        # importing the existing CLI; no persistent config or keys are modified.
        args = ["--video-script", " ".join(idea[3]), "--video-source", "local",
                "--video-materials", ",".join(str(path) for path in images),
                "--video-aspect", "9:16", "--video-count", "1",
                "--video-concat-mode", "sequential", "--bgm-type", "none",
                "--no-subtitle-enabled", "--voice-name", "en-US-JennyNeural-Female",
                "--stop-at", "video"]
        if no_voice:
            args[args.index("en-US-JennyNeural-Female")] = "no-voice"
        launcher = ("from app.config import config; "
                    "config.app[\"upload_post_auto_upload\"]=False; "
                    "import cli,sys; raise SystemExit(cli.run_cli(sys.argv[1:]))")
        # Only bundled local images, the supplied script and Edge TTS are used.
        completed = subprocess.run([sys.executable, "-c", launcher, *args],
                                   cwd=ROOT, capture_output=True, text=True,
                                   encoding="utf-8", errors="replace", timeout=1800, check=False)
        if completed.returncode != 0:
            raise RuntimeError(f"Video pipeline failed (exit {completed.returncode}): "
                               f"{completed.stderr[-500:]}")
        output_lines = completed.stdout.strip().splitlines()
        result = json.loads(output_lines[-1])
        videos = result.get("result", {}).get("videos") or []
        if not videos or not all(Path(video).is_file() for video in videos):
            raise RuntimeError("Pipeline returned no verified video files")
        with locked(state_path):
            state = load(state_path)
            state["items"][idea_id].update(status="created", task_id=result["task_id"],
                                           video_paths=videos, finished=now())
            save(state_path, state)
        return {"id": idea_id, "task_id": result["task_id"], "videos": videos,
                "published": False, "paid_services_requested": False}
    except Exception as exc:
        with locked(state_path):
            state = load(state_path)
            state["items"][idea_id].update(status="failed", error=str(exc), finished=now())
            save(state_path, state)
        raise


def feedback(idea_id: str, state_path: Path, views: int, completed: int, replays: int) -> dict:
    if idea_id not in {idea[0] for idea in IDEAS}:
        raise ValueError("Unknown idea")
    if views < 0 or not 0 <= completed <= views or replays < 0:
        raise ValueError("Invalid analytics: completed must be between zero and views")
    with locked(state_path):
        state = load(state_path)
        item = state["items"][idea_id]
        if item["status"] != "created":
            raise ValueError("Analytics require an actually created video")
        if views < item["views"]:
            raise ValueError("Use cumulative view totals, not per-period counts")
        item.update(views=views, completed=completed, replays=replays, observed=now())
        save(state_path, state)
        return {"id": idea_id, "views": views,
                "completion_rate": completed / views if views else None,
                "evidence_weight": round(confidence(item), 4), "score": round(score(item), 4)}


def command(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Create original child-friendly learning videos; publishing is disabled")
    parser.add_argument("action", choices=("status", "plan", "make", "watch", "feedback"))
    parser.add_argument("--state", type=Path, default=DEFAULT_STATE)
    parser.add_argument("--id", default="")
    parser.add_argument("--views", type=int, default=0)
    parser.add_argument("--completed", type=int, default=0)
    parser.add_argument("--replays", type=int, default=0)
    parser.add_argument("--no-voice", action="store_true")
    parser.add_argument("--interval-minutes", type=float, default=60)
    parser.add_argument("--limit", type=int, default=0, help="0 keeps the worker alive")
    args = parser.parse_args(argv)
    state_path = args.state.resolve()
    if args.action in {"status", "plan"}:
        with locked(state_path):
            state = load(state_path)
            if not state_path.exists():
                save(state_path, state)
        if args.action == "plan":
            print(json.dumps(ranked(state), indent=2))
        else:
            print(json.dumps({"heartbeat": state["heartbeat"], "updated": state["updated"],
                              "ready": sum(i["status"] == "ready" for i in state["items"].values()),
                              "created": sum(i["status"] == "created" for i in state["items"].values()),
                              "failed": sum(i["status"] == "failed" for i in state["items"].values())}, indent=2))
        return 0
    if args.action == "feedback":
        print(json.dumps(feedback(args.id, state_path, args.views, args.completed, args.replays), indent=2))
        return 0
    if args.action == "make":
        print(json.dumps(produce(args.id, state_path, args.no_voice), indent=2))
        return 0
    if not math.isfinite(args.interval_minutes) or args.interval_minutes <= 0 or args.limit < 0:
        parser.error("watch requires positive finite interval-minutes and limit")
    processed = 0
    while args.limit == 0 or processed < args.limit:
        with locked(state_path):
            state = load(state_path)
            state["heartbeat"] = now()
            save(state_path, state)
            available = [row for row in ranked(state) if row["status"] == "ready"]
        if not available:
            print(json.dumps({"status": "idle", "created_this_run": processed}), flush=True)
            if args.limit:
                break
            time.sleep(args.interval_minutes * 60)
            continue
        try:
            print(json.dumps(produce(available[0]["id"], state_path, args.no_voice)), flush=True)
        except Exception as exc:
            print(json.dumps({"id": available[0]["id"], "error": str(exc)}), file=sys.stderr, flush=True)
        processed += 1
        if args.limit == 0 or processed < args.limit:
            time.sleep(args.interval_minutes * 60)
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(command())
    except (ValueError, RuntimeError, OSError, json.JSONDecodeError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        raise SystemExit(1)
