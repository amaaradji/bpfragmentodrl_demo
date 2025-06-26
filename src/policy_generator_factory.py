"""
policy_generator_factory.py

Factory for creating policy generators based on the specified approach.
"""

import logging
from src.enhanced_policy_generator import EnhancedPolicyGenerator
from src.enhanced_policy_generator_llm_fixed import EnhancedPolicyGeneratorLLM

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class PolicyGeneratorFactory:
    """Factory for creating policy generators."""
    
    @staticmethod
    def create_policy_generator(approach, bp_model, fragments, fragment_dependencies, bp_policy=None):
        """
        Create a policy generator based on the specified approach.
        
        Args:
            approach (str): Policy generation approach ('template' or 'llm')
            bp_model (dict): Business process model
            fragments (list): List of fragments
            fragment_dependencies (dict): Fragment dependencies
            bp_policy (dict, optional): BP-level policy
            
        Returns:
            object: Policy generator instance
        """
        if approach.lower() == 'llm':
            logger.info("Creating LLM-based policy generator")
            return EnhancedPolicyGeneratorLLM(bp_model, fragments, fragment_dependencies, bp_policy)
        else:
            logger.info("Creating template-based policy generator")
            return EnhancedPolicyGenerator(bp_model, fragments, fragment_dependencies, bp_policy)
    
    @staticmethod
    def get_available_approaches():
        """
        Get the list of available policy generation approaches.
        
        Returns:
            list: List of available approaches
        """
        return ['template', 'llm']
