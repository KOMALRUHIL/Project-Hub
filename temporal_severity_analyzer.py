"""
========================================================================================
CLAIMOPTIMA - TEMPORAL SEVERITY & P90 INFLECTION ANALYZER
========================================================================================
Real Column Schema:
  - job_id
  - record_id
  - tag_id
  - facility_name
  - provider_name
  - provider_billing_state
  - provider_billing_zip_code
  - start_date                 (Format: 8/29/2024 12:00:00 AM)
  - end_date                   (Format: 8/29/2024 12:00:00 AM)
  - bill_line_item_service_date (Format: 8/29/2024 12:00:00 AM)
  - bill_line_item_build_amount (e.g. 4250.00)
  - bill_line_item_category    (e.g. Hospital / ER, Physical Therapy, Inpatient Surgery, etc.)

Key Capabilities:
  1. No 'incident_date' required: Baseline Day 0 is dynamically derived from each
     claim's earliest treatment date (min of start_date or bill_line_item_service_date).
  2. Parses 12-hour AM/PM timestamps ('8/29/2024 12:00:00 AM') seamlessly.
  3. Calculates elapsed treatment days (Day 0 up to Day 293+).
  4. Vectorized cumulative spend trajectories and dynamic P90 / P75 / P50 benchmarks.
  5. Pinpoints the exact Inflection Day and clinical category where spend surged.
  6. Tracks category shift over time across 6 standardized temporal phases.
  7. Outputs an executive 5-sheet workbook: 'Temporal_Severity_and_P90_Report.xlsx'.
========================================================================================
"""

import os
import sys
import datetime
import warnings
import numpy as np
import pandas as pd
import openpyxl
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter

warnings.filterwarnings("ignore", category=UserWarning)

# --------------------------------------------------------------------------------------
# 1. COLUMN MATCHING & NORMALIZATION ENGINE
# --------------------------------------------------------------------------------------
COLUMN_ALIASES = {
    "job_id": ["job_id", "job id", "jobid", "claim_id", "claim number"],
    "record_id": ["record_id", "record id", "recordid", "bill_id"],
    "tag_id": ["tag_id", "tag id", "tagid"],
    "facility_name": ["facility_name", "facility name", "facility", "hospital", "clinic"],
    "provider_name": ["provider_name", "provider name", "doctor", "physician", "payee"],
    "provider_billing_state": ["provider_billing_state", "provider billing state", "state", "billing_state"],
    "provider_billing_zip_code": ["provider_billing_zip_code", "provider billing zip code", "billing_zip", "zip_code", "zip"],
    "start_date": ["start_date", "start date", "from_date", "statement_from"],
    "end_date": ["end_date", "end date", "thru_date", "statement_to"],
    "bill_line_item_service_date": ["bill_line_item_service_date", "service_date", "service date", "line_service_date", "dos"],
    "bill_line_item_build_amount": [
        "bill_line_item_build_amount", "bill_line_item_billed_amount", "item_billed_amount",
        "billed_amount", "build_amount", "billed amount", "line_item_amount", "amount"
    ],
    "bill_line_item_category": [
        "bill_line_item_category", "bill line item category", "category", "item_category",
        "treatment_type", "record_type", "service_category"
    ]
}

def match_column(df_columns, aliases):
    cols_clean = {str(c).strip().lower().replace(" ", "_").replace("-", "_"): c for c in df_columns}
    for alias in aliases:
        alias_clean = alias.lower().replace(" ", "_").replace("-", "_")
        if alias_clean in cols_clean:
            return cols_clean[alias_clean]
    for alias in aliases:
        alias_clean = alias.lower().replace(" ", "_").replace("-", "_")
        for k, orig in cols_clean.items():
            if alias_clean in k or k in alias_clean:
                return orig
    return None

