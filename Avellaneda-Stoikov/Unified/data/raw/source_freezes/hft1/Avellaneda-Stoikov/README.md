# Avellaneda–Stoikov Market Making 📈

Companion simulations for the Starting Finance Club PoliTo Research article “High-Frequency Market Making under Avellaneda–Stoikov”.

## 👥 Authors

Salvatore Gabriele Messina; Niccolò Soriano.

## 🎯 Purpose

Compare naive and inventory-aware market making under classical price diffusions and a covariance-aware multi-asset extension.

## 🗂️ Structure

`_gen_notebook.py` generates `articolo1_applicazione.ipynb`. `_gen_github_notebook.py` builds the commented companion notebook. Existing notebook variants are preserved; edit the generators rather than notebook JSON.

## ⚙️ Setup

Use the existing Python environment with NumPy, Matplotlib, Jupyter and nbconvert. Dependency versions have not been newly pinned or validated in this organizational migration.

## ▶️ Run

From this directory:

```sh
python _gen_notebook.py
python -m jupyter nbconvert --execute --inplace articolo1_applicazione.ipynb
```

## 📊 Outputs

The executed notebook exports `py1.png` and `py2.png` in its working directory. Compare regenerated figures with the article before copying them into Overleaf. Existing article figures were preserved during migration; numerical code was not changed or rerun.

## 📚 Citation

Salvatore Gabriele Messina and Niccolò Soriano, *High-Frequency Market Making under Avellaneda–Stoikov*, Starting Finance Club PoliTo, Research.
