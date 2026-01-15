#!/usr/bin/env python3
"""
Back-of-the-Envelope Capacity Calculator for System Design

Helps estimate storage, bandwidth, and compute requirements.

Usage:
    python capacity_calculator.py [--interactive]
    python capacity_calculator.py --storage --users 1000000 --data-per-user 1MB
    python capacity_calculator.py --bandwidth --rps 10000 --response-size 10KB
    python capacity_calculator.py --qps --daily-users 1000000 --requests-per-user 10
"""

import argparse
import sys
from dataclasses import dataclass
from typing import Optional


# Unit conversions
UNITS = {
    'B': 1,
    'KB': 1024,
    'MB': 1024 ** 2,
    'GB': 1024 ** 3,
    'TB': 1024 ** 4,
    'PB': 1024 ** 5,
}


def parse_size(size_str: str) -> int:
    """Parse size string like '10MB' or '1.5GB' to bytes."""
    size_str = size_str.strip().upper()
    for unit, multiplier in sorted(UNITS.items(), key=lambda x: -len(x[0])):
        if size_str.endswith(unit):
            number = float(size_str[:-len(unit)])
            return int(number * multiplier)
    return int(size_str)


def format_size(bytes_val: float) -> str:
    """Format bytes to human-readable string."""
    for unit in ['B', 'KB', 'MB', 'GB', 'TB', 'PB']:
        if abs(bytes_val) < 1024:
            return f"{bytes_val:.2f} {unit}"
        bytes_val /= 1024
    return f"{bytes_val:.2f} PB"


def format_number(num: float) -> str:
    """Format large numbers with K, M, B suffixes."""
    for suffix in ['', 'K', 'M', 'B', 'T']:
        if abs(num) < 1000:
            return f"{num:.2f}{suffix}"
        num /= 1000
    return f"{num:.2f}T"


@dataclass
class StorageEstimate:
    users: int
    data_per_user: int
    growth_rate: float
    retention_years: int

    def calculate(self) -> dict:
        base_storage = self.users * self.data_per_user
        results = {'base_storage': base_storage, 'yearly_projections': []}
        current = base_storage
        for year in range(1, self.retention_years + 1):
            current *= self.growth_rate
            results['yearly_projections'].append({'year': year, 'storage': current})
        results['final_storage'] = current
        results['replication_3x'] = current * 3
        return results

    def print_report(self):
        results = self.calculate()
        print("\n" + "=" * 60)
        print("STORAGE CAPACITY ESTIMATE")
        print("=" * 60)
        print(f"\nInputs:")
        print(f"  Users:              {format_number(self.users)}")
        print(f"  Data per user:      {format_size(self.data_per_user)}")
        print(f"  Annual growth:      {(self.growth_rate - 1) * 100:.1f}%")
        print(f"  Retention:          {self.retention_years} years")
        print(f"\nBase Storage:         {format_size(results['base_storage'])}")
        print(f"\nYearly Projections:")
        for proj in results['yearly_projections']:
            print(f"  Year {proj['year']}:            {format_size(proj['storage'])}")
        print(f"\nWith 3x replication:  {format_size(results['replication_3x'])}")


@dataclass
class BandwidthEstimate:
    requests_per_second: int
    request_size: int
    response_size: int
    peak_multiplier: float

    def calculate(self) -> dict:
        incoming_bps = self.requests_per_second * self.request_size
        outgoing_bps = self.requests_per_second * self.response_size
        total_bps = incoming_bps + outgoing_bps
        return {
            'total_bps': total_bps,
            'peak_total': total_bps * self.peak_multiplier,
            'daily_transfer': total_bps * 86400,
            'monthly_transfer': total_bps * 86400 * 30,
        }

    def print_report(self):
        results = self.calculate()
        print("\n" + "=" * 60)
        print("BANDWIDTH ESTIMATE")
        print("=" * 60)
        print(f"\nInputs:")
        print(f"  Requests/sec:       {format_number(self.requests_per_second)}")
        print(f"  Request size:       {format_size(self.request_size)}")
        print(f"  Response size:      {format_size(self.response_size)}")
        print(f"\nBandwidth:")
        print(f"  Average:            {format_size(results['total_bps'])}/s")
        print(f"  Peak ({self.peak_multiplier}x):          {format_size(results['peak_total'])}/s")
        print(f"\nData Transfer:")
        print(f"  Daily:              {format_size(results['daily_transfer'])}")
        print(f"  Monthly:            {format_size(results['monthly_transfer'])}")