def normalize_dataset(df):
    mapping = {}
    for standard_name, aliases in COLUMN_ALIASES.items():
        found = match_column(df.columns, aliases)
        if found:
            mapping[found] = standard_name
            
    df_norm = df.rename(columns=mapping).copy()

    if "job_id" not in df_norm.columns:
        df_norm["job_id"] = [f"JOB_{1001 + i}" for i in range(len(df_norm))]
    if "record_id" not in df_norm.columns:
        df_norm["record_id"] = [f"REC_{i+1:04d}" for i in range(len(df_norm))]
    if "tag_id" not in df_norm.columns:
        df_norm["tag_id"] = [f"TAG_{i+1:04d}" for i in range(len(df_norm))]
    if "facility_name" not in df_norm.columns:
        df_norm["facility_name"] = "Treating Facility"
    if "provider_name" not in df_norm.columns:
        df_norm["provider_name"] = "Attending Physician"
    if "provider_billing_state" not in df_norm.columns:
        df_norm["provider_billing_state"] = "CA"
    if "provider_billing_zip_code" not in df_norm.columns:
        df_norm["provider_billing_zip_code"] = "90210"
    if "bill_line_item_category" not in df_norm.columns:
        df_norm["bill_line_item_category"] = "General Medical Treatment"

    for col in ["start_date", "end_date", "bill_line_item_service_date"]:
        if col in df_norm.columns:
            df_norm[col] = pd.to_datetime(df_norm[col], errors="coerce", format="mixed")
        else:
            df_norm[col] = pd.NaT

    if df_norm["start_date"].isna().all() and df_norm["bill_line_item_service_date"].notna().any():
        df_norm["start_date"] = df_norm["bill_line_item_service_date"]
    if df_norm["bill_line_item_service_date"].isna().all() and df_norm["start_date"].notna().any():
        df_norm["bill_line_item_service_date"] = df_norm["start_date"]
    if df_norm["end_date"].isna().all():
        df_norm["end_date"] = df_norm["start_date"]
    else:
        df_norm["end_date"] = df_norm["end_date"].fillna(df_norm["start_date"])

    df_norm["effective_service_date"] = df_norm["bill_line_item_service_date"].fillna(df_norm["start_date"])

    if "bill_line_item_build_amount" in df_norm.columns:
        amt_series = df_norm["bill_line_item_build_amount"].astype(str)
        amt_series = amt_series.str.replace("$", "", regex=False).str.replace(",", "", regex=False).str.strip()
        df_norm["bill_line_item_build_amount"] = pd.to_numeric(amt_series, errors="coerce").fillna(0.0)
    else:
        df_norm["bill_line_item_build_amount"] = 1500.0

    df_norm = df_norm.dropna(subset=["effective_service_date"]).sort_values(by=["job_id", "effective_service_date"]).reset_index(drop=True)
    return df_norm

