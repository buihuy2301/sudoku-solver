#!/bin/bash
# Sudoku Solver - Streamlit App Launcher

echo "🧩 Sudoku Solver - Interactive Web App"
echo "========================================"
echo ""

# Check if we're in the correct directory
if [ ! -f "app.py" ]; then
    echo "❌ Error: app.py not found. Please run this script from the sudoku-solver directory."
    exit 1
fi

# Sync dependencies with uv
echo "⚙️  Syncing dependencies..."
uv sync
echo "✓ Dependencies synced"

echo ""
echo "🚀 Starting Sudoku Solver web app..."
echo "📍 The app will open at: http://localhost:8501"
echo ""
echo "Press Ctrl+C to stop the server"
echo "========================================"
echo ""

# Run the Streamlit app
uv run streamlit run app.py
