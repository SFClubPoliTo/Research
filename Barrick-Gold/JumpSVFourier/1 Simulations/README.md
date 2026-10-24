# Simulations 🧪

Simulation stage for the Article 6 synthetic examples.

## 🎯 Role

This folder generates synthetic price-path and variance-path examples for article figures. Run the script from the `JumpSVFourier/` root folder so output paths remain stable.

## 📄 Files

| Path | Role |
| --- | --- |
| `simulate_examples.py` | Runs both simulations and writes data plus images. |
| `fourier_pricing_check.py` | Prices Heston and Merton calls from their characteristic functions and checks them against Monte Carlo and the Merton series. |
| `img/` | Stores article-ready raster figures. |
| `output/` | Stores the CSV data used to draw the figures. |

## ▶️ Run

From the `JumpSVFourier/` root folder:

```bash
python "1 Simulations/simulate_examples.py"
python "1 Simulations/fourier_pricing_check.py"
```
