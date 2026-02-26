"""Basic backtracking algorithm for Sudoku solving."""

from ..core.solver_base import SudokuSolver


class BacktrackingSolver(SudokuSolver):
    """Basic backtracking algorithm - O(9^n) where n is number of empty cells."""

    def solve(self) -> bool:
        """
        Solve using basic backtracking.

        Returns:
            True if solved, False if no solution exists
        """
        return self._solve_recursive()

    def _solve_recursive(self) -> bool:
        """
        Recursive backtracking solver.

        Returns:
            True if current state leads to solution, False otherwise
        """
        # Find next empty cell
        empty_cells = self.board.get_empty_cells()
        if not empty_cells:
            # All cells filled - check if valid
            return self.board.is_solved()

        row, col = empty_cells[0]

        # Try each value 1-9
        for value in range(1, 10):
            if self._is_valid_move(row, col, value):
                # Place value
                self.board.board[row][col] = value
                self._record_assignment(row, col, value)
                self.guesses += 1

                # Recurse
                if self._solve_recursive():
                    return True

                # Backtrack
                self.board.board[row][col] = 0
                self.backtracks += 1

        return False

    def _is_valid_move(self, row: int, col: int, value: int) -> bool:
        """
        Check if a value can be placed at a position.

        Args:
            row: Row index
            col: Column index
            value: Value to check (1-9)

        Returns:
            True if placement is valid, False otherwise
        """
        return self.board._is_valid_placement(row, col, value)
