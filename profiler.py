"""Profiling and optimization utilities for Sudoku solver."""

import cProfile
import io
import pstats
import time
import tracemalloc
from typing import Dict, List

from sudoku_solver.algorithms.backtracking import BacktrackingSolver
from sudoku_solver.algorithms.backtracking_mrv import BacktrackingMRVSolver
from sudoku_solver.algorithms.dancing_links import DancingLinksSolver
from sudoku_solver.algorithms.naked_singles import NakedSinglesSolver
from sudoku_solver.core.sudoku import SudokuBoard
from sudoku_solver.utils.puzzle_loader import PuzzleLoader


class ProfileResult:
    """Result from a profiling run."""

    def __init__(self, algorithm: str, puzzle_name: str):
        self.algorithm = algorithm
        self.puzzle_name = puzzle_name
        self.total_time = 0.0
        self.peak_memory = 0
        self.avg_memory = 0
        self.top_functions = []


class Profiler:
    """CPU and memory profiler for Sudoku solvers."""

    def __init__(self):
        """Initialize profiler."""
        self.results: List[ProfileResult] = []

    def profile_algorithm(
        self, algorithm_class, puzzle_str: str, algorithm_name: str, puzzle_name: str
    ) -> ProfileResult:
        """
        Profile a single algorithm on a puzzle.

        Args:
            algorithm_class: Solver class to profile
            puzzle_str: Puzzle string
            algorithm_name: Name of algorithm
            puzzle_name: Name of puzzle

        Returns:
            ProfileResult with profiling data
        """
        result = ProfileResult(algorithm_name, puzzle_name)

        # CPU profiling
        pr = cProfile.Profile()

        # Memory profiling setup
        tracemalloc.start()

        try:
            board = PuzzleLoader.from_string(puzzle_str)

            # Start profiling
            start_time = time.time()
            pr.enable()

            # Run solver
            solver = algorithm_class(board)
            solver.solve()

            # Stop profiling
            pr.disable()
            end_time = time.time()

            # Get memory stats
            current, peak = tracemalloc.get_traced_memory()
            tracemalloc.stop()

            result.total_time = end_time - start_time
            result.peak_memory = peak / (1024 * 1024)  # Convert to MB
            result.avg_memory = current / (1024 * 1024)  # Convert to MB

            # Get top functions by time
            s = io.StringIO()
            ps = pstats.Stats(pr, stream=s).sort_stats("cumulative")
            ps.print_stats(10)  # Top 10 functions

            # Parse results
            lines = s.getvalue().split("\n")
            for line in lines[5:15]:  # Skip header, get top 10
                if line.strip():
                    result.top_functions.append(line.strip())

            self.results.append(result)

        except Exception as e:
            print(f"Error profiling {algorithm_name}: {e}")

        return result

    def profile_all_algorithms(self, puzzle_name: str, puzzle_str: str) -> Dict:
        """
        Profile all algorithms on a puzzle.

        Args:
            puzzle_name: Name of puzzle
            puzzle_str: Puzzle string

        Returns:
            Dictionary of results by algorithm
        """
        algorithms = {
            "Backtracking": BacktrackingSolver,
            "Backtracking + MRV": BacktrackingMRVSolver,
            "Naked Singles": NakedSinglesSolver,
            "Dancing Links": DancingLinksSolver,
        }

        results = {}
        for algo_name, algo_class in algorithms.items():
            print(f"Profiling {algo_name} on {puzzle_name}...")
            result = self.profile_algorithm(
                algo_class, puzzle_str, algo_name, puzzle_name
            )
            results[algo_name] = result

        return results

    def generate_profile_report(self) -> str:
        """
        Generate profiling report.

        Returns:
            Formatted report string
        """
        lines = []
        lines.append("PROFILING REPORT - CPU AND MEMORY ANALYSIS")
        lines.append("=" * 100)

        # Group by puzzle
        by_puzzle = {}
        for result in self.results:
            if result.puzzle_name not in by_puzzle:
                by_puzzle[result.puzzle_name] = []
            by_puzzle[result.puzzle_name].append(result)

        for puzzle_name, puzzle_results in by_puzzle.items():
            lines.append(f"\n{puzzle_name.upper()}")
            lines.append("-" * 100)

            # Sort by execution time
            sorted_results = sorted(puzzle_results, key=lambda x: x.total_time)

            # Header
            header = (
                f"{'Algorithm':<25} {'Time (s)':<15} "
                f"{'Peak Mem (MB)':<15} {'Avg Mem (MB)':<15}"
            )
            lines.append(header)
            lines.append("-" * 100)

            for result in sorted_results:
                line = (
                    f"{result.algorithm:<25} "
                    f"{result.total_time:<15.4f} "
                    f"{result.peak_memory:<15.2f} "
                    f"{result.avg_memory:<15.2f}"
                )
                lines.append(line)

            # Top functions
            if sorted_results[0].top_functions:
                lines.append("\nTop functions (by time):")
                lines.append(sorted_results[0].top_functions[0])

        return "\n".join(lines)


