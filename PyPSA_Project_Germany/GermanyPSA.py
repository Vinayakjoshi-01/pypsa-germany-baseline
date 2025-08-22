import os
import sys
import warnings
import pandas as pd
import matplotlib.pyplot as plt

# Silence noisy-but-okay warnings to keep the console clean
warnings.simplefilter(action="ignore", category=FutureWarning)

# ---------- CONFIG ----------
CSV_FILE = "entsoe_germany_load_aug2025.csv"  # <- your ENTSO-E CSV
DATETIME_COL_CANDIDATES = ["datetime", "time", "timestamp"]
LOAD_COL_CANDIDATES = ["load_MW", "Load", "load", "quantity", "value"]

OUTPUT_CSV = "germany_load_vs_gen_results.csv"
OUTPUT_PNG = "germany_load_vs_gen.png"

# Generator settings (simple thermal proxy)
GEN_P_NOM_MW = 85_000        # Max capacity (MW). Set safely above Germany hourly peaks
GEN_MARGINAL_COST = 50.0      # €/MWh (placeholder for a thermal plant)
SOLVER_ORDER = ["highs", "glpk"]  # Try HiGHS first, then GLPK


def find_column(df, candidates, kind):
    for c in candidates:
        if c in df.columns:
            return c
        # also try case-insensitive
        for col in df.columns:
            if col.lower() == c.lower():
                return col
    raise ValueError(
        f"Could not find a {kind} column. Looked for any of: {candidates}. "
        f"Available columns: {list(df.columns)}"
    )


def prepare_timeseries(csv_path):
    if not os.path.exists(csv_path):
        raise FileNotFoundError(
            f"Input CSV '{csv_path}' not found. Ensure your ENTSO-E fetch script "
            f"saved the file in this folder."
        )

    df = pd.read_csv(csv_path)
    # Identify columns
    dt_col = find_column(df, DATETIME_COL_CANDIDATES, "datetime")
    load_col = find_column(df, LOAD_COL_CANDIDATES, "load")

    # Parse datetime
    df[dt_col] = pd.to_datetime(df[dt_col], utc=True, errors="coerce")

    # Clean + set index
    df = df[[dt_col, load_col]].dropna()
    df = df.rename(columns={dt_col: "datetime", load_col: "load_MW"})
    df = df.set_index("datetime").sort_index()

    # Ensure hourly (ENTSO-E GL A65 is hourly; just in case, force hourly)
    # If duplicates or gaps exist, we forward-fill short gaps
    df = df[~df.index.duplicated(keep="first")]
    df = df.resample("h").mean().interpolate(limit=2)

    # Sanity checks
    df["load_MW"] = pd.to_numeric(df["load_MW"], errors="coerce").fillna(0.0)
    df.loc[df["load_MW"] < 0, "load_MW"] = 0.0

    if len(df) == 0:
        raise ValueError("After cleaning, no rows remain. Check input CSV content.")

    return df


def run_pypsa(df):
    import pypsa

    # Build network
    n = pypsa.Network()
    n.set_snapshots(df.index)

    n.add("Bus", "DE_bus")

    # Add the load (PyPSA expects p_set indexed by snapshots)
    n.add(
        "Load",
        name="DE_load",
        bus="DE_bus",
        p_set=df["load_MW"]
    )

    # Simple thermal generator to serve demand
    n.add(
        "Generator",
        name="DE_gen",
        bus="DE_bus",
        p_nom=GEN_P_NOM_MW,
        marginal_cost=GEN_MARGINAL_COST
    )

    # Solve: try HiGHS, then GLPK
    print("✅ Network setup complete. Running LOPF...")
    solver_used = None
    last_error = None

    for solver in SOLVER_ORDER:
        try:
            # A couple of reasonable default options; safe if unsupported
            n.optimize(
                solver_name=solver,
                threads=4,
                time_limit=120
            )
            solver_used = solver.upper()
            break
        except Exception as e:
            print(f"⚠️  {solver.upper()} failed: {e}")
            last_error = e

    if solver_used is None:
        raise RuntimeError(
            "❌ No solver worked. Check HiGHS/GLPK installations. "
            f"Last error: {last_error}"
        )

    print(f"✅ LOPF complete using {solver_used}!")

    return n, solver_used


def export_outputs(n, solver_used):
    # Export head of results to console
    print("\nLoad output (first 5 rows):")
    print(n.loads_t.p.head())

    print("\nGenerator output (first 5 rows):")
    print(n.generators_t.p.head())

    # Save results to CSV
    df_out = pd.DataFrame({
        "load_MW": n.loads_t.p["DE_load"],
        "generator_MW": n.generators_t.p["DE_gen"]
    })
    df_out.to_csv(OUTPUT_CSV)
    print(f"✅ Results saved to {OUTPUT_CSV}")

    # Plot
    plt.figure(figsize=(12, 6))
    plt.plot(df_out.index, df_out["load_MW"], label="Load (MW)", linewidth=1)
    plt.plot(df_out.index, df_out["generator_MW"], label="Generator (MW)", linewidth=1)
    plt.title(f"Germany: Load vs Generator Dispatch ({solver_used})")
    plt.xlabel("Date")
    plt.ylabel("Power (MW)")
    plt.legend()
    plt.grid(True, linestyle="--", alpha=0.6)
    plt.tight_layout()
    plt.savefig(OUTPUT_PNG, dpi=300)
    plt.close()
    print(f"📊 Plot saved as {OUTPUT_PNG}")


def main():
    try:
        df = prepare_timeseries(CSV_FILE)
    except Exception as e:
        print(f"❌ Failed to prepare time series: {e}")
        sys.exit(1)

    try:
        n, solver_used = run_pypsa(df)
    except Exception as e:
        print(f"❌ Optimisation failed: {e}")
        sys.exit(1)

    try:
        export_outputs(n, solver_used)
    except Exception as e:
        print(f"❌ Export/plot failed: {e}")
        sys.exit(1)

    print("\n🎯 Done. This baseline shows least-cost dispatch of a single generator meeting hourly demand.")
    print("   Perfect as a ‘starter’ modelling artifact; we can extend with RES, marginal prices, curtailment next.")


if __name__ == "__main__":
    main()
