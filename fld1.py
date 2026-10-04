"""Small, dependency-free reference implementation of the FLD1 base profile."""
from dataclasses import dataclass
import math
from pathlib import Path
import struct

HEADER = struct.Struct('<4sIIIdII')
RECORD = struct.Struct('<8f')

@dataclass(frozen=True)
class Header:
    particle_count: int
    frame_count: int
    sample_rate: float
    stride_floats: int = 8

    @property
    def duration(self):
        """Legacy name: cache progress span, not a DCC presentation duration."""
        return (self.frame_count - 1) / self.sample_rate

    @property
    def frame_bytes(self):
        return self.particle_count * self.stride_floats * 4

    def validate(self):
        if not (1 <= self.particle_count <= 0xffffffff and
                1 <= self.frame_count <= 0xffffffff):
            raise ValueError('Counts must be positive uint32 values')
        if not math.isfinite(self.sample_rate) or self.sample_rate <= 0:
            raise ValueError('sample_rate must be finite and positive')
        if self.stride_floats != 8:
            raise ValueError('Reference implementation supports only stride=8')

class Reader:
    """Seek to frames without loading the entire cache. Use as a context manager."""
    def __init__(self, path):
        self._file = Path(path).open('rb')
        try:
            raw = self._file.read(HEADER.size)
            if len(raw) != HEADER.size:
                raise ValueError('Truncated header')
            magic, version, n, frames, hz, stride, reserved = HEADER.unpack(raw)
            if magic != b'FLD1' or version != 1 or reserved != 0:
                raise ValueError('Unsupported magic, version or reserved field')
            self.header = Header(n, frames, hz, stride)
            self.header.validate()
            self._file.seek(0, 2)
            expected = HEADER.size + frames * self.header.frame_bytes
            if self._file.tell() != expected:
                raise ValueError('File size does not match header')
        except BaseException:
            self._file.close()
            raise

    def frame(self, index):
        if not 0 <= index < self.header.frame_count:
            raise IndexError(index)
        self._file.seek(HEADER.size + index * self.header.frame_bytes)
        raw = self._file.read(self.header.frame_bytes)
        if len(raw) != self.header.frame_bytes:
            raise ValueError('Truncated frame')
        return list(RECORD.iter_unpack(raw))

    def close(self):
        self._file.close()

    def __enter__(self):
        return self

    def __exit__(self, *args):
        self.close()

def write(path, header, frames):
    """Stream frames to a file; each record has exactly eight finite floats.

    Invalid input can leave a partial output. Use a temporary path and rename
    after success when updating a cache being consumed by another application.
    """
    header.validate()
    with Path(path).open('wb') as f:
        f.write(HEADER.pack(b'FLD1', 1, header.particle_count,
                            header.frame_count, header.sample_rate, 8, 0))
        count = 0
        for frame in frames:
            if count >= header.frame_count:
                raise ValueError('Too many frames')
            records = 0
            for record in frame:
                if records >= header.particle_count:
                    raise ValueError('Too many particles in frame')
                if len(record) != 8 or not all(math.isfinite(x) for x in record):
                    raise ValueError('Each record needs eight finite values')
                f.write(RECORD.pack(*record))
                records += 1
            if records != header.particle_count:
                raise ValueError('Particle count mismatch')
            count += 1
        if count != header.frame_count:
            raise ValueError('Frame count mismatch')

def interpolate(a, b, s, dt):
    """Example playback policy: cubic Hermite position; linear remaining fields.

    dt is the cache interval in progress-coordinate units (legacy argument name).
    Interpolated velocity is dx/dq, the derivative
    of the position curve. Visibility and scalar are linearly interpolated.
    """
    if not 0 <= s <= 1 or not math.isfinite(dt) or dt <= 0:
        raise ValueError('Need 0 <= s <= 1 and finite dt > 0')
    h00 = 2*s**3 - 3*s**2 + 1
    h10 = s**3 - 2*s**2 + s
    h01 = -2*s**3 + 3*s**2
    h11 = s**3 - s**2
    p = tuple(h00*a[k] + h10*dt*a[k+3] + h01*b[k] + h11*dt*b[k+3]
              for k in range(3))
    v = tuple(((6*s*s-6*s)*a[k] + (3*s*s-4*s+1)*dt*a[k+3]
              + (-6*s*s+6*s)*b[k] + (3*s*s-2*s)*dt*b[k+3]) / dt
              for k in range(3))
    return p + v + tuple((1-s)*a[k] + s*b[k] for k in (6, 7))
