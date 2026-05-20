#!/usr/bin/env python3
"""Plot radiosonde BUFR tank receipt latency using nceplibs-bufr."""

from __future__ import annotations

import argparse
from dataclasses import dataclass
from datetime import datetime
import os
import sys
from typing import Iterable


@dataclass
class LatencyRecord:
    valid_time: datetime
    receipt_time: datetime
    latency_minutes: float


def parse_yyyymmddhhmm(value: int) -> datetime | None:
    """Convert YYYYMMDDHHMM integer time to datetime."""
    if value is None or value < 0:
        return None
    text = str(int(value)).zfill(12)
    return datetime.strptime(text, "%Y%m%d%H%M")


def _to_int(value) -> int | None:
    """Best-effort conversion for values returned by nceplibs-bufr."""
    if value is None:
        return None
    if hasattr(value, "mask") and bool(getattr(value, "mask", False)):
        return None
    try:
        return int(value)
    except (TypeError, ValueError):
        return None


def parse_valid_time(time_values) -> datetime | None:
    """Parse YEAR/MNTH/DAYS/HOUR/MINU values into datetime."""
    flattened = []
    for value in getattr(time_values, "flat", time_values):
        parsed = _to_int(value)
        if parsed is not None:
            flattened.append(parsed)
        if len(flattened) == 5:
            break

    if len(flattened) < 5:
        return None

    year, month, day, hour, minute = flattened
    try:
        return datetime(year, month, day, hour, minute)
    except ValueError:
        return None


def collect_latencies(bufr_path: str, message_type_filter: str = "") -> list[LatencyRecord]:
    """Read BUFR and compute latency from report valid time to tank receipt time."""
    if not os.path.isfile(bufr_path):
        raise FileNotFoundError(f"BUFR file not found: {bufr_path}")

    try:
        import ncepbufr
    except ModuleNotFoundError as exc:
        raise ModuleNotFoundError(
            "nceplibs-bufr Python API is required. Install the package that provides "
            "the 'ncepbufr' module."
        ) from exc

    records: list[LatencyRecord] = []
    bufr = ncepbufr.open(bufr_path)
    try:
        while bufr.advance() == 0:
            if message_type_filter and message_type_filter not in (bufr.msg_type or ""):
                continue

            receipt_time = parse_yyyymmddhhmm(bufr.receipt_time)
            if receipt_time is None:
                continue

            while bufr.load_subset() == 0:
                valid_time = parse_valid_time(bufr.read_subset("YEAR MNTH DAYS HOUR MINU"))
                if valid_time is None:
                    continue

                latency_minutes = (receipt_time - valid_time).total_seconds() / 60.0
                records.append(
                    LatencyRecord(
                        valid_time=valid_time,
                        receipt_time=receipt_time,
                        latency_minutes=latency_minutes,
                    )
                )
    finally:
        bufr.close()

    return records


def plot_latencies(records: Iterable[LatencyRecord], output_path: str, title: str) -> None:
    """Create scatter plot of latency minutes vs radiosonde valid time."""
    import matplotlib.pyplot as plt

    data = list(records)
    if not data:
        raise ValueError("No latency records available for plotting.")

    x_values = [record.valid_time for record in data]
    y_values = [record.latency_minutes for record in data]

    fig, ax = plt.subplots(figsize=(10, 5))
    ax.scatter(x_values, y_values, s=8, alpha=0.6)
    ax.set_title(title)
    ax.set_xlabel("Radiosonde report valid time (UTC)")
    ax.set_ylabel("Tank receipt latency (minutes)")
    ax.grid(True, linestyle="--", alpha=0.4)
    fig.autofmt_xdate()
    fig.tight_layout()
    fig.savefig(output_path, dpi=150)


def build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Plot radiosonde BUFR latency between report valid time and BUFR tank "
            "receipt time (from rtrcpt via nceplibs-bufr)."
        )
    )
    parser.add_argument("bufr_file", help="Path to BUFR file containing radiosonde reports")
    parser.add_argument(
        "--output",
        default="radiosonde_latency.png",
        help="Output image path (default: radiosonde_latency.png)",
    )
    parser.add_argument(
        "--message-type-filter",
        default="",
        help="Optional substring filter for BUFR message type (e.g. ADPUPA)",
    )
    parser.add_argument(
        "--cutoff-minutes",
        type=float,
        default=None,
        help="Optional data assimilation cutoff in minutes for summary statistics",
    )
    parser.add_argument(
        "--title",
        default="Radiosonde BUFR Tank Receipt Latency",
        help="Plot title",
    )
    return parser


def main() -> int:
    args = build_arg_parser().parse_args()
    try:
        records = collect_latencies(args.bufr_file, args.message_type_filter)
        plot_latencies(records, args.output, args.title)
    except Exception as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1

    print(f"Plotted {len(records)} latency records to {args.output}")

    if args.cutoff_minutes is not None:
        within_cutoff = sum(record.latency_minutes <= args.cutoff_minutes for record in records)
        fraction = within_cutoff / len(records)
        print(
            f"Records within {args.cutoff_minutes:.1f} minute cutoff: "
            f"{within_cutoff}/{len(records)} ({fraction:.1%})"
        )

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
