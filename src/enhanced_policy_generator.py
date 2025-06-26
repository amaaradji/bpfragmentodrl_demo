"""
enhanced_policy_generator.py

Enhanced policy generator for generating policies based on templates.
"""

import logging
import time
from src.policy_consistency_checker import PolicyConsistencyChecker

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class EnhancedPolicyGenerator:
    """Enhanced policy generator for generating policies based on templates."""
    
    def __init__(self, bp_model, fragments, fragment_dependencies, bp_policy=None):
        """
        Initialize the enhanced policy generator.
        
        Args:
            bp_model (dict): Business process model
            fragments (list): Process fragments
            fragment_dependencies (dict): Fragment dependencies
            bp_policy (dict, optional): BP-level policy
        """
        self.bp_model = bp_model
        self.fragments = fragments
        self.fragment_dependencies = fragment_dependencies
        self.bp_policy = bp_policy
    
    def generate_policies(self):
        """
        Generate policies for fragments.
        
        Returns:
            tuple: (fragment_activity_policies, fragment_dependency_policies)
        """
        start_time = time.time()
        
        # Generate activity policies
        fragment_activity_policies = self._generate_activity_policies()
        
        # Generate dependency policies
        fragment_dependency_policies = self._generate_dependency_policies()
        
        logger.info(f"Policy generation completed in {time.time() - start_time:.2f} seconds")
        
        return fragment_activity_policies, fragment_dependency_policies
    
    def _generate_activity_policies(self):
        """
        Generate activity policies for fragments.
        
        Returns:
            dict: Fragment activity policies
        """
        fragment_activity_policies = {}
        
        for fragment in self.fragments:
            fragment_id = fragment['id']
            activities = fragment.get('activities', [])
            
            # Initialize policies for this fragment
            fragment_policies = []
            
            for activity in activities:
                activity_id = activity.get('id')
                activity_name = activity.get('name', '').lower()
                
                # Generate policies based on activity name semantics
                if 'approve' in activity_name or 'review' in activity_name:
                    # Approval activities
                    fragment_policies.extend(self._generate_approval_policies(activity_id))
                elif 'payment' in activity_name or 'pay' in activity_name:
                    # Payment activities
                    fragment_policies.extend(self._generate_payment_policies(activity_id))
                elif 'verify' in activity_name or 'check' in activity_name:
                    # Verification activities
                    fragment_policies.extend(self._generate_verification_policies(activity_id))
                else:
                    # Default activities
                    fragment_policies.extend(self._generate_default_policies(activity_id))
            
            fragment_activity_policies[fragment_id] = fragment_policies
        
        return fragment_activity_policies
    
    def _generate_dependency_policies(self):
        """
        Generate dependency policies for fragments.
        
        Returns:
            dict: Fragment dependency policies
        """
        fragment_dependency_policies = {}
        
        for dependency_key, dependency in self.fragment_dependencies.items():
            source_fragment_id = dependency.get('source_fragment_id')
            target_fragment_id = dependency.get('target_fragment_id')
            
            # Create dependency policies
            policies = [
                {
                    "rule_type": "permission",
                    "action": "execute",
                    "assigner": "SystemPolicy",
                    "assignee": "ProcessEngine",
                    "constraints": [
                        {
                            "constraint_type": "dependency",
                            "operator": "eq",
                            "value": f"fragment_{source_fragment_id}_completed"
                        }
                    ]
                },
                {
                    "rule_type": "prohibition",
                    "action": "execute",
                    "assigner": "SystemPolicy",
                    "assignee": "ProcessEngine",
                    "constraints": [
                        {
                            "constraint_type": "dependency",
                            "operator": "neq",
                            "value": f"fragment_{source_fragment_id}_completed"
                        }
                    ]
                }
            ]
            
            fragment_dependency_policies[dependency_key] = policies
        
        return fragment_dependency_policies
    
    def _generate_approval_policies(self, activity_id):
        """
        Generate policies for approval activities.
        
        Args:
            activity_id (str): Activity ID
            
        Returns:
            list: Generated policies
        """
        return [
            {
                "target_activity_id": activity_id,
                "rule_type": "permission",
                "action": "execute",
                "assigner": "SystemPolicy",
                "assignee": "Manager",
                "constraints": []
            },
            {
                "target_activity_id": activity_id,
                "rule_type": "permission",
                "action": "execute",
                "assigner": "SystemPolicy",
                "assignee": "Supervisor",
                "constraints": []
            },
            {
                "target_activity_id": activity_id,
                "rule_type": "prohibition",
                "action": "execute",
                "assigner": "SystemPolicy",
                "assignee": "Clerk",
                "constraints": []
            },
            {
                "target_activity_id": activity_id,
                "rule_type": "obligation",
                "action": "log",
                "assigner": "SystemPolicy",
                "assignee": "Manager",
                "constraints": [
                    {
                        "constraint_type": "temporal",
                        "operator": "lteq",
                        "value": "24h"
                    }
                ]
            }
        ]
    
    def _generate_payment_policies(self, activity_id):
        """
        Generate policies for payment activities.
        
        Args:
            activity_id (str): Activity ID
            
        Returns:
            list: Generated policies
        """
        return [
            {
                "target_activity_id": activity_id,
                "rule_type": "permission",
                "action": "execute",
                "assigner": "SystemPolicy",
                "assignee": "FinancialOfficer",
                "constraints": []
            },
            {
                "target_activity_id": activity_id,
                "rule_type": "prohibition",
                "action": "execute",
                "assigner": "SystemPolicy",
                "assignee": "Clerk",
                "constraints": []
            },
            {
                "target_activity_id": activity_id,
                "rule_type": "prohibition",
                "action": "execute",
                "assigner": "SystemPolicy",
                "assignee": "Manager",
                "constraints": []
            },
            {
                "target_activity_id": activity_id,
                "rule_type": "obligation",
                "action": "record",
                "assigner": "SystemPolicy",
                "assignee": "FinancialOfficer",
                "constraints": [
                    {
                        "constraint_type": "temporal",
                        "operator": "lteq",
                        "value": "1h"
                    }
                ]
            }
        ]
    
    def _generate_verification_policies(self, activity_id):
        """
        Generate policies for verification activities.
        
        Args:
            activity_id (str): Activity ID
            
        Returns:
            list: Generated policies
        """
        return [
            {
                "target_activity_id": activity_id,
                "rule_type": "permission",
                "action": "execute",
                "assigner": "SystemPolicy",
                "assignee": "QualityController",
                "constraints": []
            },
            {
                "target_activity_id": activity_id,
                "rule_type": "permission",
                "action": "execute",
                "assigner": "SystemPolicy",
                "assignee": "Supervisor",
                "constraints": []
            },
            {
                "target_activity_id": activity_id,
                "rule_type": "prohibition",
                "action": "execute",
                "assigner": "SystemPolicy",
                "assignee": "Clerk",
                "constraints": []
            },
            {
                "target_activity_id": activity_id,
                "rule_type": "obligation",
                "action": "report",
                "assigner": "SystemPolicy",
                "assignee": "QualityController",
                "constraints": [
                    {
                        "constraint_type": "temporal",
                        "operator": "lteq",
                        "value": "48h"
                    }
                ]
            }
        ]
    
    def _generate_default_policies(self, activity_id):
        """
        Generate default policies for activities.
        
        Args:
            activity_id (str): Activity ID
            
        Returns:
            list: Generated policies
        """
        return [
            {
                "target_activity_id": activity_id,
                "rule_type": "permission",
                "action": "execute",
                "assigner": "SystemPolicy",
                "assignee": "Clerk",
                "constraints": []
            },
            {
                "target_activity_id": activity_id,
                "rule_type": "permission",
                "action": "execute",
                "assigner": "SystemPolicy",
                "assignee": "Manager",
                "constraints": []
            },
            {
                "target_activity_id": activity_id,
                "rule_type": "obligation",
                "action": "log",
                "assigner": "SystemPolicy",
                "assignee": "Clerk",
                "constraints": [
                    {
                        "constraint_type": "temporal",
                        "operator": "lteq",
                        "value": "24h"
                    }
                ]
            }
        ]
