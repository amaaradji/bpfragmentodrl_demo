"""
policy_metrics_fixed.py

Fixed version of policy metrics that handles the actual data structure.
"""

import json
import logging
from collections import defaultdict

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class PolicyMetrics:
    """
    Calculate metrics for generated policies.
    """
    
    def calculate_metrics(self, fragment_activity_policies, fragment_dependency_policies, fragments=None, consistency_results=None):
        """
        Calculate comprehensive metrics for the generated policies.
        
        Args:
            fragment_activity_policies (dict): Fragment activity policies
            fragment_dependency_policies (dict): Fragment dependency policies
            fragments (list, optional): List of fragments
            consistency_results (dict, optional): Results from consistency checking
            
        Returns:
            dict: Metrics dictionary
        """
        metrics = {}
        
        # Count fragments and activities
        if fragments:
            metrics['total_fragments'] = len(fragments)
            metrics['total_activities'] = sum(len(fragment.get('activities', [])) for fragment in fragments)
        
        # Count rules by type
        permission_count = 0
        prohibition_count = 0
        obligation_count = 0
        
        # Count activity policies - handle the actual data structure
        for fragment_id, policies in fragment_activity_policies.items():
            if isinstance(policies, list):
                for policy in policies:
                    rule_type = policy.get('rule_type', '')
                    if rule_type == 'permission':
                        permission_count += 1
                    elif rule_type == 'prohibition':
                        prohibition_count += 1
                    elif rule_type == 'obligation':
                        obligation_count += 1
        
        # Count dependency policies
        for dependency_key, policies in fragment_dependency_policies.items():
            if isinstance(policies, list):
                for policy in policies:
                    rule_type = policy.get('rule_type', '')
                    if rule_type == 'permission':
                        permission_count += 1
                    elif rule_type == 'prohibition':
                        prohibition_count += 1
                    elif rule_type == 'obligation':
                        obligation_count += 1
        
        metrics['permissions'] = permission_count
        metrics['prohibitions'] = prohibition_count
        metrics['obligations'] = obligation_count
        metrics['total_rules'] = permission_count + prohibition_count + obligation_count
        
        # Calculate rules per fragment
        if fragments and metrics.get('total_fragments', 0) > 0:
            metrics['rules_per_fragment'] = metrics['total_rules'] / metrics['total_fragments']
        
        # Calculate rules per activity
        if metrics.get('total_activities', 0) > 0:
            metrics['rules_per_activity'] = metrics['total_rules'] / metrics['total_activities']
        
        # Count conflicts if available
        if consistency_results and 'conflicts' in consistency_results:
            metrics['conflicts'] = len(consistency_results['conflicts'])
        else:
            metrics['conflicts'] = 0
        
        # Calculate policy distribution by fragment
        if fragments:
            fragment_rule_counts = {}
            for fragment_id, policies in fragment_activity_policies.items():
                fragment_rule_counts[fragment_id] = len(policies) if isinstance(policies, list) else 0
            
            metrics['fragment_rule_counts'] = fragment_rule_counts
        
        # Calculate policy type distribution
        if metrics['total_rules'] > 0:
            metrics['permission_percentage'] = (permission_count / metrics['total_rules']) * 100
            metrics['prohibition_percentage'] = (prohibition_count / metrics['total_rules']) * 100
            metrics['obligation_percentage'] = (obligation_count / metrics['total_rules']) * 100
        
        return metrics
    
    def generate_metrics_report(self, metrics):
        """
        Generate a human-readable metrics report.
        
        Args:
            metrics (dict): Metrics dictionary
            
        Returns:
            str: Formatted metrics report
        """
        report = []
        report.append("Policy Generation Metrics Report")
        report.append("=" * 40)
        
        # Fragment and activity counts
        if 'total_fragments' in metrics:
            report.append(f"Total Fragments: {metrics['total_fragments']}")
        if 'total_activities' in metrics:
            report.append(f"Total Activities: {metrics['total_activities']}")
        
        # Rule counts
        report.append(f"Total Rules: {metrics.get('total_rules', 0)}")
        report.append(f"  Permissions: {metrics.get('permissions', 0)}")
        report.append(f"  Prohibitions: {metrics.get('prohibitions', 0)}")
        report.append(f"  Obligations: {metrics.get('obligations', 0)}")
        
        # Averages
        if 'rules_per_fragment' in metrics:
            report.append(f"Rules per Fragment: {metrics['rules_per_fragment']:.2f}")
        if 'rules_per_activity' in metrics:
            report.append(f"Rules per Activity: {metrics['rules_per_activity']:.2f}")
        
        # Percentages
        if 'permission_percentage' in metrics:
            report.append(f"Permission Percentage: {metrics['permission_percentage']:.1f}%")
        if 'prohibition_percentage' in metrics:
            report.append(f"Prohibition Percentage: {metrics['prohibition_percentage']:.1f}%")
        if 'obligation_percentage' in metrics:
            report.append(f"Obligation Percentage: {metrics['obligation_percentage']:.1f}%")
        
        # Conflicts
        report.append(f"Conflicts: {metrics.get('conflicts', 0)}")
        
        # Fragment distribution
        if 'fragment_rule_counts' in metrics:
            report.append("\nFragment Rule Distribution:")
            for fragment_id, count in metrics['fragment_rule_counts'].items():
                report.append(f"  Fragment {fragment_id}: {count} rules")
        
        return "\n".join(report)
    
    def save_metrics_report(self, metrics, output_file):
        """
        Save metrics report to file.
        
        Args:
            metrics (dict): Metrics dictionary
            output_file (str): Output file path
        """
        report = self.generate_metrics_report(metrics)
        
        with open(output_file, 'w') as f:
            f.write(report)
        
        logger.info(f"Metrics report saved to {output_file}")

