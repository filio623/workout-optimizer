# Workout Optimizer

An AI-powered workout analysis and optimization platform that helps users track, analyze, and improve their fitness routines through intelligent insights and personalized recommendations.

## 🚀 Features

- **AI Chat Assistant**: Interactive chat interface for workout analysis and recommendations
- **Real-time Communication**: Backend integration with session-based conversations
- **Message Persistence**: Conversation history saved locally
- **Markdown Support**: Rich formatting for AI responses
- **Modern UI**: Beautiful, responsive interface with multiple themes
- **Error Handling**: Comprehensive error management and user feedback
- **Data Visualization**: Ready for workout analytics and progress tracking

## 🏗️ Architecture

- **Frontend**: React + TypeScript + Vite + Tailwind CSS
- **Backend**: FastAPI + Python
- **AI Integration**: OpenAI GPT for workout analysis
- **Database**: SQLite for conversation storage
- **Styling**: Tailwind CSS with custom theme system

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

### Chat Interface
- Real-time AI-powered workout analysis
- Session-based conversation history
- Markdown formatting for rich responses
- Comprehensive error handling
- Auto-scroll and keyboard shortcuts

### Theme System
- 5 beautiful color themes
- Ocean Blue (default)
- Sunset Orange
- Forest Green
- Purple Gradient
- Dark Mode

### Data Persistence
- Conversation history saved locally
- Automatic message persistence
- Cross-session continuity

## 🔧 API Endpoints

### Chat
- `POST /chat` - Send message to AI assistant
- `GET /` - Health check

### Workout Data (Ready for integration)
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

## 🚧 Future Development

See `INTEGRATION_GUIDE.md` for detailed information about:
- Sidebar component integration
- Workout data visualization
- User authentication system
- Additional API endpoints
- Mobile responsiveness improvements

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