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
        Generate activity policies for fragments, considering BP-level policy.
        
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
                
                # Generate base policies based on activity name semantics
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
                
                # Apply BP-level policy constraints if available
                if self.bp_policy:
                    fragment_policies = self._apply_bp_policy_constraints(fragment_policies, activity_id)
            
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

    def _apply_bp_policy_constraints(self, fragment_policies, activity_id):
        """
        Apply BP-level policy constraints to fragment policies.
        
        Args:
            fragment_policies (list): Current fragment policies
            activity_id (str): Activity ID
            
        Returns:
            list: Updated fragment policies with BP constraints
        """
        if not self.bp_policy:
            return fragment_policies
        
        try:
            # Extract constraints from BP-level policy
            bp_permissions = self.bp_policy.get('permission', [])
            bp_prohibitions = self.bp_policy.get('prohibition', [])
            bp_obligations = self.bp_policy.get('obligation', [])
            
            # Apply BP-level permissions as additional constraints
            for bp_permission in bp_permissions:
                if 'constraint' in bp_permission:
                    for policy in fragment_policies:
                        if policy.get('rule_type') == 'permission':
                            # Add BP constraints to fragment permissions
                            if 'constraints' not in policy:
                                policy['constraints'] = []
                            
                            for bp_constraint in bp_permission['constraint']:
                                policy['constraints'].append({
                                    "constraint_type": "bp_policy",
                                    "operator": bp_constraint.get('operator', 'eq'),
                                    "value": bp_constraint.get('rightOperand', 'unknown'),
                                    "source": "bp_level_policy"
                                })
            
            # Apply BP-level prohibitions
            for bp_prohibition in bp_prohibitions:
                # Add prohibition policies derived from BP level
                fragment_policies.append({
                    "target_activity_id": activity_id,
                    "rule_type": "prohibition",
                    "action": bp_prohibition.get('action', 'execute'),
                    "assigner": "BPLevelPolicy",
                    "assignee": bp_prohibition.get('assignee', 'role:any'),
                    "constraints": [
                        {
                            "constraint_type": "bp_policy_prohibition",
                            "operator": "inherited",
                            "value": "bp_level_constraint",
                            "source": "bp_level_policy"
                        }
                    ]
                })
            
            # Apply BP-level obligations
            for bp_obligation in bp_obligations:
                # Add obligation policies derived from BP level
                fragment_policies.append({
                    "target_activity_id": activity_id,
                    "rule_type": "obligation",
                    "action": bp_obligation.get('action', 'log'),
                    "assigner": "BPLevelPolicy",
                    "assignee": bp_obligation.get('assignee', 'system:audit'),
                    "constraints": [
                        {
                            "constraint_type": "bp_policy_obligation",
                            "operator": "inherited",
                            "value": "bp_level_requirement",
                            "source": "bp_level_policy"
                        }
                    ]
                })
            
            logger.info(f"Applied BP-level policy constraints to activity {activity_id}")
            
        except Exception as e:
            logger.warning(f"Error applying BP policy constraints: {str(e)}")
        
        return fragment_policies

