#!/usr/bin/env python3
"""
Fit piecewise constant correction to regression model based on n mod 16.

Computes optimal c₁ and c₂ values that minimize MSE when:
- Add c₁ for residues {0, 4, 8, 10}
- Subtract c₂ for residues {7, 9, 11, 14, 15}
- No correction for {1, 2, 3, 5, 6, 12, 13}

Reports new regression equation and R².
"""

import json
import math


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
    # Original regression coefficients
    slope = 2.594375
    intercept = 21.546398
    
    # Define correction groups
    group_c1 = {0, 4, 8, 10}  # Add c₁
    group_c2 = {7, 9, 11, 14, 15}  # Subtract c₂
    
    # Collect residuals by group
    residuals_c1 = []
    residuals_c2 = []
    residuals_uncorrected = []
    all_actuals = []
    
    max_n = 10_000_000
    
    print(f"Computing optimal piecewise corrections for n = 1 to {max_n:,}...")
    
    # Pass 1: Calculate optimal c₁ and c₂ as mean residuals of each group
    for n in range(1, max_n + 1):
        if n % 500_000 == 0:
            print(f"Pass 1 - Progress: {n:,} / {max_n:,}")
        
        actual_total_steps, odd_steps = collatz_sequence_stats(n)
        predicted_total_steps = slope * odd_steps + intercept
        residual = actual_total_steps - predicted_total_steps
        
        residue = n % 16
        
        if residue in group_c1:
            residuals_c1.append(residual)
        elif residue in group_c2:
            residuals_c2.append(residual)
        else:
            residuals_uncorrected.append(residual)
        
        all_actuals.append(actual_total_steps)
    
    # Optimal corrections are the mean residuals
    c1 = sum(residuals_c1) / len(residuals_c1)
    c2 = -sum(residuals_c2) / len(residuals_c2)  # Negative because we subtract it
    
    print(f"\nOptimal corrections:")
    print(f"c₁ = {c1:.6f} (add for residues {{0, 4, 8, 10}})")
    print(f"c₂ = {c2:.6f} (subtract for residues {{7, 9, 11, 14, 15}})")
    
    # Pass 2: Calculate new MSE and R² with corrections
    print(f"\nApplying corrections and calculating R²...")
    
    sum_squared_residuals = 0
    sum_squared_total = 0
    mean_actual = sum(all_actuals) / len(all_actuals)
    
    for n in range(1, max_n + 1):
        if n % 500_000 == 0:
            print(f"Pass 2 - Progress: {n:,} / {max_n:,}")
        
        actual_total_steps, odd_steps = collatz_sequence_stats(n)
        predicted_total_steps = slope * odd_steps + intercept
        
        # Apply piecewise correction
        residue = n % 16
        if residue in group_c1:
            predicted_total_steps += c1
        elif residue in group_c2:
            predicted_total_steps -= c2
        
        # Calculate new residual and contributions to R²
        new_residual = actual_total_steps - predicted_total_steps
        sum_squared_residuals += new_residual ** 2
        sum_squared_total += (actual_total_steps - mean_actual) ** 2
    
    # Calculate metrics
    mse = sum_squared_residuals / max_n
    rmse = math.sqrt(mse)
    r_squared = 1 - (sum_squared_residuals / sum_squared_total)
    
    # Prepare results
    results = {
        "original_regression": {
            "equation": f"total_steps = {slope} × odd_steps + {intercept}",
            "slope": slope,
            "intercept": intercept
        },
        "piecewise_corrections": {
            "c1": round(c1, 6),
            "c1_applies_to": list(group_c1),
            "c2": round(c2, 6),
            "c2_applies_to": list(group_c2),
            "description": f"Add {c1:.6f} for n≡{{0,4,8,10}} (mod 16), subtract {c2:.6f} for n≡{{7,9,11,14,15}} (mod 16)"
        },
        "corrected_model": {
            "base_equation": f"total_steps = {slope} × odd_steps + {intercept}",
            "correction": "Add c₁ for n≡{0,4,8,10} (mod 16); subtract c₂ for n≡{7,9,11,14,15} (mod 16)",
            "mse": round(mse, 6),
            "rmse": round(rmse, 6),
            "r_squared": round(r_squared, 6)
        },
        "original_model_r_squared": 0.999466
    }
    
    # Save to file
    output_file = "collatz_piecewise_correction_10000000.json"
    with open(output_file, 'w') as f:
        json.dump(results, f, indent=2)
    
    print(f"\n{'=' * 70}")
    print("PIECEWISE CONSTANT CORRECTION RESULTS")
    print(f"{'=' * 70}")
    print(f"\nOriginal Regression:")
    print(f"  total_steps = {slope} × odd_steps + {intercept}")
    print(f"  R² = 0.999466")
    print(f"\nOptimal Corrections:")
    print(f"  c₁ = {c1:.6f} (add for n ≡ {{0, 4, 8, 10}} mod 16)")
    print(f"  c₂ = {c2:.6f} (subtract for n ≡ {{7, 9, 11, 14, 15}} mod 16)")
    print(f"\nCorrected Model:")
    print(f"  Base: total_steps = {slope} × odd_steps + {intercept}")
    print(f"  + c₁ if n mod 16 ∈ {{0, 4, 8, 10}}")
    print(f"  - c₂ if n mod 16 ∈ {{7, 9, 11, 14, 15}}")
    print(f"\nCorrected Model Performance:")
    print(f"  MSE  = {mse:.6f}")
    print(f"  RMSE = {rmse:.6f}")
    print(f"  R²   = {r_squared:.6f}")
    print(f"\nImprovement:")
    print(f"  ΔR² = {r_squared - 0.999466:.6f}")
    print(f"\nResults saved to {output_file}")


if __name__ == "__main__":
    main()
