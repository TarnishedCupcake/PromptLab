import streamlit as st
import random
from logs.logger import PromptLabLogger

class PromptSimulator:
    def __init__(self):
        self.logger = PromptLabLogger()
        self.personas = self._initialize_personas()
        
    def _initialize_personas(self):
        """Initialize LLM persona configurations"""
        return {
            "Professional Assistant": {
                "description": "Formal, structured, and comprehensive responses",
                "tone": "professional",
                "creativity": 3,
                "reasoning_style": "systematic",
                "response_length": "detailed",
                "characteristics": ["formal language", "structured format", "comprehensive coverage"]
            },
            "Creative Writer": {
                "description": "Imaginative, expressive, and artistic responses",
                "tone": "creative",
                "creativity": 9,
                "reasoning_style": "associative",
                "response_length": "elaborate", 
                "characteristics": ["vivid language", "metaphors", "storytelling elements"]
            },
            "Technical Expert": {
                "description": "Precise, technical, and solution-focused responses",
                "tone": "technical",
                "creativity": 2,
                "reasoning_style": "logical",
                "response_length": "concise",
                "characteristics": ["technical accuracy", "step-by-step approach", "practical solutions"]
            },
            "Casual Friend": {
                "description": "Friendly, approachable, and conversational responses",
                "tone": "casual",
                "creativity": 6,
                "reasoning_style": "intuitive",
                "response_length": "moderate",
                "characteristics": ["informal language", "personal anecdotes", "encouraging tone"]
            },
            "Academic Scholar": {
                "description": "Scholarly, analytical, and research-oriented responses",
                "tone": "academic",
                "creativity": 4,
                "reasoning_style": "analytical",
                "response_length": "comprehensive",
                "characteristics": ["citations", "theoretical frameworks", "critical analysis"]
            },
            "Mentor Coach": {
                "description": "Supportive, guiding, and development-focused responses",
                "tone": "mentoring",
                "creativity": 5,
                "reasoning_style": "developmental",
                "response_length": "detailed",
                "characteristics": ["guidance questions", "growth mindset", "actionable advice"]
            },
            "Sarcastic Critic": {
                "description": "Witty, critical, and unconventional responses",
                "tone": "sarcastic",
                "creativity": 8,
                "reasoning_style": "contrarian",
                "response_length": "moderate",
                "characteristics": ["wit", "critical perspective", "unconventional angles"]
            },
            "Minimalist": {
                "description": "Brief, direct, and to-the-point responses",
                "tone": "direct",
                "creativity": 2,
                "reasoning_style": "efficient",
                "response_length": "brief",
                "characteristics": ["conciseness", "key points only", "no fluff"]
            }
        }
    
    def render(self):
        st.header("🎭 Prompt Simulator")
        st.markdown("Simulate how different LLM personas would respond to your prompts.")
        
        # Input section
        col1, col2 = st.columns([2, 1])
        
        with col1:
            st.subheader("Prompt to Simulate")
            
            # Source prompt selection
            source_option = st.radio("Prompt Source:", ["Use Current Prompt", "Enter Custom Prompt"])
            
            if source_option == "Use Current Prompt":
                if st.session_state.current_prompt:
                    simulation_prompt = st.text_area("Current Prompt:", value=st.session_state.current_prompt, height=150, disabled=True)
                else:
                    st.warning("No current prompt set. Please create one first.")
                    simulation_prompt = ""
            else:
                simulation_prompt = st.text_area("Enter Prompt to Simulate:", height=150)
        
        with col2:
            st.subheader("Simulation Settings")
            
            # Persona selection
            selected_personas = st.multiselect(
                "Select Personas:",
                list(self.personas.keys()),
                default=["Professional Assistant", "Creative Writer", "Technical Expert"]
            )
            
            # Simulation parameters
            response_variance = st.slider("Response Variance:", 1, 5, 3)
            include_reasoning = st.checkbox("Include Reasoning Process", value=True)
            show_persona_stats = st.checkbox("Show Persona Statistics", value=True)
        
        # Run simulation
        if st.button("Run Simulation", type="primary") and simulation_prompt and selected_personas:
            with st.spinner("Simulating responses..."):
                simulations = self.simulate_responses(
                    simulation_prompt, 
                    selected_personas, 
                    response_variance,
                    include_reasoning
                )
                
                st.session_state.simulations = simulations
                self.logger.log(f"Simulated responses for {len(selected_personas)} personas", "SUCCESS")
        
        # Display simulations
        if st.session_state.simulations:
            st.markdown("---")
            st.subheader("Simulated Responses")
            
            for i, simulation in enumerate(st.session_state.simulations):
                persona_name = simulation['persona']
                persona_info = self.personas[persona_name]
                
                with st.expander(f"🎭 {persona_name} Response (Quality: {simulation['quality_score']:.1f}/10)"):
                    # Persona information
                    if show_persona_stats:
                        col_info, col_stats = st.columns([2, 1])
                        
                        with col_info:
                            st.write(f"**Description:** {persona_info['description']}")
                            st.write(f"**Characteristics:** {', '.join(persona_info['characteristics'])}")
                        
                        with col_stats:
                            st.metric("Creativity", f"{persona_info['creativity']}/10")
                            st.write(f"**Tone:** {persona_info['tone']}")
                            st.write(f"**Style:** {persona_info['reasoning_style']}")
                    
                    # Simulated response
                    st.markdown("**Simulated Response:**")
                    st.write(simulation['response'])
                    
                    # Reasoning process
                    if include_reasoning and simulation.get('reasoning'):
                        st.markdown("**Reasoning Process:**")
                        st.info(simulation['reasoning'])
                    
                    # Response analysis
                    st.markdown("**Response Analysis:**")
                    analysis_col1, analysis_col2 = st.columns(2)
                    
                    with analysis_col1:
                        st.write(f"**Length:** {simulation['response_length']} words")
                        st.write(f"**Tone Match:** {simulation['tone_match']:.1f}/10")
                    
                    with analysis_col2:
                        st.write(f"**Creativity Level:** {simulation['creativity_level']:.1f}/10")
                        st.write(f"**Coherence:** {simulation['coherence']:.1f}/10")
                    
                    # Action buttons
                    if st.button(f"Use as Reference", key=f"ref_{i}"):
                        st.success("Response saved as reference!")
    
    def simulate_responses(self, prompt, selected_personas, variance, include_reasoning):
        """Simulate responses from different personas"""
        simulations = []
        
        for persona_name in selected_personas:
            persona = self.personas[persona_name]
            
            # Generate simulated response
            response = self._generate_persona_response(prompt, persona, variance)
            
            # Generate reasoning if requested
            reasoning = self._generate_reasoning_process(prompt, persona) if include_reasoning else ""
            
            # Calculate metrics
            quality_score = self._calculate_response_quality(response, persona)
            response_length = len(response.split())
            tone_match = self._calculate_tone_match(response, persona)
            creativity_level = self._calculate_creativity_level(response, persona)
            coherence = self._calculate_coherence(response)
            
            simulation = {
                'persona': persona_name,
                'response': response,
                'reasoning': reasoning,
                'quality_score': quality_score,
                'response_length': response_length,
                'tone_match': tone_match,
                'creativity_level': creativity_level,
                'coherence': coherence
            }
            
            simulations.append(simulation)
        
        return simulations
    
    def _generate_persona_response(self, prompt, persona, variance):
        """Generate a response based on persona characteristics"""
        # Base response templates based on persona type
        response_templates = {
            "professional": [
                "I understand you're looking for {task}. Based on my analysis, I recommend the following approach:",
                "Thank you for your inquiry. I'll provide a comprehensive response to address your requirements:",
                "I've carefully reviewed your request and will outline a structured solution:"
            ],
            "creative": [
                "What an intriguing challenge! Let me paint you a picture of possibilities:",
                "Your request sparks my imagination! Here's a creative approach that might inspire you:",
                "I love the creative potential in your prompt! Let's explore some innovative ideas:"
            ],
            "technical": [
                "Analyzing your requirements, the optimal solution involves:",
                "From a technical perspective, here's the systematic approach:",
                "Based on best practices, I recommend implementing:"
            ],
            "casual": [
                "Hey! That's a great question. Here's what I think:",
                "Oh, I've dealt with something similar before! Let me share:",
                "That's totally doable! Here's how I'd approach it:"
            ],
            "academic": [
                "This inquiry merits careful scholarly consideration. Research indicates:",
                "From an academic standpoint, the literature suggests:",
                "Theoretical frameworks in this domain propose:"
            ],
            "mentoring": [
                "I appreciate you bringing this to me. Let's work through this together:",
                "This is a valuable learning opportunity. Consider these perspectives:",
                "Great question! Let me guide you through the thinking process:"
            ],
            "sarcastic": [
                "Well, well, well... another fascinating prompt. Let me enlighten you:",
                "Oh, you want me to tackle this? How refreshingly original... but sure:",
                "I suppose I could share my infinite wisdom on this topic:"
            ],
            "direct": [
                "Here's what you need:",
                "Solution:",
                "Bottom line:"
            ]
        }
        
        # Select appropriate template
        tone = persona['tone']
        templates = response_templates.get(tone, response_templates['professional'])
        base_response = random.choice(templates)
        
        # Extract task from prompt
        task = self._extract_task_from_prompt(prompt)
        base_response = base_response.format(task=task)
        
        # Generate content based on persona characteristics
        content = self._generate_content_by_persona(prompt, persona, variance)
        
        # Combine base response with content
        full_response = f"{base_response}\n\n{content}"
        
        # Adjust length based on persona preference
        length_pref = persona['response_length']
        if length_pref == "brief":
            full_response = self._shorten_response(full_response)
        elif length_pref in ["elaborate", "comprehensive"]:
            full_response = self._extend_response(full_response, persona)
        
        return full_response
    
    def _extract_task_from_prompt(self, prompt):
        """Extract the main task from the prompt"""
        # Simple extraction - look for action words
        action_words = ['create', 'generate', 'write', 'analyze', 'explain', 'describe', 'help', 'solve']
        
        for word in action_words:
            if word in prompt.lower():
                return f"assistance with {word}ing"
        
        return "your inquiry"
    
    def _generate_content_by_persona(self, prompt, persona, variance):
        """Generate response content based on persona characteristics"""
        creativity = persona['creativity']
        reasoning_style = persona['reasoning_style']
        
        # Base content elements
        content_elements = []
        
        if reasoning_style == "systematic":
            content_elements = [
                "1. First, I'll identify the key requirements",
                "2. Next, I'll analyze potential approaches", 
                "3. Then, I'll recommend the optimal solution",
                "4. Finally, I'll outline implementation steps"
            ]
        elif reasoning_style == "associative":
            content_elements = [
                "This reminds me of a beautiful metaphor...",
                "Imagine this concept as a flowing river of ideas",
                "The creative possibilities are endless here",
                "Let's explore this from multiple artistic angles"
            ]
        elif reasoning_style == "logical":
            content_elements = [
                "The logical approach requires systematic analysis",
                "Key variables to consider include:",
                "Optimal parameters would be:",
                "Expected outcomes based on these inputs:"
            ]
        elif reasoning_style == "intuitive":
            content_elements = [
                "My gut feeling is that this approach would work well",
                "From experience, I've found that...",
                "The natural way to handle this would be:",
                "Trust me on this one - here's what usually works:"
            ]
        elif reasoning_style == "analytical":
            content_elements = [
                "A thorough analysis reveals several key factors",
                "Academic research in this area suggests:",
                "Critical examination of the evidence indicates:",
                "Scholarly consensus points toward:"
            ]
        elif reasoning_style == "developmental":
            content_elements = [
                "Let's think about your growth in this area",
                "What learning opportunities does this present?",
                "How can we build on your existing strengths?",
                "What skills might you develop through this process?"
            ]
        elif reasoning_style == "contrarian":
            content_elements = [
                "But have you considered the opposite approach?",
                "Everyone thinks X, but what if Y is actually better?",
                "The conventional wisdom is wrong here because...",
                "Let me challenge your assumptions about this:"
            ]
        elif reasoning_style == "efficient":
            content_elements = [
                "Key points:",
                "Essential steps:",
                "Core requirements:",
                "Bottom line:"
            ]
        
        # Add variance
        num_elements = max(1, len(content_elements) + random.randint(-variance, variance))
        selected_elements = random.sample(content_elements, min(num_elements, len(content_elements)))
        
        # Add creativity-based elaboration
        if creativity > 6:
            selected_elements.append("This opens up fascinating possibilities for innovation and creative exploration.")
        elif creativity < 3:
            selected_elements.append("The most efficient solution focuses on proven methodologies.")
        
        return "\n\n".join(selected_elements)
    
    def _generate_reasoning_process(self, prompt, persona):
        """Generate reasoning process explanation"""
        reasoning_patterns = {
            "systematic": "I approached this by breaking down the problem into components, analyzing each systematically, and synthesizing a comprehensive solution.",
            "associative": "My creative process involved free association, drawing connections between concepts, and exploring unexpected pathways to innovative solutions.",
            "logical": "I applied logical reasoning, evaluating variables, considering constraints, and deriving conclusions based on sound principles.",
            "intuitive": "I drew on experience and pattern recognition, trusting instinctive responses while validating them against practical knowledge.",
            "analytical": "I conducted a thorough analysis, examining evidence, considering multiple perspectives, and building arguments based on rigorous evaluation.",
            "developmental": "I focused on growth opportunities, considering learning objectives, and structuring guidance to promote skill development.",
            "contrarian": "I deliberately challenged conventional thinking, explored alternative viewpoints, and questioned underlying assumptions.",
            "efficient": "I prioritized efficiency, identifying core requirements, and eliminating unnecessary complexity to deliver focused results."
        }
        
        return reasoning_patterns.get(persona['reasoning_style'], "I processed this request using my standard analytical approach.")
    
    def _shorten_response(self, response):
        """Shorten response for brief personas"""
        sentences = response.split('.')
        # Keep first 2-3 sentences
        shortened = '. '.join(sentences[:3])
        return shortened + '.' if not shortened.endswith('.') else shortened
    
    def _extend_response(self, response, persona):
        """Extend response for elaborate personas"""
        extensions = [
            "Additionally, it's worth considering the broader implications of this approach.",
            "Furthermore, there are several advanced techniques that could enhance this solution.",
            "It's also important to note potential challenges and mitigation strategies.",
            "For optimal results, consider these best practices and optimization opportunities."
        ]
        
        num_extensions = random.randint(1, 2)
        selected_extensions = random.sample(extensions, num_extensions)
        
        return response + "\n\n" + "\n\n".join(selected_extensions)
    
    def _calculate_response_quality(self, response, persona):
        """Calculate overall response quality score"""
        base_score = 7.0
        
        # Length appropriateness
        word_count = len(response.split())
        if persona['response_length'] == "brief" and word_count < 50:
            base_score += 1.0
        elif persona['response_length'] == "detailed" and 100 < word_count < 300:
            base_score += 1.0
        elif persona['response_length'] == "comprehensive" and word_count > 200:
            base_score += 1.0
        
        # Coherence check
        if len(response.split('.')) > 2:  # Multiple sentences
            base_score += 0.5
        
        # Persona consistency
        base_score += random.uniform(-0.5, 1.0)  # Some randomness
        
        return max(1.0, min(10.0, base_score))
    
    def _calculate_tone_match(self, response, persona):
        """Calculate how well response matches persona tone"""
        expected_tone = persona['tone']
        
        # Simple tone indicators
        tone_indicators = {
            'professional': ['recommend', 'analysis', 'approach', 'solution'],
            'creative': ['imagine', 'creative', 'possibilities', 'innovative'],
            'technical': ['systematic', 'optimal', 'implementation', 'variables'],
            'casual': ['hey', 'great', 'totally', 'sure'],
            'academic': ['research', 'analysis', 'scholarly', 'framework'],
            'mentoring': ['together', 'learning', 'growth', 'development'],
            'sarcastic': ['well', 'fascinating', 'enlighten', 'wisdom'],
            'direct': ['bottom line', 'key points', 'essential', 'core']
        }
        
        indicators = tone_indicators.get(expected_tone, [])
        matches = sum(1 for indicator in indicators if indicator in response.lower())
        
        base_score = 6.0 + (matches * 0.5)
        return max(1.0, min(10.0, base_score))
    
    def _calculate_creativity_level(self, response, persona):
        """Calculate creativity level of response"""
        expected_creativity = persona['creativity']
        
        # Creativity indicators
        creative_words = ['innovative', 'creative', 'unique', 'original', 'imaginative', 'artistic']
        creative_count = sum(1 for word in creative_words if word in response.lower())
        
        actual_creativity = min(10, 3 + creative_count)
        
        # Compare to expected
        difference = abs(actual_creativity - expected_creativity)
        score = 10 - difference
        
        return max(1.0, min(10.0, score))
    
    def _calculate_coherence(self, response):
        """Calculate response coherence"""
        sentences = response.split('.')
        word_count = len(response.split())
        
        base_score = 7.0
        
        # Check for reasonable sentence structure
        if len(sentences) > 1 and word_count > 10:
            base_score += 1.0
        
        # Check for transitions and flow
        transitions = ['however', 'furthermore', 'additionally', 'therefore', 'consequently']
        if any(trans in response.lower() for trans in transitions):
            base_score += 0.5
        
        # Random factor
        base_score += random.uniform(-0.5, 0.5)
        
        return max(1.0, min(10.0, base_score))
