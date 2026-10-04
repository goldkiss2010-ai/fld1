from pathlib import Path
import sys
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from fld1 import Header, Reader, interpolate, write
from normalize_cache import normalize

class NormalizeTests(unittest.TestCase):
    def test_same_geometry_under_coordinate_conversion(self):
        with tempfile.TemporaryDirectory() as d:
            a=Path(d)/'old.fld1'; b=Path(d)/'new.fld1'
            start=(0,0,0,0,0,0,1,7)
            end=(0.125,0,0,0.75,0,0,0.5,9)
            write(a,Header(1,2,2),[[start],[end]])
            normalize(a,b)
            with Reader(a) as old,Reader(b) as new:
                self.assertEqual(new.header.sample_rate,1)
                x,y=new.frame(0)[0],new.frame(1)[0]
                self.assertEqual(y[:3],end[:3])
                self.assertEqual(y[6:],end[6:])
                self.assertEqual(y[3],0.375)
                for s in [0,0.2,0.5,0.8,1]:
                    p=interpolate(start,end,s,0.5)
                    n=interpolate(x,y,s,1)
                    for k in range(3): self.assertAlmostEqual(p[k],n[k])
                    for k in range(3,6): self.assertAlmostEqual(p[k]/2,n[k])
            before=a.read_bytes()
            with self.assertRaises(ValueError): normalize(a,a,overwrite=True)
            with self.assertRaises(FileExistsError): normalize(a,b)
            self.assertEqual(a.read_bytes(),before)