class OptimizationAnalyzer:
    """Analyze optimization opportunities."""

    @staticmethod
    def analyze_candidates_efficiency():
        """Analyze efficiency of candidate tracking."""
        print("Analyzing candidate tracking efficiency...")

        board = SudokuBoard()

        # Measure time to access candidates
        start = time.perf_counter()
        for _ in range(10000):
            for r in range(9):
                for c in range(9):
                    _ = len(board.candidates[r][c])
        end = time.perf_counter()

        access_time = (end - start) / 10000
        print(f"Average candidate access time: {access_time*1e6:.2f} µs")

        return {
            "access_time_us": access_time * 1e6,
            "operations_per_second": 1 / access_time,
        }

    @staticmethod
    def analyze_board_copy_efficiency():
        """Analyze efficiency of board copying."""
        print("Analyzing board copy efficiency...")

        board = SudokuBoard()

        start = time.perf_counter()
        for _ in range(1000):
            _ = board.copy()
        end = time.perf_counter()

        copy_time = (end - start) / 1000
        print(f"Average board copy time: {copy_time*1e6:.2f} µs")

        return {"copy_time_us": copy_time * 1e6, "copies_per_second": 1 / copy_time}

    @staticmethod
    def analyze_validation_efficiency():
        """Analyze efficiency of move validation."""
        print("Analyzing move validation efficiency...")

        board = SudokuBoard()

        start = time.perf_counter()
        for _ in range(10000):
            board.is_valid()
        end = time.perf_counter()

        valid_time = (end - start) / 10000
        print(f"Average validation time: {valid_time*1e6:.2f} µs")

        return {
            "validation_time_us": valid_time * 1e6,
            "validations_per_second": 1 / valid_time,
        }

    @staticmethod
    def generate_optimization_recommendations(metrics: Dict) -> List[str]:
        """
        Generate optimization recommendations based on metrics.

        Args:
            metrics: Dictionary of optimization metrics

        Returns:
            List of recommendations
        """
        recommendations = []

        # Check candidate access time
        if metrics.get("access_time_us", 0) > 1:
            recommendations.append(
                "CANDIDATE TRACKING: Consider caching candidate lists "
                "or using BitSet for faster access"
            )

        # Check board copy time
        if metrics.get("copy_time_us", 0) > 100:
            recommendations.append(
                "BOARD COPYING: Consider using shallow copies where possible "
                "or implementing copy-on-write"
            )

        # Check validation time
        if metrics.get("validation_time_us", 0) > 10:
            recommendations.append(
                "VALIDATION: Consider caching validation results "
                "or using incremental validation"
            )

        if not recommendations:
            recommendations.append(
                "OPTIMIZATION: Current implementation is well-optimized. "
                "No critical bottlenecks detected."
            )

        return recommendations


class CoverageAnalyzer:
    """Analyze test coverage metrics."""

    @staticmethod
    def calculate_coverage_report() -> Dict:
        """
        Calculate test coverage data.

        Returns:
            Coverage report dictionary
        """
        return {
            "metric": "Test coverage analysis",
            "recommendation": "Run with pytest-cov plugin: pytest --cov=sudoku_solver tests/",
            "minimum_coverage": 80,
            "examples": [
                "pytest --cov=sudoku_solver tests/ --cov-report=html",
                "open htmlcov/index.html  # View in browser",
            ],
        }


def main():
    """Run comprehensive profiling and optimization analysis."""
    print("SUDOKU SOLVER - PROFILING AND OPTIMIZATION ANALYSIS")
    print("=" * 100)

    # Get test puzzles
    exemplars = PuzzleLoader.exemplars()

    # Profile on key puzzles
    puzzles = {
        "easy": exemplars["easy"],
        "hard": exemplars["hard"],
    }

    profiler = Profiler()

    for puzzle_name, puzzle_str in puzzles.items():
        profiler.profile_all_algorithms(puzzle_name, puzzle_str)

    # Print profiling report
    print(profiler.generate_profile_report())

    # Optimization analysis
    print("\n" + "=" * 100)
    print("OPTIMIZATION ANALYSIS")
    print("=" * 100)

    analyzer = OptimizationAnalyzer()
    metrics = {}

    metrics["candidates"] = analyzer.analyze_candidates_efficiency()
    print()
    metrics["copy"] = analyzer.analyze_board_copy_efficiency()
    print()
    metrics["validation"] = analyzer.analyze_validation_efficiency()

    # Generate recommendations
    print("\n" + "=" * 100)
    print("OPTIMIZATION RECOMMENDATIONS")
    print("=" * 100)

    combined_metrics = {}
    combined_metrics.update(metrics.get("candidates", {}))
    combined_metrics.update(metrics.get("copy", {}))
    combined_metrics.update(metrics.get("validation", {}))

    recommendations = analyzer.generate_optimization_recommendations(combined_metrics)
    for rec in recommendations:
        print(f"• {rec}")

    # Test coverage
    print("\n" + "=" * 100)
    print("TEST COVERAGE")
    print("=" * 100)

    coverage = CoverageAnalyzer.calculate_coverage_report()
    print(f"Metric: {coverage['metric']}")
    print(f"Recommendation: {coverage['recommendation']}")
    print(f"Minimum Coverage Target: {coverage['minimum_coverage']}%")
    print("\nExample commands:")
    for example in coverage["examples"]:
        print(f"  $ {example}")

    print("\n" + "=" * 100)
    print("Profiling complete!")


if __name__ == "__main__":
    main()
