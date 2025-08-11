# Workout Optimizer

An AI-powered workout analysis and optimization platform that integrates with Hevy fitness app data to provide intelligent insights and personalized recommendations through an advanced AI agent system.

## 🚀 Features

- **AI Workout Coach**: Advanced AI agent with 7+ specialized function tools for workout analysis
- **Real Workout Data**: Live integration with Hevy API showing recent workouts, sets, and progress
- **Intelligent Analysis**: AI-powered routine optimization, progressive overload tracking, and form recommendations
- **Interactive Chat**: Session-based conversations with comprehensive workout context
- **Live Dashboard**: Real-time workout statistics with scrollable workout history
- **Performance Optimized**: Sub-second response times with intelligent caching (0.00s vs 12s improvement)
- **Modern UI**: Professional interface with 5 theme options and responsive design

## 🏗️ Architecture

- **Frontend**: React + TypeScript + Vite + Tailwind CSS
- **Backend**: FastAPI + Python with Hevy API integration
- **AI System**: OpenAI Agents SDK with specialized workout function tools
- **Data Layer**: SQLite for conversations + static JSON for exercise templates
- **Performance**: Optimized caching and real-time data integration

## 📋 Prerequisites

- **Python 3.8+**
- **Node.js 16+**
- **npm or yarn**

## 🛠️ Installation

### 1. Clone the repository
```bash
git clone <repository-url>
cd workout-optimizer
```

### 2. Backend Setup
```bash
# Create virtual environment
python -m venv .venv

# Activate virtual environment
# On macOS/Linux:
source .venv/bin/activate
# On Windows:
.venv\Scripts\activate

# Install Python dependencies
pip install -r requirements.txt
```

### 3. Frontend Setup
```bash
# Install frontend dependencies
npm run install:frontend
```

### 4. Environment Configuration
Create a `.env` file in the root directory:
```env
OPENAI_API_KEY=your_openai_api_key_here
# Add other environment variables as needed
```

## 🚀 Running the Application

### Development Mode

**Option 1: Using npm scripts (Recommended)**
```bash
# Terminal 1: Start backend
npm run dev:backend

# Terminal 2: Start frontend
npm run dev:frontend
```

**Option 2: Manual startup**
```bash
# Terminal 1: Start backend
source .venv/bin/activate
python -m app.main

# Terminal 2: Start frontend
cd frontend
npm run dev
```

### Production Build
```bash
# Build frontend for production
npm run build:frontend
```

## 🌐 Access Points

- **Frontend**: http://localhost:5173 (or next available port)
- **Backend API**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs

## 🎨 Features Overview

### AI Workout Coach
- 7+ specialized function tools for workout analysis
- Real-time routine optimization and recommendations
- Progressive overload tracking and suggestions
- Exercise form and technique guidance
- Personalized workout planning based on your Hevy data

### Live Workout Dashboard
- Real-time workout history from Hevy API
- Scrollable list of recent workouts with set counts
- Relative date formatting (Today, Yesterday, etc.)
- Quick stats and performance metrics
- Responsive design with smooth scrolling

### Advanced Chat Interface
- Session-based conversation with workout context
- Markdown formatting for rich AI responses
- Comprehensive error handling and recovery
- Message persistence across sessions
- Professional UI with loading states and animations

### Theme System
- 5 beautiful color themes with smooth transitions
- Ocean Blue, Sunset Orange, Forest Green, Purple Gradient, Dark Mode
- Consistent theming across all components
- Mobile-responsive design

## 🔧 API Endpoints

### Chat
- `POST /chat` - Send message to AI assistant
- `GET /` - Health check

### Workout Data
- `GET /workout-history` - Recent workouts with real-time data
- `GET /api/workout-frequency` - Weekly workout counts
- `GET /api/top-exercises` - Most performed exercises
- `GET /api/top-muscle-groups` - Most targeted muscle groups

## 📁 Project Structure

```
workout-optimizer/
├── app/                    # Backend application
│   ├── main.py            # FastAPI application
│   ├── config.py          # Configuration
│   ├── models.py          # Data models
│   ├── hevy/              # Hevy API integration
│   ├── llm/               # AI/LLM integration
│   └── services/          # Business logic
├── frontend/              # React frontend
│   ├── src/
│   │   ├── components/    # React components
│   │   ├── services/      # API services
│   │   └── App.tsx        # Main app component
│   ├── package.json       # Frontend dependencies
│   └── vite.config.ts     # Vite configuration
├── .kiro/                 # Kiro IDE specifications
├── tests/                 # Test files
├── requirements.txt       # Python dependencies
├── package.json          # Root package.json with scripts
└── README.md             # This file
```

## 🧪 Testing

### Backend Testing
```bash
# Run backend tests
python -m pytest tests/
```

### Frontend Testing
```bash
# Run frontend tests
cd frontend
npm test
```

### Manual Testing
1. Start both servers
2. Open http://localhost:5173
3. Send a message in the chat interface
4. Verify AI response with markdown formatting
5. Refresh page and confirm message persistence

## 🔍 Troubleshooting

### Common Issues

**1. "Can't connect to server" error**
- Ensure backend is running on port 8000
- Check CORS configuration in `app/main.py`
- Verify frontend is making requests to correct URL

**2. Frontend white screen**
- Check browser console for errors
- Ensure all dependencies are installed
- Try clearing browser cache

**3. Backend not starting**
- Verify virtual environment is activated
- Check all dependencies are installed
- Ensure port 8000 is not in use

**4. CORS errors**
- Backend includes CORS middleware for development
- Configured for ports 5173, 5174, 5175
- Check `app/main.py` for CORS settings

## 🚧 Next Development Phase: AI Enhancement

**Current Focus**: Enhancing the AI agent system for more sophisticated workout analysis

**Upcoming Features**:
- Advanced function tools for progressive overload tracking
- Intelligent workout split optimization
- Recovery time analysis and recommendations
- Enhanced pattern recognition in workout data
- Proactive workout suggestions based on performance trends

See `BUILD_PLAN.md` for detailed development roadmap.

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- OpenAI for GPT integration
- FastAPI for the excellent Python web framework
- React and Vite for the modern frontend stack
- Tailwind CSS for beautiful styling
- Lucide React for icons