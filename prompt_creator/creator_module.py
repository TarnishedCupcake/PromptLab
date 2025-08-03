import streamlit as st
from .utils import PromptUtils
from logs.logger import PromptLabLogger

class PromptCreator:
    def __init__(self):
        self.logger = PromptLabLogger()
        self.utils = PromptUtils()
        
    def render(self):
        st.header("🏗️ Prompt Creator Lab")
        st.markdown("Create advanced prompts with guided assistance and contextual guidance.")
        
        # Multi-step prompt creation
        col1, col2 = st.columns([1, 1])
        
        with col1:
            st.subheader("Step 1: Task Configuration")
            
            # Task type selection
            task_types = [
                "Text Generation", "Question Answering", "Code Generation", 
                "Creative Writing", "Analysis", "Translation", "Summarization",
                "Classification", "Instruction Following", "Problem Solving"
            ]
            task_type = st.selectbox("Select Task Type:", task_types)
            
            # Role selection
            roles = [
                "Assistant", "Expert", "Teacher", "Analyst", "Creative Writer",
                "Technical Advisor", "Consultant", "Researcher", "Mentor", "Specialist"
            ]
            role = st.selectbox("AI Role:", roles)
            
            # Industry context
            industries = [
                "General", "Technology", "Healthcare", "Finance", "Education",
                "Marketing", "Legal", "Science", "Engineering", "Arts"
            ]
            industry = st.selectbox("Industry Context:", industries)
            
            # Tone settings
            tones = ["Professional", "Casual", "Formal", "Friendly", "Authoritative", "Creative"]
            tone = st.selectbox("Tone:", tones)
            
            # Clarity level
            clarity = st.slider("Clarity Level (1-10):", 1, 10, 7)
            
            # Advanced options
            with st.expander("Advanced Options"):
                include_examples = st.checkbox("Include Examples")
                step_by_step = st.checkbox("Request Step-by-Step Response")
                specify_format = st.checkbox("Specify Output Format")
                add_constraints = st.checkbox("Add Constraints")
                
                if specify_format:
                    output_format = st.text_input("Desired Output Format:", "")
                else:
                    output_format = ""
                    
                if add_constraints:
                    constraints = st.text_area("Constraints:", "")
                else:
                    constraints = ""
        
        with col2:
            st.subheader("Step 2: Prompt Preview & Details")
            
            # User input for specific task
            user_task = st.text_area("Describe your specific task:", height=100)
            
            # Context injection
            context = st.text_area("Additional Context (optional):", height=80)
            
            # Generate prompt preview
            prompt_components = {
                'task_type': task_type,
                'role': role,
                'industry': industry,
                'tone': tone,
                'clarity': clarity,
                'user_task': user_task,
                'context': context,
                'include_examples': include_examples,
                'step_by_step': step_by_step,
                'output_format': output_format,
                'constraints': constraints
            }
            
            generated_prompt = self.utils.build_prompt(prompt_components)
            
            st.markdown("**Live Prompt Preview:**")
            st.code(generated_prompt, language="text")
            
            # Action buttons
            col_save, col_use = st.columns(2)
            
            with col_save:
                if st.button("Save Prompt", type="primary"):
                    st.session_state.created_prompts.append({
                        'prompt': generated_prompt,
                        'components': prompt_components,
                        'timestamp': self.utils.get_timestamp()
                    })
                    self.logger.log(f"Prompt saved: {task_type} for {industry}", "SUCCESS")
                    st.success("Prompt saved!")
            
            with col_use:
                if st.button("Use as Current Prompt"):
                    st.session_state.current_prompt = generated_prompt
                    self.logger.log(f"Set current prompt: {task_type}", "INFO")
                    st.success("Set as current prompt!")
        
        # Display saved prompts
        if st.session_state.created_prompts:
            st.markdown("---")
            st.subheader("Saved Prompts")
            
            for i, saved_prompt in enumerate(reversed(st.session_state.created_prompts)):
                with st.expander(f"Prompt {len(st.session_state.created_prompts) - i}: {saved_prompt['components']['task_type']} - {saved_prompt['timestamp']}"):
                    st.code(saved_prompt['prompt'], language="text")
                    
                    col_load, col_delete = st.columns(2)
                    with col_load:
                        if st.button(f"Load as Current", key=f"load_{i}"):
                            st.session_state.current_prompt = saved_prompt['prompt']
                            st.success("Loaded as current prompt!")
                            st.rerun()
                    
                    with col_delete:
                        if st.button(f"Delete", key=f"delete_{i}"):
                            actual_index = len(st.session_state.created_prompts) - 1 - i
                            del st.session_state.created_prompts[actual_index]
                            st.success("Prompt deleted!")
                            st.rerun()
