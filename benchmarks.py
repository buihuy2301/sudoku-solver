"""Performance benchmarking suite for Sudoku solver algorithms"""

import json
import statistics
import time
from typing import Dict, List

from sudoku_solver.algorithms.backtracking import BacktrackingSolver
from sudoku_solver.algorithms.backtracking_mrv import BacktrackingMRVSolver
from sudoku_solver.algorithms.dancing_links import DancingLinksSolver
from sudoku_solver.algorithms.naked_singles import NakedSinglesSolver
from sudoku_solver.utils.puzzle_loader import PuzzleLoader


class BenchmarkEntry:
    """Entry for a single algorithm benchmark run."""

    def __init__(self, algorithm: str, puzzle_name: str, puzzle_difficulty: str):
        self.algorithm = algorithm
        self.puzzle_name = puzzle_name
        self.puzzle_difficulty = puzzle_difficulty
        self.execution_time = 0.0
        self.cells_assigned = 0
        self.guesses = 0
        self.solved = False
        self.solution = None


class BenchmarkSuite:
    """Comprehensive benchmarking suite for Sudoku solvers."""

    ALGORITHMS = {
        "Backtracking": BacktrackingSolver,
        "Backtracking + MRV": BacktrackingMRVSolver,
        "Naked Singles": NakedSinglesSolver,
        "Dancing Links": DancingLinksSolver,
    }

    def __init__(self):
        """Initialize benchmark suite."""
        self.results: List[BenchmarkEntry] = []
        self.puzzles: Dict[str, Dict] = {}
        self._load_puzzles()

    def _load_puzzles(self):
        """Load all test puzzles."""
        exemplars = PuzzleLoader.exemplars()

        # Standard exemplar puzzles
        self.puzzles["exemplars"] = {
            "easy": exemplars.get("easy", ""),
            "medium": exemplars.get("medium", ""),
            "hard": exemplars.get("hard", ""),
            "very_hard": exemplars.get("expert", "").replace(".", "0"),
        }

        # Add additional test puzzles
        self.puzzles["additional"] = {
            "empty_board": "0" * 81,
            "single_clue": (
                "100000000000000000000000000000000000000000000000000000"
                "000000000000000000000000000"
            ),
            "minimal": (
                "100000002020000080003000004000100000005000600000001000"
                "700000300090000010800000009"
            ),
        }

    def benchmark_algorithm(
        self,
        algorithm_name: str,
        algorithm_class,
        puzzle_str: str,
        puzzle_name: str,
        puzzle_difficulty: str,
    ) -> BenchmarkEntry:
        """
        Benchmark a single algorithm on a single puzzle.

        Args:
            algorithm_name: Display name of algorithm
            algorithm_class: Solver class
            puzzle_str: Puzzle string (81 chars)
            puzzle_name: Name of puzzle
            puzzle_difficulty: Difficulty level

        Returns:
            BenchmarkEntry with results
        """
        entry = BenchmarkEntry(algorithm_name, puzzle_name, puzzle_difficulty)

        try:
            # Load puzzle
            board = PuzzleLoader.from_string(puzzle_str)

            # Run solver with timing
            solver = algorithm_class(board)
            start_time = time.time()
            solved = solver.solve()
            end_time = time.time()

            # Collect statistics
            entry.execution_time = end_time - start_time
            entry.solved = solved

            if solved:
                stats = solver.get_statistics()
                entry.cells_assigned = stats.get("cells_assigned", 0)
                entry.guesses = stats.get("guesses", 0)
                entry.solution = solver.board.to_string()

        except Exception as e:
            print(f"Error benchmarking {algorithm_name} on {puzzle_name}: {e}")
            entry.solved = False

        return entry

    def run_full_benchmark(self, num_runs: int = 3) -> Dict:
        """
        Run complete benchmarking suite.

        Args:
            num_runs: Number of times to run each test

        Returns:
            Dictionary with aggregated results
        """
        print(f"Starting Sudoku Solver Benchmark Suite ({num_runs} runs per test)")
        print("=" * 80)

        all_results = {}
        total_benchmarks = 0

        # Benchmark each puzzle with each algorithm
        for puzzle_category, puzzles in self.puzzles.items():
            all_results[puzzle_category] = {}

            for puzzle_name, puzzle_str in puzzles.items():
                all_results[puzzle_category][puzzle_name] = {}

                # Determine difficulty
                if puzzle_category == "exemplars":
                    difficulty = puzzle_name
                else:
                    difficulty = "custom"

                print(
                    f"\nBenchmarking {puzzle_category}/{puzzle_name} ({difficulty})..."
                )

                for algo_name, algo_class in self.ALGORITHMS.items():
                    times = []
                    cells_assigned = []
                    guesses = []
                    success_count = 0

                    for run in range(num_runs):
                        entry = self.benchmark_algorithm(
                            algo_name, algo_class, puzzle_str, puzzle_name, difficulty
                        )
                        self.results.append(entry)

                        if entry.solved:
                            times.append(entry.execution_time)
                            cells_assigned.append(entry.cells_assigned)
                            guesses.append(entry.guesses)
                            success_count += 1

                        total_benchmarks += 1

                    # Aggregate results
                    result = {
                        "success_rate": success_count / num_runs,
                        "avg_time": statistics.mean(times) if times else float("inf"),
                        "min_time": min(times) if times else float("inf"),
                        "max_time": max(times) if times else float("inf"),
                        "stdev_time": statistics.stdev(times) if len(times) > 1 else 0,
                        "avg_cells": (
                            statistics.mean(cells_assigned) if cells_assigned else 0
                        ),
                        "avg_guesses": statistics.mean(guesses) if guesses else 0,
                    }

                    all_results[puzzle_category][puzzle_name][algo_name] = result

                    status = "✓" if success_count == num_runs else "✗"
                    print(
                        f"  {algo_name}: {status} {result['avg_time']:.4f}s (±{result['stdev_time']:.4f}s)"
                    )

        print("\n" + "=" * 80)
        print(f"Benchmark complete! Total tests: {total_benchmarks}")

        return all_results

    def generate_comparison_table(self, results: Dict) -> str:
        """
        Generate a comparison table of results.

        Args:
            results: Benchmark results

        Returns:
            Formatted table string
        """
        lines = []
        lines.append("SUDOKU SOLVER PERFORMANCE COMPARISON")
        lines.append("=" * 120)

        for puzzle_category, puzzles in results.items():
            lines.append(f"\n{puzzle_category.upper()}")
            lines.append("-" * 120)

            for puzzle_name, algo_results in puzzles.items():
                lines.append(f"\n  {puzzle_name.upper()}")

                # Header
                header = (
                    "  "
                    + f"{'Algorithm':<20} {'Time (s)':<15} "
                    + f"{'Cells':<10} {'Guesses':<10} {'Success':<10}"
                )
                lines.append(header)
                lines.append("  " + "-" * 80)

                # Sort by execution time
                sorted_algos = sorted(
                    algo_results.items(), key=lambda x: x[1]["avg_time"]
                )

                fastest = sorted_algos[0][1]["avg_time"]

                for algo_name, result in sorted_algos:
                    time_str = f"{result['avg_time']:.4f}±{result['stdev_time']:.4f}"
                    speedup = (
                        fastest / result["avg_time"] if result["avg_time"] > 0 else 1
                    )
                    _speedup_str = f"({speedup:.1f}x)" if speedup > 1 else ""

                    line = (
                        f"  {algo_name:<20} "
                        f"{time_str:<15} "
                        f"{result['avg_cells']:<10.0f} "
                        f"{result['avg_guesses']:<10.0f} "
                        f"{result['success_rate']*100:<9.0f}%"
                    )
                    lines.append(line)

        return "\n".join(lines)

    def save_results(self, filepath: str = "benchmark_results.json"):
        """
        Save benchmark results to JSON file.

        Args:
            filepath: Path to save results
        """
        data = []
        for entry in self.results:
            data.append(
                {
                    "algorithm": entry.algorithm,
                    "puzzle_name": entry.puzzle_name,
                    "puzzle_difficulty": entry.puzzle_difficulty,
                    "execution_time": entry.execution_time,
                    "cells_assigned": entry.cells_assigned,
                    "guesses": entry.guesses,
                    "solved": entry.solved,
                }
            )

        with open(filepath, "w") as f:
            json.dump(data, f, indent=2)

        print(f"\nResults saved to {filepath}")

    def generate_summary_stats(self, results: Dict) -> str:
        """
        Generate summary statistics.

        Args:
            results: Benchmark results

        Returns:
            Summary statistics string
        """
        lines = []
        lines.append("\nSUMMARY STATISTICS")
        lines.append("=" * 80)

        # Overall fastest algorithm
        all_times = {}
        for puzzles in results.values():
            for algo_results in puzzles.values():
                for algo_name, result in algo_results.items():
                    if algo_name not in all_times:
                        all_times[algo_name] = []
                    if result["avg_time"] < float("inf"):
                        all_times[algo_name].append(result["avg_time"])

        if all_times:
            avg_by_algo = {
                algo: statistics.mean(times) for algo, times in all_times.items()
            }

            lines.append("\nAverage execution time by algorithm:")
            for algo, avg_time in sorted(avg_by_algo.items(), key=lambda x: x[1]):
                lines.append(f"  {algo:<25} {avg_time:.4f}s")

            # Relative speedups
            _fastest_time = min(avg_by_algo.values())
            lines.append("\nRelative speedup (vs slowest):")
            slowest_time = max(avg_by_algo.values())

            for algo, avg_time in sorted(
                avg_by_algo.items(), key=lambda x: x[1], reverse=True
            ):
                speedup = slowest_time / avg_time
                lines.append(f"  {algo:<25} {speedup:.1f}x")

        return "\n".join(lines)


def main():
    """Run full benchmark suite."""
    suite = BenchmarkSuite()
    results = suite.run_full_benchmark(num_runs=3)

    # Print results
    print(suite.generate_comparison_table(results))
    print(suite.generate_summary_stats(results))

    # Save results
    suite.save_results("benchmark_results.json")


if __name__ == "__main__":
    main()
