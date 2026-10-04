# Roadmap

The FLD1 v1 public base profile is fixed in [contract-v1.md](contract-v1.md).
This roadmap is exploratory, not a promise of future compatibility or features.

## Validate v1 across implementations

- Compare byte layout between the reference implementation and existing authors.
- Audit each author for the selected coordinate and velocity convention.
- Reproduce analytic and numerical particle motion through the same consumer.
- Check low-density to high-density substitution with matching coordinates/time.
- Package an AE consumer separately with a small compatible example cache.

## Future proposals, motivated by observed limitations

| Limitation | Candidate extension |
|---|---|
| Coordinates, progress units and attribute meanings travel separately | Typed metadata for length/progress units, axes and attributes |
| Smooth interpolation cannot represent hard changes | Explicit discontinuity / interpolation policy data |
| Fixed slot identities restrict changing populations | Particle IDs and variable-count samples |
| Noncompressed files become large | Chunking, compression and indexed frame access |
| Only one scalar is available | Named typed attributes |

Do not create one format per physical solver. Add a capability when a consumer
needs information that v1 cannot preserve. Consider decoding cost, random access
and backward compatibility for every proposal. Future layouts, profile names
and the version-2 magic have not been standardized.
