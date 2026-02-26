"""Metrics collection and visualization support."""

from typing import Any, Dict, List

from ..core.solver_base import SudokuSolver


class Metrics:
    """Collect and aggregate solver metrics for visualization."""

    def __init__(self):
        """Initialize metrics collector."""
        self.solver_metrics: Dict[str, Dict[str, Any]] = {}

    def collect(self, solver: SudokuSolver) -> None:
        """
        Collect metrics from a solver.

        Args:
            solver: Solver instance to collect metrics from
        """
        stats = solver.get_statistics()
        self.solver_metrics[stats["algorithm"]] = stats

    def compare(self) -> Dict[str, Any]:
        """
        Generate comparison metrics across all solvers.

        Returns:
            Dictionary with comparison data
        """
        if not self.solver_metrics:
            return {}

        times = {
            name: stats["execution_time"] for name, stats in self.solver_metrics.items()
        }
        assignments = {
            name: stats["cells_assigned"] for name, stats in self.solver_metrics.items()
        }
        backtracks = {
            name: stats["backtracks"] for name, stats in self.solver_metrics.items()
        }

        fastest = min(times, key=times.get) if times else None

        return {
            "times": times,
            "assignments": assignments,
            "backtracks": backtracks,
            "fastest_algorithm": fastest,
            "fastest_time": times.get(fastest) if fastest else None,
        }

    def reset(self) -> None:
        """Clear all metrics."""
        self.solver_metrics.clear()

    def get_stats_table(self) -> List[Dict[str, Any]]:
        """
        Get metrics formatted as table rows.

        Returns:
            List of dictionaries suitable for display
        """
        rows = []
        for algorithm, stats in sorted(self.solver_metrics.items()):
            rows.append(
                {
                    "Algorithm": algorithm,
                    "Time (s)": f"{stats['execution_time']:.6f}",
                    "Cells Assigned": stats["cells_assigned"],
                    "Backtracks": stats["backtracks"],
                    "Guesses": stats["guesses"],
                    "Solved": "✓" if stats["solved"] else "✗",
                }
            )
        return rows