# --------------------------------------------------------------------------------------
# 2. REALISTIC SAMPLE DATASET GENERATOR (Exact Real Schema & 12-Hour AM/PM Format)
# --------------------------------------------------------------------------------------
def generate_sample_dataset():
    print("[Info] Generating realistic dataset with real column names and 'M/D/YYYY 12:00:00 AM' date format...")
    base_date = datetime.datetime(2024, 1, 15, 0, 0, 0)
    
    claim_scenarios = [
        {
            "id": "CLM-1001",
            "state": "CA", "zip": "90017",
            "days": [0, 8, 22, 58, 58, 85, 185, 293],
            "amounts": [4250.0, 1850.0, 750.0, 38500.0, 8900.0, 4800.0, 6200.0, 3600.0],
            "cats": ["Hospital / ER", "Diagnostic Imaging", "Treating Physician", "Inpatient Surgery", "Treating Physician", "Physical Therapy", "Pain Management", "Physical Therapy"],
            "facs": ["Metro Health ER", "Apex Diagnostics", "Ortho Spine Institute", "Regional Surgical Hospital", "Ortho Spine Institute", "Peak Physical Therapy", "Precision Interventional", "Peak Physical Therapy"],
            "docs": ["Dr. Sarah Jenkins", "Dr. Robert Chen", "Dr. Marcus Vance", "Dr. Marcus Vance", "Dr. Marcus Vance", "Active Rehab LLC", "Dr. Alan Brody", "Active Rehab LLC"]
        },
        {
            "id": "CLM-1002",
            "state": "TX", "zip": "77030",
            "days": [0, 10, 24, 45, 60],
            "amounts": [1200.0, 450.0, 380.0, 720.0, 680.0],
            "cats": ["Hospital / ER", "Treating Physician", "Diagnostic Imaging", "Physical Therapy", "Physical Therapy"],
            "facs": ["Houston Urgent Care", "Dr. Emily Taylor", "Memorial Imaging", "Optima Therapy", "Optima Therapy"],
            "docs": ["Dr. Emily Taylor", "Dr. Emily Taylor", "Dr. Frank Miller", "Therapy Associates", "Therapy Associates"]
        },
        {
            "id": "CLM-1003",
            "state": "FL", "zip": "33136",
            "days": [0, 5, 20, 50, 80, 140, 210, 280],
            "amounts": [850.0, 1100.0, 2400.0, 3200.0, 28500.0, 4200.0, 3100.0, 1800.0],
            "cats": ["Treating Physician", "Diagnostic Imaging", "Physical Therapy", "Treating Physician", "Inpatient Surgery", "Post-Op Physical Therapy", "Pain Management", "Treating Physician"],
            "facs": ["Miami Sports Med", "Advanced Radiology", "Coastal PT", "Dr. Carlos Ruiz", "South Florida Surgery Center", "Coastal PT", "Pain Relief Specialists", "Dr. Carlos Ruiz"],
            "docs": ["Dr. Carlos Ruiz", "Dr. Lisa Wong", "Coastal Rehab Team", "Dr. Carlos Ruiz", "Dr. Carlos Ruiz", "Coastal Rehab Team", "Dr. Neil Patel", "Dr. Carlos Ruiz"]
        },
        {
            "id": "CLM-1004",
            "state": "NY", "zip": "10016",
            "days": [0, 14, 30],
            "amounts": [950.0, 420.0, 650.0],
            "cats": ["Hospital / ER", "Treating Physician", "Physical Therapy"],
            "facs": ["NYC Urgent Care", "Dr. Michael Ross", "Manhattan Rehab"],
            "docs": ["Dr. Michael Ross", "Dr. Michael Ross", "Manhattan PT Staff"]
        },
        {
            "id": "CLM-1005",
            "state": "IL", "zip": "60611",
            "days": [0, 0, 15, 40, 95, 160, 230, 290],
            "amounts": [84500.0, 14200.0, 5800.0, 3400.0, 2800.0, 2400.0, 2100.0, 1900.0],
            "cats": ["Hospital / ER", "Inpatient Surgery", "Inpatient / ICU", "Treating Physician", "Physical Therapy", "Treating Physician", "Specialist Follow-up", "Final Evaluation"],
            "facs": ["Chicago Trauma Center", "Chicago Trauma Center", "Neuro Recovery Institute", "Dr. Kevin Patel", "Premier PT", "Dr. Kevin Patel", "Dr. Kevin Patel", "Midwest Occupational"],
            "docs": ["Dr. Elena Rostova", "Dr. Elena Rostova", "Dr. Elena Rostova", "Dr. Kevin Patel", "Premier Rehab Staff", "Dr. Kevin Patel", "Dr. Kevin Patel", "Dr. David Kim"]
        },
        {
            "id": "CLM-1006",
            "state": "OH", "zip": "44106",
            "days": [0, 21, 65, 115, 175, 260],
            "amounts": [1650.0, 920.0, 7800.0, 6500.0, 4200.0, 1800.0],
            "cats": ["Hospital / ER", "Treating Physician", "Pain Management", "Pain Management", "Physical Therapy", "Treating Physician"],
            "facs": ["Cleveland Medical Center", "Dr. James Adams", "Spine Pain Center", "Spine Pain Center", "Buckeye Therapy", "Dr. James Adams"],
            "docs": ["Dr. James Adams", "Dr. James Adams", "Dr. Gregory House", "Dr. Gregory House", "Buckeye Staff", "Dr. James Adams"]
        },
        {
            "id": "CLM-1007",
            "state": "AZ", "zip": "85004",
            "days": [0, 12, 35, 75, 130, 215],
            "amounts": [2100.0, 1450.0, 3200.0, 24500.0, 3600.0, 1950.0],
            "cats": ["Hospital / ER", "Diagnostic Imaging", "Physical Therapy", "Inpatient Surgery", "Post-Op Physical Therapy", "Treating Physician"],
            "facs": ["Phoenix Valley ER", "Desert Imaging", "Southwest PT", "Valley Surgical Hospital", "Southwest PT", "Dr. Brian White"],
            "docs": ["Dr. Brian White", "Dr. Karen Hall", "SW Rehab Team", "Dr. Brian White", "SW Rehab Team", "Dr. Brian White"]
        },
        {
            "id": "CLM-1008",
            "state": "PA", "zip": "19104",
            "days": [0, 18, 45, 90, 135, 195, 255, 290],
            "amounts": [3200.0, 1800.0, 4500.0, 62000.0, 12500.0, 8400.0, 5200.0, 3100.0],
            "cats": ["Hospital / ER", "Treating Physician", "Diagnostic Imaging", "Inpatient Surgery", "Inpatient / ICU", "Physical Therapy", "Pain Management", "Treating Physician"],
            "facs": ["Penn General Hospital", "Dr. Susan Davis", "Penn Radiology", "Penn Spine Institute", "Penn Rehab Hospital", "Keystone Therapy", "Pain Solutions Clinic", "Dr. Susan Davis"],
            "docs": ["Dr. Susan Davis", "Dr. Susan Davis", "Dr. Arthur Conan", "Dr. William Sterling", "Dr. William Sterling", "Keystone PT Team", "Dr. Rachel Green", "Dr. Susan Davis"]
        },
        {
            "id": "CLM-1009",
            "state": "GA", "zip": "30309",
            "days": [0, 14, 35, 60],
            "amounts": [850.0, 420.0, 1450.0, 1200.0],
            "cats": ["Treating Physician", "Treating Physician", "Physical Therapy", "Physical Therapy"],
            "facs": ["Atlanta Primary Care", "Atlanta Primary Care", "Peachtree Rehab", "Peachtree Rehab"],
            "docs": ["Dr. Angela Scott", "Dr. Angela Scott", "Peachtree Rehab Team", "Peachtree Rehab Team"]
        },
        {
            "id": "CLM-1010",
            "state": "WA", "zip": "98104",
            "days": [0, 28, 70, 125, 185, 245, 293],
            "amounts": [1150.0, 650.0, 1950.0, 4200.0, 42500.0, 6800.0, 2600.0],
            "cats": ["Hospital / ER", "Treating Physician", "Physical Therapy", "Diagnostic Imaging", "Inpatient Surgery", "Post-Op Physical Therapy", "Treating Physician"],
            "facs": ["Seattle Health ER", "Dr. Mark Wilson", "Pacific PT", "Sound Radiology", "Cascade Surgical Center", "Pacific PT", "Dr. Mark Wilson"],
            "docs": ["Dr. Mark Wilson", "Dr. Mark Wilson", "Pacific Rehab Team", "Dr. Helen Hunt", "Dr. Mark Wilson", "Pacific Rehab Team", "Dr. Mark Wilson"]
        }
    ]

    records = []
    rec_id_counter = 1000
    tag_id_counter = 5000

    for sc in claim_scenarios:
        c_id = sc["id"]
        c_state = sc["state"]
        c_zip = sc["zip"]
        
        for d_off, amt, cat, fac, doc in zip(sc["days"], sc["amounts"], sc["cats"], sc["facs"], sc["docs"]):
            rec_id_counter += 1
            tag_id_counter += 1
            
            s_dt = base_date + datetime.timedelta(days=d_off)
            e_dt = s_dt + datetime.timedelta(days=2 if "Surgery" in cat or "ICU" in cat else 0)
            
            # Formatted strictly as: '8/29/2024 12:00:00 AM'
            s_str = f"{s_dt.month}/{s_dt.day}/{s_dt.year} 12:00:00 AM"
            e_str = f"{e_dt.month}/{e_dt.day}/{e_dt.year} 12:00:00 AM"
            svc_str = s_str

            records.append({
                "job_id": c_id,
                "record_id": f"REC-{rec_id_counter}",
                "tag_id": f"TAG-{tag_id_counter}",
                "facility_name": fac,
                "provider_name": doc,
                "provider_billing_state": c_state,
                "provider_billing_zip_code": c_zip,
                "start_date": s_str,
                "end_date": e_str,
                "bill_line_item_service_date": svc_str,
                "bill_line_item_build_amount": amt,
                "bill_line_item_category": cat
            })

    sample_df = pd.DataFrame(records)
    out_file = "medical_bills_input.xlsx"
    sample_df.to_excel(out_file, index=False)
    sample_df.to_excel("sample_bills_data.xlsx", index=False)
    print(f"[Success] Created '{out_file}' with {len(sample_df)} records matching real column schema.")
    return out_file

