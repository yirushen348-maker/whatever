from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple

import pandas as pd


GROUP_KEYWORDS = ["group", "treatment", "condition"]
VALUE_KEYWORDS = ["value", "intensity", "expression", "ratio", "relative expression"]
SAMPLE_KEYWORDS = ["sample", "replicate", "mouse", "patient", "subject", "clone", "id"]
WIDE_SAMPLE_HINTS = ["sample id", "mouse id", "replicate", "subject", "patient", "clone"]


@dataclass
class InferenceResult:
    format_type: str
    group_column: Optional[str]
    value_column: Optional[str]
    sample_id_column: Optional[str]
    paired: bool
    group_count: int
    recommended_methods: List[str]
    confidence: str



def _normalize(name: str) -> str:
    return name.strip().lower()



def _match_column(columns: List[str], keywords: List[str]) -> Optional[str]:
    normalized = [(_normalize(c), c) for c in columns]
    for keyword in keywords:
        for ncol, raw in normalized:
            if keyword in ncol:
                return raw
    return None



def _numeric_columns(df: pd.DataFrame) -> List[str]:
    cols: List[str] = []
    for col in df.columns:
        if pd.api.types.is_numeric_dtype(df[col]):
            cols.append(col)
    return cols



def detect_format(df: pd.DataFrame) -> str:
    numeric_cols = _numeric_columns(df)
    if len(numeric_cols) >= max(2, int(len(df.columns) * 0.6)):
        return "wide"
    return "long"



def infer_wide(df: pd.DataFrame) -> Tuple[Optional[str], Optional[str], Optional[str], bool, int, str]:
    columns = list(df.columns)

    sample_col = columns[0] if columns else None
    if sample_col and _normalize(sample_col) not in WIDE_SAMPLE_HINTS:
        hint = _match_column([sample_col], WIDE_SAMPLE_HINTS)
        if hint is None and _match_column(columns, WIDE_SAMPLE_HINTS):
            sample_col = _match_column(columns, WIDE_SAMPLE_HINTS)

    numeric_cols = _numeric_columns(df)
    group_cols = [c for c in numeric_cols if c != sample_col]

    paired = False
    if group_cols:
        row_non_null = df[group_cols].notna().sum(axis=1)
        paired = bool((row_non_null >= 2).any())

    group_count = len(group_cols)
    confidence = "High" if sample_col and group_count >= 2 else "Medium"

    # wide format does not need group/value columns explicitly
    return None, None, sample_col, paired, group_count, confidence



def infer_long(df: pd.DataFrame) -> Tuple[Optional[str], Optional[str], Optional[str], bool, int, str]:
    columns = list(df.columns)
    group_col = _match_column(columns, GROUP_KEYWORDS)
    value_col = _match_column(columns, VALUE_KEYWORDS)
    sample_col = _match_column(columns, SAMPLE_KEYWORDS)

    if value_col is None:
        numeric_cols = _numeric_columns(df)
        value_col = numeric_cols[0] if numeric_cols else None

    paired = False
    group_count = 0
    if group_col and sample_col:
        group_count = int(df[group_col].nunique(dropna=True))
        link = df[[sample_col, group_col]].dropna().drop_duplicates()
        grp_per_sample = link.groupby(sample_col)[group_col].nunique()
        paired = bool((grp_per_sample > 1).any())

    confidence_hits = sum(v is not None for v in [group_col, value_col, sample_col])
    confidence = "High" if confidence_hits == 3 else "Medium" if confidence_hits == 2 else "Low"

    return group_col, value_col, sample_col, paired, group_count, confidence



def recommend_methods(group_count: int, paired: bool) -> List[str]:
    if group_count <= 2:
        if paired:
            return ["paired t-test", "Wilcoxon signed-rank test"]
        return ["unpaired t-test", "Mann–Whitney U test"]

    if paired:
        return ["repeated-measures ANOVA", "Friedman test"]
    return ["one-way ANOVA", "Kruskal–Wallis test"]



def infer_from_file(path: str) -> InferenceResult:
    if path.lower().endswith(".csv"):
        df = pd.read_csv(path)
    else:
        df = pd.read_excel(path)

    fmt = detect_format(df)
    if fmt == "wide":
        group_col, value_col, sample_col, paired, group_count, confidence = infer_wide(df)
    else:
        group_col, value_col, sample_col, paired, group_count, confidence = infer_long(df)

    methods = recommend_methods(group_count, paired)

    return InferenceResult(
        format_type=fmt,
        group_column=group_col,
        value_column=value_col,
        sample_id_column=sample_col,
        paired=paired,
        group_count=group_count,
        recommended_methods=methods,
        confidence=confidence,
    )
