# pypsa-germany-baseline
Baseline Germany power system model using PyPSA and HiGHS, with hourly load &amp; generation simulation and access to forecasted data till Nov 2025.

# Germany_PyPSA_Model

A baseline **Germany power system model** built with [PyPSA](https://pypsa.org/) and solved using the **HiGHS optimizer**.  
This project simulates **hourly electricity load and generation dispatch**, providing a foundation for extending into renewable integration, marginal pricing, and curtailment studies.  

---

## 🔹 Features
- ✅ Built on **PyPSA** with **HiGHS** solver for least-cost optimization.  
- ✅ Access to **historical & forecasted load data** (till Nov 2025).  
- ✅ Hourly load vs. generation balance results stored in CSV.  
- ✅ Modular structure → extendable for RES integration, CO₂ caps, and storage.  

---

## 📊 Outputs
- `germany_load_vs_gen_results.csv` → Hourly load and generation balance.  
- `germany_load_vs_gen.png` → Visualization of system balance (optional).  

---

## 🚀 How to Run
1. Clone the repo:  
   ```bash
   git clone https://github.com/YOUR_USERNAME/Germany_PyPSA_Model.git
   cd Germany_PyPSA_Model
Install dependencies:
conda create -n pypsa_env python=3.11
conda activate pypsa_env
pip install pypsa pandas matplotlib highs

Run the model:
python GermanyPSA.py

