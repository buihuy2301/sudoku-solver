"""
Sudoku Solver - Interactive Streamlit Web Application

Visualize and compare 4 different Sudoku-solving algorithms:
- Backtracking
- Backtracking with MRV Heuristic
- Naked Singles Constraint Propagation
- Dancing Links (Algorithm X)
"""

import time
from typing import Any, Dict, List, Optional, Tuple

import pandas as pd
import streamlit as st

from sudoku_solver.algorithms.backtracking import BacktrackingSolver
from sudoku_solver.algorithms.backtracking_mrv import BacktrackingMRVSolver
from sudoku_solver.algorithms.dancing_links import DancingLinksSolver
from sudoku_solver.algorithms.naked_singles import NakedSinglesSolver
from sudoku_solver.core.sudoku import SudokuBoard
from sudoku_solver.utils.puzzle_loader import PuzzleLoader, PuzzleGenerator
from sudoku_solver.utils.validators import Validators

# Page configuration
st.set_page_config(
    page_title="Sudoku Solver",
    page_icon="🧩",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Custom CSS
st.markdown(
    """
<style>
    .sudoku-board {
        display: grid;
        grid-template-columns: repeat(9, 1fr);
        gap: 2px;
        padding: 10px;
        background-color: #000;
        border: 2px solid #000;
    }
    .sudoku-cell {
        aspect-ratio: 1;
        display: flex;
        align-items: center;
        justify-content: center;
        font-weight: 400;
        font-size: 80px;
        border: 1px solid #ccc;
    }
    .cell-given {
        background-color: #e8e8e8;
        color: #000;
    }
    .cell-solved {
        background-color: #a8d8ff;
        color: #000;
    }
    .cell-current {
        background-color: #fff9c4;
        color: #000;
    }
    .cell-empty {
        background-color: #fff;
        color: #ccc;
    }
    .cell-conflict {
        background-color: #ffcdd2;
        color: #000;
    }
</style>
""",
    unsafe_allow_html=True,
)


class SudokuVisualizerApp:
    """Main Streamlit application for Sudoku visualization and solving."""

    ALGORITHMS = {
        "Backtracking": BacktrackingSolver,
        "Backtracking + MRV": BacktrackingMRVSolver,
        "Naked Singles": NakedSinglesSolver,
        "Dancing Links": DancingLinksSolver,
    }

    # Sample puzzle difficulty levels (will be generated dynamically)
    PUZZLE_DIFFICULTIES = ["Easy", "Medium", "Hard", "Very Hard"]

    def __init__(self):
        """Initialize the application."""
        self._init_session_state()

    @staticmethod
    def _init_session_state():
        """Initialize session state variables."""
        if "board" not in st.session_state:
            st.session_state.board = None
        if "original_board" not in st.session_state:
            st.session_state.original_board = None
        if "solver" not in st.session_state:
            st.session_state.solver = None
        if "current_step" not in st.session_state:
            st.session_state.current_step = 0
        if "solving" not in st.session_state:
            st.session_state.solving = False
        if "algorithm_results" not in st.session_state:
            st.session_state.algorithm_results = {}
        if "animation_playing" not in st.session_state:
            st.session_state.animation_playing = False
        if "animation_speed" not in st.session_state:
            st.session_state.animation_speed = 100
        if "animate_now" not in st.session_state:
            st.session_state.animate_now = False

    def load_puzzle(self, puzzle_str: str):
        """Load a puzzle from string with validation."""
        try:
            board = PuzzleLoader.from_string(puzzle_str)
            
            # Validate the puzzle
            is_valid, error_msg = Validators.is_valid_puzzle(board)
            if not is_valid:
                st.error(f"Invalid Sudoku puzzle: {error_msg}")
                return False
            
            st.session_state.original_board = board.copy()
            st.session_state.board = board.copy()
            st.session_state.current_step = 0
            st.session_state.solver = None
            st.session_state.algorithm_results = {}
            return True
        except Exception as e:
            st.error(f"Error loading puzzle: {e}")
            return False

    def display_board(
        self,
        board: SudokuBoard,
        current_step_history: Optional[List[Tuple[int, int, int]]] = None,
        current_step_index: int = 0,
        title: str = "Sudoku Board",
    ):
        """Display the Sudoku board with colored cells."""
        st.subheader(title)

        # Create the HTML grid
        html = '<div class="sudoku-board">'

        assigned_cells = set()
        if current_step_history:
            assigned_cells = {
                (r, c) for r, c, _ in current_step_history[:current_step_index]
            }

        for row in range(9):
            for col in range(9):
                value = board.board[row][col]
                is_given = st.session_state.original_board.board[row][col] != 0
                is_current = (row, col) in assigned_cells if assigned_cells else False

                # Determine cell class
                if is_given:
                    cell_class = "cell-given"
                elif is_current and value != 0:
                    cell_class = "cell-current"
                elif value != 0:
                    cell_class = "cell-solved"
                else:
                    cell_class = "cell-empty"

                display_value = str(value) if value != 0 else "·"
                html += f'<div class="sudoku-cell {cell_class}">{display_value}</div>'

        html += "</div>"
        st.markdown(html, unsafe_allow_html=True)

    def solve_with_algorithm(
        self, algorithm_class, board: SudokuBoard
    ) -> Dict[str, Any]:
        """Solve puzzle with specified algorithm and track statistics."""
        try:
            solver = algorithm_class(board)
            start_time = time.time()
            success = solver.solve()
            elapsed = time.time() - start_time

            stats = solver.get_statistics()
            stats["solved"] = success
            stats["execution_time"] = elapsed
            stats["step_history"] = solver.step_history

            return {
                "solver": solver,
                "success": success,
                "stats": stats,
                "board": solver.board.copy(),
            }
        except Exception as e:
            st.error(f"Error solving with {algorithm_class.__name__}: {e}")
            return None

    def run_single_algorithm(self):
        """Run and visualize a single algorithm."""
        if st.session_state.board is None:
            st.warning("Please load a puzzle first")
            return

        col1, col2 = st.columns([3, 1])

        # Main visualization area
        with col1:
            st.subheader("Sudoku Solver - Live Visualization")

            # Display board container
            board_container = st.empty()

            # Show current board state
            if st.session_state.solver and st.session_state.solver.step_history:
                current_board = st.session_state.original_board.copy()
                for row, col, value in st.session_state.solver.step_history[
                    : st.session_state.current_step
                ]:
                    current_board.board[row][col] = value

                with board_container:
                    self.display_board(
                        current_board,
                        st.session_state.solver.step_history,
                        st.session_state.current_step,
                        title="",
                    )
            else:
                with board_container:
                    self.display_board(st.session_state.original_board, title="")

        # Control panel
        with col2:
            st.subheader("Controls")
            selected_algo = st.radio(
                "Select Algorithm",
                list(self.ALGORITHMS.keys()),
                key="single_algo_select",
            )

            # Animation speed slider
            animation_speed = st.slider(
                "Animation Speed",
                min_value=10,
                max_value=500,
                value=st.session_state.animation_speed,
                step=10,
                help="Lower = slower, Higher = faster",
            )
            st.session_state.animation_speed = animation_speed

            if st.button("🚀 Solve", key="single_solve", use_container_width=True):
                st.session_state.board = st.session_state.original_board.copy()
                result = self.solve_with_algorithm(
                    self.ALGORITHMS[selected_algo], st.session_state.board
                )

                if result:
                    st.session_state.solver = result["solver"]
                    st.session_state.current_step = 0
                    st.session_state.animation_playing = True
                    st.session_state.animate_now = True

            # Animation controls (moved to control panel)
            max_steps = 0
            if st.session_state.solver and st.session_state.solver.step_history:
                st.divider()
                max_steps = len(st.session_state.solver.step_history)

                # Progress display container
                progress_container = st.empty()
                progress_container.metric(
                    "Progress", f"{st.session_state.current_step}/{max_steps}"
                )

                # Play/Pause buttons
                btn_col1, btn_col2 = st.columns(2)
                with btn_col1:
                    if st.button(
                        "▶ Play",
                        key="play_btn",
                        disabled=st.session_state.animation_playing,
                        use_container_width=True,
                    ):
                        st.session_state.animation_playing = True
                        st.session_state.animate_now = True
                with btn_col2:
                    if st.button(
                        "⏸ Pause",
                        key="pause_btn",
                        disabled=not st.session_state.animation_playing,
                        use_container_width=True,
                    ):
                        st.session_state.animation_playing = False

                # Step control
                if st.session_state.animation_playing:
                    pass
                else:
                    new_step = st.slider(
                        "Step",
                        min_value=0,
                        max_value=max_steps,
                        value=st.session_state.current_step,
                        key="animation_slider",
                    )
                    st.session_state.current_step = new_step

            # Run animation loop
            if st.session_state.animate_now:
                while (
                    st.session_state.animation_playing
                    and st.session_state.current_step < max_steps
                ):
                    # Create board at current step
                    current_board = st.session_state.original_board.copy()
                    for row, col, value in st.session_state.solver.step_history[
                        : st.session_state.current_step
                    ]:
                        current_board.board[row][col] = value

                    # Update board
                    with board_container:
                        self.display_board(
                            current_board,
                            st.session_state.solver.step_history,
                            st.session_state.current_step,
                            title="",
                        )

                    # Update progress
                    progress_container.metric(
                        "Progress", f"{st.session_state.current_step}/{max_steps}"
                    )

                    time.sleep((600 - animation_speed) / 1000)
                    st.session_state.current_step += 1

                st.session_state.animate_now = False
                st.session_state.animation_playing = False
                st.rerun()

        # Display statistics at bottom
        st.divider()
        st.subheader("Statistics")

        if st.session_state.solver:
            stats_col1, stats_col2, stats_col3, stats_col4, stats_col5 = st.columns(5)
            stats = st.session_state.solver.get_statistics()

            with stats_col1:
                st.metric("Solved", "✓ Yes" if stats["solved"] else "✗ No")
            with stats_col2:
                st.metric("Time", f"{stats['execution_time']*1000:.2f} ms")
            with stats_col3:
                st.metric("Cells", stats["cells_assigned"])
            with stats_col4:
                st.metric("Guesses", stats["guesses"])
            with stats_col5:
                st.metric("Backtracks", stats["backtracks"])
        else:
            st.info("Run an algorithm to see statistics")

    def run_comparison_mode(self):
        """Run all algorithms side-by-side for comparison."""
        if st.session_state.board is None:
            st.warning("Please load a puzzle first")
            return

        # Load original
        st.subheader("Original Puzzle")
        col1, col2, col3, col4 = st.columns(4)

        with col1:
            self.display_board(st.session_state.original_board, title="")

        # Solve button
        cols = st.columns(5)
        with cols[2]:
            if st.button("🚀 Run All Algorithms", key="compare_solve"):
                with st.spinner("Solving with all algorithms..."):
                    st.session_state.board = st.session_state.original_board.copy()
                    st.session_state.algorithm_results = {}

                    for algo_name, algo_class in self.ALGORITHMS.items():
                        board_copy = st.session_state.original_board.copy()
                        result = self.solve_with_algorithm(algo_class, board_copy)
                        if result:
                            st.session_state.algorithm_results[algo_name] = result

                    st.rerun()

        # Display results if available
        if st.session_state.algorithm_results:
            st.divider()
            st.subheader("Results Comparison")

            # Display solutions
            st.markdown("### Solutions")
            cols = st.columns(4)

            for idx, (algo_name, result) in enumerate(
                st.session_state.algorithm_results.items()
            ):
                with cols[idx]:
                    st.markdown(f"**{algo_name}**")
                    self.display_board(result["board"], title="")

                    if result["stats"]["solved"]:
                        st.success("✓ Solved")
                    else:
                        st.error("✗ Not solved")

            # Display statistics comparison table
            st.markdown("### Statistics Comparison")

            stats_data = []
            for algo_name, result in st.session_state.algorithm_results.items():
                stats = result["stats"]
                stats_data.append(
                    {
                        "Algorithm": algo_name,
                        "Solved": "✓" if stats["solved"] else "✗",
                        "Time (ms)": f"{stats['execution_time']*1000:.3f}",
                        "Cells": stats["cells_assigned"],
                        "Guesses": stats["guesses"],
                        "Backtracks": stats["backtracks"],
                    }
                )

            df = pd.DataFrame(stats_data)
            st.dataframe(df, use_container_width=True)

            # Performance ranking
            st.markdown("### Performance Ranking")

            sorted_results = sorted(
                st.session_state.algorithm_results.items(),
                key=lambda x: x[1]["stats"]["execution_time"],
            )

            ranking_data = []
            for rank, (algo_name, result) in enumerate(sorted_results, 1):
                ranking_data.append(
                    {
                        "Rank": rank,
                        "Algorithm": algo_name,
                        "Time (ms)": f"{result['stats']['execution_time']*1000:.3f}",
                    }
                )

            df_ranking = pd.DataFrame(ranking_data)
            st.dataframe(df_ranking, use_container_width=True)

            # Analysis
            fastest = sorted_results[0][0]
            slowest = sorted_results[-1][0]
            speedup = (
                st.session_state.algorithm_results[slowest]["stats"]["execution_time"]
                / st.session_state.algorithm_results[fastest]["stats"]["execution_time"]
            )

            st.info(
                f"🏆 **Fastest**: {fastest} | "
                f"🐢 **Slowest**: {slowest} | "
                f"⚡ **Speedup**: {speedup:.1f}x"
            )

    def sidebar(self):
        """Render the sidebar with controls."""
        st.sidebar.title("🧩 Sudoku Solver")
        st.sidebar.divider()

        # Puzzle Input Section
        st.sidebar.subheader("📥 Load Puzzle")
        input_method = st.sidebar.radio(
            "Input Method",
            ["Sample Puzzle", "Paste String", "Upload File"],
            key="input_method",
        )

        if input_method == "Sample Puzzle":
            difficulty = st.sidebar.selectbox(
                "Select Difficulty", self.PUZZLE_DIFFICULTIES, key="difficulty_select"
            )
            if st.sidebar.button("🔄 Generate & Load Sample", key="load_sample"):
                with st.spinner(f"Generating {difficulty} puzzle..."):
                    try:
                        # Generate a new puzzle each time
                        puzzle = PuzzleGenerator.generate(difficulty.lower().replace(" ", "_"))
                        # Convert board to string format
                        puzzle_str = "".join(
                            str(puzzle.board[r][c])
                            for r in range(9)
                            for c in range(9)
                        )
                        if self.load_puzzle(puzzle_str):
                            st.success(f"✓ Generated {difficulty} puzzle")
                            st.rerun()
                    except Exception as e:
                        st.error(f"Error generating puzzle: {e}")

        elif input_method == "Paste String":
            puzzle_str = st.sidebar.text_area(
                "Paste 81-digit puzzle (0 for empty)",
                height=80,
                placeholder="e.g., 530070000600195000098000060...",
                key="puzzle_paste",
            )
            if st.sidebar.button("Load Puzzle", key="load_paste"):
                if puzzle_str.strip():
                    if self.load_puzzle(puzzle_str):
                        st.rerun()

        elif input_method == "Upload File":
            uploaded_file = st.sidebar.file_uploader(
                "Upload puzzle file (one puzzle per line)",
                type=["txt"],
                key="upload_file",
            )
            if uploaded_file and st.sidebar.button("Load from File", key="load_file"):
                try:
                    content = uploaded_file.read().decode("utf-8")
                    puzzles = content.strip().split("\n")
                    selected_idx = st.sidebar.selectbox(
                        "Select Puzzle",
                        range(len(puzzles)),
                        format_func=lambda i: f"Puzzle {i+1}",
                    )
                    if self.load_puzzle(puzzles[selected_idx]):
                        st.rerun()
                except Exception as e:
                    st.sidebar.error(f"Error reading file: {e}")

        st.sidebar.divider()

        # Mode Selection
        st.sidebar.subheader("🎯 Solve Mode")
        mode = st.sidebar.radio(
            "Select Mode", ["Single Algorithm", "Compare All"], key="solve_mode"
        )

        st.sidebar.divider()

        # Display current puzzle status
        if st.session_state.board:
            st.sidebar.subheader("Puzzle Status")
            empty_count = sum(
                1
                for r in range(9)
                for c in range(9)
                if st.session_state.board.board[r][c] == 0
            )
            st.sidebar.info(f"Empty cells: **{empty_count}**")

        return mode

    def main(self):
        """Main application logic."""
        st.title("🧩 Sudoku Solver")
        st.markdown(
            "Visualize and compare 4 different solving algorithms: "
            "**Backtracking**, **Backtracking+MRV**, **Naked Singles**, and **Dancing Links**"
        )

        # Sidebar
        mode = self.sidebar()

        # Main content
        if st.session_state.board is None:
            st.info(
                "👈 **Start by loading a puzzle** in the sidebar. "
                "You can use a sample puzzle, paste an 81-digit string, or upload a file."
            )
            return

        st.divider()

        # Route to appropriate mode
        if mode == "Single Algorithm":
            self.run_single_algorithm()
        else:
            self.run_comparison_mode()


def main():
    """Application entry point."""
    app = SudokuVisualizerApp()
    app.main()


if __name__ == "__main__":
    main()
