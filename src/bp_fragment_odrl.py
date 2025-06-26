"""
bp_fragment_odrl.py

Main class for the BPFragmentODRL tool.
"""

import os
import json
import logging
import time
from src.bpmn_parser import BPMNParser
from src.bpmn_validator import BPMNValidator
from src.enhanced_fragmenter import EnhancedFragmenter
from src.policy_generator_factory import PolicyGeneratorFactory
from src.policy_consistency_checker import PolicyConsistencyChecker
from src.policy_metrics_fixed import PolicyMetrics

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class BPFragmentODRL:
    """Main class for the BPFragmentODRL tool."""
    
    def __init__(self):
        """Initialize the BPFragmentODRL tool."""
        self.bp_model = None
        self.fragments = None
        self.fragment_dependencies = None
        self.fragment_activity_policies = None
        self.fragment_dependency_policies = None
        self.consistency_results = None
        self.metrics = None
    
    def load_bpmn_file(self, file_path):
        """
        Load a BPMN file.
        
        Args:
            file_path (str): Path to the BPMN file
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            # Validate BPMN file
            validator = BPMNValidator()
            is_valid, validation_results = validator.validate_bpmn_file(file_path)
            
            if not is_valid:
                logger.error(f"Invalid BPMN file: {file_path}")
                logger.error(f"Validation results: {validation_results}")
                return False
            
            # Parse BPMN file
            parser = BPMNParser()
            self.bp_model = parser.parse_file(file_path)
            
            if not self.bp_model:
                logger.error(f"Failed to parse BPMN file: {file_path}")
                return False
            
            # Add source file information
            self.bp_model['source_file'] = os.path.basename(file_path)
            
            logger.info(f"Successfully loaded BPMN file: {file_path}")
            return True
        except Exception as e:
            logger.error(f"Error loading BPMN file: {str(e)}")
            return False
    
    def fragment_process(self, strategy='activity'):
        """
        Fragment the business process.
        
        Args:
            strategy (str): Fragmentation strategy ('activity', 'gateway', 'hybrid')
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            if not self.bp_model:
                logger.error("No BP model available. Call load_bpmn_file() first.")
                return False
            
            # Fragment the process
            fragmenter = EnhancedFragmenter(self.bp_model)
            self.fragments, self.fragment_dependencies = fragmenter.fragment_process(strategy)
            
            # Ensure we have valid data structures
            if not self.fragments:
                self.fragments = []
            if not self.fragment_dependencies:
                self.fragment_dependencies = {}
            
            logger.info(f"Process fragmented into {len(self.fragments)} fragments using {strategy} strategy")
            return True
        except Exception as e:
            logger.error(f"Error fragmenting process: {str(e)}")
            return False
    
    def generate_policies(self, approach='template', bp_policy=None):
        """
        Generate policies for fragments.
        
        Args:
            approach (str): Policy generation approach ('template' or 'llm')
            bp_policy (dict, optional): BP-level policy
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            if not self.fragments:
                logger.error("No fragments available. Call fragment_process() first.")
                return False
            
            # Create policy generator
            policy_generator = PolicyGeneratorFactory.create_policy_generator(
                approach, self.bp_model, self.fragments, self.fragment_dependencies, bp_policy
            )
            
            # Generate policies
            start_time = time.time()
            self.fragment_activity_policies, self.fragment_dependency_policies = policy_generator.generate_policies()
            
            # Ensure we have valid data structures
            if not self.fragment_activity_policies:
                self.fragment_activity_policies = {}
            if not self.fragment_dependency_policies:
                self.fragment_dependency_policies = {}
            
            logger.info(f"Policies generated using {approach} approach in {time.time() - start_time:.2f} seconds")
            logger.info(f"Generated {sum(len(policies) for policies in self.fragment_activity_policies.values())} activity policies")
            logger.info(f"Generated {sum(len(policies) for policies in self.fragment_dependency_policies.values())} dependency policies")
            
            return True
        except Exception as e:
            logger.error(f"Error generating policies: {str(e)}")
            return False
    
    def check_policy_consistency(self):
        """
        Check policy consistency.
        
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            if not self.fragment_activity_policies:
                logger.error("No policies available. Call generate_policies() first.")
                return False
            
            # Check policy consistency
            checker = PolicyConsistencyChecker(
                self.fragment_activity_policies, 
                self.fragment_dependency_policies if self.fragment_dependency_policies else {}
            )
            self.consistency_results = checker.check_consistency()
            
            # Ensure we have valid data structure
            if not self.consistency_results:
                self.consistency_results = {'conflicts': [], 'warnings': []}
            
            logger.info(f"Policy consistency checked: {len(self.consistency_results.get('conflicts', []))} conflicts, {len(self.consistency_results.get('warnings', []))} warnings")
            
            return True
        except Exception as e:
            logger.error(f"Error checking policy consistency: {str(e)}")
            return False
    
    def get_policy_metrics(self):
        """
        Get policy metrics.
        
        Returns:
            dict: Policy metrics
        """
        try:
            if not self.fragment_activity_policies:
                logger.error("No policies available. Call generate_policies() first.")
                return None
            
            # Calculate metrics
            metrics_calculator = PolicyMetrics()
            self.metrics = metrics_calculator.calculate_metrics(
                self.fragment_activity_policies, 
                self.fragment_dependency_policies if self.fragment_dependency_policies else {},
                self.fragments,
                self.consistency_results
            )
            
            logger.info(f"Policy metrics calculated")
            
            return self.metrics
        except Exception as e:
            logger.error(f"Error calculating policy metrics: {str(e)}")
            return None
    
    def save_results(self, output_dir):
        """
        Save results to files.
        
        Args:
            output_dir (str): Output directory
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            # Create output directory if it doesn't exist
            os.makedirs(output_dir, exist_ok=True)
            
            # Save BP model
            if self.bp_model:
                with open(os.path.join(output_dir, 'bp_model.json'), 'w') as f:
                    json.dump(self.bp_model, f, indent=2)
            
            # Save fragments
            if self.fragments:
                with open(os.path.join(output_dir, 'fragments.json'), 'w') as f:
                    json.dump(self.fragments, f, indent=2)
            
            # Save fragment dependencies
            if self.fragment_dependencies:
                with open(os.path.join(output_dir, 'fragment_dependencies.json'), 'w') as f:
                    json.dump(self.fragment_dependencies, f, indent=2)
            
            # Save policies
            if self.fragment_activity_policies:
                with open(os.path.join(output_dir, 'fragment_activity_policies.json'), 'w') as f:
                    json.dump(self.fragment_activity_policies, f, indent=2)
            
            if self.fragment_dependency_policies:
                with open(os.path.join(output_dir, 'fragment_dependency_policies.json'), 'w') as f:
                    json.dump(self.fragment_dependency_policies, f, indent=2)
            
            # Save consistency results
            if self.consistency_results:
                with open(os.path.join(output_dir, 'consistency_results.json'), 'w') as f:
                    json.dump(self.consistency_results, f, indent=2)
            
            # Save metrics
            if self.metrics:
                with open(os.path.join(output_dir, 'metrics.json'), 'w') as f:
                    json.dump(self.metrics, f, indent=2)
            
            logger.info(f"Results saved to {output_dir}")
            
            return True
        except Exception as e:
            logger.error(f"Error saving results: {str(e)}")
            return False
