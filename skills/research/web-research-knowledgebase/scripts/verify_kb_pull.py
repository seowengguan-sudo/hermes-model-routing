#!/usr/bin/env python3
"""Ad-hoc verifier for web-research-knowledgebase deliverables.

NOT a test suite -- checks artifact constraints from the skill workflow.
Cron jobs block execute_code and /tmp writes, so copy this to a writable path
(e.g. the client log dir or /opt/data/scripts) and run via terminal:

    python3 verify_kb_pull.py <log> <raw> <summary> [expected_pain_points]

Exit 0 = all constraints pass; 1 = at least one fail; 2 = bad usage.
"""
import os
import re
import sys


def chk(cond, name, detail=""):
    print(f"[{'PASS' if cond else 'FAIL'}] {name}  {detail}")
    return bool(cond)


def main():
    if len(sys.argv) < 4:
        print("usage: verify_kb_pull.py <log> <raw> <summary> [expected_pain_points]")
        return 2
    LOG, RAW, SUM = sys.argv[1], sys.argv[2], sys.argv[3]
    exp_pain = int(sys.argv[4]) if len(sys.argv) > 4 else 7

    passed = total = 0
    for p in (LOG, RAW, SUM):
        total += 1
        passed += chk(os.path.isfile(p), f"exists {os.path.basename(p)}")

    L = open(LOG, encoding="utf-8").read()
    R = open(RAW, encoding="utf-8").read()
    S = open(SUM, encoding="utf-8").read()

    total += 1
    passed += chk(len(L.split()) < 1500, "log <1500 words", f"{len(L.split())}w")
    sb = len(S.encode("utf-8"))
    total += 1
    passed += chk(sb <= 32768, "summary <=32768 bytes", f"{sb}B")
    total += 1
    passed += chk("SUMMARY_CAP_HIT" not in (L + R + S), "no SUMMARY_CAP_HIT")
    total += 1
    passed += chk("[cache missing" not in R, "raw not placeholder")

    # pain-point numbering: lines beginning with "N. " (broad, N in 1..exp_pain)
    nums = sorted(
        {int(m.group(1)) for m in re.finditer(r"^(\d+)\.\s", L, re.M)}
    )
    total += 1
    passed += chk(
        nums[:exp_pain] == list(range(1, exp_pain + 1)),
        f"{exp_pain} pain points",
        f"{nums}",
    )

    print("=" * 50)
    print(f"AD-HOC VERIFY: {passed}/{total} passed (artifact constraint check, not a suite)")
    return 0 if passed == total else 1


if __name__ == "__main__":
    sys.exit(main())
