"""Analytic circular motion; q is an abstract progress coordinate, not DCC time."""
import argparse
import math
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from fld1 import Header, write

def main():
    p = argparse.ArgumentParser()
    p.add_argument('--output', default='orbit.fld1')
    p.add_argument('--count', type=int, default=128)
    args = p.parse_args()
    header = Header(args.count, 25, 12.0)
    header.validate()
    def frames():
        for j in range(header.frame_count):
            t = j / header.sample_rate
            def particles():
                for i in range(header.particle_count):
                    angle = 2*math.pi*i/header.particle_count + t
                    radius = 1 + 0.15*math.sin(i)
                    yield (radius*math.cos(angle), radius*math.sin(angle),
                           0.1*math.sin(i), -radius*math.sin(angle),
                           radius*math.cos(angle), 0, 1, i/header.particle_count)
            yield particles()
    write(args.output, header, frames())
    print(f'Wrote {args.output}: {header.particle_count} particles, 25 frames')

if __name__ == '__main__':
    main()
