"""
Collatz Regression Analysis
Computes linear regression coefficients for total steps vs odd steps,
analyzes residuals, and computes correlation between odd steps and peak value.
"""

import sys
import time
import json
import math
from collections import Counter


def collatz_full_analysis(n):
    """
    Analyze Collatz sequence for starting number n.
    Returns (total_steps, odd_steps, peak_value)
    """
    if n <= 0:
        raise ValueError("n must be a positive integer")
    
    total_steps = 0
    odd_steps = 0
    current = n
    peak = n
    
    while current != 1:
        if current % 2 == 1:  # Odd number
            odd_steps += 1
            current = 3 * current + 1
        else:  # Even number
            current = current // 2
        
        peak = max(peak, current)
        total_steps += 1
    
    return total_steps, odd_steps, peak


def online_regression_analysis(n_max, progress_interval=100000):
    """
    Calculate regression coefficients and correlations using online algorithm.
    """
    # Variables for regression: total_steps = slope * odd_steps + intercept
    n_count = 0
    sum_odd = 0
    sum_total = 0
    sum_peak = 0
    sum_odd_sq = 0
    sum_total_sq = 0
    sum_peak_sq = 0
    sum_odd_total = 0
    sum_odd_peak = 0
    
    # For residuals analysis
    residuals_counter = Counter()
    
    start_time = time.time()
    
    print("=" * 60)
    print("COLLATZ REGRESSION ANALYSIS")
    print("=" * 60)
    print(f"\nAnalyzing Collatz sequences for n = 1 to {n_max:,}")
    print("Computing regression coefficients and residuals...")
    print("This may take several minutes...\n")
    
    for n in range(1, n_max + 1):
        total_steps, odd_steps, peak = collatz_full_analysis(n)
        
        # Update sums for regression and correlations
        n_count += 1
        sum_odd += odd_steps
        sum_total += total_steps
        sum_peak += peak
        sum_odd_sq += odd_steps * odd_steps
        sum_total_sq += total_steps * total_steps
        sum_peak_sq += peak * peak
        sum_odd_total += odd_steps * total_steps
        sum_odd_peak += odd_steps * peak
        
        # Progress reporting
        if n % progress_interval == 0:
            elapsed = time.time() - start_time
            rate = n / elapsed
            eta = (n_max - n) / rate
            print(f"Progress: {n:,}/{n_max:,} ({100*n/n_max:.1f}%) - "
                  f"Rate: {rate:,.0f} nums/sec - ETA: {eta:.1f}s")
    
    # Calculate means
    mean_odd = sum_odd / n_count
    mean_total = sum_total / n_count
    mean_peak = sum_peak / n_count
    
    # Calculate linear regression coefficients
    # y = slope * x + intercept
    # where y = total_steps, x = odd_steps
    # slope = (n*Σxy - Σx*Σy) / (n*Σx² - (Σx)²)
    # intercept = (Σy - slope*Σx) / n
    
    numerator_slope = n_count * sum_odd_total - sum_odd * sum_total
    denominator_slope = n_count * sum_odd_sq - sum_odd * sum_odd
    slope = numerator_slope / denominator_slope if denominator_slope != 0 else 0
    intercept = (sum_total - slope * sum_odd) / n_count
    
    # Calculate correlation: odd_steps vs total_steps
    numerator_corr_total = n_count * sum_odd_total - sum_odd * sum_total
    denominator_corr_total = math.sqrt(
        (n_count * sum_odd_sq - sum_odd * sum_odd) *
        (n_count * sum_total_sq - sum_total * sum_total)
    )
    corr_odd_total = numerator_corr_total / denominator_corr_total if denominator_corr_total != 0 else 0
    
    # Calculate correlation: odd_steps vs peak_value
    numerator_corr_peak = n_count * sum_odd_peak - sum_odd * sum_peak
    denominator_corr_peak = math.sqrt(
        (n_count * sum_odd_sq - sum_odd * sum_odd) *
        (n_count * sum_peak_sq - sum_peak * sum_peak)
    )
    corr_odd_peak = numerator_corr_peak / denominator_corr_peak if denominator_corr_peak != 0 else 0
    
    # Second pass: calculate residuals
    print("\nCalculating residuals...")
    sum_residuals = 0
    sum_residuals_sq = 0
    max_residual = float('-inf')
    min_residual = float('inf')
    max_residual_n = 0
    min_residual_n = 0
    
    for n in range(1, n_max + 1):
        total_steps, odd_steps, _ = collatz_full_analysis(n)
        predicted = slope * odd_steps + intercept
        residual = total_steps - predicted
        residual_rounded = round(residual)
        
        sum_residuals += residual
        sum_residuals_sq += residual * residual
        residuals_counter[residual_rounded] += 1
        
        if residual > max_residual:
            max_residual = residual
            max_residual_n = n
        if residual < min_residual:
            min_residual = residual
            min_residual_n = n
        
        if n % progress_interval == 0:
            elapsed = time.time() - start_time
            rate = n / elapsed
            eta = (n_max - n) / rate
            print(f"Progress: {n:,}/{n_max:,} ({100*n/n_max:.1f}%) - "
                  f"Rate: {rate:,.0f} nums/sec - ETA: {eta:.1f}s")
    
    mean_residual = sum_residuals / n_count
    variance_residual = sum_residuals_sq / n_count - mean_residual * mean_residual
    std_residual = math.sqrt(variance_residual)
    
    # Calculate R-squared
    r_squared = corr_odd_total ** 2
    
    elapsed = time.time() - start_time
    
    return {
        "n_count": n_count,
        "computation_time_seconds": round(elapsed, 2),
        "linear_regression": {
            "equation": f"total_steps = {slope:.6f} * odd_steps + {intercept:.6f}",
            "slope": round(slope, 6),
            "intercept": round(intercept, 6),
            "r_squared": round(r_squared, 6)
        },
        "correlations": {
            "odd_steps_vs_total_steps": {
                "pearson_r": round(corr_odd_total, 6),
                "interpretation": interpret_correlation(corr_odd_total)
            },
            "odd_steps_vs_peak_value": {
                "pearson_r": round(corr_odd_peak, 6),
                "r_squared": round(corr_odd_peak ** 2, 6),
                "interpretation": interpret_correlation(corr_odd_peak)
            }
        },
        "residuals": {
            "mean": round(mean_residual, 6),
            "std_dev": round(std_residual, 6),
            "variance": round(variance_residual, 6),
            "min": round(min_residual, 6),
            "min_at_n": min_residual_n,
            "max": round(max_residual, 6),
            "max_at_n": max_residual_n,
            "distribution": dict(sorted(residuals_counter.items()))
        },
        "statistics": {
            "mean_odd_steps": round(mean_odd, 6),
            "mean_total_steps": round(mean_total, 6),
            "mean_peak_value": round(mean_peak, 6)
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
        print("Usage: python collatz_regression_analysis.py <max_n>")
        print("Example: python collatz_regression_analysis.py 10000000")
        sys.exit(1)
    
    try:
        n_max = int(sys.argv[1])
        if n_max <= 0:
            raise ValueError("n_max must be positive")
    except ValueError as e:
        print(f"Error: {e}")
        sys.exit(1)
    
    # Run analysis
    results = online_regression_analysis(n_max)
    
    # Display results
    print(f"\n{'=' * 60}")
    print("REGRESSION ANALYSIS COMPLETE")
    print("=" * 60)
    print(f"\nComputation time: {results['computation_time_seconds']} seconds")
    print(f"Numbers analyzed: 1 to {results['n_count']:,}")
    
    print("\n--- LINEAR REGRESSION ---")
    lr = results['linear_regression']
    print(f"Equation: {lr['equation']}")
    print(f"  Slope: {lr['slope']}")
    print(f"  Intercept: {lr['intercept']}")
    print(f"  R²: {lr['r_squared']} ({100*lr['r_squared']:.2f}% of variance explained)")
    
    print("\n--- CORRELATIONS ---")
    corr_total = results['correlations']['odd_steps_vs_total_steps']
    print(f"\nOdd Steps vs. Total Steps:")
    print(f"  Pearson r = {corr_total['pearson_r']}")
    print(f"  Interpretation: {corr_total['interpretation']}")
    
    corr_peak = results['correlations']['odd_steps_vs_peak_value']
    print(f"\nOdd Steps vs. Peak Value:")
    print(f"  Pearson r = {corr_peak['pearson_r']}")
    print(f"  R² = {corr_peak['r_squared']} ({100*corr_peak['r_squared']:.2f}% of variance explained)")
    print(f"  Interpretation: {corr_peak['interpretation']}")
    
    print("\n--- RESIDUALS ANALYSIS ---")
    res = results['residuals']
    print(f"Mean residual: {res['mean']:.6f}")
    print(f"Std deviation: {res['std_dev']:.6f}")
    print(f"Variance: {res['variance']:.6f}")
    print(f"Min residual: {res['min']:.6f} (at n={res['min_at_n']:,})")
    print(f"Max residual: {res['max']:.6f} (at n={res['max_at_n']:,})")
    
    print("\n--- RESIDUALS DISTRIBUTION (Top 20) ---")
    sorted_dist = sorted(res['distribution'].items(), key=lambda x: x[1], reverse=True)[:20]
    for residual, count in sorted_dist:
        percentage = count / results['n_count'] * 100
        print(f"Residual {residual:3d}: {count:,} occurrences ({percentage:.2f}%)")
    
    # Save results to JSON
    output_file = f"collatz_regression_{n_max}.json"
    with open(output_file, 'w') as f:
        json.dump(results, f, separators=(',', ':'))
    
    print(f"\nDetailed results saved to: {output_file}")
    print("=" * 60)


if __name__ == "__main__":
    main()