@dataclass
class QPSEstimate:
    daily_active_users: int
    requests_per_user_per_day: int
    peak_hour_percentage: float
    read_write_ratio: float

    def calculate(self) -> dict:
        daily_requests = self.daily_active_users * self.requests_per_user_per_day
        avg_qps = daily_requests / 86400
        peak_qps = (daily_requests * self.peak_hour_percentage / 100) / 3600
        total_ratio = self.read_write_ratio + 1
        return {
            'daily_requests': daily_requests,
            'avg_qps': avg_qps,
            'peak_qps': peak_qps,
            'read_qps': peak_qps * (self.read_write_ratio / total_ratio),
            'write_qps': peak_qps * (1 / total_ratio),
        }

    def print_report(self):
        results = self.calculate()
        print("\n" + "=" * 60)
        print("QPS ESTIMATE")
        print("=" * 60)
        print(f"\nInputs:")
        print(f"  Daily Active Users: {format_number(self.daily_active_users)}")
        print(f"  Requests/user/day:  {self.requests_per_user_per_day}")
        print(f"  Read:Write ratio:   {self.read_write_ratio}:1")
        print(f"\nQPS:")
        print(f"  Average:            {format_number(results['avg_qps'])}")
        print(f"  Peak:               {format_number(results['peak_qps'])}")
        print(f"  Peak Read:          {format_number(results['read_qps'])}")
        print(f"  Peak Write:         {format_number(results['write_qps'])}")


def print_quick_reference():
    print("\n" + "=" * 60)
    print("QUICK REFERENCE")
    print("=" * 60)
    print("\n📊 SCALE:")
    print("  Seconds/day: 86,400 (~100K)")
    print("  Seconds/year: 31.5M (~30M)")
    print("\n💾 STORAGE:")
    print("  1 tweet ≈ 300 bytes")
    print("  1 photo ≈ 200KB - 1MB")
    print("  1 min HD video ≈ 100MB")
    print("\n⏱️ LATENCY:")
    print("  RAM: 100 ns")
    print("  SSD: 100 μs")
    print("  HDD: 10 ms")
    print("  Same DC: 0.5 ms")
    print("  Cross-continent: 150 ms")
    print("\n🔢 QPS:")
    print("  MySQL: 1K-10K QPS")
    print("  Redis: 100K+ QPS")


def main():
    parser = argparse.ArgumentParser(description='Capacity Calculator')
    parser.add_argument('--reference', '-r', action='store_true')
    parser.add_argument('--storage', action='store_true')
    parser.add_argument('--users', type=int)
    parser.add_argument('--data-per-user', type=str)
    parser.add_argument('--growth-rate', type=float, default=1.2)
    parser.add_argument('--retention-years', type=int, default=3)
    parser.add_argument('--bandwidth', action='store_true')
    parser.add_argument('--rps', type=int)
    parser.add_argument('--request-size', type=str, default='1KB')
    parser.add_argument('--response-size', type=str, default='10KB')
    parser.add_argument('--peak-multiplier', type=float, default=3)
    parser.add_argument('--qps', action='store_true')
    parser.add_argument('--daily-users', type=int)
    parser.add_argument('--requests-per-user', type=int, default=10)
    parser.add_argument('--peak-hour-pct', type=float, default=20)
    parser.add_argument('--read-write-ratio', type=float, default=10)

    args = parser.parse_args()

    if args.reference or len(sys.argv) == 1:
        print_quick_reference()
        return

    if args.storage and args.users and args.data_per_user:
        StorageEstimate(args.users, parse_size(args.data_per_user),
                       args.growth_rate, args.retention_years).print_report()
    elif args.bandwidth and args.rps:
        BandwidthEstimate(args.rps, parse_size(args.request_size),
                         parse_size(args.response_size), args.peak_multiplier).print_report()
    elif args.qps and args.daily_users:
        QPSEstimate(args.daily_users, args.requests_per_user,
                   args.peak_hour_pct, args.read_write_ratio).print_report()
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
