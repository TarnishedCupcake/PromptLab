import streamlit as st
import re
import random
from logs.logger import PromptLabLogger

class PromptAnalyzer:
    def __init__(self):
        self.logger = PromptLabLogger()
        self.analysis_categories = {
            'clarity': 'How clear and understandable is the prompt?',
            'tone': 'What is the tone and how appropriate is it?',
            'bias': 'Does the prompt contain biases or problematic assumptions?',
            'effectiveness': 'How likely is this prompt to achieve its intended goal?'
        }
        
    def render(self):
        st.header("📊 Prompt Analyzer")
        st.markdown("Analyze prompts for quality, bias, tone, and effectiveness using advanced metrics.")
        
        # Input section
        col1, col2 = st.columns([2, 1])
        
        with col1:
            st.subheader("Prompt to Analyze")
            
            # Source prompt selection
            source_option = st.radio("Prompt Source:", ["Use Current Prompt", "Enter Custom Prompt"])
            
            if source_option == "Use Current Prompt":
                if st.session_state.current_prompt:
                    analysis_prompt = st.text_area("Current Prompt:", value=st.session_state.current_prompt, height=150, disabled=True)
                else:
                    st.warning("No current prompt set. Please create one first.")
                    analysis_prompt = ""
            else:
                analysis_prompt = st.text_area("Enter Prompt to Analyze:", height=150)
        
        with col2:
            st.subheader("Analysis Settings")
            
            # Analysis depth
            analysis_depth = st.selectbox("Analysis Depth:", ["Quick Scan", "Standard Analysis", "Deep Analysis"])
            
            # Specific categories to analyze
            selected_categories = st.multiselect(
                "Analysis Categories:",
                list(self.analysis_categories.keys()),
                default=list(self.analysis_categories.keys())
            )
            
            # Advanced options
            with st.expander("Advanced Options"):
                include_suggestions = st.checkbox("Include Improvement Suggestions", value=True)
                compare_benchmarks = st.checkbox("Compare Against Benchmarks", value=True)
                detailed_breakdown = st.checkbox("Detailed Score Breakdown", value=False)
        
        # Run analysis
        if st.button("Analyze Prompt", type="primary") and analysis_prompt and selected_categories:
            with st.spinner("Analyzing prompt..."):
                analysis_results = self.analyze_prompt(
                    analysis_prompt,
                    selected_categories,
                    analysis_depth,
                    include_suggestions,
                    compare_benchmarks,
                    detailed_breakdown
                )
                
                st.session_state.analysis_results = analysis_results
                self.logger.log(f"Analyzed prompt with {len(selected_categories)} categories", "SUCCESS")
        
        # Display results
        if st.session_state.analysis_results:
            self._display_analysis_results(st.session_state.analysis_results, detailed_breakdown)
    
    def analyze_prompt(self, prompt, categories, depth, include_suggestions, compare_benchmarks, detailed_breakdown):
        """Perform comprehensive prompt analysis"""
        results = {
            'prompt': prompt,
            'overall_score': 0.0,
            'category_scores': {},
            'analysis_depth': depth,
            'timestamp': self._get_timestamp()
        }
        
        total_score = 0.0
        
        for category in categories:
            if category == 'clarity':
                score, details = self._analyze_clarity(prompt, depth)
            elif category == 'tone':
                score, details = self._analyze_tone(prompt, depth)
            elif category == 'bias':
                score, details = self._analyze_bias(prompt, depth)
            elif category == 'effectiveness':
                score, details = self._analyze_effectiveness(prompt, depth)
            else:
                score, details = 5.0, {"analysis": "Category not recognized"}
            
            results['category_scores'][category] = {
                'score': score,
                'details': details,
                'grade': self._score_to_grade(score)
            }
            
            total_score += score
        
        results['overall_score'] = total_score / len(categories) if categories else 0.0
        results['overall_grade'] = self._score_to_grade(results['overall_score'])
        
        # Add suggestions if requested
        if include_suggestions:
            results['suggestions'] = self._generate_suggestions(prompt, results['category_scores'])
        
        # Add benchmark comparison if requested
        if compare_benchmarks:
            results['benchmark_comparison'] = self._compare_to_benchmarks(results['overall_score'], categories)
        
        # Add detailed breakdown if requested
        if detailed_breakdown:
            results['detailed_breakdown'] = self._generate_detailed_breakdown(prompt, results['category_scores'])
        
        return results
    
    def _analyze_clarity(self, prompt, depth):
        """Analyze prompt clarity"""
        score = 5.0  # Base score
        details = {}
        
        # Length analysis
        word_count = len(prompt.split())
        sentence_count = len([s for s in prompt.split('.') if s.strip()])
        
        details['word_count'] = word_count
        details['sentence_count'] = sentence_count
        
        # Optimal length check
        if 20 <= word_count <= 200:
            score += 1.0
            details['length_assessment'] = "Optimal length"
        elif word_count < 10:
            score -= 1.5
            details['length_assessment'] = "Too short - may lack context"
        elif word_count > 300:
            score -= 1.0
            details['length_assessment'] = "May be too verbose"
        else:
            details['length_assessment'] = "Acceptable length"
        
        # Sentence structure
        avg_sentence_length = word_count / sentence_count if sentence_count > 0 else word_count
        
        if 10 <= avg_sentence_length <= 25:
            score += 0.5
            details['sentence_structure'] = "Well-structured sentences"
        elif avg_sentence_length > 40:
            score -= 0.5
            details['sentence_structure'] = "Sentences may be too complex"
        else:
            details['sentence_structure'] = "Acceptable sentence structure"
        
        # Instruction clarity
        instruction_words = ['create', 'generate', 'analyze', 'explain', 'describe', 'write', 'help', 'provide']
        has_clear_instruction = any(word in prompt.lower() for word in instruction_words)
        
        if has_clear_instruction:
            score += 1.0
            details['instruction_clarity'] = "Clear instructions present"
        else:
            score -= 1.0
            details['instruction_clarity'] = "Instructions could be clearer"
        
        # Specificity check
        specific_terms = len(re.findall(r'\b[A-Z][a-z]*\b', prompt))  # Proper nouns/specific terms
        if specific_terms > 2:
            score += 0.5
            details['specificity'] = f"Good specificity ({specific_terms} specific terms)"
        else:
            details['specificity'] = "Could be more specific"
        
        # Question vs statement analysis
        question_count = prompt.count('?')
        if question_count > 0:
            details['question_analysis'] = f"Contains {question_count} questions"
        else:
            details['question_analysis'] = "Statement-based prompt"
        
        # Complexity indicators
        complex_words = len([word for word in prompt.split() if len(word) > 8])
        complexity_ratio = complex_words / word_count if word_count > 0 else 0
        
        if complexity_ratio < 0.2:
            score += 0.5
            details['complexity'] = "Appropriately simple language"
        elif complexity_ratio > 0.4:
            score -= 0.5
            details['complexity'] = "May be overly complex"
        else:
            details['complexity'] = "Balanced complexity"
        
        # Deep analysis for higher depth levels
        if depth in ["Standard Analysis", "Deep Analysis"]:
            # Readability assessment
            details['readability_notes'] = self._assess_readability(prompt)
            
            # Context completeness
            context_indicators = ['context', 'background', 'situation', 'scenario']
            has_context = any(word in prompt.lower() for word in context_indicators)
            if has_context:
                score += 0.5
                details['context_assessment'] = "Includes contextual information"
            else:
                details['context_assessment'] = "Limited contextual information"
        
        if depth == "Deep Analysis":
            # Ambiguity detection
            ambiguous_terms = ['it', 'this', 'that', 'they', 'something', 'anything']
            ambiguity_count = sum(prompt.lower().count(term) for term in ambiguous_terms)
            if ambiguity_count > 3:
                score -= 0.5
                details['ambiguity_warning'] = f"High ambiguity ({ambiguity_count} ambiguous terms)"
            else:
                details['ambiguity_assessment'] = "Low ambiguity"
        
        return max(1.0, min(10.0, score)), details
    
    def _analyze_tone(self, prompt, depth):
        """Analyze prompt tone"""
        score = 5.0  # Base score
        details = {}
        
        # Tone indicators
        tone_patterns = {
            'professional': ['please', 'kindly', 'would you', 'could you', 'thank you'],
            'casual': ['hey', 'hi', 'cool', 'awesome', 'great'],
            'formal': ['request', 'require', 'shall', 'must', 'should'],
            'urgent': ['urgent', 'immediately', 'asap', 'quickly', 'fast'],
            'friendly': ['help', 'assist', 'support', 'guide', 'thanks'],
            'demanding': ['need', 'want', 'give me', 'do this', 'make sure']
        }
        
        detected_tones = []
        tone_scores = {}
        
        for tone, patterns in tone_patterns.items():
            pattern_count = sum(prompt.lower().count(pattern) for pattern in patterns)
            if pattern_count > 0:
                detected_tones.append(tone)
                tone_scores[tone] = pattern_count
        
        details['detected_tones'] = detected_tones
        details['tone_distribution'] = tone_scores
        
        # Tone consistency
        if len(detected_tones) == 1:
            score += 1.0
            details['tone_consistency'] = f"Consistent {detected_tones[0]} tone"
        elif len(detected_tones) <= 2:
            score += 0.5
            details['tone_consistency'] = f"Mostly consistent tone ({', '.join(detected_tones)})"
        elif len(detected_tones) > 3:
            score -= 1.0
            details['tone_consistency'] = "Mixed tones may confuse the AI"
        else:
            details['tone_consistency'] = "Neutral tone"
        
        # Politeness assessment
        polite_indicators = ['please', 'thank you', 'kindly', 'would you mind', 'if possible']
        politeness_score = sum(prompt.lower().count(indicator) for indicator in polite_indicators)
        
        if politeness_score > 0:
            score += 0.5
            details['politeness'] = f"Polite tone ({politeness_score} polite expressions)"
        else:
            details['politeness'] = "Neutral politeness"
        
        # Emotional indicators
        emotional_words = {
            'positive': ['exciting', 'amazing', 'wonderful', 'excellent', 'fantastic'],
            'negative': ['terrible', 'awful', 'horrible', 'disappointing', 'frustrating'],
            'neutral': ['standard', 'normal', 'regular', 'typical', 'ordinary']
        }
        
        emotion_detected = None
        for emotion, words in emotional_words.items():
            if any(word in prompt.lower() for word in words):
                emotion_detected = emotion
                break
        
        if emotion_detected:
            details['emotional_tone'] = f"Contains {emotion_detected} emotional language"
            if emotion_detected == 'positive':
                score += 0.3
            elif emotion_detected == 'negative':
                score -= 0.3
        else:
            details['emotional_tone'] = "Neutral emotional tone"
        
        # Deep analysis
        if depth in ["Standard Analysis", "Deep Analysis"]:
            # Authority level
            authority_indicators = ['must', 'should', 'need to', 'required', 'mandatory']
            authority_score = sum(prompt.lower().count(indicator) for indicator in authority_indicators)
            
            if authority_score > 2:
                details['authority_level'] = "High authority/demanding"
            elif authority_score > 0:
                details['authority_level'] = "Moderate authority"
            else:
                details['authority_level'] = "Low authority/collaborative"
        
        if depth == "Deep Analysis":
            # Formality analysis
            formal_indicators = ['furthermore', 'therefore', 'consequently', 'accordingly']
            informal_indicators = ['gonna', 'wanna', 'yeah', 'okay', 'stuff']
            
            formality_score = sum(prompt.lower().count(word) for word in formal_indicators)
            informality_score = sum(prompt.lower().count(word) for word in informal_indicators)
            
            if formality_score > informality_score:
                details['formality_level'] = "Formal language"
            elif informality_score > formality_score:
                details['formality_level'] = "Informal language"
            else:
                details['formality_level'] = "Balanced formality"
        
        return max(1.0, min(10.0, score)), details
    
    def _analyze_bias(self, prompt, depth):
        """Analyze prompt for potential biases"""
        score = 8.0  # Start with high score, deduct for issues
        details = {}
        
        # Gender bias indicators
        gender_biased_terms = {
            'male_biased': ['he should', 'men are', 'guys', 'mankind', 'manpower'],
            'female_biased': ['she should', 'women are', 'girls', 'emotional', 'nurturing'],
            'neutral_preferred': ['they', 'people', 'individuals', 'humans', 'persons']
        }
        
        bias_findings = {}
        for bias_type, terms in gender_biased_terms.items():
            count = sum(prompt.lower().count(term) for term in terms)
            if count > 0:
                bias_findings[bias_type] = count
        
        if bias_findings.get('male_biased', 0) > 0 or bias_findings.get('female_biased', 0) > 0:
            score -= 1.5
            details['gender_bias_warning'] = f"Potential gender bias detected: {bias_findings}"
        else:
            details['gender_bias_assessment'] = "No obvious gender bias"
        
        # Cultural bias indicators
        cultural_assumptions = ['everyone knows', 'obviously', 'clearly', 'of course', 'naturally']
        assumption_count = sum(prompt.lower().count(phrase) for phrase in cultural_assumptions)
        
        if assumption_count > 0:
            score -= 1.0
            details['cultural_assumptions'] = f"Contains {assumption_count} assumptive phrases"
        else:
            details['cultural_assumptions'] = "No obvious cultural assumptions"
        
        # Economic bias
        economic_terms = ['expensive', 'cheap', 'luxury', 'premium', 'budget', 'high-end']
        economic_count = sum(prompt.lower().count(term) for term in economic_terms)
        
        if economic_count > 2:
            details['economic_bias_note'] = f"Contains economic assumptions ({economic_count} terms)"
        else:
            details['economic_bias_assessment'] = "No significant economic bias"
        
        # Accessibility considerations
        accessibility_issues = ['see', 'look at', 'hear', 'listen', 'walk', 'run']
        accessibility_count = sum(prompt.lower().count(term) for term in accessibility_issues)
        
        if accessibility_count > 3:
            score -= 0.5
            details['accessibility_warning'] = "May not be inclusive of all abilities"
        else:
            details['accessibility_assessment'] = "Generally inclusive language"
        
        # Deep analysis
        if depth in ["Standard Analysis", "Deep Analysis"]:
            # Age bias
            age_biased_terms = ['young people', 'old people', 'millennials', 'boomers', 'kids these days']
            age_bias_count = sum(prompt.lower().count(term) for term in age_biased_terms)
            
            if age_bias_count > 0:
                score -= 0.5
                details['age_bias_warning'] = f"Potential age bias ({age_bias_count} terms)"
            else:
                details['age_bias_assessment'] = "No obvious age bias"
        
        if depth == "Deep Analysis":
            # Technology bias
            tech_assumptions = ['use your phone', 'google it', 'check online', 'download app']
            tech_assumption_count = sum(prompt.lower().count(phrase) for phrase in tech_assumptions)
            
            if tech_assumption_count > 0:
                details['technology_assumptions'] = f"Assumes technology access ({tech_assumption_count} references)"
            else:
                details['technology_assumptions'] = "No significant technology assumptions"
            
            # Language complexity bias
            complex_words = len([word for word in prompt.split() if len(word) > 10])
            if complex_words > len(prompt.split()) * 0.3:
                score -= 0.5
                details['language_complexity_bias'] = "High complexity may exclude some users"
            else:
                details['language_accessibility'] = "Appropriate language complexity"
        
        return max(1.0, min(10.0, score)), details
    
    def _analyze_effectiveness(self, prompt, depth):
        """Analyze prompt effectiveness"""
        score = 5.0  # Base score
        details = {}
        
        # Goal clarity
        goal_indicators = ['goal', 'objective', 'purpose', 'aim', 'target', 'result', 'outcome']
        has_clear_goal = any(word in prompt.lower() for word in goal_indicators)
        
        if has_clear_goal:
            score += 1.5
            details['goal_clarity'] = "Clear goal/objective present"
        else:
            details['goal_clarity'] = "Goal could be more explicit"
        
        # Action words (effectiveness indicators)
        action_words = ['create', 'generate', 'analyze', 'explain', 'describe', 'compare', 'evaluate', 'design']
        action_count = sum(prompt.lower().count(word) for word in action_words)
        
        if action_count >= 2:
            score += 1.0
            details['action_clarity'] = f"Clear actions specified ({action_count} action words)"
        elif action_count == 1:
            score += 0.5
            details['action_clarity'] = "Basic action specified"
        else:
            score -= 1.0
            details['action_clarity'] = "No clear actions specified"
        
        # Specificity assessment
        specific_details = {
            'numbers': len(re.findall(r'\b\d+\b', prompt)),
            'proper_nouns': len(re.findall(r'\b[A-Z][a-z]+\b', prompt)),
            'technical_terms': len([word for word in prompt.split() if len(word) > 8])
        }
        
        specificity_score = sum(min(count, 3) for count in specific_details.values())
        
        if specificity_score >= 6:
            score += 1.0
            details['specificity'] = f"Highly specific ({specificity_score} specificity indicators)"
        elif specificity_score >= 3:
            score += 0.5
            details['specificity'] = f"Moderately specific ({specificity_score} specificity indicators)"
        else:
            details['specificity'] = "Could be more specific"
        
        # Context provision
        context_words = ['because', 'since', 'for', 'context', 'background', 'situation']
        context_count = sum(prompt.lower().count(word) for word in context_words)
        
        if context_count > 0:
            score += 0.5
            details['context_provision'] = f"Provides context ({context_count} context indicators)"
        else:
            details['context_provision'] = "Limited context provided"
        
        # Output format specification
        format_indicators = ['format', 'structure', 'organize', 'list', 'bullet', 'table', 'summary']
        format_count = sum(prompt.lower().count(word) for word in format_indicators)
        
        if format_count > 0:
            score += 0.5
            details['format_specification'] = f"Output format specified ({format_count} format indicators)"
        else:
            details['format_specification'] = "No specific output format requested"
        
        # Deep analysis
        if depth in ["Standard Analysis", "Deep Analysis"]:
            # Constraint analysis
            constraint_words = ['must', 'should', 'cannot', 'avoid', 'exclude', 'limit', 'within']
            constraint_count = sum(prompt.lower().count(word) for word in constraint_words)
            
            if constraint_count > 0:
                score += 0.3
                details['constraints'] = f"Includes constraints ({constraint_count} constraint words)"
            else:
                details['constraints'] = "No explicit constraints"
            
            # Examples provision
            example_indicators = ['example', 'instance', 'such as', 'like', 'for example']
            example_count = sum(prompt.lower().count(phrase) for phrase in example_indicators)
            
            if example_count > 0:
                score += 0.5
                details['examples'] = f"Includes examples ({example_count} example indicators)"
            else:
                details['examples'] = "No examples provided"
        
        if depth == "Deep Analysis":
            # Success criteria
            success_indicators = ['success', 'complete', 'finished', 'done', 'criteria', 'requirements']
            success_count = sum(prompt.lower().count(word) for word in success_indicators)
            
            if success_count > 0:
                details['success_criteria'] = f"Includes success criteria ({success_count} indicators)"
            else:
                details['success_criteria'] = "No explicit success criteria"
            
            # Measurability
            measurable_terms = ['how many', 'what percentage', 'how much', 'quantify', 'measure']
            measurable_count = sum(prompt.lower().count(phrase) for phrase in measurable_terms)
            
            if measurable_count > 0:
                score += 0.3
                details['measurability'] = f"Includes measurable elements ({measurable_count} indicators)"
            else:
                details['measurability'] = "Limited measurable criteria"
        
        return max(1.0, min(10.0, score)), details
    
    def _assess_readability(self, prompt):
        """Assess readability of the prompt"""
        sentences = len([s for s in prompt.split('.') if s.strip()])
        words = len(prompt.split())
        
        if sentences == 0:
            return "Single sentence or fragment"
        
        avg_words_per_sentence = words / sentences
        
        if avg_words_per_sentence <= 15:
            return "Easy to read"
        elif avg_words_per_sentence <= 25:
            return "Moderately complex"
        else:
            return "Complex - may be difficult to parse"
    
    def _generate_suggestions(self, prompt, category_scores):
        """Generate improvement suggestions based on analysis"""
        suggestions = []
        
        for category, score_data in category_scores.items():
            score = score_data['score']
            
            if category == 'clarity' and score < 7:
                suggestions.append("🔍 Clarity: Consider breaking down complex sentences and adding more specific instructions.")
            
            if category == 'tone' and score < 6:
                suggestions.append("🎯 Tone: Ensure consistent tone throughout and consider adding polite language.")
            
            if category == 'bias' and score < 7:
                suggestions.append("⚖️ Bias: Review for inclusive language and avoid cultural assumptions.")
            
            if category == 'effectiveness' and score < 6:
                suggestions.append("🚀 Effectiveness: Add clear goals, specific requirements, and desired output format.")
        
        # General suggestions
        word_count = len(prompt.split())
        if word_count < 20:
            suggestions.append("📏 Length: Consider adding more context and specific requirements.")
        elif word_count > 200:
            suggestions.append("✂️ Length: Consider condensing to focus on essential requirements.")
        
        return suggestions
    
    def _compare_to_benchmarks(self, overall_score, categories):
        """Compare scores to industry benchmarks"""
        benchmarks = {
            'excellent': 8.5,
            'good': 7.0,
            'average': 5.5,
            'needs_improvement': 4.0
        }
        
        comparison = {}
        
        for benchmark, threshold in benchmarks.items():
            if overall_score >= threshold:
                comparison['level'] = benchmark
                comparison['percentile'] = self._calculate_percentile(overall_score)
                break
        
        comparison['recommendation'] = self._get_benchmark_recommendation(overall_score)
        
        return comparison
    
    def _calculate_percentile(self, score):
        """Calculate approximate percentile based on score"""
        # Simulated percentile calculation
        if score >= 9.0:
            return random.randint(90, 99)
        elif score >= 8.0:
            return random.randint(75, 89)
        elif score >= 7.0:
            return random.randint(60, 74)
        elif score >= 6.0:
            return random.randint(40, 59)
        elif score >= 5.0:
            return random.randint(25, 39)
        else:
            return random.randint(1, 24)
    
    def _get_benchmark_recommendation(self, score):
        """Get recommendation based on benchmark comparison"""
        if score >= 8.5:
            return "Excellent prompt! Consider sharing as a best practice example."
        elif score >= 7.0:
            return "Good prompt with minor areas for improvement."
        elif score >= 5.5:
            return "Average prompt. Focus on clarity and specificity improvements."
        else:
            return "Significant improvements needed. Review all categories."
    
    def _generate_detailed_breakdown(self, prompt, category_scores):
        """Generate detailed score breakdown"""
        breakdown = {
            'word_analysis': {
                'total_words': len(prompt.split()),
                'unique_words': len(set(prompt.lower().split())),
                'avg_word_length': sum(len(word) for word in prompt.split()) / len(prompt.split()) if prompt.split() else 0
            },
            'sentence_analysis': {
                'total_sentences': len([s for s in prompt.split('.') if s.strip()]),
                'avg_sentence_length': len(prompt.split()) / len([s for s in prompt.split('.') if s.strip()]) if [s for s in prompt.split('.') if s.strip()] else 0
            },
            'category_weights': {
                'clarity': 30,
                'effectiveness': 25,
                'tone': 25,
                'bias': 20
            }
        }
        
        return breakdown
    
    def _score_to_grade(self, score):
        """Convert numerical score to letter grade"""
        if score >= 9.0:
            return "A+"
        elif score >= 8.5:
            return "A"
        elif score >= 8.0:
            return "A-"
        elif score >= 7.5:
            return "B+"
        elif score >= 7.0:
            return "B"
        elif score >= 6.5:
            return "B-"
        elif score >= 6.0:
            return "C+"
        elif score >= 5.5:
            return "C"
        elif score >= 5.0:
            return "C-"
        elif score >= 4.0:
            return "D"
        else:
            return "F"
    
    def _get_timestamp(self):
        """Get current timestamp"""
        import datetime
        return datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    def _display_analysis_results(self, results, detailed_breakdown):
        """Display comprehensive analysis results"""
        st.markdown("---")
        st.subheader("📊 Analysis Results")
        
        # Overall score display
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric(
                "Overall Score",
                f"{results['overall_score']:.1f}/10",
                help="Composite score across all analyzed categories"
            )
        
        with col2:
            st.metric(
                "Grade",
                results['overall_grade'],
                help="Letter grade equivalent"
            )
        
        with col3:
            if 'benchmark_comparison' in results:
                st.metric(
                    "Percentile",
                    f"{results['benchmark_comparison']['percentile']}th",
                    help="Compared to industry benchmarks"
                )
        
        # Category scores
        st.markdown("### Category Breakdown")
        
        for category, score_data in results['category_scores'].items():
            with st.expander(f"📋 {category.title()} Analysis (Score: {score_data['score']:.1f}/10, Grade: {score_data['grade']})"):
                
                # Score visualization
                progress = score_data['score'] / 10.0
                st.progress(progress)
                
                # Details
                st.markdown("**Analysis Details:**")
                for key, value in score_data['details'].items():
                    if isinstance(value, dict):
                        st.write(f"**{key.replace('_', ' ').title()}:** {value}")
                    else:
                        st.write(f"**{key.replace('_', ' ').title()}:** {value}")
        
        # Suggestions
        if 'suggestions' in results and results['suggestions']:
            st.markdown("### 💡 Improvement Suggestions")
            for suggestion in results['suggestions']:
                st.info(suggestion)
        
        # Benchmark comparison
        if 'benchmark_comparison' in results:
            st.markdown("### 📈 Benchmark Comparison")
            comparison = results['benchmark_comparison']
            st.success(f"**Performance Level:** {comparison['level'].title()}")
            st.info(comparison['recommendation'])
        
        # Detailed breakdown
        if detailed_breakdown and 'detailed_breakdown' in results:
            st.markdown("### 🔍 Detailed Breakdown")
            breakdown = results['detailed_breakdown']
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("**Word Analysis:**")
                for key, value in breakdown['word_analysis'].items():
                    st.write(f"- {key.replace('_', ' ').title()}: {value:.1f}" if isinstance(value, float) else f"- {key.replace('_', ' ').title()}: {value}")
            
            with col2:
                st.markdown("**Sentence Analysis:**")
                for key, value in breakdown['sentence_analysis'].items():
                    st.write(f"- {key.replace('_', ' ').title()}: {value:.1f}" if isinstance(value, float) else f"- {key.replace('_', ' ').title()}: {value}")
        
        # Export results
        if st.button("📥 Export Analysis Results"):
            import json
            results_json = json.dumps(results, indent=2, default=str)
            st.download_button(
                label="Download as JSON",
                data=results_json,
                file_name=f"prompt_analysis_{results['timestamp'].replace(' ', '_').replace(':', '-')}.json",
                mime="application/json"
            )
