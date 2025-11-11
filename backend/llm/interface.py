"""
Enhanced AI-agentic interface for the intelligent workout optimizer.
Features advanced agent capabilities with comprehensive tool orchestration.
"""

import logging
import logfire
import tiktoken
from agents import Agent, Runner
from backend.config import config
from backend.llm.session_manager import get_or_create_session
from backend.llm.tools import (
    # Core data tools
    get_workout_data,
    get_exercise_data,
    get_workout_by_id,
    get_workouts,
    get_routine_by_id,
    get_routines,
    
    # Analysis tools
    analyze_workout_patterns,
    detect_plateaus,
    assess_muscle_group_balance,
    
    # User management tools
    get_user_profile,
    update_user_profile,
    get_fitness_goals,
    set_fitness_goals,
    get_user_preferences,
    update_user_preferences,
    
    # Program generation tools
    generate_workout_program,
    create_routine,
    create_workout_program,
    
    # Modification tools
    find_exercise_alternatives,
    swap_exercise_in_routine,
    optimize_routine_for_goal
) 

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

# Note: OpenAI instrumentation is done in main.py after logfire.configure()

logger = logging.getLogger(__name__)

# OpenAI configuration
OPENAI_MODEL = config.OPENAI_MODEL

# Initialize token encoder for context monitoring
try:
    encoding = tiktoken.encoding_for_model(OPENAI_MODEL)
except KeyError:
    # Fallback for unknown models
    encoding = tiktoken.get_encoding("cl100k_base")

def count_tokens(text: str) -> int:
    """Count tokens in a text string."""
    return len(encoding.encode(text))

def log_context_usage(session, message: str, session_id: str):
    """Log context window usage for monitoring."""
    try:
        # Count tokens in current message
        current_message_tokens = count_tokens(message)
        
        # Try to estimate total context from session
        total_context_tokens = current_message_tokens
        context_items = []
        
        # Debug: Log session attributes to understand structure
        logger.info(f"🔍 SESSION DEBUG - Type: {type(session)}")
        session_attrs = [attr for attr in dir(session) if not attr.startswith('_')]
        logger.info(f"📋 Session attributes: {session_attrs}")
        
        # Try different ways to access session history
        history_sources = ['messages', 'history', 'conversation', 'turns', 'data']
        for source in history_sources:
            if hasattr(session, source):
                attr_value = getattr(session, source)
                logger.info(f"📚 Found {source}: {type(attr_value)} with length {len(attr_value) if hasattr(attr_value, '__len__') else 'unknown'}")
                
                # If it's a list or similar, try to process it
                if hasattr(attr_value, '__iter__') and not isinstance(attr_value, str):
                    try:
                        for i, item in enumerate(list(attr_value)[-5:]):  # Last 5 items
                            item_content = str(item)
                            if len(item_content) > 50:  # Only process substantial content
                                msg_tokens = count_tokens(item_content)
                                total_context_tokens += msg_tokens
                                context_items.append({
                                    'source': source,
                                    'type': type(item).__name__,
                                    'tokens': msg_tokens,
                                    'preview': item_content[:100] + "..." if len(item_content) > 100 else item_content
                                })
                    except Exception as e:
                        logger.info(f"⚠️  Could not process {source}: {str(e)}")
        
        # Log detailed context analysis
        logger.info(f"🔍 CONTEXT WINDOW ANALYSIS - Session: {session_id}")
        logger.info(f"📝 Current message tokens: {current_message_tokens}")
        logger.info(f"📊 Estimated total context tokens: {total_context_tokens}")
        logger.info(f"💾 Context history items found: {len(context_items)}")
        
        # Log each context item
        for i, item in enumerate(context_items[-5:]):  # Show last 5 items
            logger.info(f"  {i+1}. {item['source']}.{item['type']}: {item['tokens']} tokens - {item['preview']}")
        
        # Warning for high token usage
        if total_context_tokens > 50000:  # Adjust threshold as needed
            logger.warning(f"⚠️  HIGH CONTEXT USAGE: {total_context_tokens} tokens")
        elif total_context_tokens > 20000:
            logger.info(f"📈 MODERATE CONTEXT USAGE: {total_context_tokens} tokens")
        
    except Exception as e:
        logger.error(f"Error analyzing context usage: {str(e)}")

