# Workout Optimizer - MCP + Expo Migration Plan
## Strategic Refactor: Model Context Protocol & Cross-Platform Mobile

### Executive Summary

This document outlines a comprehensive migration plan to transform the current workout optimizer into a modern, cross-platform application using industry-standard protocols and frameworks. The migration involves two major architectural improvements:

1. **Backend Modernization**: Migrate from OpenAI Agents SDK to Model Context Protocol (MCP) for standardized, model-agnostic AI integration
2. **Frontend Evolution**: Migrate from React web-only to Expo (React Native) for unified web, iOS, and Android deployment

**Timeline**: 3-4 weeks of focused development
**Risk Level**: Medium - refactoring working system with proven better architecture
**Expected Outcome**: More maintainable, extensible, cross-platform application

---

## Current State Analysis

### ✅ Strong Foundation (Keep & Build Upon)

**Architecture & Code Quality**:
- Clean separation of concerns (services, models, API, LLM layers)
- Proper Pydantic data models with type validation
- Well-organized 18 function tools across 6 logical categories
- Professional FastAPI backend with proper CORS and error handling
- Modern React + TypeScript frontend with Tailwind CSS
- Performance optimizations already in place (exercise caching: 12s → 0.00s)
- Comprehensive documentation and planning

**Working Features**:
- Full Hevy API integration (workouts, routines, exercises, folders)
- AI agent system with specialized tools
- Session-based conversation management (SQLite)
- Real-time workout data display
- User profile, goals, and preferences system
- Workout pattern analysis and plateau detection
- Theme system with 5 color options
- Message persistence and markdown rendering

**Code Statistics**:
- Backend: 588KB across modular structure
- LLM Tools: 2,417 lines across 6 organized modules
- Frontend: 150MB React TypeScript application
- Database: 384KB SQLite for conversations
- Exercise Cache: 432 exercises, 0.00s load time

### ⚠️ Current Limitations (Why We're Migrating)

**Backend Architecture**:
- ❌ **Custom Hevy Client Maintenance**: 8.2KB of custom API wrapper code to maintain
- ❌ **OpenAI SDK Lock-in**: Tied to OpenAI's Agents SDK (proprietary, less flexible)
- ❌ **Redundant Tool Implementations**: Reimplementing what MCP already provides
- ❌ **Model Inflexibility**: Difficult to switch between Claude, GPT, or future models
- ❌ **Non-Standard Protocol**: Custom tool architecture vs industry standard (MCP)

**Frontend Limitations**:
- ❌ **Web-Only Deployment**: No mobile app despite fitness tracking being mobile-first
- ❌ **Desktop-Focused Layout**: Design optimized for laptop/desktop screens
- ❌ **No Native Features**: Can't access phone notifications, health data, etc.
- ❌ **Separate Codebase Needed**: Would need React Native app separately (~200% effort)

**Maintenance Burden**:
- Maintaining custom Hevy API client when community MCP exists
- Updating tool signatures when OpenAI SDK changes
- Duplicate UI development if mobile needed later
- Missing out on MCP ecosystem improvements

---

## Vision: Modern, Cross-Platform AI Workout Assistant

### Strategic Goals

**1. Backend Modernization via MCP**
- Leverage Model Context Protocol for standardized AI integration
- Eliminate custom Hevy API client in favor of community-maintained MCP server
- Enable model flexibility (Claude, GPT, future models)
- Focus development effort on unique value-add (workout intelligence, program design)
- Join MCP ecosystem for future interoperability

**2. Frontend Evolution via Expo**
- Single codebase for web, iOS, and Android
- ~90-95% code sharing across platforms
- Native mobile experience with app store distribution
- Maintain current UI/UX quality
- Enable mobile-native features (notifications, offline mode, biometric auth)

**3. Architectural Simplification**
- Remove ~30% of codebase (Hevy client + redundant tools)
- Standardize on MCP protocol for all external tool integrations
- Focus custom tools on unique fitness intelligence
- Improve testability with clearer boundaries

---

## Part 1: MCP Backend Migration

### Understanding MCP (Model Context Protocol)

**What is MCP?**
- Industry standard protocol created by Anthropic
- Connects AI models to external tools and data sources
- Model-agnostic: works with Claude, GPT, or any LLM
- Server-client architecture for tool discovery and execution

