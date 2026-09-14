#!/usr/bin/env python3
"""Keep the daily one-thing cron registered and aimed at the owner's chat, at boot.

`hermes cron` keeps jobs in /var/lib/hermes/cron/jobs.json and nothing replays
them on a fresh home, so the supervisor makes sure the one job exists. The home
also outlives a re-mint, so an existing job whose delivery target is not the
current home channel gets retargeted rather than trusted.

Never read "could not tell what is registered" as "nothing is": that duplicates
the job. Only a missing jobs.json means empty; anything unreadable raises.
"""
import json
import os
import subprocess
import sys

HERMES = "/opt/hermes/bin/hermes"
JOBS_FILE = "/var/lib/hermes/cron/jobs.json"
NAME = "one-thing"
SCHEDULE = "0 8 * * *"
PROMPT = (
    "Run the one-thing skill now: read the owner's goal, pick the one important, "
    "not-urgent thing to do today, record it, and return it as the final response."
)


def registered(jobs_path=JOBS_FILE):
    """The one-thing job as hermes persisted it, or None when there is none."""
    try:
        with open(jobs_path) as f:
            jobs = json.load(f)["jobs"]
    except FileNotFoundError:
        return None
    return next((job for job in jobs if job["name"] == NAME), None)


def delivery_target(home_channel):
    if not (home_channel or "").strip():
        raise SystemExit("one-thing: PLOW_HOME_CHANNEL is blank; refusing a cron that delivers nowhere")
    return f"plow_chat:{home_channel.strip()}"


def main(home_channel, jobs_path=JOBS_FILE, run=subprocess.run):
    deliver = delivery_target(home_channel)
    job = registered(jobs_path)
    if job is None:
        return run([HERMES, "cron", "create", SCHEDULE, PROMPT, "--name", NAME,
                    "--skill", NAME, "--deliver", deliver]).returncode
    if job["deliver"] == deliver:
        print(f"one-thing: already registered for {deliver}")
        return 0
    return run([HERMES, "cron", "edit", job["id"], "--deliver", deliver]).returncode


if __name__ == "__main__":
    sys.exit(main(os.environ.get("PLOW_HOME_CHANNEL", "")))
