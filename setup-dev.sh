#!/bin/bash

# Security Monitor - Development Setup Script

echo "🚀 Setting up Security Monitor Development Environment"

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo "❌ Docker is not installed. Please install Docker first."
    exit 1
fi

# Check if Docker Compose is installed
if ! command -v docker-compose &> /dev/null; then
    echo "❌ Docker Compose is not installed. Please install Docker Compose first."
    exit 1
fi

echo "✅ Docker and Docker Compose are installed"

# Create necessary directories
echo "📁 Creating necessary directories..."
mkdir -p logs
mkdir -p data/postgres
mkdir -p nginx/ssl

# Start the development environment
echo "🐳 Starting development environment..."
docker-compose up -d

# Wait for services to be ready
echo "⏳ Waiting for services to start..."
sleep 30

# Check if services are running
echo "🔍 Checking service health..."

# Check backend
if curl -f http://localhost:8000/health > /dev/null 2>&1; then
    echo "✅ Backend API is running on http://localhost:8000"
    echo "📚 API Documentation: http://localhost:8000/docs"
else
    echo "❌ Backend API is not responding"
fi

# Check frontend
if curl -f http://localhost:3000 > /dev/null 2>&1; then
    echo "✅ Frontend is running on http://localhost:3000"
else
    echo "❌ Frontend is not responding"
fi

# Check database
if docker-compose exec -T db pg_isready -U postgres > /dev/null 2>&1; then
    echo "✅ Database is running"
else
    echo "❌ Database is not responding"
fi

echo ""
echo "🎉 Setup complete!"
echo ""
echo "📝 Default login credentials:"
echo "   Username: admin"
echo "   Password: secret"
echo ""
echo "🌐 Access points:"
echo "   Frontend:  http://localhost:3000"
echo "   Backend:   http://localhost:8000"
echo "   API Docs:  http://localhost:8000/docs"
echo ""
echo "🛠️ Useful commands:"
echo "   docker-compose logs -f        # View all logs"
echo "   docker-compose logs backend   # View backend logs"
echo "   docker-compose logs frontend  # View frontend logs"
echo "   docker-compose down           # Stop all services"
echo ""
