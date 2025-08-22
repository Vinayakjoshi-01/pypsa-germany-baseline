pypsa-germany-baseline

Baseline Germany power system model using PyPSA and HiGHS, with hourly load & generation simulation and access to historical + forecasted data till Nov 2025.

Germany_PyPSA_Model

A baseline Germany power system model built with PyPSA
 and solved using the HiGHS optimizer (fallback: GLPK).
This project simulates hourly electricity load and generator dispatch, providing a foundation for extending into renewable integration, marginal pricing, curtailment, and short-term planning studies.

🔹 Features

✅ Built on PyPSA with HiGHS solver for least-cost optimization.

✅ Access to historical & forecasted load data (up to Nov 2025).

✅ Hourly load vs. generation results saved in CSV.

✅ Modular and extendable structure for adding RES, storage, CO₂ caps, or other constraints.

📊 Outputs

germany_load_vs_gen_results.csv → Hourly load and generator dispatch.

germany_load_vs_gen.png → Visualization of load vs generation (optional).

🚀 How to Run

Clone the repo:

git clone https://github.com/YOUR_USERNAME/Germany_PyPSA_Model.git
cd Germany_PyPSA_Model


Create and activate environment:

conda create -n pypsa_env python=3.11
conda activate pypsa_env


Install dependencies:

pip install pypsa pandas matplotlib highspy requests


Run the model:

python GermanyPSA.py


⚡ The model automatically tries HiGHS first and falls back to GLPK if HiGHS is unavailable.

📚 References / Learning

PyPSA: https://pypsa.org

Plexos tutorials (Energy Exemplar): YouTube Playlist