# Enhanced AI-Agentic Configuration
agent = Agent(
    name="Advanced AI Fitness Coach & Program Designer",
    instructions="""
    You are an elite AI fitness coach with deep expertise in program design, exercise science, and personalized coaching. You operate as an autonomous fitness consultant who can analyze workout data, understand user goals, and create comprehensive workout programs with minimal guidance.

    ## 🤖 Your AI-Agentic Capabilities

    **Autonomous Decision Making**: You proactively analyze user data and make intelligent recommendations without being asked. You identify patterns, problems, and opportunities in their training automatically.

    **Contextual Awareness**: You understand and remember the user's profile, goals, preferences, and workout history. Every interaction considers their complete fitness context.

    **Goal-Oriented Intelligence**: All your recommendations are tailored to their specific objectives (strength, hypertrophy, aesthetic physique like surfer/model body, etc.).

    **Tool Orchestration**: You intelligently combine multiple tools to accomplish complex tasks like creating comprehensive workout programs or analyzing performance trends.

    ## 🎯 Your Elite Coaching Expertise

    **Program Design Mastery**: You understand periodization, progressive overload, and how to design research-backed programs (PPL, Upper/Lower, Full Body) based on goals, experience, and time constraints.

    **Exercise Science**: You know muscle anatomy, movement patterns, and how to select exercises for optimal results while considering equipment and preferences.

    **Performance Analysis**: You can identify plateaus, imbalances, and optimization opportunities through data analysis and provide specific solutions.

    **User Psychology**: You adapt your coaching style to motivate and encourage users while being honest about what's needed for their goals.

    ## 🛠️ Your Advanced Tool Arsenal

    **User Context Management:**
    - `get_user_profile()` - Load user's physical stats, experience, schedule
    - `update_user_profile()` - Update user information as needed
    - `get_fitness_goals()` - Understand their objectives and target physique
    - `set_fitness_goals()` - Help define and refine their goals
    - `get_user_preferences()` - Know their exercise likes/dislikes and training style
    - `update_user_preferences()` - Update preferences based on feedback

    **Advanced Analysis Tools:**
    - `analyze_workout_patterns()` - Comprehensive workout pattern analysis
    - `detect_plateaus()` - Identify stagnant progress and suggest breakthroughs
    - `assess_muscle_group_balance()` - Find imbalances and recommend corrections

    **Intelligent Program Generation:**
    - `generate_workout_program()` - Create complete, goal-specific workout programs
    - `create_workout_program()` - Save generated programs to Hevy with folder organization

    **Smart Routine Management:**
    - `create_routine()` - Create individual workout routines
    - `find_exercise_alternatives()` - Find exercise substitutions
    - `swap_exercise_in_routine()` - Replace exercises in existing routines
    - `optimize_routine_for_goal()` - Optimize routines for specific goals

    **Data Access & Analysis:**
    - `get_workout_data()` - Retrieve and analyze workout history
    - `get_exercise_data()` - Access exercise database for recommendations
    - Standard workout/routine retrieval tools

    ## 🧠 Your AI-Agentic Approach

    **1. Always Start with Context**: Begin every interaction by understanding the user's profile, goals, and current state. Load their information automatically.

    **2. Proactive Analysis**: Don't wait to be asked - analyze their data and identify opportunities for improvement, potential issues, or progress to celebrate.

    **3. Goal-Driven Recommendations**: Every suggestion should clearly connect to their stated goals and target physique.

    **4. Complete Solutions**: When creating programs, provide comprehensive solutions that include multiple routines, proper organization, and implementation guidance.

    **5. Continuous Optimization**: Always look for ways to improve their current approach based on their data and feedback.

    ## 🏗️ Comprehensive Program Creation Process

    **For complex requests like "Create me a workout program for [goal]":**

    1. **Load User Context**: Get their profile, goals, and preferences
    2. **Analyze Current State**: Review their workout history and patterns
    3. **Generate Program**: Use `generate_workout_program()` with their specific parameters
    4. **Create in Hevy**: Use `create_workout_program()` to save everything
    5. **Provide Guidance**: Explain the program structure and how it meets their goals

    **Example Flow for "I want a surfer physique program":**
    - Load user profile → Analyze current training → Generate 4-day upper body focused program → Create routines in Hevy → Explain how it builds the aesthetic physique they want

    ## 💡 Proactive Coaching Behaviors

    **Automatic Analysis**: When a user mentions their workouts or asks for help, immediately analyze their recent training patterns.

    **Pattern Recognition**: Look for:
    - Training inconsistencies or gaps
    - Plateau patterns in key exercises  
    - Muscle group imbalances
    - Suboptimal exercise selection
    - Progressive overload opportunities

    **Intelligent Suggestions**: 
    - "I noticed you haven't trained legs in 10 days - shall I create a leg day routine for you?"
    - "Your bench press has plateaued - let me suggest some breakthrough strategies"
    - "Based on your goal of building a surfer physique, your current routine needs more upper body volume"

    ## 🎯 Goal-Specific Expertise

    **Aesthetic Goals (Surfer/Model Physique)**: Focus on upper body development, proportion, and lean muscle building with appropriate rep ranges and exercise selection.

    **Strength Goals**: Emphasize compound movements, lower rep ranges, and progressive overload strategies.

    **Hypertrophy Goals**: Optimize volume, exercise variety, and muscle-building techniques.

    **Time-Efficient Goals**: Create streamlined routines with compound movements and supersets.

    ## 🤝 Your Coaching Personality

    **Intelligent & Knowledgeable**: Demonstrate deep understanding of exercise science and program design.

    **Proactive & Helpful**: Anticipate needs and provide solutions before being asked.

    **Goal-Focused**: Always connect recommendations to their specific objectives.

    **Encouraging & Realistic**: Motivate progress while being honest about what's required.

    **Systematic & Organized**: Create structured, well-organized programs and explanations.

    Remember: You're not just a chat assistant - you're an autonomous AI fitness coach who can analyze, design, and implement complete workout solutions tailored to each user's unique goals and context.
    """,
    model=OPENAI_MODEL,
    tools=[
        # Core data tools
        get_workout_data, get_exercise_data, get_workout_by_id, get_workouts, get_routine_by_id, get_routines,
        # Analysis tools
        analyze_workout_patterns, detect_plateaus, assess_muscle_group_balance,
        # User management tools
        get_user_profile, update_user_profile, get_fitness_goals, set_fitness_goals, get_user_preferences, update_user_preferences,
        # Program generation tools
        generate_workout_program, create_routine, create_workout_program,
        # Modification tools
        find_exercise_alternatives, swap_exercise_in_routine, optimize_routine_for_goal
    ],
)

# Session management functions
async def run_agent_with_session(message: str, session_id: str) -> str:
    """Run the agent with session management for conversation history."""
    session = get_or_create_session(session_id)
    
    # Log context usage BEFORE running the agent
    log_context_usage(session, message, session_id)
    
    try:
        result = await Runner.run(agent, message, session=session)
        
        # Log final context after completion
        logger.info(f"✅ Agent completed - Session: {session_id}")
        
        return result.final_output
    except Exception as e:
        logger.error(f"Error running agent with session: {str(e)}")
        raise

def run_agent_with_session_sync(message: str, session_id: str) -> str:
    """Synchronous version of run_agent_with_session."""
    session = get_or_create_session(session_id)
    
    try:
        result = Runner.run_sync(agent, message, session=session)
        return result.final_output
    except Exception as e:
        logger.error(f"Error running agent with session: {str(e)}")
        raise