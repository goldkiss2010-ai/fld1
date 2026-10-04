"""Convert FLD1 v1 stride-8 to sample-index coordinates, preserving geometry."""
import argparse
from array import array
import os
from pathlib import Path
import sys
import tempfile
from fld1 import HEADER, Reader

def normalize(source, output, *, overwrite=False):
    source, output = Path(source), Path(output)
    if source.resolve() == output.resolve():
        raise ValueError('Use a separate output path')
    if output.exists() and not overwrite:
        raise FileExistsError(output)
    if not output.parent.is_dir():
        raise FileNotFoundError(output.parent)
    with Reader(source) as reader:
        h = reader.header
        fd, name = tempfile.mkstemp(prefix=output.name+'.',suffix='.tmp',dir=output.parent)
        tmp=Path(name)
        try:
            with os.fdopen(fd,'wb') as dst, source.open('rb') as src:
                src.seek(HEADER.size)
                dst.write(HEADER.pack(b'FLD1',1,h.particle_count,h.frame_count,1.0,8,0))
                remaining=h.particle_count*h.frame_count
                while remaining:
                    records=min(remaining,65536)
                    raw=src.read(records*32)
                    if len(raw)!=records*32:
                        raise ValueError('Input changed or was truncated during conversion')
                    values=array('f')
                    if values.itemsize!=4:
                        raise RuntimeError('This platform does not have 32-bit array floats')
                    values.frombytes(raw)
                    if sys.byteorder!='little': values.byteswap()
                    for base in range(0,len(values),8):
                        for k in (3,4,5): values[base+k] /= h.sample_rate
                    if sys.byteorder!='little': values.byteswap()
                    dst.write(values.tobytes())
                    remaining-=records
                if src.read(1): raise ValueError('Input changed during conversion')
            if output.exists() and not overwrite: raise FileExistsError(output)
            os.replace(tmp,output)
        finally:
            tmp.unlink(missing_ok=True)
    return h

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('source'); p.add_argument('output')
    p.add_argument('--overwrite',action='store_true')
    a=p.parse_args()
    h=normalize(a.source,a.output,overwrite=a.overwrite)
    print(f'Wrote {a.output}: {h.frame_count} samples; sample-index progression')
    print('DCC playback rate now means stored samples per presentation second.')

if __name__=='__main__': main()
