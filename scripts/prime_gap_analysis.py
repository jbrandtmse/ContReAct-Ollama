"""
Prime Gap and Twin Prime Analysis
Generates all primes up to a specified limit, analyzes gaps between consecutive primes,
counts twin primes, and provides comprehensive statistical analysis.
"""

import sys
import time
import json
import math
from collections import Counter


def sieve_of_eratosthenes(limit):
    """
    Generate all prime numbers up to limit using Sieve of Eratosthenes.
    Returns a list of primes.
    """
    if limit < 2:
        return []
    
    # Create boolean array and initialize all entries as true
    is_prime = [True] * (limit + 1)
    is_prime[0] = is_prime[1] = False
    
    # Sieve process
    for i in range(2, int(math.sqrt(limit)) + 1):
        if is_prime[i]:
            # Mark all multiples of i as not prime
            for j in range(i * i, limit + 1, i):
                is_prime[j] = False
    
    # Collect all primes
    primes = [i for i in range(2, limit + 1) if is_prime[i]]
    return primes


def analyze_prime_gaps(primes):
    """
    Analyze gaps between consecutive primes.
    Returns dict with gap statistics and twin prime count.
    """
    if len(primes) < 2:
        return {
            "gaps": [],
            "twin_prime_count": 0,
            "statistics": {}
        }
    
    # Calculate gaps
    gaps = [primes[i+1] - primes[i] for i in range(len(primes) - 1)]
    
    # Count twin primes (gap of 2)
    twin_prime_count = gaps.count(2)
    
    # Calculate statistics
    n = len(gaps)
    mean_gap = sum(gaps) / n
    
    # Calculate median
    sorted_gaps = sorted(gaps)
    if n % 2 == 0:
        median_gap = (sorted_gaps[n//2 - 1] + sorted_gaps[n//2]) / 2
    else:
        median_gap = sorted_gaps[n//2]
    
    # Calculate variance and standard deviation
    variance = sum((g - mean_gap) ** 2 for g in gaps) / n
    std_dev = math.sqrt(variance)
    
    # Gap distribution (histogram data)
    gap_counts = Counter(gaps)
    
    # Find interesting gaps
    min_gap = min(gaps)
    max_gap = max(gaps)
    
    # Find all occurrences of max gap
    max_gap_indices = [i for i, g in enumerate(gaps) if g == max_gap]
    max_gap_examples = [
        {
            "after_prime": primes[i],
            "next_prime": primes[i+1],
            "gap": max_gap
        }
        for i in max_gap_indices[:5]  # Show up to 5 examples
    ]
    
    return {
        "total_gaps": n,
        "twin_prime_count": twin_prime_count,
        "statistics": {
            "mean": round(mean_gap, 6),
            "median": median_gap,
            "variance": round(variance, 6),
            "std_dev": round(std_dev, 6),
            "min_gap": min_gap,
            "max_gap": max_gap
        },
        "gap_distribution": dict(sorted(gap_counts.items())),
        "max_gap_examples": max_gap_examples
    }


def main():
    if len(sys.argv) != 2:
        print("Usage: python prime_gap_analysis.py <max_n>")
        print("Example: python prime_gap_analysis.py 10000000")
        sys.exit(1)
    
    try:
        limit = int(sys.argv[1])
        if limit < 2:
            raise ValueError("limit must be at least 2")
    except ValueError as e:
        print(f"Error: {e}")
        sys.exit(1)
    
    print("=" * 60)
    print("PRIME GAP AND TWIN PRIME ANALYSIS")
    print("=" * 60)
    print(f"\nGenerating primes up to {limit:,}...")
    
    # Generate primes
    start_time = time.time()
    primes = sieve_of_eratosthenes(limit)
    sieve_time = time.time() - start_time
    
    print(f"Found {len(primes):,} primes in {sieve_time:.2f} seconds")
    print(f"\nAnalyzing prime gaps...")
    
    # Analyze gaps
    analysis_start = time.time()
    gap_analysis = analyze_prime_gaps(primes)
    analysis_time = time.time() - analysis_start
    
    total_time = time.time() - start_time
    
    # Display results
    print(f"\n{'=' * 60}")
    print("ANALYSIS COMPLETE")
    print("=" * 60)
    print(f"\nTotal computation time: {total_time:.2f} seconds")
    print(f"  - Sieve generation: {sieve_time:.2f} seconds")
    print(f"  - Gap analysis: {analysis_time:.2f} seconds")
    
    print(f"\n--- PRIME STATISTICS ---")
    print(f"Total primes found: {len(primes):,}")
    print(f"First prime: {primes[0]}")
    print(f"Last prime: {primes[-1]}")
    print(f"Total gaps analyzed: {gap_analysis['total_gaps']:,}")
    
    print(f"\n--- TWIN PRIMES ---")
    print(f"Twin prime pairs found: {gap_analysis['twin_prime_count']:,}")
    print(f"Twin prime density: {gap_analysis['twin_prime_count'] / gap_analysis['total_gaps'] * 100:.4f}%")
    
    stats = gap_analysis['statistics']
    print(f"\n--- GAP STATISTICS ---")
    print(f"Mean gap: {stats['mean']:.6f}")
    print(f"Median gap: {stats['median']}")
    print(f"Variance: {stats['variance']:.6f}")
    print(f"Standard deviation: {stats['std_dev']:.6f}")
    print(f"Minimum gap: {stats['min_gap']}")
    print(f"Maximum gap: {stats['max_gap']}")
    
    print(f"\n--- MAXIMUM GAP EXAMPLES ---")
    for example in gap_analysis['max_gap_examples']:
        print(f"Gap of {example['gap']} after prime {example['after_prime']:,} "
              f"(next prime: {example['next_prime']:,})")
    
    print(f"\n--- GAP DISTRIBUTION (Top 10) ---")
    dist = gap_analysis['gap_distribution']
    sorted_dist = sorted(dist.items(), key=lambda x: x[1], reverse=True)[:10]
    for gap, count in sorted_dist:
        percentage = count / gap_analysis['total_gaps'] * 100
        print(f"Gap {gap}: {count:,} occurrences ({percentage:.2f}%)")
    
    # Prepare output
    output = {
        "limit": limit,
        "computation_time_seconds": round(total_time, 2),
        "prime_count": len(primes),
        "first_prime": primes[0],
        "last_prime": primes[-1],
        "twin_prime_count": gap_analysis['twin_prime_count'],
        "twin_prime_density": round(gap_analysis['twin_prime_count'] / gap_analysis['total_gaps'], 6),
        "gap_statistics": stats,
        "gap_distribution": gap_analysis['gap_distribution'],
        "max_gap_examples": gap_analysis['max_gap_examples']
    }
    
    # Save to JSON
    output_file = f"prime_gap_analysis_{limit}.json"
    with open(output_file, 'w') as f:
        json.dump(output, f, separators=(',', ':'))
    
    print(f"\nDetailed results saved to: {output_file}")
    print("=" * 60)


if __name__ == "__main__":
    main()
