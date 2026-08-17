#!/usr/bin/env python3
import sys
sys.path.insert(0, '/opt/data/scripts')
import build_hermes_arch_pdf as m
orig = m.ht
def spy(data, wd=None, sm=False, hdr=m.NAVY):
    r = orig(data, wd, sm, hdr)
    print(f'ht-> {type(r).__name__}')
    return r
m.ht = spy
from reportlab.platypus import BaseDocTemplate
def spy_build(self, story, *a, **kw):
    print(f"Story has {len(story)} items")
    for i, item in enumerate(story):
        t = type(item).__name__
        extra = ''
        if t == 'list':
            extra = f' [contains: {[type(x).__name__ for x in item]}]'
        print(f"  [{i}] {t}{extra}")
BaseDocTemplate.build = spy_build
try:
    m.build()
except Exception as e:
    print(f"Error: {e}")