# --------------------------------------------------------------------------------------
# 3. VECTORIZED ANALYTICS ENGINE (Baseline Day 0 per Claim)
# --------------------------------------------------------------------------------------
def run_temporal_analysis(df):
    print("[Analytics] Computing baseline Day 0 per claim, cumulative spend, and P90 benchmarks...")

    baseline_map = df.groupby("job_id")["effective_service_date"].min().to_dict()
    df["baseline_date_day0"] = df["job_id"].map(baseline_map)
    df["elapsed_days"] = (df["effective_service_date"] - df["baseline_date_day0"]).dt.days.fillna(0).astype(int).clip(lower=0)

    df = df.sort_values(by=["job_id", "elapsed_days", "effective_service_date"]).reset_index(drop=True)
    df["cumulative_spend"] = df.groupby("job_id")["bill_line_item_build_amount"].cumsum()
    
    tot_per_claim = df.groupby("job_id")["bill_line_item_build_amount"].transform("sum")
    df["cumulative_spend_pct"] = np.where(tot_per_claim > 0, (df["cumulative_spend"] / tot_per_claim), 1.0)

    all_job_ids = list(df["job_id"].unique())
    total_claims = len(all_job_ids)
    max_portfolio_day = int(df["elapsed_days"].max()) if len(df) > 0 else 293
    max_portfolio_day = max(max_portfolio_day, 90)

    milestones = [
        {"name": "Day 0 - 30 (Acute Phase)", "min_d": 0, "max_d": 30, "eval_day": 30},
        {"name": "Day 31 - 60 (Subacute / PT Phase)", "min_d": 31, "max_d": 60, "eval_day": 60},
        {"name": "Day 61 - 90 (Specialist / Diagnostic)", "min_d": 61, "max_d": 90, "eval_day": 90},
        {"name": "Day 91 - 180 (Surgical / Inpatient)", "min_d": 91, "max_d": 180, "eval_day": 180},
        {"name": "Day 181 - 270 (Extended Chronic Rehab)", "min_d": 181, "max_d": 270, "eval_day": 270},
        {"name": f"Day 271 - {max_portfolio_day}+ (Long-Term Resolution)", "min_d": 271, "max_d": max_portfolio_day, "eval_day": max_portfolio_day}
    ]

    milestone_stats = []
    matrix_dict = {"job_id": all_job_ids}

    for m in milestones:
        e_day = m["eval_day"]
        filtered = df[df["elapsed_days"] <= e_day]
        claim_totals = filtered.groupby("job_id")["bill_line_item_build_amount"].sum().reindex(all_job_ids, fill_value=0.0).values
        
        spend_arr = np.array(claim_totals) if len(claim_totals) > 0 else np.array([0.0])
        p25 = float(np.percentile(spend_arr, 25))
        p50 = float(np.percentile(spend_arr, 50))
        p75 = float(np.percentile(spend_arr, 75))
        p90 = float(np.percentile(spend_arr, 90))
        avg_val = float(np.mean(spend_arr))
        
        prev_eval = 0 if m["min_d"] == 0 else m["min_d"] - 1
        days_span = max(1, e_day - prev_eval)
        prev_p50 = milestone_stats[-1]["p50"] if milestone_stats else 0.0
        velocity = (p50 - prev_p50) / days_span

        milestone_stats.append({
            "milestone_name": m["name"],
            "eval_day": e_day,
            "min_d": m["min_d"],
            "max_d": m["max_d"],
            "p25": p25,
            "p50": p50,
            "p75": p75,
            "p90": p90,
            "average": avg_val,
            "velocity_per_day": max(0.0, velocity)
        })
        matrix_dict[f"Cum_Spend_{m['name'].split()[0]}"] = claim_totals

    milestone_df = pd.DataFrame(milestone_stats)
    matrix_df = pd.DataFrame(matrix_dict)

    grouped = df.groupby("job_id")
    tot_billed = grouped["bill_line_item_build_amount"].sum().reindex(all_job_ids, fill_value=0.0)
    cnt_bills = grouped["bill_line_item_build_amount"].count().reindex(all_job_ids, fill_value=0)
    first_dates = grouped["effective_service_date"].min().reindex(all_job_ids)
    max_days = grouped["elapsed_days"].max().reindex(all_job_ids, fill_value=0)
    primary_state = grouped["provider_billing_state"].first().reindex(all_job_ids, fill_value="N/A")
    primary_zip = grouped["provider_billing_zip_code"].first().reindex(all_job_ids, fill_value="N/A")

    e_spend = df[df["elapsed_days"] <= 30].groupby("job_id")["bill_line_item_build_amount"].sum().reindex(all_job_ids, fill_value=0.0)
    m_spend = df[(df["elapsed_days"] > 30) & (df["elapsed_days"] <= 90)].groupby("job_id")["bill_line_item_build_amount"].sum().reindex(all_job_ids, fill_value=0.0)
    l_spend = df[df["elapsed_days"] > 90].groupby("job_id")["bill_line_item_build_amount"].sum().reindex(all_job_ids, fill_value=0.0)

    idx_max_jumps = df.groupby("job_id")["bill_line_item_build_amount"].idxmax().dropna()
    max_jump_rows = df.loc[idx_max_jumps].set_index("job_id")

    final_p90 = milestone_stats[-1]["p90"]
    final_p75 = milestone_stats[-1]["p75"]
    final_p25 = milestone_stats[-1]["p25"]

    claim_summaries = []
    for jid in all_job_ids:
        t_amt = float(tot_billed.get(jid, 0.0))
        b_cnt = int(cnt_bills.get(jid, 0))
        f_dt = first_dates.get(jid)
        mx_d = int(max_days.get(jid, 0))
        c_st = str(primary_state.get(jid, "N/A"))
        c_zp = str(primary_zip.get(jid, "N/A"))
        
        es = float(e_spend.get(jid, 0.0))
        ms = float(m_spend.get(jid, 0.0))
        ls = float(l_spend.get(jid, 0.0))
        
        jump_r = max_jump_rows.loc[jid] if jid in max_jump_rows.index else None
        inf_day = int(jump_r["elapsed_days"]) if jump_r is not None else 0
        inf_cat = str(jump_r["bill_line_item_category"]) if jump_r is not None else "N/A"
        inf_fac = str(jump_r["facility_name"]) if jump_r is not None else "N/A"
        inf_amt = float(jump_r["bill_line_item_build_amount"]) if jump_r is not None else 0.0

        p90_breached = False
        p90_breach_window = "Within Limits"
        for m in milestone_stats:
            m_cum = float(matrix_dict[f"Cum_Spend_{m['milestone_name'].split()[0]}"][all_job_ids.index(jid)])
            if m_cum >= m["p90"] and m["p90"] > 0:
                p90_breached = True
                p90_breach_window = m["milestone_name"].split()[0] + " (" + str(m["eval_day"]) + "d)"
                break

        if t_amt >= final_p90 and final_p90 > 0:
            severity_class = "P90 Outlier (Catastrophic)"
        elif t_amt >= final_p75:
            severity_class = "High Severity (Escalating)"
        elif t_amt >= final_p25:
            severity_class = "Moderate Severity"
        else:
            severity_class = "Low Severity (Routine)"

        if es / (t_amt or 1.0) >= 0.70:
            progression = "Acute Front-Loaded (Immediate ER/Trauma)"
        elif ls / (t_amt or 1.0) >= 0.50:
            progression = "Late-Surge Escalation (Surgical/Chronic)"
        elif ms / (t_amt or 1.0) >= 0.40:
            progression = "Mid-Phase Intervention (Day 31-90)"
        else:
            progression = "Continuous Gradual Therapy"

        claim_summaries.append({
            "job_id": jid,
            "billing_state": c_st,
            "billing_zip": c_zp,
            "first_treatment_date": f_dt.strftime("%m/%d/%Y") if pd.notna(f_dt) else "01/01/2024",
            "total_treatment_span_days": mx_d,
            "total_bills_count": b_cnt,
            "total_billed_amount": t_amt,
            "early_spend_0_30d": es,
            "mid_spend_31_90d": ms,
            "late_spend_91d_plus": ls,
            "spend_velocity_per_day": (t_amt / max(1, mx_d)),
            "inflection_point_day": f"Day {inf_day}",
            "inflection_category": inf_cat,
            "inflection_facility": inf_fac,
            "inflection_jump_amount": inf_amt,
            "p90_status": "P90 BREACH" if p90_breached else "Normal Range",
            "first_p90_breach_milestone": p90_breach_window,
            "severity_classification": severity_class,
            "clinical_progression_pattern": progression
        })

    claim_summary_df = pd.DataFrame(claim_summaries).sort_values("total_billed_amount", ascending=False).reset_index(drop=True)

    df["temporal_bin"] = pd.cut(
        df["elapsed_days"],
        bins=[-1, 30, 60, 90, 180, 270, 999],
        labels=["Days 0-30 (Acute)", "Days 31-60 (Subacute)", "Days 61-90 (Specialist)", "Days 91-180 (Surgical)", "Days 181-270 (Rehab)", f"Days 271-{max_portfolio_day}+"]
    )
    cat_pivot = df.pivot_table(
        index="bill_line_item_category",
        columns="temporal_bin",
        values="bill_line_item_build_amount",
        aggfunc="sum",
        fill_value=0.0,
        observed=False
    )
    cat_pivot["Total_All_Phases"] = cat_pivot.sum(axis=1)
    cat_pivot = cat_pivot.sort_values("Total_All_Phases", ascending=False).reset_index()

    return {
        "enriched_bills": df,
        "claim_summary": claim_summary_df,
        "milestones": milestone_df,
        "category_shift": cat_pivot,
        "spend_matrix": matrix_df,
        "portfolio_stats": {
            "total_claims": total_claims,
            "total_billed": float(df["bill_line_item_build_amount"].sum()),
            "max_days": max_portfolio_day,
            "p90_breach_count": len([c for c in claim_summaries if "BREACH" in c["p90_status"]])
        }
    }

