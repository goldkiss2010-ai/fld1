# FLD1 version 1: documented base profile

All numbers are little-endian; floats use IEEE 754. No C/C++ struct padding is
part of the file. This documents the inspected prototype's stride-8 authors.
Some readers accept larger strides; extra channel semantics remain unspecified.
The fixed public conventions are in [contract-v1.md](contract-v1.md).

## Header: 32 bytes

| Offset | Bytes | Type | Field | Value |
|---:|---:|---|---|---|
| 0 | 4 | ASCII | magic | FLD1 |
| 4 | 4 | uint32 | version | 1 |
| 8 | 4 | uint32 | particle_count | N > 0 |
| 12 | 4 | uint32 | frame_count | F > 0 |
| 16 | 8 | float64 | sample_rate | finite samples per q-unit > 0 |
| 24 | 4 | uint32 | stride_floats | 8 |
| 28 | 4 | uint32 | reserved | 0 |

Python packing: `struct.Struct('<4sIIIdII')`.

## Records

Frame-major, then particle-major. Each record is eight float32 values:

| Float index | Field | Meaning |
|---:|---|---|
| 0–2 | x, y, z | Position in author's coordinates |
| 3–5 | vx, vy, vz | Position derivative dx/dq in those coordinates |
| 6 | visibility | Visibility weight; examples use 1 for visible |
| 7 | scalar0 | Application-defined scalar |

Authoring convention: finite values, visibility in [0,1]. Consumers define how
visibility affects rendering. scalar0 has no inherent unit or semantic meaning.

Sample j has cache progress `q=j/sample_rate`, starting at zero.
`sample_rate` is the legacy field name; its unit is samples per q-unit, not
necessarily Hz. The author defines q; the DCC maps presentation time to q.
Record k of sample j starts at `32 + (j*N+k)*stride_floats*4`.
Base-profile file size is `32 + F*N*32` bytes.
The cache progress span is `(F-1)/sample_rate`. Presentation duration is
determined by the DCC time map.

Three million particles use 96,000,000 bytes per sample. A cache spanning five
q-units at eight samples per q-unit, including both endpoints, has 41 samples: 3,936,000,032 bytes, about 3.67 GiB.

## Identity and coordinates

Particle index is the implicit identity; keep N and particle ordering fixed
through all samples. Birth/death can use stable slots and visibility changes.
There is no ID table or topology. Reordering breaks trajectory interpolation.

The public contract selects right-handed XYZ with +Z up. These conventions are
not encoded in the header. Supply length scale, coordinate-frame description
and scalar meaning alongside the cache; audit legacy caches before assuming
they follow the public orientation convention. In moving coordinate systems,
velocity must include the derivative of the coordinate transformation.

## Playback is a consumer policy

The format does not mandate interpolation. The example uses cubic Hermite
position with endpoint derivatives dx/dq and cache interval `dq=1/sample_rate`, and returns the curve's
derivative as velocity. Visibility/scalar are interpolated linearly. This is
an example, not a promise to match all AE prototype playback behavior.

Holding, linear interpolation, looping, clamping, retiming and motion blur are
consumer decisions. Discontinuities can need special handling; v1 has no hold
flag. For a DCC map q=g(t), playback-time velocity is (dx/dq)*g'(t).

## Validation

Check magic/version, positive counts, finite positive rate, supported stride,
reserved value, overflow in size arithmetic, expected file length, frame bounds
and read completion before allocating from header values. Production consumers
should also impose practical allocation limits. The reference reader strictly
accepts stride 8, reserved 0 and exact file size.

Extensions need agreed semantics and a version/profile. Do not assign new
meaning to reserved data and assume compatibility.
