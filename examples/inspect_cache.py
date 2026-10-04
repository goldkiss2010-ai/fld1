import argparse
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from fld1 import Reader

p = argparse.ArgumentParser()
p.add_argument('path')
p.add_argument('--frame', type=int, default=0)
args = p.parse_args()
with Reader(args.path) as cache:
    print(cache.header)
    print('Cache progress span (q units):', cache.header.duration)
    frame = cache.frame(args.frame)
    print('First particle:', frame[0])
