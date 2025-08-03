class MutationConfig:
    """Configuration settings for prompt mutations"""
    
    def __init__(self):
        # Default mutation settings
        self.default_intensity = 3
        self.max_mutations = 10
        self.min_mutations = 1
        
        # Quality thresholds
        self.min_quality_score = 3.0
        self.max_quality_score = 10.0
        
        # Mutation type weights (higher = more likely to be selected)
        self.mutation_weights = {
            'Word Replacement': 3,
            'Tone Shift': 2,
            'Length Extension': 2,
            'Length Reduction': 1,
            'Structure Reformat': 2,
            'Role Change': 1,
            'Context Addition': 2,
            'Instruction Modification': 3
        }
        
        # Preservation settings
        self.default_preserve_core = True
        self.default_ensure_clarity = True
        
        # Advanced settings
        self.max_word_replacements_per_mutation = 5
        self.synonym_replacement_probability = 0.3
        self.sentence_reorder_threshold = 3  # minimum intensity for sentence reordering
        
        # Quality scoring weights
        self.length_ratio_weight = 1.0
        self.word_overlap_weight = 1.5
        self.clarity_weight = 1.0
        self.structure_weight = 0.5
    
    def get_mutation_parameters(self, mutation_type, intensity):
        """Get specific parameters for a mutation type"""
        params = {
            'intensity': intensity,
            'preserve_meaning': self.default_preserve_core
        }
        
        if mutation_type == 'Word Replacement':
            params['max_replacements'] = min(intensity * 2, self.max_word_replacements_per_mutation)
            params['replacement_prob'] = self.synonym_replacement_probability
            
        elif mutation_type == 'Length Extension':
            params['num_extensions'] = intensity
            params['extension_complexity'] = intensity
            
        elif mutation_type == 'Length Reduction':
            params['reduction_rate'] = intensity * 0.1
            params['preserve_key_sentences'] = True
            
        elif mutation_type == 'Structure Reformat':
            params['formatting_level'] = intensity
            params['add_sections'] = intensity > 3
            
        return params
    
    def validate_mutation_settings(self, mutation_types, num_mutations, intensity):
        """Validate mutation settings"""
        errors = []
        
        if not mutation_types:
            errors.append("At least one mutation type must be selected")
        
        if not (self.min_mutations <= num_mutations <= self.max_mutations):
            errors.append(f"Number of mutations must be between {self.min_mutations} and {self.max_mutations}")
        
        if not (1 <= intensity <= 5):
            errors.append("Intensity must be between 1 and 5")
        
        return errors
