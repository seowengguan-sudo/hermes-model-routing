#!/usr/bin/env python3
"""Debug: check bracket structure of P1 table call."""
import ast

lines = open('/opt/data/scripts/build_hermes_arch_pdf.py').readlines()

expr = ''.join(lines[123:126])
expr = expr.rstrip().rstrip(',')
print("Expression:")
print(repr(expr[:200]))
print("Ends with:")
print(repr(expr[-30:]))

opens_sq = expr.count('[')
closes_sq = expr.count(']')
opens_par = expr.count('(')
closes_par = expr.count(')')
print(f"Brackets: [{opens_sq} opens / {closes_sq} closes = {opens_sq - closes_sq}")
print(f"Parens:  ({opens_par} opens / {closes_par} closes = {opens_par - closes_par}")

try:
    tree = ast.parse(expr, 'eval')
    print("Parsed OK")
except SyntaxError as e:
    print(f"SyntaxError: {e.msg}")
    print(f"  text: {repr(e.text[:80]) if e.text else 'None'}")
