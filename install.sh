#!/usr/bin/env bash
set -euo pipefail

echo "============================================"
echo "   AI Journalist Studio - Installation"
echo "============================================"
echo ""

# --------------------------------------------------
# Step 1: Check Python
# --------------------------------------------------
echo "[1/5] Checking Python..."

if command -v python3 &>/dev/null; then
    PY=python3
elif command -v python &>/dev/null; then
    PY=python
else
    echo "ERROR: Python is not installed."
    echo "Install it: https://www.python.org/downloads/"
    echo "Or via package manager: brew install python / apt install python3"
    exit 1
fi

pyver=$($PY --version 2>&1)
echo "    Found $pyver"
echo ""

# --------------------------------------------------
# Step 2: Check pip
# --------------------------------------------------
echo "[2/5] Checking pip..."

PIP=""
if command -v pip3 &>/dev/null; then
    PIP=pip3
elif command -v pip &>/dev/null; then
    PIP=pip
fi

if [ -z "$PIP" ]; then
    # Try python -m pip
    if $PY -m pip --version &>/dev/null; then
        PIP="$PY -m pip"
    else
        echo "ERROR: pip is not available."
        echo "Install it: $PY -m ensurepip --upgrade"
        echo "Or: apt install python3-pip / brew install python"
        exit 1
    fi
fi

echo "    pip is available"
echo ""

# --------------------------------------------------
# Step 3: Install requirements
# --------------------------------------------------
echo "[3/5] Installing Python dependencies..."

if [ "$PIP" = "$PY -m pip" ]; then
    $PY -m pip install -r requirements.txt
else
    $PIP install -r requirements.txt
fi

echo "    Dependencies installed successfully"
echo ""

# --------------------------------------------------
# Step 4: Check Ollama
# --------------------------------------------------
echo "[4/5] Checking Ollama..."

if ! command -v ollama &>/dev/null; then
    echo "WARNING: Ollama is not installed or not in PATH."
    echo "Install it: https://ollama.com/download"
    echo ""
    echo "  # macOS (also available as brew install ollama)"
    echo "  # Linux:"
    echo "  curl -fsSL https://ollama.com/install.sh | sh"
    echo ""
    echo "After installing, run:"
    echo "  ollama pull qwen2.5-coder:1.5b"
    echo "  ollama pull qwen2.5-coder:7b"
    echo "  ollama pull llama3.2:3b"
    echo "  ollama serve"
    echo ""
    OLLAMA_MISSING=1
else
    echo "    Found Ollama"
    echo ""

    # --------------------------------------------------
    # Step 5: Check models
    # --------------------------------------------------
    echo "[5/5] Checking Ollama models..."

    pull_model() {
        local model="$1"
        local label="$2"
        if ollama list 2>/dev/null | grep -q "$model"; then
            echo "    Model $model found"
        else
            echo "    Model $model not found."
            read -rp "    Pull it now? [Y/n]: " choice
            case "$choice" in
                n|N|no|No) echo "    Skipped. Pull later: ollama pull $model" ;;
                *) echo "    Pulling $model..."; ollama pull "$model" ;;
            esac
        fi
    }

    pull_model "qwen2.5-coder:1.5b" "fast research"
    pull_model "qwen2.5-coder:7b"   "deep research"
    pull_model "llama3.2:3b"        "writer"
fi

echo ""
echo "============================================"
echo "   Installation complete!"
echo "============================================"
echo ""
echo "Next steps:"
echo "  1. Start Ollama:     ollama serve"
echo "  2. Run journalist:   $PY journalist.py \"Your topic\""
echo "  3. Or open the UI:   $PY journalist.py --web"
echo ""

if [ -n "${OLLAMA_MISSING:-}" ]; then
    echo "NOTE: Ollama was not detected. Install it from:"
    echo "      https://ollama.com/download"
    echo ""
fi