**Hevy MCP Server** (https://github.com/chrisdoc/hevy-mcp):
- Community-maintained MCP server for Hevy API
- Docker-ready with stdio and HTTP transport modes
- Provides standardized tools for workouts, routines, exercises, folders, webhooks
- Type-safe with auto-generated TypeScript types from OpenAPI specs
- Active maintenance with test coverage

**Benefits for Our App**:
- 🗑️ **Delete**: `app/hevy/client.py` (no longer needed)
- 🗑️ **Delete**: Redundant tools that duplicate MCP functionality
- ✅ **Gain**: Model flexibility (switch between Claude, GPT, future models)
- ✅ **Gain**: Community maintenance of Hevy integration
- ✅ **Gain**: Standardized protocol for future integrations
- ✅ **Focus**: Custom tools on actual value-add (AI coaching, program design)

### Current vs Future Architecture

**Current Architecture**:
```
React Frontend (Web Only)
    ↓ HTTP
FastAPI Backend
    ├── app/hevy/client.py (Custom Hevy API wrapper)
    │   └── Workouts, Routines, Exercises, Folders
    ├── OpenAI Agents SDK
    │   ├── @function_tool decorators
    │   ├── 18 custom function tools
    │   └── gpt-4o-mini model
    └── SQLite (session management)
```

**Future MCP Architecture**:
```
Expo App (Web + iOS + Android)
    ↓ HTTP
FastAPI Backend
    ├── MCP Client
    │   ├── Hevy MCP Server (stdio/Docker)
    │   │   └── Workouts, Routines, Exercises, Folders (standardized)
    │   └── Future MCP servers (extensible)
    ├── Claude/GPT/etc API (direct integration)
    │   ├── Custom Fitness Intelligence Tools
    │   │   ├── analyze_workout_patterns()
    │   │   ├── detect_plateaus()
    │   │   ├── assess_muscle_balance()
    │   │   ├── generate_workout_program()
    │   │   ├── optimize_routine()
    │   │   └── swap_exercises()
    │   └── User management tools
    └── SQLite (session management)
```

### Tool Categorization: Keep vs Migrate to MCP

**🗑️ DELETE - Redundant with Hevy MCP** (6 tools):
```python
# These are handled by Hevy MCP server
- get_workout_by_id()          # MCP: mcp__hevy__get-workout
- get_workouts()                # MCP: mcp__hevy__get-workouts
- get_exercises()               # MCP: mcp__hevy__get-exercise-templates
- get_routine_by_id()           # MCP: mcp__hevy__get-routine
- create_routine()              # MCP: mcp__hevy__create-routine
- update_routine()              # MCP: mcp__hevy__update-routine
```

**✅ KEEP - Custom Fitness Intelligence** (~12 tools):
```python
# Analysis Tools (unique value)
- analyze_workout_patterns()    # Pattern detection, volume analysis
- detect_plateaus()             # Performance stagnation identification
- assess_muscle_group_balance() # Imbalance detection

# User Management Tools (app-specific)
- get_user_profile()
- update_user_profile()
- get_user_goals()
- update_user_goals()
- get_user_preferences()
- update_user_preferences()

# Program Intelligence Tools (core IP)
- generate_workout_program()    # AI-powered program design
- optimize_routine()            # Intelligent routine refinement
- swap_exercises()              # Smart exercise substitution
```

### MCP Integration Technical Plan

**Step 1: Set Up Hevy MCP Server**

Option A - Docker (Recommended for Development):
```bash
# Run Hevy MCP server in Docker
docker run -d \
  --name hevy-mcp \
  -e HEVY_API_KEY=$HEVY_API_KEY \
  -p 3000:3000 \
  ghcr.io/chrisdoc/hevy-mcp:latest

# Server exposes HTTP transport on localhost:3000
```

Option B - Native Installation:
```bash
# Clone and install
git clone https://github.com/chrisdoc/hevy-mcp.git
cd hevy-mcp
npm install
npm run build

# Run with stdio transport
HEVY_API_KEY=$HEVY_API_KEY npm start
```

**Step 2: Add MCP Client to FastAPI**

```bash
# Add dependencies
pip install anthropic  # For Claude API (recommended)
# OR
pip install openai     # For GPT-4 (current)
# AND
pip install mcp        # MCP client library
```

New file structure:
```python
# app/mcp/client.py
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

class MCPManager:
    """Manages MCP server connections and tool access"""

    def __init__(self):
        self.hevy_session = None
        self.tools = {}

    async def connect_hevy(self):
        """Connect to Hevy MCP server"""
        server_params = StdioServerParameters(
            command="docker",
            args=["exec", "-i", "hevy-mcp", "node", "build/index.js"],
            env=None
        )

        async with stdio_client(server_params) as (read, write):
            async with ClientSession(read, write) as session:
                await session.initialize()
                self.hevy_session = session

                # List available tools
                tools_list = await session.list_tools()
                self.tools = {tool.name: tool for tool in tools_list.tools}

    async def call_tool(self, tool_name: str, arguments: dict):
        """Execute MCP tool"""
        result = await self.hevy_session.call_tool(tool_name, arguments)
        return result.content
```

**Step 3: Refactor LLM Interface**

Replace OpenAI Agents SDK with direct API + MCP:

```python
# app/llm/mcp_interface.py
from anthropic import Anthropic
from app.mcp.client import MCPManager
from app.llm.custom_tools import FITNESS_TOOLS  # Our custom tools

class MCPWorkoutAgent:
    """AI workout assistant using MCP protocol"""

    def __init__(self):
        self.client = Anthropic(api_key=settings.ANTHROPIC_API_KEY)
        self.mcp_manager = MCPManager()
        self.custom_tools = FITNESS_TOOLS  # Our unique tools

    async def initialize(self):
        """Connect to MCP servers"""
        await self.mcp_manager.connect_hevy()

        # Combine MCP tools + custom tools
        self.all_tools = {
            **self.mcp_manager.tools,      # Hevy MCP tools
            **self.custom_tools              # Our fitness intelligence
        }

    async def chat(self, message: str, session_id: str):
        """Process user message with tool access"""
        messages = await self._load_history(session_id)
        messages.append({"role": "user", "content": message})

        response = await self.client.messages.create(
            model="claude-3-5-sonnet-20241022",
            max_tokens=4096,
            tools=list(self.all_tools.values()),
            messages=messages
        )

        # Handle tool calls
        while response.stop_reason == "tool_use":
            tool_use = next(
                block for block in response.content
                if block.type == "tool_use"
            )

            # Route to MCP or custom tool
            if tool_use.name.startswith("mcp__hevy__"):
                result = await self.mcp_manager.call_tool(
                    tool_use.name,
                    tool_use.input
                )
            else:
                result = await self._execute_custom_tool(
                    tool_use.name,
                    tool_use.input
                )

            # Continue conversation with tool result
            messages.append({
                "role": "assistant",
                "content": response.content
            })
            messages.append({
                "role": "user",
                "content": [{
                    "type": "tool_result",
                    "tool_use_id": tool_use.id,
                    "content": result
                }]
            })

            response = await self.client.messages.create(
                model="claude-3-5-sonnet-20241022",
                max_tokens=4096,
                tools=list(self.all_tools.values()),
                messages=messages
            )

        await self._save_history(session_id, messages)
        return response.content[0].text
```

**Step 4: Define Custom Fitness Tools**

Keep our unique intelligence:

```python
# app/llm/custom_tools.py
FITNESS_TOOLS = {
    "analyze_workout_patterns": {
        "name": "analyze_workout_patterns",
        "description": "Analyze workout patterns to identify trends, volume, frequency, and consistency",
        "input_schema": {
            "type": "object",
            "properties": {
                "user_id": {"type": "string"},
                "time_period": {"type": "string", "enum": ["week", "month", "3months", "year"]}
            },
            "required": ["user_id"]
        }
    },

    "detect_plateaus": {
        "name": "detect_plateaus",
        "description": "Detect performance plateaus in specific exercises or muscle groups",
        "input_schema": {
            "type": "object",
            "properties": {
                "user_id": {"type": "string"},
                "exercise_id": {"type": "string"},
                "lookback_weeks": {"type": "integer", "default": 8}
            },
            "required": ["user_id"]
        }
    },

    "generate_workout_program": {
        "name": "generate_workout_program",
        "description": "Generate intelligent workout program based on user goals, experience, and available equipment",
        "input_schema": {
            "type": "object",
            "properties": {
                "user_id": {"type": "string"},
                "program_type": {"type": "string", "enum": ["hypertrophy", "strength", "endurance", "hybrid"]},
                "duration_weeks": {"type": "integer"},
                "days_per_week": {"type": "integer"}
            },
            "required": ["user_id", "program_type", "duration_weeks", "days_per_week"]
        }
    },

    # ... other custom tools
}
```

**Step 5: Update FastAPI Endpoints**

Minimal changes to API layer:

```python
# app/main.py
from app.llm.mcp_interface import MCPWorkoutAgent

# Initialize MCP agent on startup
agent = MCPWorkoutAgent()

@app.on_event("startup")
async def startup():
    await agent.initialize()

@app.post("/chat")
async def chat(message: ChatMessage):
    """Chat with AI workout assistant (now using MCP)"""
    try:
        response = await agent.chat(
            message=message.message,
            session_id=message.session_id
        )
        return {"response": response}
    except Exception as e:
        logger.error(f"Chat error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Other endpoints remain mostly unchanged
```

### Migration Checklist - Backend

**Phase 1: MCP Setup** (Week 1, Days 1-2)
- [ ] Install Hevy MCP server (Docker)
- [ ] Test MCP server connectivity with Hevy API
- [ ] Verify available tools match documentation
- [ ] Add MCP client library to requirements.txt
- [ ] Create `app/mcp/client.py` with MCPManager class

**Phase 2: LLM Interface Refactor** (Week 1, Days 3-5)
- [ ] Create `app/llm/mcp_interface.py` with MCPWorkoutAgent
- [ ] Extract custom tools to `app/llm/custom_tools.py`
- [ ] Implement tool routing (MCP vs custom)
- [ ] Add proper error handling for tool calls
- [ ] Update session management for new interface
- [ ] Add Anthropic API key to config (or keep OpenAI)

**Phase 3: Code Cleanup** (Week 1, Days 6-7)
- [ ] Delete `app/hevy/client.py` (no longer needed)
- [ ] Remove redundant tools from `app/llm/tools/core_tools.py`
- [ ] Update imports throughout codebase
- [ ] Remove OpenAI Agents SDK dependency
- [ ] Clean up unused function_tool decorators

**Phase 4: Testing & Validation** (Week 2, Days 1-3)
- [ ] Test all MCP tool calls (workouts, routines, exercises)
- [ ] Test custom tool execution (pattern analysis, plateaus)
- [ ] Verify session persistence still works
- [ ] Test tool orchestration (multiple tool calls)
- [ ] Validate conversation quality vs old implementation
- [ ] Load testing with concurrent requests
- [ ] Error recovery testing (MCP server disconnect)

**Phase 5: Documentation** (Week 2, Days 4-5)
- [ ] Update README with MCP setup instructions
- [ ] Document new architecture in ARCHITECTURE_PLAN.md
- [ ] Add MCP troubleshooting guide
- [ ] Update API documentation
- [ ] Create developer onboarding guide

---

## Part 2: Expo Frontend Migration

### Understanding Expo

**What is Expo?**
- Framework for building React Native apps
- Unified development for iOS, Android, and Web
- Same codebase = 90-95% code sharing
- Built on React Native with enhanced developer experience
- Managed workflow for easy deployment

**Key Benefits**:
- ✅ **Write Once, Deploy Everywhere**: Web + iOS + Android from single codebase
- ✅ **React Knowledge Transfers**: Same components, hooks, patterns
- ✅ **NativeWind**: Tailwind CSS syntax for React Native (minimal migration)
- ✅ **OTA Updates**: Push updates without app store review (for non-native changes)
- ✅ **Expo Go**: Test on real devices instantly during development
- ✅ **Managed Services**: Push notifications, auth, updates built-in

**Expo vs React Web**:
```javascript
// React Web (Current)
<div className="bg-blue-500 p-4 rounded-lg">
  <h1 className="text-2xl font-bold">Hello</h1>
  <button onClick={handleClick}>Click</button>
</div>

// Expo with NativeWind (Future) - Nearly identical!
<View className="bg-blue-500 p-4 rounded-lg">
  <Text className="text-2xl font-bold">Hello</Text>
  <Pressable onPress={handleClick}>
    <Text>Click</Text>
  </Pressable>
</View>
```

### Migration Strategy

**Component Mapping**:
| React Web | React Native | Effort |
|-----------|--------------|--------|
| `<div>` | `<View>` | Find & replace |
| `<span>`, `<p>`, `<h1-6>` | `<Text>` | Find & replace |
| `<button>` | `<Pressable>` | Minimal logic change |
| `<input>` | `<TextInput>` | Props adjustment |
| `<img>` | `<Image>` | Source handling |
| CSS-in-JS | StyleSheet / NativeWind | Use NativeWind (Tailwind syntax) |

**What Stays the Same**:
- ✅ React hooks (useState, useEffect, useContext, etc.)
- ✅ State management patterns
- ✅ API calls (fetch, axios)
- ✅ TypeScript interfaces
- ✅ Component logic and business rules
- ✅ Most Tailwind class names (via NativeWind)

**What Changes**:
- ❌ HTML elements → React Native primitives
- ❌ Vite → Metro bundler
- ❌ React Router → React Navigation
- ❌ Some CSS properties (web-specific ones)
- ❌ npm packages (need RN-compatible versions)

### Detailed Migration Plan

**Step 1: Create Expo Project**

```bash
# Create new Expo app with TypeScript
npx create-expo-app@latest workout-optimizer-mobile --template tabs

cd workout-optimizer-mobile

# Add required dependencies
npx expo install react-native-web react-dom
npm install nativewind
npm install --save-dev tailwindcss@3.3.2

# Add navigation
npx expo install @react-navigation/native @react-navigation/native-stack
npx expo install react-native-screens react-native-safe-area-context

# Add markdown rendering
npm install react-native-markdown-display

# Add API client
npm install axios
```

**Step 2: Configure NativeWind (Tailwind for RN)**

```javascript
// tailwind.config.js
module.exports = {
  content: [
    "./App.{js,jsx,ts,tsx}",
    "./app/**/*.{js,jsx,ts,tsx}",
    "./components/**/*.{js,jsx,ts,tsx}"
  ],
  theme: {
    extend: {
      colors: {
        // Port your theme colors
        ocean: { /* ... */ },
        sunset: { /* ... */ },
        // etc.
      }
    }
  },
  plugins: []
}

// babel.config.js
module.exports = function(api) {
  api.cache(true);
  return {
    presets: ['babel-preset-expo'],
    plugins: ['nativewind/babel']
  };
};
```

**Step 3: Port Components**

Example: ChatArea component migration

```typescript
// frontend/src/components/ChatArea.tsx (BEFORE - React Web)
import React, { useState, useEffect, useRef } from 'react';
import ReactMarkdown from 'react-markdown';

export const ChatArea: React.FC<Props> = ({ theme }) => {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState('');
  const scrollRef = useRef<HTMLDivElement>(null);

  return (
    <div className="flex flex-col h-full bg-gray-50">
      <div className="flex-1 overflow-y-auto p-4" ref={scrollRef}>
        {messages.map(msg => (
          <div key={msg.id} className={`mb-4 ${msg.role === 'user' ? 'text-right' : ''}`}>
            <div className="inline-block bg-white p-3 rounded-lg shadow">
              <ReactMarkdown>{msg.content}</ReactMarkdown>
            </div>
          </div>
        ))}
      </div>

      <div className="border-t p-4 bg-white">
        <input
          type="text"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          className="w-full px-4 py-2 border rounded-lg"
          placeholder="Ask about your workouts..."
        />
        <button onClick={sendMessage} className="mt-2 px-4 py-2 bg-blue-500 text-white rounded">
          Send
        </button>
      </div>
    </div>
  );
};

// workout-optimizer-mobile/components/ChatArea.tsx (AFTER - Expo)
import React, { useState, useEffect, useRef } from 'react';
import { View, ScrollView, TextInput, Pressable, Text } from 'react-native';
import Markdown from 'react-native-markdown-display';

export const ChatArea: React.FC<Props> = ({ theme }) => {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState('');
  const scrollRef = useRef<ScrollView>(null);

  // EXACT SAME LOGIC - just different components!

  return (
    <View className="flex-1 bg-gray-50">
      <ScrollView
        ref={scrollRef}
        className="flex-1 p-4"
      >
        {messages.map(msg => (
          <View key={msg.id} className={`mb-4 ${msg.role === 'user' ? 'items-end' : 'items-start'}`}>
            <View className="bg-white p-3 rounded-lg shadow">
              <Markdown>{msg.content}</Markdown>
            </View>
          </View>
        ))}
      </ScrollView>

      <View className="border-t p-4 bg-white">
        <TextInput
          value={input}
          onChangeText={setInput}
          className="w-full px-4 py-2 border rounded-lg"
          placeholder="Ask about your workouts..."
        />
        <Pressable
          onPress={sendMessage}
          className="mt-2 px-4 py-2 bg-blue-500 rounded"
        >
          <Text className="text-white text-center">Send</Text>
        </Pressable>
      </View>
    </View>
  );
};
```

**Key Changes**:
- `<div>` → `<View>`
- `<input>` → `<TextInput>` (onChange → onChangeText)
- `<button>` → `<Pressable>` (onClick → onPress)
- `ReactMarkdown` → `react-native-markdown-display`
- `ref<HTMLDivElement>` → `ref<ScrollView>`
- Tailwind classes work the same! (thanks to NativeWind)

**Step 4: Set Up Navigation**

```typescript
// app/_layout.tsx (Expo file-based routing)
import { Stack } from 'expo-router';

export default function RootLayout() {
  return (
    <Stack>
      <Stack.Screen
        name="(tabs)"
        options={{ headerShown: false }}
      />
    </Stack>
  );
}

// app/(tabs)/_layout.tsx
import { Tabs } from 'expo-router';
import { Dumbbell, BarChart, Settings } from 'lucide-react-native';

export default function TabLayout() {
  return (
    <Tabs>
      <Tabs.Screen
        name="chat"
        options={{
          title: 'Coach',
          tabBarIcon: ({ color }) => <Dumbbell color={color} />
        }}
      />
      <Tabs.Screen
        name="analytics"
        options={{
          title: 'Analytics',
          tabBarIcon: ({ color }) => <BarChart color={color} />
        }}
      />
      <Tabs.Screen
        name="settings"
        options={{
          title: 'Settings',
          tabBarIcon: ({ color }) => <Settings color={color} />
        }}
      />
    </Tabs>
  );
}
```

**Step 5: Port API Service**

```typescript
// services/api.ts - EXACT SAME CODE
// Works on web, iOS, Android with zero changes!

const API_BASE = process.env.EXPO_PUBLIC_API_URL || 'http://localhost:8000';

export const api = {
  async sendMessage(message: string, sessionId: string) {
    const response = await fetch(`${API_BASE}/chat`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ message, session_id: sessionId })
    });
    return response.json();
  },

  async getWorkoutHistory() {
    const response = await fetch(`${API_BASE}/workout-history`);
    return response.json();
  }

  // ... rest is identical
};
```

**Step 6: Configure Multi-Platform Build**

```json
// app.json
{
  "expo": {
    "name": "Workout Optimizer",
    "slug": "workout-optimizer",
    "version": "1.0.0",
    "platforms": ["ios", "android", "web"],

    "ios": {
      "bundleIdentifier": "com.yourname.workoutoptimizer",
      "supportsTablet": true
    },

    "android": {
      "package": "com.yourname.workoutoptimizer",
      "adaptiveIcon": {
        "foregroundImage": "./assets/adaptive-icon.png",
        "backgroundColor": "#ffffff"
      }
    },

    "web": {
      "bundler": "metro",
      "output": "static",
      "favicon": "./assets/favicon.png"
    }
  }
}
```

### Component Migration Checklist

**Core Components** (Priority 1):
- [ ] `Layout.tsx` → App shell structure
- [ ] `Header.tsx` → Navigation header
- [ ] `ChatArea.tsx` → Main chat interface
- [ ] `MessageBubble.tsx` → Message display
- [ ] `TypingIndicator.tsx` → Loading animation
- [ ] `Sidebar.tsx` → Workout history (maybe drawer on mobile?)

**UI Components** (Priority 2):
- [ ] `ThemeSelector.tsx` → Theme switching
- [ ] `ChartsSection.tsx` → Analytics (react-native-chart-kit)
- [ ] Form inputs (if any)
- [ ] Modal dialogs

**Services** (Priority 3):
- [ ] `api.ts` → API client (minimal/no changes)
- [ ] Theme context/state
- [ ] Session management

### Platform-Specific Considerations

**Mobile-Specific Features to Add**:
```typescript
// 1. Native notifications
import * as Notifications from 'expo-notifications';

// 2. Biometric authentication
import * as LocalAuthentication from 'expo-local-authentication';

// 3. Offline storage
import AsyncStorage from '@react-native-async-storage/async-storage';

// 4. Camera for progress photos
import * as ImagePicker from 'expo-image-picker';

// 5. Health data integration (iOS HealthKit, Android Health Connect)
import AppleHealthKit from 'react-native-health';
```

**Responsive Design**:
```typescript
import { Platform, Dimensions } from 'react-native';

const { width } = Dimensions.get('window');
const isTablet = width >= 768;
const isMobile = Platform.OS !== 'web';

// Adjust layout based on platform
{isMobile ? (
  <DrawerLayout> {/* Sidebar as drawer */}
    <ChatArea />
  </DrawerLayout>
) : (
  <View className="flex-row"> {/* Side-by-side on web/tablet */}
    <Sidebar />
    <ChatArea />
  </View>
)}
```

### Deployment Strategy

**Development**:
```bash
# Web
npx expo start --web

# iOS Simulator
npx expo start --ios

# Android Emulator
npx expo start --android

# Physical Device (via Expo Go app)
npx expo start
# Scan QR code with Expo Go
```

**Production Builds**:

```bash
# Web deployment (static export)
npx expo export:web
# Deploy to Vercel/Netlify/CloudFlare

# iOS App Store
eas build --platform ios
eas submit --platform ios

# Google Play Store
eas build --platform android
eas submit --platform android
```

**Expo Application Services (EAS)**:
- Managed build service (cloud-based)
- Automatic code signing
- TestFlight/Internal testing integration
- OTA updates for JS/asset changes

---

## Unified Timeline & Milestones

### Week 1: Backend MCP Migration

**Days 1-2: MCP Setup**
- Monday Morning: Install Hevy MCP server (Docker)
- Monday Afternoon: Test connectivity, verify tools
- Tuesday Morning: Add MCP client to FastAPI
- Tuesday Afternoon: Create MCPManager class

**Days 3-5: LLM Refactor**
- Wednesday: Create mcp_interface.py, implement tool routing
- Thursday: Extract custom tools, update agent instructions
- Friday: Session management, error handling

**Days 6-7: Backend Cleanup & Testing**
- Saturday: Delete old code, update imports
- Sunday: Integration testing, bug fixes

**Deliverable**: ✅ Working FastAPI backend with MCP integration

---

### Week 2: Expo Project Foundation

**Days 1-2: Expo Setup**
- Monday Morning: Create Expo project, configure NativeWind
- Monday Afternoon: Set up navigation structure
- Tuesday: Port theme system and configuration

**Days 3-5: Core Component Migration**
- Wednesday: ChatArea + MessageBubble components
- Thursday: Sidebar/drawer component, Header
- Friday: API service integration, test on all platforms

**Days 6-7: Testing & Polish**
- Saturday: Cross-platform testing (web, iOS simulator, Android)
- Sunday: UI/UX refinements, responsive design

**Deliverable**: ✅ Working Expo app with core chat functionality

---

### Week 3: Feature Completion

**Days 1-3: Advanced Features**
- Workout history display
- Analytics/charts (react-native-chart-kit)
- User profile/settings screens
- Theme switching across platforms

**Days 4-5: Mobile-Specific Features**
- Push notification setup
- Offline mode with AsyncStorage
- Biometric authentication (optional)
- Platform-specific UI optimizations

**Days 6-7: Testing & Bug Fixes**
- Comprehensive testing on real devices
- Performance profiling
- Edge case handling

**Deliverable**: ✅ Feature-complete cross-platform app

---

### Week 4: Polish & Deployment

**Days 1-2: Production Prep**
- Environment configuration (staging, production)
- API endpoint configuration
- Error tracking setup (Sentry)
- Analytics setup (if desired)

**Days 3-4: Documentation**
- Update all documentation
- Create deployment guide
- User documentation
- Developer onboarding

**Days 5-7: Deployment**
- Deploy backend to production
- Web app deployment (Vercel/Netlify)
- iOS TestFlight build
- Android internal testing build

**Deliverable**: ✅ Deployed application on all platforms

---

## Technical Decisions & Trade-offs

### Model Selection: Claude vs GPT

**Option A: Claude 3.5 Sonnet (Recommended)**
```python
# Pros:
✅ Native MCP support (built by Anthropic)
✅ Excellent tool use and function calling
✅ Strong reasoning capabilities
✅ 200K context window (vs GPT-4's 128K)
✅ More affordable pricing

# Cons:
❌ Slightly different API than current OpenAI
❌ Less familiar if team knows GPT well
```

**Option B: GPT-4 Turbo/GPT-4o**
```python
# Pros:
✅ Minimal API changes from current
✅ Team familiarity
✅ Strong performance

# Cons:
❌ MCP integration less native
❌ Higher costs
❌ Smaller context window
```

**Recommendation**: Start with Claude 3.5 Sonnet for best MCP experience, keep GPT as fallback option.

### Expo Managed vs Bare Workflow

**Managed Workflow (Recommended)**:
- ✅ Easier setup and maintenance
- ✅ Automatic updates
- ✅ EAS build service
- ✅ OTA updates
- ❌ Limited native module customization

**Bare Workflow**:
- ✅ Full control over native code
- ✅ Any native module
- ❌ More complex maintenance
- ❌ Manual Xcode/Android Studio configuration

**Recommendation**: Start with managed workflow. Can eject to bare if needed later.

### State Management

Current app doesn't use Redux/MobX. For Expo:

**Option A: Keep Current Approach (Recommended)**
- React Context for theme
- Local state for UI
- Server state from API

**Option B: Add State Management**
- TanStack Query (React Query) for server state
- Zustand for global state (lightweight)

**Recommendation**: Keep current approach unless state complexity grows.

---

## Risk Mitigation

### Migration Risks

**Risk 1: MCP Server Reliability**
- **Impact**: High - core functionality depends on it
- **Mitigation**:
  - Run MCP server in Docker with restart policy
  - Implement connection retry logic
  - Add health check endpoint
  - Keep fallback to direct Hevy API if needed

**Risk 2: Expo Platform Differences**
- **Impact**: Medium - some features may not work identically
- **Mitigation**:
  - Test on all platforms early and often
  - Use Platform.select() for platform-specific code
  - Leverage NativeWind for consistent styling
  - Have web-specific and mobile-specific fallbacks

**Risk 3: Tool Call Compatibility**
- **Impact**: Medium - tools may behave differently
- **Mitigation**:
  - Comprehensive testing of all tool calls
  - Schema validation for tool inputs/outputs
  - Detailed error logging
  - Gradual migration (feature flags)

**Risk 4: App Store Approval**
- **Impact**: Low - fitness apps generally approved
- **Mitigation**:
  - Follow Apple/Google guidelines
  - Clear privacy policy
  - Proper API usage descriptions
  - TestFlight beta testing first

### Rollback Plan

If migration fails:

**Backend Rollback**:
```bash
# Keep old code in git branch
git checkout -b pre-mcp-migration main
git checkout main
# ... do migration work

# If needed to rollback:
git checkout pre-mcp-migration
```

**Frontend Rollback**:
- Web app continues working independently
- Can deploy Expo web separately or keep Vite version

**Phased Rollout**:
- Deploy MCP backend to staging first
- A/B test with small user group
- Monitor error rates and performance
- Full rollout only after validation

---

## Success Metrics

### Technical Metrics

**Backend (MCP Migration)**:
- [ ] Reduce codebase by ~30% (delete Hevy client + redundant tools)
- [ ] Tool call latency < 500ms (p95)
- [ ] Zero regressions in existing features
- [ ] 100% tool coverage parity with old system
- [ ] Session management working identically

**Frontend (Expo Migration)**:
- [ ] 90%+ code sharing across web/iOS/Android
- [ ] App bundle size < 20MB (iOS), < 15MB (Android)
- [ ] Time to Interactive < 2s on mobile
- [ ] No web performance regression
- [ ] Consistent UI across all platforms

### User Experience Metrics

- [ ] Chat response quality maintained or improved
- [ ] UI/UX consistency across platforms
- [ ] Mobile app feels native (smooth animations, gestures)
- [ ] Offline mode works (if implemented)
- [ ] Theme switching works on all platforms

### Business Metrics

- [ ] App available in iOS App Store
- [ ] App available in Google Play Store
- [ ] Web app deployed and accessible
- [ ] User can install on phone home screen
- [ ] Cross-platform user accounts work

---

## Future Enhancements (Post-Migration)

### Immediate Next Steps
1. **Enhanced Analytics**: Interactive charts with react-native-chart-kit
2. **Offline Mode**: AsyncStorage for workouts, sync when online
3. **Push Notifications**: Workout reminders, program updates
4. **Progressive Photo Tracking**: Camera integration for progress photos

### Medium-Term (3-6 months)
1. **Health Data Integration**: iOS HealthKit, Android Health Connect
2. **Social Features**: Share workouts, community programs
3. **Video Exercise Library**: Embedded technique videos
4. **Voice Input**: Speech-to-text for logging workouts

### Long-Term (6-12 months)
1. **Apple Watch App**: Log workouts from wrist
2. **Wearable Integration**: Heart rate, sleep, recovery data
3. **AI Form Check**: Camera-based exercise form analysis
4. **Marketplace**: User-generated programs, trainer partnerships

---

## Developer Workflow

### Local Development Setup

**Backend**:
```bash
# Terminal 1: Hevy MCP Server
docker run -d --name hevy-mcp \
  -e HEVY_API_KEY=$HEVY_API_KEY \
  ghcr.io/chrisdoc/hevy-mcp:latest

# Terminal 2: FastAPI Backend
cd app
pip install -r requirements.txt
uvicorn main:app --reload --port 8000
```

**Frontend**:
```bash
# Terminal 3: Expo
cd workout-optimizer-mobile
npx expo start

# Choose platform:
# Press 'w' for web
# Press 'i' for iOS simulator
# Press 'a' for Android emulator
# Scan QR with Expo Go for physical device
```

### Git Workflow

**Branch Strategy**:
```bash
main                    # Production-ready code
├── develop             # Integration branch
├── feature/mcp-backend        # Backend migration
├── feature/expo-frontend      # Frontend migration
└── feature/mobile-features    # Platform-specific features
```

**Pull Request Process**:
1. Feature branch from `develop`
2. PR to `develop` with tests
3. Code review + approval
4. Merge to `develop`
5. Periodic releases: `develop` → `main`

---

## Resources & References

### MCP Resources
- [MCP Specification](https://spec.modelcontextprotocol.io/)
- [Hevy MCP Server](https://github.com/chrisdoc/hevy-mcp)
- [Anthropic MCP Docs](https://docs.anthropic.com/en/docs/mcp)
- [MCP TypeScript SDK](https://github.com/modelcontextprotocol/typescript-sdk)

### Expo Resources
- [Expo Documentation](https://docs.expo.dev/)
- [React Native Docs](https://reactnative.dev/)
- [NativeWind Docs](https://www.nativewind.dev/)
- [React Navigation](https://reactnavigation.org/)
- [Expo Router](https://docs.expo.dev/router/introduction/)

### Hevy API
- [Hevy API Docs](https://docs.hevyapp.com/)
- [OpenAPI Spec](https://api.hevyapp.com/openapi.json)

### Community
- [Expo Discord](https://chat.expo.dev/)
- [MCP Community](https://github.com/modelcontextprotocol/community)

---

## Appendix A: File Structure (Post-Migration)

```
Workout_Optimizer/
├── app/                          # FastAPI Backend
│   ├── mcp/
│   │   ├── __init__.py
│   │   └── client.py             # NEW: MCP client manager
│   ├── llm/
│   │   ├── mcp_interface.py      # NEW: MCP-based agent
│   │   ├── custom_tools.py       # NEW: Custom fitness tools
│   │   └── instructions.py       # Agent system prompt
│   ├── services/
│   │   ├── workout_analyzer.py   # KEEP: Pattern analysis
│   │   ├── exercise_analyzer.py  # KEEP: Exercise intelligence
│   │   └── program_analyzer.py   # KEEP: Program generation
│   ├── models.py                 # KEEP: Pydantic models
│   ├── config.py                 # UPDATE: Add MCP config
│   └── main.py                   # UPDATE: Use MCP agent
│
├── workout-optimizer-mobile/     # NEW: Expo App
│   ├── app/
│   │   ├── (tabs)/
│   │   │   ├── chat.tsx          # Chat screen
│   │   │   ├── analytics.tsx     # Analytics screen
│   │   │   └── settings.tsx      # Settings screen
│   │   └── _layout.tsx           # Root layout
│   ├── components/
│   │   ├── ChatArea.tsx          # Migrated from React
│   │   ├── MessageBubble.tsx     # Migrated from React
│   │   ├── WorkoutCard.tsx       # Migrated from React
│   │   └── ThemeSelector.tsx     # Migrated from React
│   ├── services/
│   │   └── api.ts                # Same as React version
│   ├── app.json                  # Expo config
│   ├── tailwind.config.js        # NativeWind config
│   └── package.json
│
├── docs/
│   ├── MCP_EXPO_MIGRATION_PLAN.md  # THIS DOCUMENT
│   ├── ARCHITECTURE_PLAN.md        # Update post-migration
│   └── ...
│
└── user_data/                    # User profiles (keep)
    ├── profiles/
    ├── goals/
    └── preferences/
```

---

## Appendix B: Comparison Matrix

### Before vs After

| Aspect | Current (OpenAI + React) | Future (MCP + Expo) | Benefit |
|--------|--------------------------|---------------------|---------|
| **Backend** | | | |
| LLM Integration | OpenAI Agents SDK | MCP + Claude/GPT | Model flexibility |
| Hevy API Client | Custom 8.2KB client | Community MCP server | -30% code, maintained externally |
| Tool Architecture | 18 custom @function_tool | 6 MCP + 12 custom | Focus on value-add |
| Model Lock-in | OpenAI only | Any model (Claude, GPT, etc.) | Future-proof |
| Protocol | Proprietary | Industry standard (MCP) | Interoperability |
| | | | |
| **Frontend** | | | |
| Platforms | Web only | Web + iOS + Android | 3x reach |
| Codebase | React (Vite) | Expo (React Native) | 90% code sharing |
| Styling | Tailwind CSS | NativeWind (Tailwind syntax) | Minimal migration |
| Deployment | Vercel/Netlify | Web + App Stores | True mobile app |
| Updates | Redeploy web | OTA for JS/assets | Faster iteration |
| Native Features | None | Camera, notifications, biometrics | Rich UX |
| | | | |
| **Maintenance** | | | |
| Lines of Code | ~3,000 (est.) | ~2,100 (est.) | -30% less code |
| External Dependencies | Hevy client maintained by us | Hevy MCP maintained by community | Less burden |
| Platform Codebases | 1 (web) | 1 (shared) | Same effort, 3x output |
| Testing Surface | Backend + Web frontend | Backend + 3 frontends (shared tests) | More coverage |

---

## Appendix C: Quick Start (Post-Migration)

For developers onboarding after migration:

**1. Clone & Setup Backend**:
```bash
git clone <repo>
cd Workout_Optimizer

# Start Hevy MCP
docker-compose up -d hevy-mcp

# Start FastAPI
cd app
pip install -r requirements.txt
cp .env.example .env  # Add your keys
uvicorn main:app --reload
```

**2. Setup Frontend**:
```bash
cd workout-optimizer-mobile
npm install
npx expo start

# Choose:
# w - web browser
# i - iOS simulator
# a - Android emulator
# Scan QR - physical device
```

**3. Configure**:
```bash
# .env (backend)
HEVY_API_KEY=your_key
ANTHROPIC_API_KEY=your_key  # Or OPENAI_API_KEY

# .env (Expo)
EXPO_PUBLIC_API_URL=http://localhost:8000
```

Done! App running on web, iOS, and Android from single codebase.

---

## Conclusion

This migration represents a significant architectural improvement while preserving the solid foundation you've built. The end result will be:

1. **More Maintainable**: -30% code, standardized protocols, community-maintained integrations
2. **More Extensible**: MCP enables easy addition of new tools/integrations
3. **More Accessible**: Web + iOS + Android from single codebase
4. **More Future-Proof**: Industry-standard protocols, model flexibility
5. **More Focused**: Development effort on unique fitness intelligence, not infrastructure

**The best part**: You're building on strength, not starting over. Your workout analysis logic, AI coaching intelligence, and user experience design are all preserved and enhanced.

---

**Status**: Planning Phase
**Next Steps**: Review plan → Approve → Begin Week 1 (MCP Backend Migration)
**Questions/Concerns**: Document here as they arise

---

*Last Updated*: 2025-11-09
*Document Version*: 1.0
*Author*: Migration Planning Session
