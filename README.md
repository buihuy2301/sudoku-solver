# Sudoku Solver 🧩

A Python package for solving Sudoku puzzles using multiple advanced algorithms with an interactive web interface.

## Features

✨ **Multiple Solving Algorithms:**
- **Backtracking** - Classic recursive backtracking algorithm
- **Backtracking with MRV** - Minimum Remaining Values heuristic for faster solving
- **Naked Singles** - Constraint propagation technique
- **Dancing Links (Algorithm X)** - Knuth's Algorithm X for exact cover problems

🎨 **Interactive Web Interface:**
- Real-time visualization of the solving process
- Compare algorithm performance
- Load puzzles from preset library
- Metrics tracking and statistics

⚡ **Additional Features:**
- Puzzle validation
- Performance benchmarking
- Comprehensive test suite
- Type hints throughout

## Installation

### Prerequisites
- Python 3.11 or higher
- [uv](https://github.com/astral-sh/uv) package manager

### Quick Start

1. **Clone the repository**
```bash
git clone <repository-url>
cd sudoku-solver
```

2. **Using the setup script (macOS/Linux)**
```bash
chmod +x run_app.sh
./run_app.sh
```

3. **Manual setup**
```bash
# Install dependencies with uv
uv sync
```

## Usage

### Web Interface

Launch the interactive Streamlit application:

```bash
uv run streamlit run app.py
```

Then open your browser to `http://localhost:8501`

### Programmatic Usage

```python
from sudoku_solver.algorithms import BacktrackingSolver, DancingLinksSolver
from sudoku_solver.core.sudoku import SudokuBoard

# Create a board from a puzzle string
puzzle = "4.....8.5.3..........7......2.....6.....8.3.....9.2......5.1.3..............4"
board = SudokuBoard.from_string(puzzle)

# Solve using backtracking with MRV heuristic
from sudoku_solver.algorithms import BacktrackingMRVSolver
solver = BacktrackingMRVSolver()
solution = solver.solve(board)

# Check if solved
if solution.is_complete():
    print(solution.to_string())
```

## Project Structure

```
sudoku-solver/
├── app.py                          # Streamlit web application
├── benchmarks.py                   # Performance benchmarking
├── profiler.py                     # Code profiling utilities
├── validate.py                     # Puzzle validation
├── run_app.sh                      # App launcher script
├── run_tests.py                    # Test runner
│
├── sudoku_solver/                  # Main package
│   ├── algorithms/                 # Solving algorithms
│   │   ├── backtracking.py
│   │   ├── backtracking_mrv.py
│   │   ├── dancing_links.py
│   │   └── naked_singles.py
│   │
│   ├── core/                       # Core functionality
│   │   ├── solver_base.py          # Abstract base solver
│   │   └── sudoku.py               # Sudoku board representation
│   │
│   ├── utils/                      # Utilities
│   │   ├── puzzle_loader.py        # Puzzle loading utilities
│   │   └── validators.py           # Validation functions
│   │
│   └── visualization/              # Visualization
│       └── metrics.py              # Performance metrics
│
└── tests/                          # Test suite
    ├── test_algorithms.py          # Algorithm tests
    └── test_integration.py         # Integration tests
```

## Algorithms Explained

### 1. Backtracking
A recursive algorithm that:
- Tries placing numbers in empty cells
- Backtracks when a constraint is violated
- Simple but can be slow on hard puzzles

**Complexity:** O(9^n) worst case, where n is the number of empty cells

### 2. Backtracking with MRV (Minimum Remaining Values)
An optimized backtracking that:
- Selects the cell with fewest possible values
- Reduces the search space significantly
- Much faster than basic backtracking

**Complexity:** Better average case than standard backtracking

### 3. Naked Singles
A constraint propagation technique:
- Identifies cells with only one possible value
- Eliminates candidates based on Sudoku rules
- Efficient for easier puzzles
- May need combination with other techniques for hard puzzles

**Complexity:** Linear in puzzle size

### 4. Dancing Links (Algorithm X)
Knuth's exact cover algorithm:
- Models Sudoku as an exact cover problem
- Uses circular doubly-linked lists for efficiency
- Very fast and reliable
- Industry-standard approach

**Complexity:** Efficient for most practical Sudoku puzzles

## Testing

Run the test suite:

```bash
# Using pytest
pytest

# Or use the test runner script
python run_tests.py
```

## Performance Benchmarking

Compare algorithm performance:

```bash
python benchmarks.py
```

This will generate timing statistics for all algorithms on various difficulty levels.

## Development

### Code Style
- Type hints required
- Follow PEP 8
- Docstrings for all public functions

### Adding a New Algorithm

1. Create a new file in `sudoku_solver/algorithms/`
2. Inherit from `SolverBase`
3. Implement the `solve()` method
4. Add tests in `tests/test_algorithms.py`
5. Register in `sudoku_solver/algorithms/__init__.py`

Example:

```python
from sudoku_solver.core.solver_base import SolverBase
from sudoku_solver.core.sudoku import SudokuBoard

class MyCustomSolver(SolverBase):
    """Your custom solver implementation."""
    
    def solve(self, board: SudokuBoard) -> SudokuBoard:
        """Solve the Sudoku puzzle."""
        # Implementation here
        return board
```

## Dependencies

- **numpy** - Numerical computations
- **pandas** - Data manipulation
- **streamlit** - Web interface
- **pytest** - Testing framework


## Contributing

Contributions are welcome! Please:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git comConsider using enumerate instead of iterating with range and lenPylintC0200:consider-using-enumerate
mit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request


## Acknowledgments

- Donald Knuth for Algorithm X (Dancing Links)
- Sudoku community for puzzle datasets
- Streamlit for the web framework

---

For questions or issues, please open an issue on GitHub.
