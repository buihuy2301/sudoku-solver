"""Sudoku board representation and validation."""

import copy
from typing import List, Optional, Set, Tuple


class SudokuBoard:
    """Represents a 9x9 Sudoku board with state management and validation."""

    GRID_SIZE = 9
    BOX_SIZE = 3
    EMPTY = 0

    def __init__(self, grid: Optional[List[List[int]]] = None):
        """
        Initialize a Sudoku board.

        Args:
            grid: 9x9 grid as list of lists. 0 represents empty cells.
                  If None, creates an empty board.
        """
        if grid is None:
            self.board = [
                [self.EMPTY for _ in range(self.GRID_SIZE)]
                for _ in range(self.GRID_SIZE)
            ]
            self.initial_board = copy.deepcopy(self.board)
        else:
            if len(grid) != self.GRID_SIZE or any(
                len(row) != self.GRID_SIZE for row in grid
            ):
                raise ValueError("Grid must be 9x9")
            self.board = [row[:] for row in grid]
            self.initial_board = copy.deepcopy(self.board)

        self.candidates = self._initialize_candidates()

    def _initialize_candidates(self) -> List[List[Set[int]]]:
        """
        Initialize possible values for each cell.

        Returns:
            3D structure: candidates[row][col] = set of possible values
        """
        candidates = [
            [
                (
                    set(range(1, self.GRID_SIZE + 1))
                    if self.board[r][c] == self.EMPTY
                    else set()
                )
                for c in range(self.GRID_SIZE)
            ]
            for r in range(self.GRID_SIZE)
        ]

        # Remove values based on initial board state
        for r in range(self.GRID_SIZE):
            for c in range(self.GRID_SIZE):
                if self.board[r][c] != self.EMPTY:
                    self._remove_candidates_for_value(
                        r, c, self.board[r][c], candidates
                    )

        return candidates

    def _remove_candidates_for_value(
        self,
        row: int,
        col: int,
        value: int,
        candidates: Optional[List[List[Set[int]]]] = None,
    ) -> None:
        """
        Remove a value from candidates of all peers of a cell.

        Args:
            row: Row index
            col: Column index
            value: Value to remove
            candidates: Optional candidates structure to update. If None, uses self.candidates
        """
        if candidates is None:
            candidates = self.candidates

        target_candidates = candidates

        # Remove from row peers
        for c in range(self.GRID_SIZE):
            if c != col:
                target_candidates[row][c].discard(value)

        # Remove from column peers
        for r in range(self.GRID_SIZE):
            if r != row:
                target_candidates[r][col].discard(value)

        # Remove from box peers
        box_row = (row // self.BOX_SIZE) * self.BOX_SIZE
        box_col = (col // self.BOX_SIZE) * self.BOX_SIZE
        for r in range(box_row, box_row + self.BOX_SIZE):
            for c in range(box_col, box_col + self.BOX_SIZE):
                if r != row or c != col:
                    target_candidates[r][c].discard(value)

    def get_candidates(self, row: int, col: int) -> Set[int]:
        """
        Get possible values for a cell.

        Args:
            row: Row index
            col: Column index

        Returns:
            Set of possible values for the cell
        """
        if self.board[row][col] != self.EMPTY:
            return set()
        return self.candidates[row][col].copy()

    def set_value(self, row: int, col: int, value: int) -> bool:
        """
        Set a cell value with validation.

        Args:
            row: Row index
            col: Column index
            value: Value to set (1-9, or 0 to clear)

        Returns:
            True if value set successfully, False if invalid
        """
        if not (0 <= row < self.GRID_SIZE and 0 <= col < self.GRID_SIZE):
            return False

        if value != self.EMPTY:
            if not (1 <= value <= self.GRID_SIZE):
                return False

            # Check if value is already in row, column, or box
            if not self._is_valid_placement(row, col, value):
                return False

        self.board[row][col] = value

        # Update candidates
        if value == self.EMPTY:
            self.candidates[row][col] = set(range(1, self.GRID_SIZE + 1))
            # Recalculate candidates (simplified - remove values in row/col/box)
            for c in range(self.GRID_SIZE):
                if c != col and self.board[row][c] != self.EMPTY:
                    self.candidates[row][col].discard(self.board[row][c])
            for r in range(self.GRID_SIZE):
                if r != row and self.board[r][col] != self.EMPTY:
                    self.candidates[row][col].discard(self.board[r][col])
            box_row = (row // self.BOX_SIZE) * self.BOX_SIZE
            box_col = (col // self.BOX_SIZE) * self.BOX_SIZE
            for r in range(box_row, box_row + self.BOX_SIZE):
                for c in range(box_col, box_col + self.BOX_SIZE):
                    if (r != row or c != col) and self.board[r][c] != self.EMPTY:
                        self.candidates[row][col].discard(self.board[r][c])
        else:
            self.candidates[row][col] = set()
            self._remove_candidates_for_value(row, col, value)

        return True

    def _is_valid_placement(self, row: int, col: int, value: int) -> bool:
        """
        Check if a value can be placed at a cell position.

        Args:
            row: Row index
            col: Column index
            value: Value to check

        Returns:
            True if placement is valid, False otherwise
        """
        # Check row
        for c in range(self.GRID_SIZE):
            if c != col and self.board[row][c] == value:
                return False

        # Check column
        for r in range(self.GRID_SIZE):
            if r != row and self.board[r][col] == value:
                return False

        # Check box
        box_row = (row // self.BOX_SIZE) * self.BOX_SIZE
        box_col = (col // self.BOX_SIZE) * self.BOX_SIZE
        for r in range(box_row, box_row + self.BOX_SIZE):
            for c in range(box_col, box_col + self.BOX_SIZE):
                if (r != row or c != col) and self.board[r][c] == value:
                    return False

        return True

    def is_valid(self) -> bool:
        """
        Check if current board state is valid (no conflicts).

        Returns:
            True if valid, False otherwise
        """
        # Check rows
        for r in range(self.GRID_SIZE):
            filled_values = [
                self.board[r][c]
                for c in range(self.GRID_SIZE)
                if self.board[r][c] != self.EMPTY
            ]
            if len(filled_values) != len(set(filled_values)):
                return False

        # Check columns
        for c in range(self.GRID_SIZE):
            filled_values = [
                self.board[r][c]
                for r in range(self.GRID_SIZE)
                if self.board[r][c] != self.EMPTY
            ]
            if len(filled_values) != len(set(filled_values)):
                return False

        # Check boxes
        for box_r in range(0, self.GRID_SIZE, self.BOX_SIZE):
            for box_c in range(0, self.GRID_SIZE, self.BOX_SIZE):
                filled_values = [
                    self.board[r][c]
                    for r in range(box_r, box_r + self.BOX_SIZE)
                    for c in range(box_c, box_c + self.BOX_SIZE)
                    if self.board[r][c] != self.EMPTY
                ]
                if len(filled_values) != len(set(filled_values)):
                    return False

        return True

    def is_solved(self) -> bool:
        """
        Check if puzzle is completely solved.

        Returns:
            True if all cells filled and board is valid, False otherwise
        """
        # Check if all cells are filled
        for r in range(self.GRID_SIZE):
            for c in range(self.GRID_SIZE):
                if self.board[r][c] == self.EMPTY:
                    return False

        # Check validity
        return self.is_valid()

    def get_empty_cells(self) -> List[Tuple[int, int]]:
        """
        Get list of empty cell positions.

        Returns:
            List of (row, col) tuples for empty cells
        """
        empty_cells = []
        for r in range(self.GRID_SIZE):
            for c in range(self.GRID_SIZE):
                if self.board[r][c] == self.EMPTY:
                    empty_cells.append((r, c))
        return empty_cells

    def copy(self) -> "SudokuBoard":
        """
        Create a deep copy of the board.

        Returns:
            New SudokuBoard instance with copied state
        """
        new_board = SudokuBoard(copy.deepcopy(self.board))
        new_board.initial_board = copy.deepcopy(self.initial_board)
        return new_board

    def reset(self) -> None:
        """Reset board to its initial state."""
        self.board = copy.deepcopy(self.initial_board)
        self.candidates = self._initialize_candidates()

    def __str__(self) -> str:
        """Pretty print the board."""
        lines = []
        for r in range(self.GRID_SIZE):
            if r % self.BOX_SIZE == 0 and r != 0:
                lines.append("------+-------+------")

            row_str = ""
            for c in range(self.GRID_SIZE):
                if c % self.BOX_SIZE == 0 and c != 0:
                    row_str += "| "

                val = self.board[r][c]
                row_str += str(val) if val != self.EMPTY else "."
                row_str += " "

            lines.append(row_str)

        return "\n".join(lines)

    def to_string(self) -> str:
        """Convert board to 81-character string representation."""
        chars = []
        for r in range(self.GRID_SIZE):
            for c in range(self.GRID_SIZE):
                val = self.board[r][c]
                chars.append(str(val) if val != self.EMPTY else "0")
        return "".join(chars)

    def from_string(self, s: str) -> None:
        """Load board from 81-character string."""
        if len(s) != self.GRID_SIZE * self.GRID_SIZE:
            raise ValueError("String must be exactly 81 characters")

        self.board = []
        for r in range(self.GRID_SIZE):
            row = []
            for c in range(self.GRID_SIZE):
                idx = r * self.GRID_SIZE + c
                val = int(s[idx])
                if not 0 <= val <= self.GRID_SIZE:
                    raise ValueError(f"Invalid value {val} at position {idx}")
                row.append(val)
            self.board.append(row)

        self.initial_board = copy.deepcopy(self.board)
        self.candidates = self._initialize_candidates()
