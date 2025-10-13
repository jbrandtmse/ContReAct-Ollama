"""
Collatz Parity Structure Analysis
Analyzes the parity structure of Collatz sequences by counting odd and even steps,
and computes correlation between odd step count and stopping time.
"""

import sys
import time
import json
import math
from collections import Counter


def collatz_parity_analysis(n):
    """
    Analyze parity structure of Collatz sequence for starting number n.
    Returns (total_steps, odd_steps, even_steps)
    """
    if n <= 0:
        raise ValueError("n must be a positive integer")
    
    total_steps = 0
    odd_steps = 0
    even_steps = 0
    current = n
    
    while current != 1:
        if current % 2 == 1:  # Odd number
            odd_steps += 1
            current = 3 * current + 1
        else:  # Even number
            even_steps += 1
            current = current // 2
        total_steps += 1
    
    return total_steps, odd_steps, even_steps


def online_correlation(n_max, progress_interval=100000):
    """
    Calculate correlation between odd step count and stopping time.
    Uses online algorithm to avoid storing all data points.
    """
    # Variables for correlation calculation
    n_count = 0
    sum_odd = 0
    sum_total = 0
    sum_odd_sq = 0
    sum_total_sq = 0
    sum_odd_total = 0
    
    # Track distributions
    odd_step_distribution = Counter()
    total_step_distribution = Counter()
    
    # Track max values
    max_odd_steps = 0
    max_odd_n = 0
    max_total_steps = 0
    max_total_n = 0
    
    start_time = time.time()
    
    print("=" * 60)
    print("COLLATZ PARITY STRUCTURE ANALYSIS")
    print("=" * 60)
    print(f"\nAnalyzing parity structure for n = 1 to {n_max:,}")
    print("This may take several minutes...\n")
    
    for n in range(1, n_max + 1):
        total_steps, odd_steps, even_steps = collatz_parity_analysis(n)
        
        # Update correlation sums
        n_count += 1
        sum_odd += odd_steps
        sum_total += total_steps
        sum_odd_sq += odd_steps * odd_steps
        sum_total_sq += total_steps * total_steps
        sum_odd_total += odd_steps * total_steps
        
        # Update distributions
        odd_step_distribution[odd_steps] += 1
        total_step_distribution[total_steps] += 1
        
        # Track maximums
        if odd_steps > max_odd_steps:
            max_odd_steps = odd_steps
            max_odd_n = n
        if total_steps > max_total_steps:
            max_total_steps = total_steps
            max_total_n = n
        
        # Progress reporting
        if n % progress_interval == 0:
            elapsed = time.time() - start_time
            rate = n / elapsed
            eta = (n_max - n) / rate
            print(f"Progress: {n:,}/{n_max:,} ({100*n/n_max:.1f}%) - "
                  f"Rate: {rate:,.0f} nums/sec - ETA: {eta:.1f}s")
    
    # Calculate Pearson correlation coefficient
    # r = (n*Σxy - Σx*Σy) / sqrt((n*Σx² - (Σx)²) * (n*Σy² - (Σy)²))
    numerator = n_count * sum_odd_total - sum_odd * sum_total
    denominator = math.sqrt(
        (n_count * sum_odd_sq - sum_odd * sum_odd) *
        (n_count * sum_total_sq - sum_total * sum_total)
    )
    correlation = numerator / denominator if denominator != 0 else 0
    
    elapsed = time.time() - start_time
    
    # Calculate mean values
    mean_odd = sum_odd / n_count
    mean_total = sum_total / n_count
    
    return {
        "n_count": n_count,
        "computation_time_seconds": round(elapsed, 2),
        "correlation": {
            "odd_steps_vs_total_steps": {
                "pearson_r": round(correlation, 6),
                "r_squared": round(correlation ** 2, 6),
                "interpretation": interpret_correlation(correlation)
            }
        },
        "statistics": {
            "mean_odd_steps": round(mean_odd, 6),
            "mean_total_steps": round(mean_total, 6),
            "mean_even_steps": round(mean_total - mean_odd, 6),
            "max_odd_steps": max_odd_steps,
            "max_odd_steps_at_n": max_odd_n,
            "max_total_steps": max_total_steps,
            "max_total_steps_at_n": max_total_n
        },
        "odd_step_distribution": dict(sorted(odd_step_distribution.items())),
        "total_step_distribution_sample": dict(sorted(list(total_step_distribution.items())[:20]))
    }


def interpret_correlation(r):
    """Provide interpretation of correlation coefficient."""
    abs_r = abs(r)
    if abs_r < 0.1:
        strength = "negligible"
    elif abs_r < 0.3:
        strength = "weak"
    elif abs_r < 0.5:
        strength = "moderate"
    elif abs_r < 0.7:
        strength = "strong"
    else:
        strength = "very strong"
    
    direction = "positive" if r > 0 else "negative"
    return f"{strength} {direction} correlation"


def main():
    if len(sys.argv) != 2:
        print("Usage: python collatz_parity_analysis.py <max_n>")
        print("Example: python collatz_parity_analysis.py 10000000")
        sys.exit(1)
    
    try:
        n_max = int(sys.argv[1])
        if n_max <= 0:
            raise ValueError("n_max must be positive")
    except ValueError as e:
        print(f"Error: {e}")
        sys.exit(1)
    
    # Run analysis
    results = online_correlation(n_max)
    
    # Display results
    print(f"\n{'=' * 60}")
    print("PARITY ANALYSIS COMPLETE")
    print("=" * 60)
    print(f"\nComputation time: {results['computation_time_seconds']} seconds")
    print(f"Numbers analyzed: 1 to {results['n_count']:,}")
    
    print("\n--- CORRELATION ANALYSIS ---")
    corr = results['correlation']['odd_steps_vs_total_steps']
    print(f"\nCorrelation: Odd Steps vs. Total Stopping Time")
    print(f"  Pearson r = {corr['pearson_r']}")
    print(f"  R² = {corr['r_squared']} ({100*corr['r_squared']:.2f}% of variance explained)")
    print(f"  Interpretation: {corr['interpretation']}")
    
    print("\n--- STATISTICS ---")
    stats = results['statistics']
    print(f"Mean odd steps: {stats['mean_odd_steps']:.6f}")
    print(f"Mean even steps: {stats['mean_even_steps']:.6f}")
    print(f"Mean total steps: {stats['mean_total_steps']:.6f}")
    print(f"Odd/Total ratio: {stats['mean_odd_steps']/stats['mean_total_steps']:.4f}")
    
    print(f"\nMaximum odd steps: {stats['max_odd_steps']}")
    print(f"  Occurred at n = {stats['max_odd_steps_at_n']:,}")
    print(f"Maximum total steps: {stats['max_total_steps']}")
    print(f"  Occurred at n = {stats['max_total_steps_at_n']:,}")
    
    print("\n--- ODD STEP DISTRIBUTION (Top 15) ---")
    dist = results['odd_step_distribution']
    sorted_dist = sorted(dist.items(), key=lambda x: x[1], reverse=True)[:15]
    for odd_count, frequency in sorted_dist:
        percentage = frequency / results['n_count'] * 100
        print(f"Odd steps {odd_count}: {frequency:,} occurrences ({percentage:.2f}%)")
    
    # Save results to JSON
    output_file = f"collatz_parity_{n_max}.json"
    with open(output_file, 'w') as f:
        json.dump(results, f, separators=(',', ':'))
    
    print(f"\nDetailed results saved to: {output_file}")
    print("=" * 60)


if __name__ == "__main__":
    main()
