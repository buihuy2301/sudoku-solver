"""Load Sudoku puzzles from various sources."""

import random
from pathlib import Path
from typing import List

from ..core.sudoku import SudokuBoard
from .validators import Validators


class PuzzleLoader:
    """Load Sudoku puzzles from strings and files."""

    @staticmethod
    def from_string(puzzle_str: str) -> SudokuBoard:
        """
        Load puzzle from 81-character string.

        Args:
            puzzle_str: String of 81 digits (0 for empty cells)

        Returns:
            SudokuBoard instance

        Raises:
            ValueError: If string format is invalid
        """
        puzzle_str = puzzle_str.strip().replace(" ", "").replace("\n", "")

        if len(puzzle_str) != 81:
            raise ValueError(
                f"Puzzle string must be 81 characters, got {len(puzzle_str)}"
            )

        try:
            grid = []
            for i in range(9):
                row = []
                for j in range(9):
                    val = int(puzzle_str[i * 9 + j])
                    if not 0 <= val <= 9:
                        raise ValueError(f"Invalid value {val}")
                    row.append(val)
                grid.append(row)

            board = SudokuBoard(grid)
            return board
        except ValueError as e:
            raise ValueError(f"Invalid puzzle string: {e}") from e

    @staticmethod
    def from_file(filepath: str) -> List[SudokuBoard]:
        """
        Load puzzles from file (one puzzle per line, 81-character format).

        Args:
            filepath: Path to puzzle file

        Returns:
            List of SudokuBoard instances

        Raises:
            FileNotFoundError: If file doesn't exist
            ValueError: If file format is invalid
        """
        path = Path(filepath)
        if not path.exists():
            raise FileNotFoundError(f"Puzzle file not found: {filepath}")

        puzzles = []
        try:
            with open(path, "r", encoding="utf-8") as f:
                for line_num, line in enumerate(f, 1):
                    line = line.strip()
                    if line and not line.startswith("#"):
                        try:
                            board = PuzzleLoader.from_string(line)
                            puzzles.append(board)
                        except ValueError as e:
                            raise ValueError(
                                f"Invalid puzzle on line {line_num}: {e}"
                            ) from e
        except IOError as e:
            raise IOError(f"Error reading file {filepath}: {e}") from e

        return puzzles

    @staticmethod
    def from_grid(grid: List[List[int]]) -> SudokuBoard:
        """
        Load puzzle from 9x9 grid.

        Args:
            grid: 9x9 list of integers (0 for empty cells)

        Returns:
            SudokuBoard instance

        Raises:
            ValueError: If grid format is invalid
        """
        return SudokuBoard(grid)

    @staticmethod
    def exemplars() -> dict:
        """
        Get exemplar puzzles of various difficulties.

        Returns:
            Dictionary with difficulty level as key and puzzle string as value
        """
        return {
            "easy": (
                "530070000600195000098000060800060003400803001700020006"
                "060000280000419005000080079"
            ),
            "medium": (
                "003020600900305001001806400008102900700000008006708200"
                "002609500800203006005010300"
            ),
            "hard": (
                "006000070050080000000000006000010300080000020005030000"
                "100000000000070040030000200"
            ),
            "expert": (
                "006000070050080000000000006000010300080000020005030000"
                "100000000000070040030000200"
            ),
        }


