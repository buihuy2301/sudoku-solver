"""Backtracking with Minimum Remaining Values (MRV) heuristic."""

from typing import Optional, Tuple
import time
import copy

from ..core.solver_base import SudokuSolver


class BacktrackingMRVSolver(SudokuSolver):
    """
    Backtracking with Minimum Remaining Values heuristic.

    Selects the cell with fewest possible values, reducing branching factor.
    Much faster than basic backtracking on hard puzzles.
    """

    def solve(self) -> bool:
        """
        Solve using backtracking with MRV heuristic.

        Returns:
            True if solved, False if no solution exists
        """
        return self._solve_recursive()

    def _solve_recursive(self) -> bool:
        """
        Recursive backtracking solver with MRV cell selection.

        Returns:
            True if current state leads to solution, False otherwise
        """
        # Check if solved
        if self.board.is_solved():
            return True

        # Select best cell (MRV heuristic)
        cell = self._select_best_cell()
        if cell is None:
            # No empty cells but not solved = contradiction
            return False

        row, col = cell
        candidates = self.board.get_candidates(row, col)
        if not candidates:
            # No valid candidates for this cell = contradiction
            return False
        
        # time.sleep(0.1)
        # Try each candidate value
        for value in sorted(candidates):
            # Place value
            self.board.board[row][col] = value
            self._record_assignment(row, col, value)
            self.guesses += 1

            # Update candidates for peers
            old_candidates = copy.deepcopy(self.board.candidates)
            self.board.candidates[row][col] = set()
            self.board._remove_candidates_for_value(row, col, value)

            # Recurse
            if self._solve_recursive():
                return True

            # Backtrack
            self.board.board[row][col] = 0
            self.board.candidates = old_candidates
            # Restore candidates (simplified - just reinitialize for cell)
            #self._restore_candidates_on_backtrack(row, col, value)
            self.backtracks += 1

        return False

    def _select_best_cell(self) -> Optional[Tuple[int, int]]:
        """
        Select the empty cell with minimum remaining values (MRV heuristic).

        Returns:
            Tuple of (row, col) for best cell, or None if no empty cells
        """
        best_cell = None
        min_candidates = 10

        for r in range(9):
            for c in range(9):
                if self.board.board[r][c] == 0:
                    num_candidates = len(self.board.candidates[r][c])
                    if num_candidates < min_candidates:
                        min_candidates = num_candidates
                        best_cell = (r, c)

        return best_cell

    def _restore_candidates_on_backtrack(self, row: int, col: int, value: int) -> None:
        """
        Restore candidates after backtracking (simplified approach).

        Args:
            row: Row index
            col: Column index
            value: Value that was removed
        """
        # Recalculate candidates for this cell
        # self.board.candidates[row][col] = set(range(1, 10))

        # Remove values in row, column, and box
        # for c in range(9):
        #     if c != col and self.board.board[row][c] != 0:
        #         self.board.candidates[row][col].discard(self.board.board[row][c])

        # for r in range(9):
        #     if r != row and self.board.board[r][col] != 0:
        #         self.board.candidates[row][col].discard(self.board.board[r][col])

        # box_row = (row // 3) * 3
        # box_col = (col // 3) * 3
        # for r in range(box_row, box_row + 3):
        #     for c in range(box_col, box_col + 3):
        #         if (r != row or c != col) and self.board.board[r][c] != 0:
        #             self.board.candidates[row][col].discard(self.board.board[r][c])
        for c in range(self.board.GRID_SIZE):
            if c != col:
                self.board.candidates[row][c].add(value)

        # Remove from column peers
        for r in range(self.board.GRID_SIZE):
            if r != row:
                self.board.candidates[r][col].add(value)

        # Remove from box peers
        box_row = (row // self.board.BOX_SIZE) * self.board.BOX_SIZE
        box_col = (col // self.board.BOX_SIZE) * self.board.BOX_SIZE
        for r in range(box_row, box_row + self.board.BOX_SIZE):
            for c in range(box_col, box_col + self.board.BOX_SIZE):
                if r != row or c != col:
                    self.board.candidates[r][c].add(value)
