# NEP potential for Pb(Zr0.5Ti0.5)O3 with oxygen vacancies

This repository provides a trained Neuroevolution Potential (NEP) and reference datasets for lead zirconate titanate (PZT), Pb(Zr0.5Ti0.5)O3. The dataset includes pristine structures and configurations containing oxygen vacancies.

## Dataset organization

The training set contains **2,344 structures**, organized by oxygen-vacancy content and `config_type`:

| Training file | Structures | Size (decimal MB) |
| --- | ---: | ---: |
| `train_pristine.xyz` | 967 | 11.71 MB |
| `train_defect_initial.xyz` | 723 | 12.16 MB |
| `train_defect_active_learning_MD.xyz` | 654 | 16.58 MB |

- **Pristine:** stoichiometric structures with O = 3 × Pb. Their `config_type` is `perturb` or absent; no initial/active-learning provenance is inferred for this group.
- **Initial defect training set:** oxygen-vacancy structures labeled `*_perturb_*`, `*_relax_*`, and `ADD`. This set includes 25 supplementary initial structures labeled `ADD`.
- **Active-learning defect training set:** oxygen-vacancy structures labeled `MD_01_02` (139), `MD_03` (375), and `MD_04` (140).

Every defect training structure has exactly one oxygen vacancy relative to O = 3 × Pb. All training structures satisfy Pb = Zr + Ti and Zr = Ti. This composition check corroborates the label-based classification.

The two `train_defect_*.xyz` files together contain **1,377 defect-only training structures**. The pristine structures are provided as a separate training subset. Each file is below 25,000,000 bytes. Each structure retains its reference metadata and atomic records.

`validation.xyz` (56 structures) and `test.xyz` (200 structures) are reserved for validation and final evaluation, respectively; both contain oxygen-vacancy structures. Do not merge them into the training files. 

## Repository contents

The repository contains eight files: the three training subsets listed above, `validation.xyz`, `test.xyz`, `nep.in` (training configuration), `nep.txt` (trained potential), and this `README.md`. Every file is smaller than 25 MB.

## Preparing the training data

To use all 2,344 training structures, concatenate the three training subsets into `train.xyz`. For example, with Python 3 from the dataset directory:

```python
from pathlib import Path

files = [
    "train_pristine.xyz",
    "train_defect_initial.xyz",
    "train_defect_active_learning_MD.xyz",
]
with open("train.xyz", "xb") as output:
    for name in files:
        output.write(Path(name).read_bytes())
```

The command creates a local training file and refuses to overwrite an existing file. It combines all original training structures in group order; it does not reproduce their original interleaving. The resulting file exceeds 25 MB and is not intended for GitHub web upload.

For a defect-only experiment, combine only `train_defect_initial.xyz` and `train_defect_active_learning_MD.xyz` (1,377 structures). This is a subset of the full training data. Keep validation and test structures out of training.

## Data format

The datasets use extended XYZ format: each structure starts with the atom count and a metadata line, followed by per-atom records. The training data includes species, positions, forces, lattice vectors, energy and virial metadata. Preserve these fields when converting the data for other tools.

## Reference calculations

- Electronic-structure code: **VASP**.
- Exchange–correlation functional: **PBEsol**, as reported in the original project notes.
- Plane-wave energy cutoff: **600 eV**.

The original notes do not specify the pseudopotential/PAW datasets, VASP version, k-point sampling or convergence thresholds. PBEsol identifies a functional, not a pseudopotential; consult the original calculation inputs for those details.

## Training configuration

The original project notes report **GPUMD v5.9.1**. The supplied `nep.in` selects **NEP version 4**; these are separate version identifiers.

Key settings from `nep.in`:

| Setting | Value |
| --- | --- |
| Species order | Zr, Ti, Pb, O |
| Radial / angular cutoffs | 8 / 6 |
| `n_max` | 8 8 |
| `basis_size` | 12 12 |
| `l_max` | 4 1 1 |
| Hidden neurons | 60 |
| Energy / force / virial loss weights | 1.0 / 1.0 / 0.1 |
| Batch size | 5000 |
| Population | 52 |
| Generations | 500000 |
| Random seed | 303 |

The full configuration, including ZBL and output settings, is in `nep.in`. Prepare `train.xyz` as described above before a training run. The validation file is distributed separately; `nep.in` alone does not establish how validation was performed.

## Using the trained potential

Copy `nep.txt` into your GPUMD simulation directory and reference it in `run.in`:

```text
potential nep.txt
```

This line is only the potential-loading directive, not a complete simulation input. Supply a compatible structure and the remaining simulation settings, and check species mapping and input requirements for your GPUMD version.

## Scope and reproducibility

No numerical accuracy metrics or validated temperature/pressure range are supplied here. Evaluate the potential on representative configurations before using it outside the training domain. Retain the test set for final evaluation rather than parameter selection.
