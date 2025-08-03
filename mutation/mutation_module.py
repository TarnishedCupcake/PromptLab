import streamlit as st
import random
import re
from .config import MutationConfig
from logs.logger import PromptLabLogger

class PromptMutator:
    def __init__(self):
        self.logger = PromptLabLogger()
        self.config = MutationConfig()
        
    def render(self):
        st.header("🔄 Prompt Mutation Lab")
        st.markdown("Generate multiple variants of your prompts for testing and optimization.")
        
        # Input section
        col1, col2 = st.columns([2, 1])
        
        with col1:
            st.subheader("Input Prompt")
            
            # Source prompt selection
            source_option = st.radio("Prompt Source:", ["Use Current Prompt", "Enter New Prompt"])
            
            if source_option == "Use Current Prompt":
                if st.session_state.current_prompt:
                    source_prompt = st.text_area("Current Prompt:", value=st.session_state.current_prompt, height=150, disabled=True)
                else:
                    st.warning("No current prompt set. Please create one in Prompt Creator Lab first.")
                    source_prompt = ""
            else:
                source_prompt = st.text_area("Enter Prompt to Mutate:", height=150)
        
        with col2:
            st.subheader("Mutation Settings")
            
            # Mutation types
            mutation_types = st.multiselect(
                "Mutation Types:",
                [
                    "Word Replacement",
                    "Tone Shift", 
                    "Length Extension",
                    "Length Reduction",
                    "Structure Reformat",
                    "Role Change",
                    "Context Addition",
                    "Instruction Modification"
                ],
                default=["Word Replacement", "Tone Shift"]
            )
            
            # Number of mutations
            num_mutations = st.slider("Number of Mutations:", 1, 10, 5)
            
            # Mutation intensity
            intensity = st.slider("Mutation Intensity:", 1, 5, 3)
            
            # Advanced settings
            with st.expander("Advanced Settings"):
                preserve_core = st.checkbox("Preserve Core Meaning", value=True)
                ensure_clarity = st.checkbox("Ensure Clarity", value=True)
                randomize_order = st.checkbox("Randomize Word Order", value=False)
        
        # Generate mutations
        if st.button("Generate Mutations", type="primary") and source_prompt:
            with st.spinner("Generating mutations..."):
                mutations = self.generate_mutations(
                    source_prompt, 
                    mutation_types, 
                    num_mutations, 
                    intensity,
                    preserve_core,
                    ensure_clarity,
                    randomize_order
                )
                
                st.session_state.mutations = mutations
                self.logger.log(f"Generated {len(mutations)} mutations with types: {', '.join(mutation_types)}", "SUCCESS")
        
        # Display mutations
        if st.session_state.mutations:
            st.markdown("---")
            st.subheader("Generated Mutations")
            
            for i, mutation in enumerate(st.session_state.mutations):
                with st.expander(f"Mutation {i+1}: {mutation['type']} (Score: {mutation['score']:.2f})"):
                    st.code(mutation['text'], language="text")
                    
                    # Mutation details
                    col_info, col_actions = st.columns([2, 1])
                    
                    with col_info:
                        st.write(f"**Type:** {mutation['type']}")
                        st.write(f"**Changes:** {mutation['changes']}")
                        st.write(f"**Quality Score:** {mutation['score']:.2f}/10")
                    
                    with col_actions:
                        if st.button(f"Use as Current", key=f"use_mut_{i}"):
                            st.session_state.current_prompt = mutation['text']
                            self.logger.log(f"Set mutation {i+1} as current prompt", "INFO")
                            st.success("Set as current prompt!")
                            st.rerun()
                        
                        if st.button(f"Test in Simulator", key=f"sim_mut_{i}"):
                            st.session_state.current_prompt = mutation['text']
                            st.success("Prompt ready for simulation!")
    
    def generate_mutations(self, source_prompt, mutation_types, num_mutations, intensity, preserve_core, ensure_clarity, randomize_order):
        """Generate prompt mutations based on specified types and settings"""
        mutations = []
        
        for i in range(num_mutations):
            # Select random mutation type for this iteration
            if mutation_types:
                mutation_type = random.choice(mutation_types)
            else:
                mutation_type = "Word Replacement"
            
            # Apply mutation based on type
            if mutation_type == "Word Replacement":
                mutated_text = self._word_replacement_mutation(source_prompt, intensity)
            elif mutation_type == "Tone Shift":
                mutated_text = self._tone_shift_mutation(source_prompt, intensity)
            elif mutation_type == "Length Extension":
                mutated_text = self._length_extension_mutation(source_prompt, intensity)
            elif mutation_type == "Length Reduction":
                mutated_text = self._length_reduction_mutation(source_prompt, intensity)
            elif mutation_type == "Structure Reformat":
                mutated_text = self._structure_reformat_mutation(source_prompt, intensity)
            elif mutation_type == "Role Change":
                mutated_text = self._role_change_mutation(source_prompt, intensity)
            elif mutation_type == "Context Addition":
                mutated_text = self._context_addition_mutation(source_prompt, intensity)
            elif mutation_type == "Instruction Modification":
                mutated_text = self._instruction_modification_mutation(source_prompt, intensity)
            else:
                mutated_text = source_prompt
            
            # Apply additional modifications
            if randomize_order and intensity > 3:
                mutated_text = self._randomize_sentence_order(mutated_text)
            
            # Calculate quality score
            score = self._calculate_mutation_score(source_prompt, mutated_text, preserve_core, ensure_clarity)
            
            # Determine changes made
            changes = self._identify_changes(source_prompt, mutated_text)
            
            mutations.append({
                'text': mutated_text,
                'type': mutation_type,
                'score': score,
                'changes': changes
            })
        
        # Sort by score (highest first)
        mutations.sort(key=lambda x: x['score'], reverse=True)
        
        return mutations
    
    def _word_replacement_mutation(self, prompt, intensity):
        """Replace words with synonyms"""
        words = prompt.split()
        num_replacements = max(1, len(words) * intensity // 10)
        
        # Synonym mappings
        synonyms = {
            'create': ['generate', 'produce', 'develop', 'build', 'construct'],
            'analyze': ['examine', 'evaluate', 'assess', 'study', 'review'],
            'write': ['compose', 'draft', 'author', 'craft', 'pen'],
            'explain': ['describe', 'clarify', 'elaborate', 'detail', 'outline'],
            'help': ['assist', 'aid', 'support', 'guide', 'facilitate'],
            'good': ['excellent', 'effective', 'quality', 'superior', 'optimal'],
            'important': ['crucial', 'vital', 'essential', 'significant', 'key'],
            'simple': ['straightforward', 'basic', 'clear', 'easy', 'direct'],
            'complex': ['sophisticated', 'intricate', 'detailed', 'comprehensive', 'advanced']
        }
        
        for _ in range(num_replacements):
            for i, word in enumerate(words):
                clean_word = re.sub(r'[^\w]', '', word.lower())
                if clean_word in synonyms and random.random() < 0.3:
                    replacement = random.choice(synonyms[clean_word])
                    # Preserve original capitalization
                    if word[0].isupper():
                        replacement = replacement.capitalize()
                    words[i] = word.replace(clean_word, replacement, 1)
        
        return ' '.join(words)
    
    def _tone_shift_mutation(self, prompt, intensity):
        """Shift the tone of the prompt"""
        tone_modifiers = {
            1: ['politely', 'kindly'],
            2: ['professionally', 'formally'],
            3: ['creatively', 'innovatively'],
            4: ['assertively', 'confidently'],
            5: ['enthusiastically', 'passionately']
        }
        
        modifiers = tone_modifiers.get(intensity, tone_modifiers[3])
        
        # Add tone modifiers
        if 'you are' in prompt.lower():
            prompt = prompt.replace('You are', f'You are {random.choice(modifiers)}')
        else:
            prompt = f"Please {random.choice(modifiers)} {prompt.lower()}"
        
        return prompt
    
    def _length_extension_mutation(self, prompt, intensity):
        """Extend the prompt with additional details"""
        extensions = [
            "Provide detailed explanations for your reasoning.",
            "Include relevant examples to illustrate your points.",
            "Consider multiple perspectives when formulating your response.",
            "Ensure your response is comprehensive and well-structured.",
            "Take into account potential edge cases or exceptions.",
            "Provide step-by-step reasoning where applicable.",
            "Consider the broader context and implications.",
            "Ensure accuracy and cite relevant information when possible."
        ]
        
        num_extensions = min(intensity, len(extensions))
        selected_extensions = random.sample(extensions, num_extensions)
        
        return prompt + ' ' + ' '.join(selected_extensions)
    
    def _length_reduction_mutation(self, prompt, intensity):
        """Reduce prompt length while preserving meaning"""
        sentences = prompt.split('.')
        
        # Remove sentences based on intensity
        removal_rate = intensity * 0.1
        num_to_remove = max(1, int(len(sentences) * removal_rate))
        
        if len(sentences) > num_to_remove + 1:  # Keep at least one sentence
            # Remove less critical sentences
            for _ in range(num_to_remove):
                if len(sentences) > 2:
                    # Prefer removing middle sentences
                    idx = random.randint(1, len(sentences) - 2)
                    sentences.pop(idx)
        
        return '.'.join(sentences)
    
    def _structure_reformat_mutation(self, prompt, intensity):
        """Reformat the structure of the prompt"""
        if intensity <= 2:
            # Minor reformatting - add bullet points
            return prompt.replace('. ', '.\n• ')
        elif intensity <= 4:
            # Medium reformatting - numbered list
            sentences = prompt.split('.')
            numbered = [f"{i+1}. {sentence.strip()}" for i, sentence in enumerate(sentences) if sentence.strip()]
            return '\n'.join(numbered)
        else:
            # Major reformatting - sections
            return f"**Objective:** {prompt}\n\n**Requirements:**\n- Be thorough\n- Be accurate\n- Be clear"
    
    def _role_change_mutation(self, prompt, intensity):
        """Change the role in the prompt"""
        roles = ['expert', 'specialist', 'professional', 'consultant', 'advisor', 'analyst', 'researcher']
        
        # Find existing role mentions
        for role in roles:
            if role in prompt.lower():
                new_role = random.choice([r for r in roles if r != role])
                prompt = prompt.replace(role, new_role)
                break
        else:
            # Add role if none exists
            prompt = f"As an {random.choice(roles)}, {prompt.lower()}"
        
        return prompt
    
    def _context_addition_mutation(self, prompt, intensity):
        """Add contextual information"""
        contexts = [
            "Consider the target audience carefully.",
            "Take into account current industry standards.",
            "Ensure the response is actionable.",
            "Consider ethical implications.",
            "Focus on practical applications.",
            "Maintain professional standards.",
            "Consider scalability and efficiency.",
            "Ensure compliance with best practices."
        ]
        
        num_contexts = min(intensity, len(contexts))
        selected_contexts = random.sample(contexts, num_contexts)
        
        return prompt + ' ' + ' '.join(selected_contexts)
    
    def _instruction_modification_mutation(self, prompt, intensity):
        """Modify existing instructions"""
        instruction_words = ['generate', 'create', 'write', 'analyze', 'explain', 'describe']
        modifications = ['thoroughly', 'carefully', 'systematically', 'comprehensively', 'precisely']
        
        for word in instruction_words:
            if word in prompt.lower():
                modifier = random.choice(modifications)
                prompt = prompt.replace(word, f"{modifier} {word}")
                break
        
        return prompt
    
    def _randomize_sentence_order(self, prompt):
        """Randomize sentence order while maintaining meaning"""
        sentences = [s.strip() for s in prompt.split('.') if s.strip()]
        
        if len(sentences) > 2:
            # Keep first sentence, randomize others
            first = sentences[0]
            rest = sentences[1:]
            random.shuffle(rest)
            sentences = [first] + rest
        
        return '. '.join(sentences) + '.'
    
    def _calculate_mutation_score(self, original, mutated, preserve_core, ensure_clarity):
        """Calculate quality score for mutation"""
        score = 5.0  # Base score
        
        # Length considerations
        len_ratio = len(mutated) / len(original) if len(original) > 0 else 1
        if 0.7 <= len_ratio <= 1.5:  # Good length ratio
            score += 1.0
        elif len_ratio < 0.5 or len_ratio > 2.0:  # Poor length ratio
            score -= 1.0
        
        # Word diversity
        original_words = set(original.lower().split())
        mutated_words = set(mutated.lower().split())
        overlap = len(original_words & mutated_words) / len(original_words) if original_words else 0
        
        if preserve_core:
            if overlap >= 0.6:  # Good core preservation
                score += 1.0
            elif overlap < 0.3:  # Poor core preservation
                score -= 2.0
        else:
            if 0.3 <= overlap <= 0.7:  # Good variation
                score += 1.0
        
        # Clarity check
        if ensure_clarity:
            if len(mutated.split()) > 5 and '.' in mutated:  # Basic structure
                score += 0.5
        
        # Randomness bonus
        score += random.uniform(-0.5, 0.5)
        
        return max(1.0, min(10.0, score))  # Clamp between 1-10
    
    def _identify_changes(self, original, mutated):
        """Identify what changes were made"""
        original_words = original.split()
        mutated_words = mutated.split()
        
        if len(mutated_words) > len(original_words) * 1.2:
            return "Extended with additional details"
        elif len(mutated_words) < len(original_words) * 0.8:
            return "Reduced length"
        elif original.lower() != mutated.lower():
            return "Modified wording and structure"
        else:
            return "Minor formatting changes"
