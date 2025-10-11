#!/usr/bin/env python3
"""
Collatz Conjecture Analysis Script

Computes the Collatz sequence for integers up to 10^7,
recording stopping time and peak values for each number.
"""

import sys
import json
from typing import Tuple, Dict
import time


def collatz_sequence_stats(n: int) -> Tuple[int, int]:
    """
    Compute Collatz sequence statistics for a starting number.
    
    Args:
        n: Starting integer
        
    Returns:
        Tuple of (stopping_time, peak_value)
    """
    if n <= 0:
        raise ValueError("n must be positive")
    
    steps = 0
    peak = n
    current = n
    
    while current != 1:
        if current % 2 == 0:
            current = current // 2
        else:
            current = 3 * current + 1
        
        steps += 1
        if current > peak:
            peak = current
    
    return steps, peak


def analyze_range(max_n: int = 10_000_000, checkpoint_interval: int = 100_000):
    """
    Analyze Collatz sequences for all integers from 1 to max_n.
    
    Args:
        max_n: Maximum integer to analyze
        checkpoint_interval: Progress reporting interval
    """
    print(f"Starting Collatz analysis for integers 1 to {max_n:,}")
    print(f"This may take several minutes...\n")
    
    start_time = time.time()
    
    # Statistics tracking
    max_stopping_time = 0
    max_stopping_time_n = 0
    max_peak_value = 0
    max_peak_value_n = 0
    total_stopping_time = 0
    total_peak_value = 0
    
    # Distribution tracking
    stopping_time_dist = {}
    
    # Process each number
    for n in range(1, max_n + 1):
        try:
            stopping_time, peak_value = collatz_sequence_stats(n)
            
            # Update maximums
            if stopping_time > max_stopping_time:
                max_stopping_time = stopping_time
                max_stopping_time_n = n
            
            if peak_value > max_peak_value:
                max_peak_value = peak_value
                max_peak_value_n = n
            
            # Update totals
            total_stopping_time += stopping_time
            total_peak_value += peak_value
            
            # Update distribution
            stopping_time_dist[stopping_time] = stopping_time_dist.get(stopping_time, 0) + 1
            
            # Progress reporting
            if n % checkpoint_interval == 0:
                elapsed = time.time() - start_time
                progress = (n / max_n) * 100
                rate = n / elapsed
                eta = (max_n - n) / rate
                print(f"Progress: {n:,}/{max_n:,} ({progress:.1f}%) - "
                      f"Rate: {rate:,.0f} nums/sec - ETA: {eta:.1f}s")
        
        except Exception as e:
            print(f"Error processing n={n}: {e}")
            continue
    
    elapsed_time = time.time() - start_time
    
    # Calculate statistics
    avg_stopping_time = total_stopping_time / max_n
    avg_peak_value = total_peak_value / max_n
    
    # Summary results
    results = {
        "range": {"min": 1, "max": max_n},
        "computation_time_seconds": round(elapsed_time, 2),
        "stopping_time": {
            "max": max_stopping_time,
            "max_at_n": max_stopping_time_n,
            "average": round(avg_stopping_time, 2),
            "distribution_sample": {
                k: v for k, v in sorted(stopping_time_dist.items())[:20]
            }
        },
        "peak_value": {
            "max": max_peak_value,
            "max_at_n": max_peak_value_n,
            "average": round(avg_peak_value, 2)
        },
        "interesting_findings": {
            "longest_sequence": {
                "n": max_stopping_time_n,
                "steps": max_stopping_time,
                "note": "This number took the most steps to reach 1"
            },
            "highest_peak": {
                "n": max_peak_value_n,
                "peak": max_peak_value,
                "note": "This sequence reached the highest value before returning to 1"
            }
        }
    }
    
    return results


def main():
    """Main execution function."""
    # Parse command line arguments
    max_n = int(sys.argv[1]) if len(sys.argv) > 1 else 10_000_000
    
    print("=" * 60)
    print("COLLATZ CONJECTURE ANALYSIS")
    print("=" * 60)
    print()
    
    # Run analysis
    results = analyze_range(max_n)
    
    # Display results
    print("\n" + "=" * 60)
    print("ANALYSIS COMPLETE")
    print("=" * 60)
    print(f"\nComputation time: {results['computation_time_seconds']} seconds")
    print(f"Numbers analyzed: {results['range']['min']:,} to {results['range']['max']:,}")
    
    print("\n--- STOPPING TIME STATISTICS ---")
    print(f"Maximum stopping time: {results['stopping_time']['max']} steps")
    print(f"  Occurred at n = {results['stopping_time']['max_at_n']:,}")
    print(f"Average stopping time: {results['stopping_time']['average']:.2f} steps")
    
    print("\n--- PEAK VALUE STATISTICS ---")
    print(f"Maximum peak value: {results['peak_value']['max']:,}")
    print(f"  Occurred at n = {results['peak_value']['max_at_n']:,}")
    print(f"Average peak value: {results['peak_value']['average']:,.2f}")
    
    print("\n--- INTERESTING FINDINGS ---")
    print(f"Longest sequence: n = {results['interesting_findings']['longest_sequence']['n']:,}")
    print(f"  Takes {results['interesting_findings']['longest_sequence']['steps']} steps to reach 1")
    
    print(f"\nHighest peak: n = {results['interesting_findings']['highest_peak']['n']:,}")
    print(f"  Reaches peak value of {results['interesting_findings']['highest_peak']['peak']:,}")
    
    # Save detailed results to JSON
    output_file = f"collatz_results_{max_n}.json"
    with open(output_file, 'w') as f:
        json.dump(results, f, indent=2)
    
    print(f"\nDetailed results saved to: {output_file}")
    print("\n" + "=" * 60)
    
    return results


if __name__ == "__main__":
    main()
