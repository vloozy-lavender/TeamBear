#!/bin/bash
echo "🚀 Roostoo Bot Setup Script"
echo "============================"

# Update system
echo "📦 Updating system packages..."
sudo dnf update -y

# Install Python 3
echo "🐍 Installing Python 3..."
sudo dnf install -y python3 python3-pip python3-venv

# Verify installation
python3 --version
pip3 --version

# Create virtual environment
echo "📁 Creating virtual environment..."
cd ~/roostoo-bot
python3 -m venv .venv

# Activate and install dependencies
echo "📦 Installing Python dependencies..."
source .venv/bin/activate
pip install --upgrade pip
pip install requests python-dotenv pandas numpy

# Create logs directory
mkdir -p logs
touch logs/trading.log

# Set permissions
chmod 600 config/.env

echo ""
echo "✅ Setup Complete!"
echo "=================="
echo "To activate venv: source .venv/bin/activate"
echo "To run bot: python main.py"
echo "To run in tmux: tmux new -s bot"
