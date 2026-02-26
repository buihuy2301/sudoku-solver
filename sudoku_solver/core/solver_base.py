"""Abstract base class for Sudoku solvers."""

import time
from abc import ABC, abstractmethod
from typing import Any, Dict, List, Tuple

from .sudoku import SudokuBoard


class SudokuSolver(ABC):
    """Abstract base class for all Sudoku solving algorithms."""

    def __init__(self, board: SudokuBoard):
        """
        Initialize solver with a Sudoku board.

        Args:
            board: SudokuBoard instance to solve
        """
        self.board = board.copy()
        self.original_board = board.copy()

        # Statistics tracking
        self.cells_assigned = 0
        self.backtracks = 0
        self.guesses = 0
        self.execution_time = 0.0
        self.step_history: List[Tuple[int, int, int]] = (
            []
        )  # List of (row, col, value) assignments

    @abstractmethod
    def solve(self) -> bool:
        """
        Solve the Sudoku puzzle.

        Returns:
            True if puzzle is solved, False if no solution exists
        """
        pass

    def get_statistics(self) -> Dict[str, Any]:
        """
        Get solver statistics.

        Returns:
            Dictionary containing:
            - cells_assigned: Number of cells assigned during solving
            - backtracks: Number of backtracks (if applicable)
            - guesses: Number of guesses/decisions made
            - execution_time: Time taken to solve in seconds
            - solved: Whether puzzle was solved
            - algorithm: Name of the algorithm
        """
        return {
            "algorithm": self.__class__.__name__,
            "cells_assigned": self.cells_assigned,
            "backtracks": self.backtracks,
            "guesses": self.guesses,
            "execution_time": self.execution_time,
            "solved": self.board.is_solved(),
        }

    def reset(self) -> None:
        """Reset solver to initial state."""
        self.board = self.original_board.copy()
        self.cells_assigned = 0
        self.backtracks = 0
        self.guesses = 0
        self.execution_time = 0.0
        self.step_history = []

    def _record_assignment(self, row: int, col: int, value: int) -> None:
        """
        Record a cell assignment in history.

        Args:
            row: Row index
            col: Column index
            value: Value assigned
        """
        self.step_history.append((row, col, value))
        self.cells_assigned += 1

    def solve_with_timer(self) -> bool:
        """
        Solve the puzzle with execution time tracking.

        Returns:
            True if puzzle is solved, False otherwise
        """
        start_time = time.time()
        result = self.solve()
        self.execution_time = time.time() - start_time
        return result
