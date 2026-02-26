#!/usr/bin/env python
"""
Test Suite Runner - Comprehensive Testing & Optimization

This script provides an easy interface to run different types of tests
and profiling on the Sudoku Solver project.
"""

import argparse
import subprocess
import sys
from pathlib import Path


class TestRunner:
    """Utility for running different types of tests."""

    def __init__(self):
        self.project_root = Path(__file__).parent
        self.tests_dir = self.project_root / "tests"

    def run_unit_tests(self, verbose: bool = False):
        """Run unit tests only."""
        cmd = [
            "pytest",
            str(self.tests_dir / "test_algorithms.py"),
            "-v" if verbose else "-q",
        ]
        print("Running unit tests...")
        return subprocess.run(cmd, check=False).returncode

    def run_integration_tests(self, verbose: bool = False):
        """Run integration tests only."""
        cmd = [
            "pytest",
            str(self.tests_dir / "test_integration.py"),
            "-v" if verbose else "-q",
        ]
        print("Running integration tests...")
        return subprocess.run(cmd, check=False).returncode

    def run_all_tests(self, verbose: bool = False, coverage: bool = False):
        """Run all tests with optional coverage."""
        cmd = ["pytest", str(self.tests_dir), "-v" if verbose else "-q"]

        if coverage:
            cmd.extend(
                [
                    "--cov=sudoku_solver",
                    "--cov-report=term-missing",
                    "--cov-report=html",
                ]
            )
            print("Running all tests with coverage report...")
        else:
            print("Running all tests...")

        return subprocess.run(cmd, check=False).returncode

    def run_benchmarks(self):
        """Run performance benchmarks."""
        cmd = [sys.executable, "benchmarks.py"]
        print("Running benchmarks...")
        return subprocess.run(cmd, cwd=self.project_root, check=False).returncode

    def run_profiling(self):
        """Run profiling and optimization analysis."""
        cmd = [sys.executable, "profiler.py"]
        print("Running profiling and optimization analysis...")
        return subprocess.run(cmd, cwd=self.project_root, check=False).returncode

    def run_linting(self):
        """Run code quality checks (if available)."""
        try:
            # Try pylint
            cmd = [
                "pylint",
                "sudoku_solver",
                "--disable=C0111",  # Disable missing docstring warnings for initial check
                "--extension-pkg-allow-list=numpy",
            ]
            print("Running linting checks...")
            return subprocess.run(cmd, cwd=self.project_root, check=False).returncode
        except FileNotFoundError:
            print("pylint not installed. Install with: pip install pylint")
            return 1

    def run_type_checking(self):
        """Run type checking (if mypy is available)."""
        try:
            cmd = ["mypy", "sudoku_solver", "--ignore-missing-imports"]
            print("Running type checking...")
            return subprocess.run(cmd, cwd=self.project_root, check=False).returncode
        except FileNotFoundError:
            print("mypy not installed. Install with: pip install mypy")
            return 1


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Test Suite Runner - Run tests, benchmarks, and profiling"
    )

    parser.add_argument("--unit", action="store_true", help="Run unit tests only")

    parser.add_argument(
        "--integration", action="store_true", help="Run integration tests only"
    )

    parser.add_argument("--all", action="store_true", help="Run all tests")

    parser.add_argument(
        "--benchmark", action="store_true", help="Run performance benchmarks"
    )

    parser.add_argument(
        "--profile", action="store_true", help="Run profiling and optimization analysis"
    )

    parser.add_argument(
        "--coverage",
        action="store_true",
        help="Generate coverage report (use with --all)",
    )

    parser.add_argument("--lint", action="store_true", help="Run linting checks")

    parser.add_argument("--type-check", action="store_true", help="Run type checking")

    parser.add_argument("-v", "--verbose", action="store_true", help="Verbose output")

    parser.add_argument(
        "--full",
        action="store_true",
        help="Run all checks: tests, coverage, benchmarks, profiling",
    )

    args = parser.parse_args()

    runner = TestRunner()
    exit_codes = []

    # If no specific tests requested, default to all
    if not any(
        [
            args.unit,
            args.integration,
            args.benchmark,
            args.profile,
            args.lint,
            args.type_check,
            args.full,
            args.all,
            args.coverage,
        ]
    ):
        args.all = True

    # Full test suite
    if args.full:
        return _extracted_from_main_(exit_codes, runner, args)
    # Individual test selections
    if args.unit:
        exit_codes.append(runner.run_unit_tests(verbose=args.verbose))

    if args.integration:
        exit_codes.append(runner.run_integration_tests(verbose=args.verbose))

    if args.all:
        exit_codes.append(
            runner.run_all_tests(verbose=args.verbose, coverage=args.coverage)
        )

    if args.benchmark:
        exit_codes.append(runner.run_benchmarks())

    if args.profile:
        exit_codes.append(runner.run_profiling())

    if args.lint:
        exit_codes.append(runner.run_linting())

    if args.type_check:
        exit_codes.append(runner.run_type_checking())

    if exit_codes:
        return max(exit_codes)
    parser.print_help()
    return 0


# TODO Rename this here and in `main`
def _extracted_from_main_(exit_codes, runner, args):
    print("=" * 80)
    print("COMPREHENSIVE TEST SUITE")
    print("=" * 80)

    exit_codes.extend(
        (
            runner.run_all_tests(verbose=args.verbose, coverage=True),
            runner.run_benchmarks(),
            runner.run_profiling(),
        )
    )
    print("\n" + "=" * 80)
    print("Summary:")
    print(f"  Tests: {'PASSED' if exit_codes[0] == 0 else 'FAILED'}")
    print(f"  Benchmarks: {'PASSED' if exit_codes[1] == 0 else 'FAILED'}")
    print(f"  Profiling: {'PASSED' if exit_codes[2] == 0 else 'FAILED'}")
    print("=" * 80)

    return max(exit_codes)


if __name__ == "__main__":
    sys.exit(main())
