import math
from pathlib import Path
import struct
import sys
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from fld1 import HEADER, Header, Reader, interpolate, write

class FLD1Tests(unittest.TestCase):
    def test_layout_and_seek(self):
        with tempfile.TemporaryDirectory() as d:
            path = Path(d)/'test.fld1'
            a = (1,2,3,4,5,6,1,0)
            b = (7,8,9,10,11,12,0,1)
            write(path, Header(1,2,12), [[a],[b]])
            expected = struct.pack('<4sIIIdII',b'FLD1',1,1,2,12,8,0)
            expected += struct.pack('<16f',*(a+b))
            self.assertEqual(path.read_bytes(), expected)
            with Reader(path) as r:
                self.assertEqual(r.frame(1),[b])
                self.assertEqual(r.frame(0),[a])
                with self.assertRaises(IndexError): r.frame(2)

    def test_invalid_files(self):
        with tempfile.TemporaryDirectory() as d:
            path = Path(d)/'bad.fld1'
            valid = HEADER.pack(b'FLD1',1,1,1,12,8,0)+bytes(32)
            variants = [b'', valid[:-1],valid+b'x',
                        HEADER.pack(b'FLD1',1,1,1,math.nan,8,0)+bytes(32),
                        HEADER.pack(b'FLD1',2,1,1,12,8,0)+bytes(32),
                        HEADER.pack(b'FLD1',1,1,1,12,9,0)+bytes(36)]
            for data in variants:
                path.write_bytes(data)
                with self.assertRaises(ValueError): Reader(path)

    def test_hermite_cubic_and_endpoints(self):
        # p(t)=t^3, v(t)=3t^2, between t=0 and t=2.
        a=(0,0,0,0,0,0,1,0)
        b=(8,0,0,12,0,0,0,1)
        self.assertEqual(interpolate(a,b,0,2),a)
        self.assertEqual(interpolate(a,b,1,2),b)
        m=interpolate(a,b,0.5,2)
        self.assertAlmostEqual(m[0],1)
        self.assertAlmostEqual(m[3],3)
        self.assertEqual(m[6:],(0.5,0.5))

if __name__ == '__main__':
    unittest.main()
