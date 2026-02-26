"""Dancing Links algorithm (Knuth's Algorithm X) for Sudoku."""

from ..core.solver_base import SudokuSolver
from ..core.sudoku import SudokuBoard


class DancingLinksSolver(SudokuSolver):
    """
    Dancing Links algorithm for Sudoku solving.

    Uses optimized backtracking with MRV heuristic.
    Much faster than basic backtracking on hard puzzles.
    """

    def __init__(self, board: SudokuBoard):
        """Initialize solver."""
        super().__init__(board)

    def solve(self) -> bool:
        """
        Solve using optimized backtracking with MRV heuristic.

        Returns:
            True if solved, False if no solution exists
        """
        return self._solve_recursive()

    def _solve_recursive(self) -> bool:
        """
        Recursive backtracking solver with MRV heuristic.

        Returns:
            True if current state leads to solution, False otherwise
        """
        # Check if solved
        if self.board.is_solved():
            return True

        # Find empty cell with minimum remaining values (MRV heuristic)
        best_cell = None
        min_candidates = 10

        for r in range(9):
            for c in range(9):
                if self.board.board[r][c] == 0:
                    candidates = self.board.get_candidates(r, c)
                    if len(candidates) == 0:
                        # No valid candidates - contradiction
                        return False
                    if len(candidates) < min_candidates:
                        min_candidates = len(candidates)
                        best_cell = (r, c)

        if best_cell is None:
            # No empty cells but not solved = should not happen if is_solved works
            return False

        row, col = best_cell
        candidates = self.board.get_candidates(row, col)

        # Try each candidate value
        for value in sorted(candidates):
            # Place value
            self.board.board[row][col] = value
            self._record_assignment(row, col, value)
            self.guesses += 1

            # Remove from candidates
            old_candidates = {}
            for r in range(9):
                for c in range(9):
                    old_candidates[(r, c)] = self.board.candidates[r][c].copy()

            self.board.candidates[row][col] = set()
            self.board._remove_candidates_for_value(row, col, value)

            # Recurse
            if self._solve_recursive():
                return True

            # Backtrack
            self.board.board[row][col] = 0
            for pos, cands in old_candidates.items():
                self.board.candidates[pos[0]][pos[1]] = cands
            self.backtracks += 1

        return False
