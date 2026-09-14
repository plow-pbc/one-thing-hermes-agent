# One Thing

A Plow agent that texts you once a day, at 08:00, with **the one important
thing worth doing today that isn't urgent** and wouldn't happen otherwise. It's
the second quadrant of the Eisenhower matrix, steered by a life/work goal you
give it.

- Text it your goal once. It keeps it at `/var/lib/hermes/one-thing/goal.md`.
- Every morning: one thing, and why it moves the goal.
- Reply `done`, `not that` (with a reason), `why?` or `another`. It learns
  from your answers.

Built on the [plow-hermes-agent](https://github.com/plow-pbc/plow-hermes-agent)
base, following the [plow-agents Quickstart](https://github.com/plow-pbc/plow-agents#quickstart).

## Run it

```sh
git clone https://github.com/plow-pbc/plow-agents.git && export PATH="$PWD/plow-agents/bin:$PATH"
git clone https://github.com/plow-pbc/one-thing-hermes-agent.git && cd one-thing-hermes-agent
plow-agents login
plow-agents lines
plow-agents mint ln_xxx
AGENT_ID=one-thing TZ=America/Los_Angeles docker compose up --build -d
```

Wait for `plow-init: configured ... as cht_` in `docker compose logs -f agent`,
then text the line your goal.

## Agent Index

The image reports usage to the [Agent Index](https://aiworthusing.com/agent-index)
every 5 minutes, through the pinned client in `vendor/client.pin`. With
`AGENT_ID=one-thing`, your usage counts toward this agent's page. Without
`AGENT_ID`, the reporter stands down.

## What's in here

| path | what |
| --- | --- |
| `runtime/persona.md` | who the agent is |
| `one-thing/SKILL.md` | the daily pick, and how it handles your replies |
| `one-thing/scripts/register_cron.py` | registers the 08:00 cron once, at boot |
| `image/s6-overlay/s6-rc.d/one-thing-cron/` | runs that script from the root-owned copy |
| `image/s6-overlay/s6-rc.d/agent-index/` | the usage reporter from life-assistant, but it registers as root so the agent never sees the Plow token |

Test: `python3 tests/test_register_cron.py`

## License

MIT, see [LICENSE](LICENSE).