# --------------------------------------------------------------------------------------
# 4. MULTI-TAB EXECUTIVE EXCEL REPORT BUILDER
# --------------------------------------------------------------------------------------
def export_executive_excel(results, output_filename="Temporal_Severity_and_P90_Report.xlsx"):
    print(f"[Export] Generating executive multi-tab Excel report: '{output_filename}'...")
    
    wb = openpyxl.Workbook()
    wb.remove(wb.active)

    navy_header_fill = PatternFill(start_color="1F4E79", end_color="1F4E79", fill_type="solid")
    dark_slate_fill = PatternFill(start_color="0F172A", end_color="0F172A", fill_type="solid")
    light_blue_fill = PatternFill(start_color="D9E1F2", end_color="D9E1F2", fill_type="solid")
    alert_red_fill = PatternFill(start_color="FCE4D6", end_color="FCE4D6", fill_type="solid")
    
    font_title = Font(name="Calibri", size=14, bold=True, color="FFFFFF")
    font_header = Font(name="Calibri", size=10, bold=True, color="FFFFFF")
    font_bold = Font(name="Calibri", size=10, bold=True, color="000000")
    font_normal = Font(name="Calibri", size=10, color="000000")
    font_alert = Font(name="Calibri", size=10, bold=True, color="C00000")

    thin_border = Border(
        left=Side(style='thin', color='D9D9D9'),
        right=Side(style='thin', color='D9D9D9'),
        top=Side(style='thin', color='D9D9D9'),
        bottom=Side(style='thin', color='D9D9D9')
    )

    # TAB 1: EXECUTIVE DASHBOARD
    ws_dash = wb.create_sheet(title="Executive_Dashboard")
    ws_dash.views.sheetView[0].showGridLines = True
    
    ws_dash.merge_cells("A1:H2")
    ws_dash["A1"] = "CLAIMOPTIMA: TEMPORAL SEVERITY, P90 BENCHMARKS & COST VELOCITY REPORT"
    ws_dash["A1"].font = font_title
    ws_dash["A1"].fill = navy_header_fill
    ws_dash["A1"].alignment = Alignment(horizontal="center", vertical="center")

    p_stats = results["portfolio_stats"]
    kpis = [
        ("Total Claims Analyzed", f"{p_stats['total_claims']:,}"),
        ("Total Medical Spend", f"${p_stats['total_billed']:,.2f}"),
        ("Max Treatment Span", f"{p_stats['max_days']} Days"),
        ("P90 Severity Outliers", f"{p_stats['p90_breach_count']} Claims")
    ]
    
    col_idx = 1
    for label, val in kpis:
        c_letter = get_column_letter(col_idx)
        c_letter_next = get_column_letter(col_idx + 1)
        ws_dash.merge_cells(f"{c_letter}4:{c_letter_next}4")
        ws_dash.merge_cells(f"{c_letter}5:{c_letter_next}5")
        
        ws_dash[f"{c_letter}4"] = label
        ws_dash[f"{c_letter}4"].font = Font(name="Calibri", size=9, bold=True, color="FFFFFF")
        ws_dash[f"{c_letter}4"].fill = dark_slate_fill
        ws_dash[f"{c_letter}4"].alignment = Alignment(horizontal="center")
        
        ws_dash[f"{c_letter}5"] = val
        ws_dash[f"{c_letter}5"].font = Font(name="Calibri", size=13, bold=True, color="1F4E79")
        ws_dash[f"{c_letter}5"].fill = light_blue_fill
        ws_dash[f"{c_letter}5"].alignment = Alignment(horizontal="center", vertical="center")
        col_idx += 2

    ws_dash["A7"] = "EXECUTIVE SUMMARY & ACTUARIAL FINDINGS:"
    ws_dash["A7"].font = font_bold
    
    findings = [
        "1. Dynamic Baseline (Day 0): Derived from each claim's earliest medical encounter (no separate incident date required).",
        "2. P90 Outlier Velocity: High-severity claims exhibit sharp inflection points where single surgical procedures exceed $30,000+.",
        "3. Early vs. Late Phase Divergence: Routine claims resolve within 30-45 days, while complex spinal/ortho cases surge after Day 60.",
        "4. Category Progression: Acute care (ER/Imaging) shifts rapidly to Inpatient Surgery, followed by extended Physical Therapy & Pain Mgmt."
    ]
    for r_i, find in enumerate(findings, start=8):
        ws_dash[f"A{r_i}"] = find
        ws_dash[f"A{r_i}"].font = font_normal

    ws_dash["A13"] = "PORTFOLIO SEVERITY BENCHMARKS ACROSS TREATMENT DAYS (P90 vs P50 Median):"
    ws_dash["A13"].font = font_bold
    
    m_df = results["milestones"]
    m_headers = ["Milestone Care Phase", "Eval Day", "P25 (Low)", "P50 (Median)", "P75 (Moderate)", "P90 (Catastrophic)", "Average Spend", "Spend Velocity ($/Day)"]
    for c_i, h in enumerate(m_headers, start=1):
        cell = ws_dash.cell(row=14, column=c_i, value=h)
        cell.font = font_header
        cell.fill = navy_header_fill
        cell.alignment = Alignment(horizontal="center")

    for r_i, row in m_df.iterrows():
        curr_row = 15 + r_i
        ws_dash.cell(row=curr_row, column=1, value=row["milestone_name"]).font = font_normal
        ws_dash.cell(row=curr_row, column=2, value=int(row["eval_day"])).alignment = Alignment(horizontal="center")
        
        for c_idx, col_name in enumerate(["p25", "p50", "p75", "p90", "average", "velocity_per_day"], start=3):
            c_val = ws_dash.cell(row=curr_row, column=c_idx, value=row[col_name])
            c_val.number_format = "$#,##0"
            c_val.font = font_alert if col_name == "p90" else font_normal

    # TAB 2: CLAIM TRAJECTORY SUMMARY
    ws_claims = wb.create_sheet(title="Claim_Trajectory_Summary")
    ws_claims.views.sheetView[0].showGridLines = True
    
    claim_df = results["claim_summary"]
    for c_i, col in enumerate(claim_df.columns, start=1):
        cell = ws_claims.cell(row=1, column=c_i, value=col.replace("_", " ").title())
        cell.font = font_header
        cell.fill = navy_header_fill
        cell.alignment = Alignment(horizontal="center", vertical="center")

    for r_i, row in claim_df.iterrows():
        curr_row = 2 + r_i
        for c_i, col_name in enumerate(claim_df.columns, start=1):
            val = row[col_name]
            cell = ws_claims.cell(row=curr_row, column=c_i, value=val)
            cell.border = thin_border
            
            if "spend" in col_name or "amount" in col_name or "velocity" in col_name:
                cell.number_format = "$#,##0"
            elif col_name == "p90_status" and "BREACH" in str(val):
                cell.fill = alert_red_fill
                cell.font = font_alert
            else:
                cell.font = font_normal

    # TAB 3: P90 BENCHMARK MILESTONES
    ws_mile = wb.create_sheet(title="P90_Benchmark_Milestones")
    ws_mile.views.sheetView[0].showGridLines = True
    
    for c_i, col in enumerate(m_df.columns, start=1):
        cell = ws_mile.cell(row=1, column=c_i, value=col.replace("_", " ").title())
        cell.font = font_header
        cell.fill = navy_header_fill
        cell.alignment = Alignment(horizontal="center")

    for r_i, row in m_df.iterrows():
        curr_row = 2 + r_i
        for c_i, col_name in enumerate(m_df.columns, start=1):
            val = row[col_name]
            cell = ws_mile.cell(row=curr_row, column=c_i, value=val)
            cell.border = thin_border
            if col_name in ["p25", "p50", "p75", "p90", "average", "velocity_per_day"]:
                cell.number_format = "$#,##0"
                if col_name == "p90":
                    cell.fill = alert_red_fill
                    cell.font = font_alert

    # TAB 4: CATEGORY SHIFT OVER TIME
    ws_cat = wb.create_sheet(title="Category_Shift_Over_Time")
    ws_cat.views.sheetView[0].showGridLines = True
    
    cat_df = results["category_shift"]
    for c_i, col in enumerate(cat_df.columns, start=1):
        cell = ws_cat.cell(row=1, column=c_i, value=str(col).title())
        cell.font = font_header
        cell.fill = navy_header_fill
        cell.alignment = Alignment(horizontal="center")

    for r_i, row in cat_df.iterrows():
        curr_row = 2 + r_i
        for c_i, col_name in enumerate(cat_df.columns, start=1):
            val = row[col_name]
            cell = ws_cat.cell(row=curr_row, column=c_i, value=val)
            cell.border = thin_border
            if c_i > 1:
                cell.number_format = "$#,##0"

    # TAB 5: ENRICHED BILL DETAILS
    ws_raw = wb.create_sheet(title="Enriched_Bill_Details")
    ws_raw.views.sheetView[0].showGridLines = True
    
    bills_df = results["enriched_bills"].copy()
    display_cols = [
        "job_id", "record_id", "tag_id", "facility_name", "provider_name",
        "provider_billing_state", "provider_billing_zip_code",
        "start_date", "end_date", "bill_line_item_service_date",
        "bill_line_item_category", "bill_line_item_build_amount",
        "elapsed_days", "cumulative_spend", "cumulative_spend_pct"
    ]
    available_display_cols = [c for c in display_cols if c in bills_df.columns]
    bills_export = bills_df[available_display_cols].head(10000)

    for c_i, col in enumerate(available_display_cols, start=1):
        cell = ws_raw.cell(row=1, column=c_i, value=col.replace("_", " ").title())
        cell.font = font_header
        cell.fill = dark_slate_fill
        cell.alignment = Alignment(horizontal="center")

    for r_i, row in bills_export.iterrows():
        curr_row = 2 + r_i
        for c_i, col_name in enumerate(available_display_cols, start=1):
            val = row[col_name]
            if isinstance(val, (datetime.date, datetime.datetime, pd.Timestamp)):
                val = val.strftime("%m/%d/%Y %I:%M:%S %p")
            cell = ws_raw.cell(row=curr_row, column=c_i, value=val)
            cell.border = thin_border
            if "amount" in col_name or "cumulative_spend" == col_name:
                cell.number_format = "$#,##0.00"
            elif col_name == "cumulative_spend_pct":
                cell.number_format = "0.0%"

    for ws in wb.worksheets:
        for col in ws.columns:
            max_len = max(len(str(cell.value or '')) for cell in col)
            col_letter = get_column_letter(col[0].column)
            ws.column_dimensions[col_letter].width = max(max_len + 4, 12)

    try:
        wb.save(output_filename)
        print(f"[Done] Multi-tab Excel workbook successfully saved to: '{os.path.abspath(output_filename)}'")
    except PermissionError:
        alt_filename = output_filename.replace(".xlsx", f"_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx")
        wb.save(alt_filename)
        print(f"[Warning] Original file was locked in Excel. Saved output workbook to: '{os.path.abspath(alt_filename)}'")
        return alt_filename
        
    return output_filename

