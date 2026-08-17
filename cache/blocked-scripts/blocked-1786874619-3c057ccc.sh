#!/bin/bash
# Auto-saved by Hermes: this command exceeded the inline command
# parser limit and was blocked from direct execution. Review it,
# then run it via: bash /opt/data/cache/blocked-scripts/blocked-1786874619-3c057ccc.sh
strings /opt/data/bin/tirith | grep -ioE "github\.com/sheeki[^\"' ]*" | sort -u | head
