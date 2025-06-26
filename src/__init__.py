"""
__init__.py

Initialize the BPFragmentODRL package.
This file enables Python to recognize the directory as a package.
"""

# Import core modules to make them available at package level
from .bpmn_parser import BPMNParser
from .bpmn_validator import BPMNValidator
from .enhanced_fragmenter import EnhancedFragmenter
from .enhanced_policy_generator import EnhancedPolicyGenerator
# from .enhanced_policy_generator_llm import EnhancedPolicyGeneratorLLM  # Commented out to avoid OpenAI dependency issues
from .policy_generator_factory import PolicyGeneratorFactory
from .policy_consistency_checker import PolicyConsistencyChecker
from .policy_metrics import PolicyMetrics
from .bp_fragment_odrl import BPFragmentODRL