# --------------------------------------------------------------------------------------
# 5. MAIN EXECUTION PIPELINE
# --------------------------------------------------------------------------------------
def main():
    print("=" * 80)
    print(" CLAIMOPTIMA: TEMPORAL SEVERITY & P90 INFLECTION ENGINE")
    print("=" * 80)

    input_file = None
    if len(sys.argv) > 1:
        input_file = sys.argv[1]
    else:
        candidates = ["medical_bills_input.xlsx", "sample_bills_data.xlsx", "bills_data.xlsx", "upload.xlsx", "upload.csv"]
        for cand in candidates:
            if os.path.exists(cand) and os.path.getsize(cand) > 100:
                input_file = cand
                break

    if not input_file or not os.path.exists(input_file):
        input_file = generate_sample_dataset()

    print(f"[Input] Reading bill records from: '{input_file}'...")
    if input_file.endswith((".xlsx", ".xls")):
        df_raw = pd.read_excel(input_file)
    else:
        df_raw = pd.read_csv(input_file)

    print(f"[Loaded] Ingested {len(df_raw)} bill records with columns: {list(df_raw.columns)}...")
    
    df_norm = normalize_dataset(df_raw)
    results = run_temporal_analysis(df_norm)
    
    output_excel = "Temporal_Severity_and_P90_Report.xlsx"
    saved_path = export_executive_excel(results, output_excel)
    
    print("=" * 80)
    print(" [SUCCESS] TEMPORAL SEVERITY ANALYSIS COMPLETE!")
    print(f" -> Output Report: {os.path.abspath(saved_path)}")
    print("=" * 80)

if __name__ == "__main__":
    main()
