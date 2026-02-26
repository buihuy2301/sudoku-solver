"""Input validation and Sudoku legality checks."""

from typing import Tuple

from ..core.sudoku import SudokuBoard


class Validators:
    """Validation utilities for Sudoku puzzles."""

    @staticmethod
    def is_valid_puzzle(board: SudokuBoard) -> Tuple[bool, str]:
        """
        Check if a puzzle is a valid Sudoku.

        Args:
            board: SudokuBoard instance to validate

        Returns:
            Tuple of (is_valid, error_message)
        """
        # Check board creation was successful
        if board is None:
            return False, "Board is None"

        # Check if board is valid
        if board.is_valid():
            return True, "Valid puzzle"
        error_msg = (
            "Board contains conflicts ("
            "duplicate values in row, column, or box)"
        )
        return False, error_msg

    @staticmethod
    def is_valid_placement(
        board: SudokuBoard, row: int, col: int, value: int
    ) -> Tuple[bool, str]:
        """
        Check if a value can be placed at a position.

        Args:
            board: SudokuBoard instance
            row: Row index (0-8)
            col: Column index (0-8)
            value: Value to place (1-9)

        Returns:
            Tuple of (is_valid, reason)
        """
        if not 0 <= row < 9:
            return False, f"Row index {row} out of range"

        if not 0 <= col < 9:
            return False, f"Column index {col} out of range"

        if not 1 <= value <= 9:
            return False, f"Value {value} must be between 1 and 9"

        if board.board[row][col] != 0:
            return False, f"Cell ({row}, {col}) is already filled"

        if not board._is_valid_placement(row, col, value):
            return False, f"Value {value} conflicts with row, column, or box"

        return True, "Valid placement"

    @staticmethod
    def has_unique_solution(board: SudokuBoard) -> bool:
        """
        Check if puzzle has a unique solution (simplified).
        This is a basic check - doesn't guarantee uniqueness.

        Args:
            board: SudokuBoard instance

        Returns:
            True if puzzle appears to have a unique solution
        """
        # Count given cells and empty cells
        given_cells = sum(
            1 for r in range(9) for c in range(9) if board.board[r][c] != 0
        )
        empty_cells = 81 - given_cells

        # Basic heuristic: well-formed puzzles typically have 17+ given cells
        # and are not over-constrained
        return given_cells >= 17 and empty_cells >= 1

    @staticmethod
    def count_solutions(board: SudokuBoard, max_solutions: int = 2) -> int:
        """
        Count number of solutions (up to max_solutions).
        Used to verify puzzle uniqueness.

        Args:
            board: SudokuBoard instance
            max_solutions: Stop counting after finding this many solutions

        Returns:
            Number of solutions (at most max_solutions)
        """
        count = [0]  # Use list to allow modification in nested function

        def solve_count(b: SudokuBoard) -> None:
            if count[0] >= max_solutions:
                return

            if b.is_solved():
                count[0] += 1
                return

            # Find first empty cell
            empty_cells = b.get_empty_cells()
            if not empty_cells:
                return

            row, col = empty_cells[0]

            for value in range(1, 10):
                if b._is_valid_placement(row, col, value):
                    test_board = b.copy()
                    test_board.set_value(row, col, value)
                    solve_count(test_board)

        solve_count(board.copy())
        return count[0]
