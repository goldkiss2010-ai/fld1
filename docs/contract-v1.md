# Canonical stored-sample authoring convention

The canonical FLD1 authoring profile selects stored-sample index q=0,1,2,... as its canonical
progression coordinate. For new distribution caches, sample_rate is exactly 1
and stored velocity is dx/dq per sample interval. The FLD1 v1 header and record
layout remain unchanged. The reader also accepts legacy rates so existing
files can be inspected and converted by normalize_cache.py.

The general progression-coordinate contract below is retained as background
and legacy interpretation; the canonical authoring subset is the sample-index
convention stated above. A normalization is a numerical change, not just a
rename. DCC playback settings must change consistently to preserve speed.

# FLD1 v1: fixed public contract

Status: repository author's selected conventions for the public v1 base profile.
These rules preserve the existing header and record bytes. Coordinate conventions
were not encoded in earlier prototype files; do not infer compliance for those
files without checking the generator. This document adds an explicit contract,
not a byte-level conversion of existing caches.

## Selected conventions

| Item | Fixed rule |
|---|---|
| Family | FLD |
| Magic / version | ASCII `FLD1` / uint32 `1` |
| Profile name | `point3-pv` (documented name, not a stored header field) |
| Byte order | Little-endian |
| Scalars | IEEE 754 float32 records; float64 sample rate |
| Header / record | 32 bytes / exactly 8 floats |
| Coordinates | Right-handed Cartesian XYZ; +Z is up; positive rotations follow the right-hand rule |
| Position | Simulation/object coordinates, never projected screen coordinates |
| Length | One consistent author-defined length unit; identify its physical scale externally when applicable |
| Progress coordinate | Uniform samples in cache coordinate q; first sample at q=0; conversion to presentation time belongs to the DCC |
| Velocity | dx/dq, the derivative of stored position with respect to cache progress q |
| Identity | Stable particle index and fixed count across all samples |
| Visibility | Finite weight in [0,1]; 0 is hidden, 1 is fully enabled; how the weight affects rendering is consumer-defined |
| scalar0 | One finite application-defined scalar; report meaning/unit externally; zero when unused |
| Reserved | Zero; no private interpretation |
| Core extensions | No appended channels, embedded metadata or trailing bytes in this profile |

There is no privileged forward axis in a point-state cache. A receiver chooses
its camera orientation. Units have not been forced to meters: analytic geometry
can be unitless, and prototype authors already use simulation units. Producers
must not mix length units within one cache.

## Interchange responsibilities

Producers using other coordinates convert position and velocity before export.
The orientation convention is a documentation agreement; no v1 flag can detect
an incorrectly oriented cache. A companion description must state length scale
(or "unitless"), scalar0 meaning/unit, and any numerical or physical limitations.

Receivers validate the header and file length and reject unsupported versions or
strides. Resource limits belong to the receiver. They must not silently swap
axes, guess units, or reinterpret fields. Display transformations remain free.

## Progress and presentation time

Cache progression and DCC time are separate. With legacy field name
`sample_rate = r`, sample j has cache coordinate `q=j/r`. Here r is samples per
unit of q; the header itself does not declare that q is seconds. For one sample
per stored step, use r=1 and velocity dx/dq per that step. If q denotes solver
steps and one sample is saved every K steps, use r=1/K and dx/dq per solver step.
Do not confuse solver steps with stored samples.

The DCC selects a mapping q=g(t), where t is presentation time. Hermite
interpolation uses the cache interval dq=1/r, not an assumed video-frame or
seconds interval. Physical/playback velocity with respect to t, if needed, is
(dx/dq)*g'(t). A reverse mapping reverses this velocity; a time hold makes it zero.

The example uses Hermite position from endpoint positions and dx/dq, returns
its derivative with respect to q, and interpolates visibility/scalar0 linearly.
This policy does not define a DCC time map. A single sample is held constant.
Consumers choose looping, clamping and retiming; the file format does not.

Existing second-based generators are a special case with q measured in their
simulation seconds. Their stored derivatives remain valid for that q. Do not
relabel their velocities as per-step values without converting both q scale
and derivatives. The current header carries no explicit q-unit metadata;
author documentation must specify q and derivative scale. The historical AE reader inspected in the audit maps presentation seconds to q through playback_speed
and time_offset, then clamps to the cache interval. Arbitrary mappings and
reverse playback are architectural possibilities, not implemented features
of that historical version. Current consumer behavior is documented separately
in [AE Handoff](https://github.com/goldkiss2010-ai/ae-handoff).

There is no discontinuity flag. Producers must not rely on smooth interpolation
across jumps, collisions or slot reuse; richer event semantics need a proposal.

## Compatibility boundary

The inspected prototype accepts strides 8–32, but that reader permissiveness
is not a schema for extra attributes. The frozen public base profile is stride
8 only. Existing non-base files require separate documentation and are not
claimed compatible with this reference implementation.

New meanings or structures go into proposals for a future version/profile.
Version 1 field meanings and offsets are not changed in place. A future version
number and magic policy will be selected with its layout, not guessed today.
