import datetime
import random

class PromptUtils:
    def __init__(self):
        self.prompt_templates = {
            'Text Generation': "You are a {role} specializing in {industry}. Generate {tone} text that {task}. {context} {examples} {steps} {format_spec} {constraints}",
            'Question Answering': "You are a {role} with expertise in {industry}. Answer the following question in a {tone} manner: {task}. {context} {examples} {steps} {format_spec} {constraints}",
            'Code Generation': "You are a {role} developer working in {industry}. Write code that {task}. Use a {tone} approach. {context} {examples} {steps} {format_spec} {constraints}",
            'Creative Writing': "You are a {role} creative writer specializing in {industry} content. Create {tone} writing that {task}. {context} {examples} {steps} {format_spec} {constraints}",
            'Analysis': "You are a {role} analyst in {industry}. Analyze the following in a {tone} manner: {task}. {context} {examples} {steps} {format_spec} {constraints}",
            'Translation': "You are a {role} translator with {industry} expertise. Translate the following with {tone} accuracy: {task}. {context} {examples} {steps} {format_spec} {constraints}",
            'Summarization': "You are a {role} specializing in {industry}. Summarize the following in a {tone} style: {task}. {context} {examples} {steps} {format_spec} {constraints}",
            'Classification': "You are a {role} classifier in {industry}. Classify the following using {tone} criteria: {task}. {context} {examples} {steps} {format_spec} {constraints}",
            'Instruction Following': "You are a {role} in {industry}. Follow these instructions with {tone} precision: {task}. {context} {examples} {steps} {format_spec} {constraints}",
            'Problem Solving': "You are a {role} problem solver in {industry}. Solve this problem using {tone} methodology: {task}. {context} {examples} {steps} {format_spec} {constraints}"
        }
        
        self.clarity_modifiers = {
            1: "Keep it very brief and simple.",
            2: "Use basic language and short sentences.",
            3: "Be concise but clear.",
            4: "Use straightforward explanations.",
            5: "Provide moderate detail.",
            6: "Be thorough in your explanation.",
            7: "Include comprehensive details.",
            8: "Provide in-depth analysis.",
            9: "Be extremely detailed and thorough.",
            10: "Include exhaustive detail and examples."
        }
    
    def build_prompt(self, components):
        """Build a complete prompt from components"""
        task_type = components.get('task_type', 'Text Generation')
        role = components.get('role', 'Assistant')
        industry = components.get('industry', 'General')
        tone = components.get('tone', 'Professional').lower()
        clarity = components.get('clarity', 7)
        user_task = components.get('user_task', '')
        context = components.get('context', '')
        
        # Get base template
        template = self.prompt_templates.get(task_type, self.prompt_templates['Text Generation'])
        
        # Build context section
        context_section = f"\nAdditional Context: {context}" if context else ""
        
        # Build examples section
        examples_section = "\nPlease provide relevant examples in your response." if components.get('include_examples') else ""
        
        # Build step-by-step section
        steps_section = "\nBreak down your response into clear, step-by-step instructions." if components.get('step_by_step') else ""
        
        # Build format specification
        format_spec = f"\nFormat your response as: {components.get('output_format', '')}" if components.get('output_format') else ""
        
        # Build constraints
        constraints_section = f"\nConstraints: {components.get('constraints', '')}" if components.get('constraints') else ""
        
        # Add clarity modifier
        clarity_instruction = f"\n{self.clarity_modifiers.get(clarity, '')}"
        
        # Fill template
        prompt = template.format(
            role=role,
            industry=industry,
            tone=tone,
            task=user_task if user_task else "[Specify your task here]",
            context=context_section,
            examples=examples_section,
            steps=steps_section,
            format_spec=format_spec,
            constraints=constraints_section
        )
        
        # Add clarity instruction
        prompt += clarity_instruction
        
        return prompt.strip()
    
    def get_timestamp(self):
        """Get current timestamp"""
        return datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    def validate_prompt(self, prompt):
        """Validate prompt quality"""
        issues = []
        
        if len(prompt) < 20:
            issues.append("Prompt is too short")
        
        if len(prompt) > 2000:
            issues.append("Prompt might be too long")
        
        if not any(word in prompt.lower() for word in ['you are', 'please', 'generate', 'create', 'analyze']):
            issues.append("Prompt lacks clear instructions")
        
        return issues
