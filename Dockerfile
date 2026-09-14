# One Thing: a Plow agent that texts its owner, once a day, the one important
# but not urgent thing worth doing today, steered by the goal they set.
#
# Built FROM an immutable base digest, never a moving tag: an agent holding a
# live Plow credential must not have code substituted underneath it.
FROM public.ecr.aws/e1h7x4a2/plow-cloud-agents:base-c22c33b11916110a7117b7c441317238e62936af@sha256:27beba91a44e7829a75a64b29fc9bebe7377aef4746144969ef8c6caa3f00b62

# plow-init composes SOUL.md on every boot as the base persona plus this file.
COPY --chmod=0644 runtime/persona.md /opt/hermes/plow-seed/persona.md
COPY LICENSE /usr/share/doc/one-thing/

# The skill the agent reads, seeded into its home by the base runtime.
COPY one-thing/ /opt/hermes/skills/one-thing/
RUN find /opt/hermes/skills/one-thing -type d -exec chmod 0755 {} + \
 && find /opt/hermes/skills/one-thing -type f -exec chmod 0644 {} +

# What the supervisor runs is root-owned under /opt/plow, never the home copy:
# everything under $HERMES_HOME belongs to the agent, so scheduling that copy
# would run whatever a turn last wrote there, holding the relay credential.
COPY one-thing/scripts/register_cron.py /opt/plow/one-thing/register_cron.py

# The usage reporter, fetched at build from the commit vendor/client.pin names
# and refused unless its checksum matches.
COPY vendor/client.pin /opt/plow/agent-index-client.pin
RUN set -eu; \
    sha="$(sed -n 's/^sha=//p' /opt/plow/agent-index-client.pin)"; \
    want="$(sed -n 's/^sha256=//p' /opt/plow/agent-index-client.pin)"; \
    path="$(sed -n 's/^path=//p' /opt/plow/agent-index-client.pin)"; \
    curl -fsS --max-time 60 -o /opt/plow/agent-index-client.py \
      "https://raw.githubusercontent.com/plow-pbc/agent-index-client/${sha}/${path}"; \
    got="$(sha256sum /opt/plow/agent-index-client.py | cut -d' ' -f1)"; \
    [ "$got" = "$want" ] || { echo "agent-index client is $got, pin says $want" >&2; exit 1; }; \
    chown -R root:root /opt/plow \
 && find /opt/plow -type d -exec chmod 0755 {} + \
 && find /opt/plow -type f -exec chmod 0644 {} +

COPY image/s6-overlay/ /etc/s6-overlay/

# Where the owner's goal and the daily picks live; the agent writes here.
RUN install -d -o 10000 -g 10000 -m 0700 /var/lib/hermes/one-thing
