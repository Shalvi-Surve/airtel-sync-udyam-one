"""Create the public, deterministic analytics demo dataset.

This generator uses only hard-coded synthetic cohorts. It never reads the
Git-ignored local smb_leads.csv or any customer/lead source file.
"""
import csv
import random
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "data" / "analytics" / "synthetic_demo_leads.csv"
SEED = 20261109
SEGMENTS = [
    ("Micro retail & services", 2710, 111),
    ("Professional services", 1000, 120),
    ("Multi-location businesses", 800, 80),
    ("Manufacturing", 490, 57),
]
FIELDS = [
    "dataset_label", "segment", "city_tier", "outcome",
    "days_lead_to_activation", "churned_within_6_months",
    "stage_reached", "has_gstin", "drop_reason",
]


def generate_rows():
    rng = random.Random(SEED)
    rows = []
    for segment, lead_count, activation_count in SEGMENTS:
        rows.extend({"segment": segment, "outcome": "Not activated"} for _ in range(lead_count))

    rng.shuffle(rows)
    activated_indices = set()
    for segment, _lead_count, activation_count in SEGMENTS:
        indexes = [i for i, row in enumerate(rows) if row["segment"] == segment]
        activated_indices.update(rng.sample(indexes, activation_count))

    activation_statuses = ["Y"] * 336 + ["N"] * 27 + ["Unknown"] * 5
    rng.shuffle(activation_statuses)
    non_activation_statuses = ["Y"] * 3164 + ["N"] * 1323 + ["Unknown"] * 145
    rng.shuffle(non_activation_statuses)
    activated_order = list(activated_indices)
    churned = set(rng.sample(activated_order, 56))
    drop_reasons = [
        "Budget constraints", "No response", "Eligibility mismatch",
        "Competitor selected", "Installation timing", "Requirements changed",
    ]
    activation_number = 0
    non_activation_number = 0
    for index, row in enumerate(rows):
        activated = index in activated_indices
        row["dataset_label"] = "SYNTHETIC DEMO DATA — NO REAL LEAD RECORDS"
        row["city_tier"] = rng.choices([1, 2], weights=[65, 35], k=1)[0]
        row["has_gstin"] = activation_statuses[activation_number] if activated else non_activation_statuses[non_activation_number]
        if activated:
            row["outcome"] = "Activated"
            row["days_lead_to_activation"] = round(10.12 + (activation_number % 16), 2)
            row["churned_within_6_months"] = "Y" if index in churned else "N"
            row["stage_reached"] = "KYC complete"
            row["drop_reason"] = ""
            activation_number += 1
        else:
            row["days_lead_to_activation"] = ""
            row["churned_within_6_months"] = "N"
            row["stage_reached"] = rng.choices(
                ["Profile submitted", "Quote generated", "KYC started", "Not started"],
                weights=[30, 25, 15, 30], k=1,
            )[0]
            row["drop_reason"] = rng.choice(drop_reasons)
            non_activation_number += 1
    return rows


def main():
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    with OUTPUT.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=FIELDS)
        writer.writeheader()
        writer.writerows(generate_rows())
    print(f"Wrote {sum(count for _, count, _ in SEGMENTS):,} synthetic rows to {OUTPUT}")


if __name__ == "__main__":
    main()
