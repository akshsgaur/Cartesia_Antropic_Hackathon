#!/bin/bash

# RepoBuddy Line Agent Setup Script
# This script sets up the complete Line agent deployment

echo "🚀 Setting up RepoBuddy Line Agent..."

# Step 1: Install Cartesia CLI
echo "📦 Installing Cartesia CLI..."
if ! command -v cartesia &> /dev/null; then
    curl -fsSL https://cartesia.sh | sh
    echo "✅ Cartesia CLI installed"
else
    echo "✅ Cartesia CLI already installed"
fi

# Step 2: Install Line SDK
echo "📦 Installing Cartesia Line SDK..."
cd server
pip install cartesia-line
cd ..
echo "✅ Line SDK installed"

# Step 3: Install server dependencies
echo "📦 Installing server dependencies..."
cd server
pip install -r requirements.txt
cd ..
echo "✅ Server dependencies installed"

# Step 4: Authenticate with Cartesia
echo "🔐 Authenticating with Cartesia..."
if [ -z "$CARTESIA_API_KEY" ]; then
    echo "Please set CARTESIA_API_KEY environment variable"
    echo "export CARTESIA_API_KEY=your_api_key_here"
    exit 1
fi

cartesia auth login
echo "✅ Authenticated with Cartesia"

# Step 5: Set up ngrok tunnel
echo "🌐 Setting up ngrok tunnel..."
if ! command -v ngrok &> /dev/null; then
    echo "Installing ngrok..."
    if [[ "$OSTYPE" == "darwin"* ]]; then
        brew install ngrok
    else
        echo "Please install ngrok manually: https://ngrok.com/download"
        exit 1
    fi
fi

# Start ngrok in background
echo "Starting ngrok tunnel..."
ngrok http 3000 > /dev/null 2>&1 &
NGROK_PID=$!

# Wait for ngrok to initialize
sleep 5

# Get ngrok URL
NGROK_URL=$(curl -s http://127.0.0.1:4040/api/tunnels | grep -o 'https://[^"]*\.ngrok\.io' | head -1)

if [ -z "$NGROK_URL" ]; then
    echo "❌ Failed to get ngrok URL"
    kill $NGROK_PID
    exit 1
fi

echo "✅ Ngrok tunnel: $NGROK_URL"

# Step 6: Set environment variables for Line agent
echo "🔧 Setting up Line agent environment..."
cd line_agent
export CARTESIA_API_KEY="$CARTESIA_API_KEY"
export ANTHROPIC_API_KEY="$ANTHROPIC_API_KEY"
export SERVER_URL="$NGROK_URL"

# Step 7: Deploy Line agent
echo "🚀 Deploying Line agent..."
cartesia deploy

if [ $? -eq 0 ]; then
    echo "✅ Line agent deployed successfully!"
    
    # Get agent ID
    echo "📋 Getting agent ID..."
    AGENT_ID=$(cartesia agents ls | grep -o 'id: [^[:space:]]*' | head -1 | cut -d' ' -f2)
    
    if [ ! -z "$AGENT_ID" ]; then
        echo "✅ Agent ID: $AGENT_ID"
        echo ""
        echo "🎉 Setup complete! Your RepoBuddy Line agent is ready."
        echo ""
        echo "Next steps:"
        echo "1. Start your local server: cd server && python main.py"
        echo "2. Open browser: https://localhost:3000"
        echo "3. Start a session and enjoy voice interaction!"
        echo ""
        echo "Ngrok tunnel will remain active. Press Ctrl+C to stop."
        
        # Keep ngrok running
        wait $NGROK_PID
    else
        echo "❌ Failed to get agent ID"
        kill $NGROK_PID
        exit 1
    fi
else
    echo "❌ Failed to deploy Line agent"
    kill $NGROK_PID
    exit 1
fi
