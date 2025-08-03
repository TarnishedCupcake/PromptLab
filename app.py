import streamlit as st
import sys
import os

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from prompt_creator.creator_module import PromptCreator
from mutation.mutation_module import PromptMutator
from simulator.simulator_module import PromptSimulator
from analyzer.analyzer_module import PromptAnalyzer
from red_team.red_module import RedTeamTester
from logs.logger import PromptLabLogger

def initialize_session_state():
    """Initialize session state variables"""
    if 'logs' not in st.session_state:
        st.session_state.logs = []
    if 'current_prompt' not in st.session_state:
        st.session_state.current_prompt = ""
    if 'created_prompts' not in st.session_state:
        st.session_state.created_prompts = []
    if 'mutations' not in st.session_state:
        st.session_state.mutations = []
    if 'simulations' not in st.session_state:
        st.session_state.simulations = []
    if 'analysis_results' not in st.session_state:
        st.session_state.analysis_results = {}
    if 'red_team_results' not in st.session_state:
        st.session_state.red_team_results = []

def main():
    st.set_page_config(
        page_title="Prompt Lab",
        page_icon="🧪",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    # Initialize session state
    initialize_session_state()
    
    # Initialize logger
    logger = PromptLabLogger()
    
    # Main title
    st.title("🧪 Prompt Lab")
    st.markdown("*Professional AI Prompt Engineering & Analysis Suite*")
    
    # Sidebar navigation
    st.sidebar.title("Navigation")
    
    tabs = [
        "🏗️ Prompt Creator Lab",
        "🔄 Prompt Mutation Lab", 
        "🎭 Prompt Simulator",
        "📊 Prompt Analyzer",
        "🔴 Red Team Sandbox",
        "📋 Live Logs"
    ]
    
    selected_tab = st.sidebar.radio("Select Tool:", tabs)
    
    # Add current prompt display in sidebar if exists
    if st.session_state.current_prompt:
        st.sidebar.markdown("---")
        st.sidebar.markdown("**Current Prompt:**")
        st.sidebar.text_area("", value=st.session_state.current_prompt[:200] + "..." if len(st.session_state.current_prompt) > 200 else st.session_state.current_prompt, height=100, disabled=True, key="sidebar_prompt")
    
    # Main content area
    if selected_tab == "🏗️ Prompt Creator Lab":
        logger.log("Accessing Prompt Creator Lab")
        creator = PromptCreator()
        creator.render()
        
    elif selected_tab == "🔄 Prompt Mutation Lab":
        logger.log("Accessing Prompt Mutation Lab")
        mutator = PromptMutator()
        mutator.render()
        
    elif selected_tab == "🎭 Prompt Simulator":
        logger.log("Accessing Prompt Simulator")
        simulator = PromptSimulator()
        simulator.render()
        
    elif selected_tab == "📊 Prompt Analyzer":
        logger.log("Accessing Prompt Analyzer")
        analyzer = PromptAnalyzer()
        analyzer.render()
        
    elif selected_tab == "🔴 Red Team Sandbox":
        logger.log("Accessing Red Team Sandbox")
        red_tester = RedTeamTester()
        red_tester.render()
        
    elif selected_tab == "📋 Live Logs":
        logger.log("Accessing Live Logs")
        st.header("📋 Live Logs")
        st.markdown("Real-time system logs from all Prompt Lab modules")
        
        # Display logs
        if st.session_state.logs:
            # Reverse to show newest first
            for log_entry in reversed(st.session_state.logs[-50:]):  # Show last 50 logs
                timestamp = log_entry.get('timestamp', 'Unknown')
                module = log_entry.get('module', 'System')
                message = log_entry.get('message', '')
                level = log_entry.get('level', 'INFO')
                
                # Color coding based on level
                if level == "ERROR":
                    st.error(f"**{timestamp}** [{module}] {message}")
                elif level == "WARNING":
                    st.warning(f"**{timestamp}** [{module}] {message}")
                elif level == "SUCCESS":
                    st.success(f"**{timestamp}** [{module}] {message}")
                else:
                    st.info(f"**{timestamp}** [{module}] {message}")
        else:
            st.info("No logs available yet. Use other tools to generate activity.")
        
        # Clear logs button
        if st.button("Clear Logs"):
            st.session_state.logs = []
            st.rerun()

if __name__ == "__main__":
    main()
