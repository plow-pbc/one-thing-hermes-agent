#!/usr/bin/env python3
"""Register the daily one-thing cron once, from the root-owned copy, at boot.

`hermes cron` keeps jobs in /var/lib/hermes/cron/jobs.json and nothing replays
them on a fresh home, so the supervisor makes sure the one job exists.

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
    try:
        with open(jobs_path) as f:
            jobs = json.load(f)["jobs"]
    except FileNotFoundError:
        return False
    return any(job["name"] == NAME for job in jobs)


def create_argv(home_channel):
    if not (home_channel or "").strip():
        raise SystemExit("one-thing: PLOW_HOME_CHANNEL is blank; refusing a cron that delivers nowhere")
    return [HERMES, "cron", "create", SCHEDULE, PROMPT, "--name", NAME,
            "--skill", NAME, "--deliver", f"plow_chat:{home_channel.strip()}"]


def main(home_channel, jobs_path=JOBS_FILE, run=subprocess.run):
    if registered(jobs_path):
        print(f"one-thing: already registered in {jobs_path}")
        return 0
    return run(create_argv(home_channel)).returncode


if __name__ == "__main__":
    sys.exit(main(os.environ.get("PLOW_HOME_CHANNEL", "")))
