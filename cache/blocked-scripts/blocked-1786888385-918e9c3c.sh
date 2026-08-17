#!/bin/bash
# Auto-saved by Hermes: this command exceeded the inline command
# parser limit and was blocked from direct execution. Review it,
# then run it via: bash /opt/data/cache/blocked-scripts/blocked-1786888385-918e9c3c.sh
rm -f /tmp/sample.txt /tmp/land3.html /tmp/land.html /tmp/live.html /tmp/dr*.log 2>/dev/null; curl -s -o /tmp/check.html http://localhost:8765/; echo "live UI bytes: $(wc -c < /tmp/check.html)"; echo "stat-card: $(grep -c stat-card /tmp/check.html)"; echo "legend-pill: $(grep -c legend-pill /tmp/check.html)"; echo "old category-group: $(grep -c category-group /tmp/check.html)"; rm -f /tmp/check.html
