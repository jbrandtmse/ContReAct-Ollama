"""
Calculate correlation coefficients for Collatz Conjecture analysis.
Computes Pearson correlation between starting number n and:
1. Stopping time (steps to reach 1)
2. Peak value reached during sequence
"""

import sys
import time
import json
import math


def collatz_sequence_stats(n):
    """
    Calculate stopping time and peak value for a given starting number.
    Returns (stopping_time, peak_value)
    """
    if n <= 0:
        raise ValueError("n must be a positive integer")
    
    steps = 0
    current = n
    peak = n
    
    while current != 1:
        if current % 2 == 0:
            current = current // 2
        else:
            current = 3 * current + 1
        
        peak = max(peak, current)
        steps += 1
    
    return steps, peak


def online_correlation(n_max, progress_interval=100000):
    """
    Calculate correlation coefficients using online algorithm (Welford's method).
    This avoids storing all data points in memory.
    """
    # Variables for stopping time correlation
    n_count = 0
    sum_n = 0
    sum_steps = 0
    sum_n_sq = 0
    sum_steps_sq = 0
    sum_n_steps = 0
    
    # Variables for peak value correlation
    sum_peak = 0
    sum_peak_sq = 0
    sum_n_peak = 0
    
    start_time = time.time()
    
    print("="*60)
    print("COLLATZ CORRELATION ANALYSIS")
    print("="*60)
    print(f"\nCalculating correlations for n = 1 to {n_max:,}")
    print("This may take several minutes...\n")
    
    for n in range(1, n_max + 1):
        steps, peak = collatz_sequence_stats(n)
        
        # Update sums for correlation calculations
        n_count += 1
        sum_n += n
        sum_steps += steps
        sum_n_sq += n * n
        sum_steps_sq += steps * steps
        sum_n_steps += n * steps
        
        sum_peak += peak
        sum_peak_sq += peak * peak
        sum_n_peak += n * peak
        
        # Progress reporting
        if n % progress_interval == 0:
            elapsed = time.time() - start_time
            rate = n / elapsed
            eta = (n_max - n) / rate
            print(f"Progress: {n:,}/{n_max:,} ({100*n/n_max:.1f}%) - "
                  f"Rate: {rate:,.0f} nums/sec - ETA: {eta:.1f}s")
    
    # Calculate Pearson correlation coefficients
    # r = (n*Σxy - Σx*Σy) / sqrt((n*Σx² - (Σx)²) * (n*Σy² - (Σy)²))
    
    # Correlation between n and stopping time
    numerator_steps = n_count * sum_n_steps - sum_n * sum_steps
    denominator_steps = math.sqrt(
        (n_count * sum_n_sq - sum_n * sum_n) * 
        (n_count * sum_steps_sq - sum_steps * sum_steps)
    )
    corr_n_steps = numerator_steps / denominator_steps if denominator_steps != 0 else 0
    
    # Correlation between n and peak value
    numerator_peak = n_count * sum_n_peak - sum_n * sum_peak
    denominator_peak = math.sqrt(
        (n_count * sum_n_sq - sum_n * sum_n) * 
        (n_count * sum_peak_sq - sum_peak * sum_peak)
    )
    corr_n_peak = numerator_peak / denominator_peak if denominator_peak != 0 else 0
    
    elapsed = time.time() - start_time
    
    return {
        "n_count": n_count,
        "computation_time_seconds": round(elapsed, 2),
        "correlations": {
            "n_vs_stopping_time": {
                "pearson_r": round(corr_n_steps, 6),
                "interpretation": interpret_correlation(corr_n_steps)
            },
            "n_vs_peak_value": {
                "pearson_r": round(corr_n_peak, 6),
                "interpretation": interpret_correlation(corr_n_peak)
            }
        },
        "summary_statistics": {
            "mean_n": round(sum_n / n_count, 2),
            "mean_stopping_time": round(sum_steps / n_count, 2),
            "mean_peak_value": round(sum_peak / n_count, 2)
        }
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
        print("Usage: python collatz_correlation.py <max_n>")
        print("Example: python collatz_correlation.py 10000000")
        sys.exit(1)
    
    try:
        n_max = int(sys.argv[1])
        if n_max <= 0:
            raise ValueError("n_max must be positive")
    except ValueError as e:
        print(f"Error: {e}")
        sys.exit(1)
    
    # Calculate correlations
    results = online_correlation(n_max)
    
    # Display results
    print(f"\n{'='*60}")
    print("CORRELATION ANALYSIS COMPLETE")
    print("="*60)
    print(f"\nComputation time: {results['computation_time_seconds']} seconds")
    print(f"Numbers analyzed: 1 to {results['n_count']:,}")
    
    print("\n--- CORRELATION COEFFICIENTS ---")
    
    corr_steps = results['correlations']['n_vs_stopping_time']
    print(f"\nCorrelation: n vs. Stopping Time")
    print(f"  Pearson r = {corr_steps['pearson_r']}")
    print(f"  Interpretation: {corr_steps['interpretation']}")
    print(f"  R² = {corr_steps['pearson_r']**2:.6f} ({100*corr_steps['pearson_r']**2:.2f}% of variance explained)")
    
    corr_peak = results['correlations']['n_vs_peak_value']
    print(f"\nCorrelation: n vs. Peak Value")
    print(f"  Pearson r = {corr_peak['pearson_r']}")
    print(f"  Interpretation: {corr_peak['interpretation']}")
    print(f"  R² = {corr_peak['pearson_r']**2:.6f} ({100*corr_peak['pearson_r']**2:.2f}% of variance explained)")
    
    print("\n--- SUMMARY STATISTICS ---")
    stats = results['summary_statistics']
    print(f"Mean n: {stats['mean_n']:,.2f}")
    print(f"Mean stopping time: {stats['mean_stopping_time']:.2f} steps")
    print(f"Mean peak value: {stats['mean_peak_value']:,.2f}")
    
    # Save results to JSON
    output_file = f"collatz_correlation_{n_max}.json"
    with open(output_file, 'w') as f:
        json.dump(results, f, indent=2)
    
    print(f"\nDetailed results saved to: {output_file}")
    print("="*60)


if __name__ == "__main__":
    main()
