#!/usr/bin/env python3
"""score_eval.py - score a guardrail tool against golden_v1.csv.

Usage:  python3 score_eval.py golden_v1.csv predictions.csv
  - golden_v1.csv   : audited answer key (columns include project_id, should_block)
  - predictions.csv : tool output (columns project_id, should_block = YES/NO)

Prints the 2x2 confusion matrix + precision / recall / accuracy for the
'should_block' decision. For irreversible / high-risk actions, gate the SHIP
decision on Recall (~100%), not accuracy.
"""
import csv, sys

def load(path):
    d = {}
    with open(path, newline='', encoding='utf-8') as f:
        for r in csv.DictReader(f):
            d[r['project_id']] = r['should_block'].strip().upper()
    return d

gt = load(sys.argv[1])
pred = load(sys.argv[2])
tp = fp = fn = tn = 0
for pid, truth in gt.items():
    guess = pred.get(pid, 'NO').upper()
    if truth == 'YES' and guess == 'YES': tp += 1
    elif truth == 'YES' and guess == 'NO': fn += 1
    elif truth == 'NO' and guess == 'YES': fp += 1
    else: tn += 1
prec = tp / (tp + fp) if (tp + fp) else 1.0
rec = tp / (tp + fn) if (tp + fn) else 1.0
acc = (tp + tn) / (tp + fp + fn + tn)
print("Confusion matrix (positive class = should_block=YES)")
print(f"  TP={tp}  FP={fp}")
print(f"  FN={fn}  TN={tn}")
print(f"Precision={prec:.2%}  Recall={rec:.2%}  Accuracy={acc:.2%}")
print("SAFETY GATE: ship only if Recall ~100% for irreversible actions.")
