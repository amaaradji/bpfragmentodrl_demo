"""
policy_consistency_checker.py

Checker for policy consistency.
"""

import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class PolicyConsistencyChecker:
    """Checker for policy consistency."""
    
    def __init__(self, fragment_activity_policies, fragment_dependency_policies):
        """
        Initialize the policy consistency checker.
        
        Args:
            fragment_activity_policies (dict): Fragment activity policies
            fragment_dependency_policies (dict): Fragment dependency policies
        """
        self.fragment_activity_policies = fragment_activity_policies
        self.fragment_dependency_policies = fragment_dependency_policies
    
    def check_consistency(self):
        """
        Check consistency of policies.
        
        Returns:
            dict: Consistency check results
        """
        # Check for conflicts within activity policies
        activity_conflicts = self._check_activity_policy_conflicts()
        
        # Check for conflicts between activity and dependency policies
        dependency_conflicts = self._check_dependency_policy_conflicts()
        
        # Combine conflicts
        all_conflicts = activity_conflicts + dependency_conflicts
        
        # Create results
        results = {
            'conflicts': all_conflicts,
            'conflict_count': len(all_conflicts),
            'is_consistent': len(all_conflicts) == 0
        }
        
        return results
    
    def _check_activity_policy_conflicts(self):
        """
        Check for conflicts within activity policies.
        
        Returns:
            list: Conflicts
        """
        conflicts = []
        
        # Check each fragment's policies
        for fragment_id, policies in self.fragment_activity_policies.items():
            # Group policies by activity
            activity_policies = {}
            for policy in policies:
                activity_id = policy.get('target_activity_id')
                if activity_id not in activity_policies:
                    activity_policies[activity_id] = []
                activity_policies[activity_id].append(policy)
            
            # Check each activity's policies
            for activity_id, act_policies in activity_policies.items():
                # Check for permission-prohibition conflicts
                permissions = [p for p in act_policies if p.get('rule_type') == 'permission']
                prohibitions = [p for p in act_policies if p.get('rule_type') == 'prohibition']
                
                for permission in permissions:
                    perm_assignee = permission.get('assignee')
                    for prohibition in prohibitions:
                        if prohibition.get('assignee') == perm_assignee and prohibition.get('action') == permission.get('action'):
                            # Found a conflict
                            conflict = {
                                'type': 'permission-prohibition',
                                'fragment_id': fragment_id,
                                'activity_id': activity_id,
                                'permission': permission,
                                'prohibition': prohibition
                            }
                            conflicts.append(conflict)
        
        return conflicts
    
    def _check_dependency_policy_conflicts(self):
        """
        Check for conflicts between activity and dependency policies.
        
        Returns:
            list: Conflicts
        """
        # For this demo, we'll assume no conflicts between activity and dependency policies
        return []
