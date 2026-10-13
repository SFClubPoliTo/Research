# Data and inputs 🗂️

The experiments use synthetic data and delivered numerical surfaces. No licensed market observations or access credentials are required.

| Path | Contents |
| --- | --- |
| `raw/source_freezes` | Original author sources, parameters, historical outputs and manuscript inputs, retained with their original relative paths. These are historical references rather than the current executable namespace. |
| `processed/manuscript_authoring` | Snapshot of the revised two-main Overleaf project: mathematical chapters, reference PNGs and cover. |
| `processed/policy_5sd_241.npz` | Policy interpolation cache bound to the SHA-256 of the delivered temporal surface. Rebuilt automatically if its source changes. |
| `processed/provenance` | Input hashes, flat-source migration, figure replay audit and report delivery records. |

The reference PNGs are immutable assets. Computed PNGs are compared against them; copying a PNG is recorded separately from rerunning a simulation. Some historical random streams remain unidentified, as specified by the root README and per-figure audit.
