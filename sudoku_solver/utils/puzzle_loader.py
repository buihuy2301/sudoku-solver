"""Load Sudoku puzzles from various sources."""

from pathlib import Path
from typing import List

from ..core.sudoku import SudokuBoard


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
