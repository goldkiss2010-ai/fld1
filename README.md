![FLD1 — Fields, concisely.](branding/key-visual.jpg)

# FLD1 — particle state handoff

**Store particle states; let the DCC choose observation and presentation.**

FLD1 is an experimental binary format for handing sampled particle states from
an authoring environment to a DCC. The generator can use any language or backend:
analytic geometry, numerical simulation, image-derived points, or procedural code.
Python is the language of the included reference tools, not a format requirement.

[日本語](README.ja.md) · [Fixed v1 contract](docs/contract-v1.md) · [Byte layout](docs/format.md) · [Design](docs/design.md) · [Roadmap](docs/roadmap.md)

## Fixed v1 profile

The selected base profile is `point3-pv`: right-handed XYZ with +Z up, fixed
particle count and ordering, and eight float32 values per particle:
`x y z vx vy vz visibility scalar0`. Files are little-endian, with a 32-byte header.

For new canonical caches, progress q is stored-sample index 0,1,2,…,
`sample_rate=1`, and velocity is dx/dq per sample interval. Absolute media time
is not encoded. The DCC selects q=g(t), together with interpolation, transforms,
camera, projection and styling. Visibility interpretation belongs to the consumer.

The reader also accepts legacy positive sample rates. Normalization preserves
positions and Hermite curves while converting stored derivatives to sample-index
units; playback settings and velocity-based styling may need adjustment.

## Try it

Python 3.10+; run from the repository root. No external dependencies.

```sh
python examples/make_orbit.py --output orbit-legacy.fld1 --count 128
python normalize_cache.py orbit-legacy.fld1 orbit.fld1
python examples/inspect_cache.py orbit.fld1 --frame 12
python -m unittest discover -s tests -v
```

The orbit example is analytic, not a fluid simulation, and writes a legacy
rate-12 cache before normalization. The reference implementation prioritizes
clarity and interoperability over bulk-array performance. It validates header,
stride and file size; record-domain constraints remain the producer's responsibility.

## Repositories and scope

This repository owns the FLD1 contract, byte layout, design, reference tools and
future-version proposals. [AE Handoff](https://github.com/goldkiss2010-ai/ae-handoff)
provides the Windows AE consumer as a compiled plugin, usage guides and particle-field
generators. It includes a materialized copy of these reference tools under `core/`.
AE plugin source, build configuration and private development history are excluded.

Version 1 has no mesh topology, explicit particle IDs, variable populations,
nonuniform timestamps, embedded metadata, discontinuity flags or named extra
channels. FLD2 and additional profiles are proposals, not implemented formats;
v1 field meanings and offsets stay fixed. See the roadmap for motivating limits.

## Development status