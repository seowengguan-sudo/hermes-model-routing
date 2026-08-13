# Golden-set eval scaffold (reusable asset for mentor / learn crons)

Drop-in pattern for building a guardrail eval "golden set" for a POC tool. Verified
2026-08-12 with `pensolar/modules/golden_v1.csv` + `score_eval.py` (TP=4 FP=1 FN=1 TN=14,
precision 80% / recall 80% / accuracy 90% on the sample).

## When to use
A cron (or mentor note) has taught evals / precision-recall / golden-set curation, and the
student's standing gap is EXECUTION — they keep failing to build the 20-case set. Ship this
scaffold instead of another teaser. (See SKILL.md "Mentor-cron adaptive override".)

## CSV schema (8 columns, ~20 rows, freeze as `golden_v1.csv`)
```
project_id,question_type,input_snapshot,correct_answer,should_block,labeled_by,labeled_date,version
```
- `question_type` = the DECISION the tool must make (e.g. "auto_schedule_crew: should block
  crew before permit clear?"), NOT the source record ("permit status = pending").
- `input_snapshot` = inputs FROZEN AT DECISION TIME. Never include the final cleared date or
  post-decision facts — that is leakage and inflates every score.
- `should_block` = YES/NO — the binary label the scorer gates on.
- `labeled_by` / `labeled_date` = human sign-off. Until a real person signs, set
  `labeled_by=EXAMPLE-SYNTH` and treat the row as a SHAPE example, not ground truth.

## Stratification rule (the trap)
Random 20 closed projects yields ~1 real block case → recall unmeasurable. Deliberately
over-include rare/ugly failure modes so ~25% (5/20) are block cases: expired permit, vendor
withdrew quote, scope change mid-install, permit pending past scheduled date, open authority
objection. A golden set is chosen for COVERAGE of failure modes, not to look like an average month.

## Known-good scorer (`score_eval.py`, ~20 lines)
```python
#!/usr/bin/env python3
"""score_eval.py - score a guardrail tool against golden_v1.csv.
Usage: python3 score_eval.py golden_v1.csv predictions.csv
  golden_v1.csv   : audited answer key (cols include project_id, should_block)
  predictions.csv : tool output (cols project_id, should_block = YES/NO)
Prints 2x2 + precision/recall/accuracy. Gate SHIP on Recall (~100%) for irreversible actions.
"""
import csv, sys
def load(path):
    d = {}
    with open(path, newline='', encoding='utf-8') as f:
        for r in csv.DictReader(f):
            d[r['project_id']] = r['should_block'].strip().upper()
    return d
gt = load(sys.argv[1]); pred = load(sys.argv[2])
tp = fp = fn = tn = 0
for pid, truth in gt.items():
    guess = pred.get(pid, 'NO').upper()   # missing prediction -> NO (still scores FN on a YES)
    if truth == 'YES' and guess == 'YES': tp += 1
    elif truth == 'YES' and guess == 'NO': fn += 1
    elif truth == 'NO' and guess == 'YES': fp += 1
    else: tn += 1
prec = tp/(tp+fp) if (tp+fp) else 1.0
rec  = tp/(tp+fn) if (tp+fn) else 1.0
acc  = (tp+tn)/(tp+fp+fn+tn)
print("Confusion matrix (positive class = should_block=YES)")
print(f"  TP={tp}  FP={fp}\n  FN={fn}  TN={tn}")
print(f"Precision={prec:.2%}  Recall={rec:.2%}  Accuracy={acc:.2%}")
print("SAFETY GATE: ship only if Recall ~100% for irreversible actions.")
```

## Verification before claiming done
Run the scorer on a sample predictions file; assert the 2x2 + recall. Use the inline heredoc
trick from SKILL.md (safe-root blocks /tmp). Also assert: a missing prediction row on a real
block case scores FN (recall penalised), so a silent skip can never inflate recall.

## Honest residual to hand back
The scaffold rows are EXAMPLE-SYNTH placeholders, NOT audited ground truth. The scorer is
real; the answer key still needs the student's (or PM's) sign-off before it is a valid eval.
