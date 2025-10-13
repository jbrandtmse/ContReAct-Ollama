#!/usr/bin/env python3
"""
Analyze regression residuals grouped by starting number modulo 8.

For each n up to 10 million:
- Calculate actual Collatz total_steps and odd_steps
- Calculate predicted_steps using regression: 2.594375 * odd_steps + 21.546398
- Calculate residual = actual - predicted
- Group by n mod 8 (residue classes 0-7)
- Return mean, std dev, and count for each residue class
"""

import json
import math
from collections import defaultdict


def collatz_sequence_stats(n):
    """Calculate stopping time and odd step count for Collatz sequence."""
    if n <= 0:
        return 0, 0
    
    total_steps = 0
    odd_steps = 0
    current = n
    
    while current != 1:
        if current % 2 == 1:
            odd_steps += 1
            current = 3 * current + 1
        else:
            current = current // 2
        total_steps += 1
    
    return total_steps, odd_steps


def main():
    # Regression coefficients from previous analysis
    slope = 2.594375
    intercept = 21.546398
    
    # Group residuals by n mod 8
    residual_groups = {i: [] for i in range(8)}
    
    max_n = 10_000_000
    
    print(f"Analyzing residuals for n = 1 to {max_n:,}...")
    
    # Calculate residuals for each n
    for n in range(1, max_n + 1):
        if n % 500_000 == 0:
            print(f"Progress: {n:,} / {max_n:,}")
        
        # Get actual values
        actual_total_steps, odd_steps = collatz_sequence_stats(n)
        
        # Calculate predicted value from regression
        predicted_total_steps = slope * odd_steps + intercept
        
        # Calculate residual
        residual = actual_total_steps - predicted_total_steps
        
        # Group by n mod 8
        residue_class = n % 8
        residual_groups[residue_class].append(residual)
    
    # Calculate statistics for each residue class
    results = {}
    
    for residue_class in range(8):
        residuals = residual_groups[residue_class]
        count = len(residuals)
        
        if count > 0:
            mean = sum(residuals) / count
            
            # Calculate standard deviation
            variance = sum((r - mean) ** 2 for r in residuals) / count
            std_dev = math.sqrt(variance)
            
            results[f"mod8_{residue_class}"] = {
                "mean_residual": round(mean, 6),
                "std_dev": round(std_dev, 6),
                "count": count
            }
        else:
            results[f"mod8_{residue_class}"] = {
                "mean_residual": 0.0,
                "std_dev": 0.0,
                "count": 0
            }
    
    # Save results to JSON file
    output_file = "collatz_residuals_mod8_10000000.json"
    with open(output_file, 'w') as f:
        json.dump(results, f, indent=2)
    
    print(f"\nResults saved to {output_file}")
    
    # Print summary
    print("\nRESIDUAL ANALYSIS BY n mod 8:")
    print("=" * 70)
    for residue_class in range(8):
        stats = results[f"mod8_{residue_class}"]
        print(f"n ≡ {residue_class} (mod 8): mean={stats['mean_residual']:8.4f}, "
              f"std={stats['std_dev']:8.4f}, count={stats['count']:,}")


if __name__ == "__main__":
    main()