class PuzzleGenerator:
    """Generate valid Sudoku puzzles of varying difficulty."""

    @staticmethod
    def _generate_complete_board() -> SudokuBoard:
        """
        Generate a complete, valid 9x9 Sudoku board.

        Returns:
            A complete SudokuBoard instance
        """
        grid = [[0] * 9 for _ in range(9)]
        PuzzleGenerator._fill_grid(grid)
        return SudokuBoard(grid)

    @staticmethod
    def _fill_grid(grid: List[List[int]]) -> bool:
        """
        Recursively fill the grid with valid numbers.

        Args:
            grid: 9x9 grid to fill

        Returns:
            True if successful, False otherwise
        """
        for row in range(9):
            for col in range(9):
                if grid[row][col] == 0:
                    # Try random numbers to make unique boards
                    numbers = list(range(1, 10))
                    random.shuffle(numbers)

                    for num in numbers:
                        if PuzzleGenerator._is_safe(grid, row, col, num):
                            grid[row][col] = num
                            if PuzzleGenerator._fill_grid(grid):
                                return True
                            grid[row][col] = 0

                    return False

        return True

    @staticmethod
    def _is_safe(grid: List[List[int]], row: int, col: int, num: int) -> bool:
        """
        Check if a number can be placed at a position.

        Args:
            grid: 9x9 grid
            row: Row index
            col: Column index
            num: Number to check (1-9)

        Returns:
            True if placement is valid, False otherwise
        """
        # Check row
        if num in grid[row]:
            return False

        # Check column
        if num in [grid[i][col] for i in range(9)]:
            return False

        # Check 3x3 box
        box_row, box_col = 3 * (row // 3), 3 * (col // 3)
        for i in range(box_row, box_row + 3):
            for j in range(box_col, box_col + 3):
                if grid[i][j] == num:
                    return False

        return True

    @staticmethod
    def generate(difficulty: str = "medium", given_cells: int = None) -> SudokuBoard:
        """
        Generate a valid Sudoku puzzle of specified difficulty or custom clue count.

        Args:
            difficulty: One of "easy", "medium", "hard", "very_hard" (ignored if given_cells is set)
            given_cells: Override difficulty with exact number of clues (15-54). If None, uses difficulty level.

        Returns:
            A valid SudokuBoard puzzle

        Raises:
            ValueError: If difficulty level or given_cells is invalid
        """
        # Use custom given_cells if provided
        if given_cells is not None:
            if not isinstance(given_cells, int) or given_cells < 15 or given_cells > 54:
                raise ValueError(
                    f"given_cells must be an integer between 15 and 54, got {given_cells}"
                )
            cells_to_remove = 81 - given_cells
        else:
            if difficulty not in ["easy", "medium", "hard", "very_hard"]:
                raise ValueError(
                    f"Difficulty must be easy, medium, hard, or very_hard, got {difficulty}"
                )

            # Number of cells to remove based on difficulty
            cells_to_remove_map = {
                "easy": 35,  # ~46 clues given
                "medium": 45,  # ~36 clues given
                "hard": 50,  # ~31 clues given
                "very_hard": 55,  # ~26 clues given
            }
            cells_to_remove = cells_to_remove_map[difficulty]

        max_attempts = 5  # Try up to 5 times to generate valid puzzle
        for attempt in range(max_attempts):
            # Generate complete board
            complete_board = PuzzleGenerator._generate_complete_board()

            # Create puzzle by removing cells
            puzzle_grid = [row[:] for row in complete_board.board]
            cells_removed = 0
            target_removals = cells_to_remove

            # Randomly remove cells while maintaining validity
            positions = [(r, c) for r in range(9) for c in range(9)]
            random.shuffle(positions)

            for row, col in positions:
                if cells_removed >= target_removals:
                    break

                # Save the value
                saved_val = puzzle_grid[row][col]
                puzzle_grid[row][col] = 0

                # Create board to validate
                test_board = SudokuBoard(puzzle_grid)

                # Check if still valid and has unique solution
                is_valid, _ = Validators.is_valid_puzzle(test_board)
                if is_valid and Validators.has_unique_solution(test_board):
                    cells_removed += 1
                else:
                    # Restore cell if it breaks validity
                    puzzle_grid[row][col] = saved_val

            # If we successfully created a puzzle, return it
            final_board = SudokuBoard(puzzle_grid)
            is_valid, _ = Validators.is_valid_puzzle(final_board)
            if is_valid:
                return final_board

        # Fallback: return a puzzle even if uniqueness check is uncertain
        final_board = SudokuBoard(puzzle_grid)
        return final_board
