"""
policy_metrics.py

Enhanced module for calculating metrics for generated policies.
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
        
        # Count activity policies
        for fragment_id, activities in fragment_activity_policies.items():
            for activity_id, policies in activities.items():
                permission_count += len(policies.get('permission', []))
                prohibition_count += len(policies.get('prohibition', []))
                obligation_count += len(policies.get('obligation', []))
        
        # Count dependency policies
        for dependency_key, policies in fragment_dependency_policies.items():
            for policy in policies:
                if 'permission' in policy:
                    permission_count += len(policy['permission'])
                if 'prohibition' in policy:
                    prohibition_count += len(policy['prohibition'])
                if 'obligation' in policy:
                    obligation_count += len(policy['obligation'])
        
        metrics['permissions'] = permission_count
        metrics['prohibitions'] = prohibition_count
        metrics['obligations'] = obligation_count
        metrics['total_rules'] = permission_count + prohibition_count + obligation_count
        
        # Calculate rules per fragment
        if fragments and metrics['total_fragments'] > 0:
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
            for fragment_id, activities in fragment_activity_policies.items():
                fragment_rule_counts[fragment_id] = 0
                for activity_id, policies in activities.items():
                    fragment_rule_counts[fragment_id] += len(policies.get('permission', []))
                    fragment_rule_counts[fragment_id] += len(policies.get('prohibition', []))
                    fragment_rule_counts[fragment_id] += len(policies.get('obligation', []))
            
            metrics['fragment_rule_counts'] = fragment_rule_counts
        
        # Calculate policy type distribution
        if metrics['total_rules'] > 0:
            metrics['permission_percentage'] = (permission_count / metrics['total_rules']) * 100
            metrics['prohibition_percentage'] = (prohibition_count / metrics['total_rules']) * 100
            metrics['obligation_percentage'] = (obligation_count / metrics['total_rules']) * 100
        
        return metrics
    
    def generate_metrics_report(self, metrics):
        """
        Generate a human-readable report from metrics.
        
        Args:
            metrics (dict): Metrics dictionary
            
        Returns:
            str: Formatted report
        """
        report = []
        report.append("# Policy Metrics Report")
        report.append("")
        
        # Basic counts
        report.append("## Overview")
        report.append(f"- Total Fragments: {metrics.get('total_fragments', 'N/A')}")
        report.append(f"- Total Activities: {metrics.get('total_activities', 'N/A')}")
        report.append(f"- Total Rules: {metrics.get('total_rules', 0)}")
        report.append("")
        
        # Rule types
        report.append("## Rule Distribution")
        report.append(f"- Permissions: {metrics.get('permissions', 0)} ({metrics.get('permission_percentage', 0):.1f}%)")
        report.append(f"- Prohibitions: {metrics.get('prohibitions', 0)} ({metrics.get('prohibition_percentage', 0):.1f}%)")
        report.append(f"- Obligations: {metrics.get('obligations', 0)} ({metrics.get('obligation_percentage', 0):.1f}%)")
        report.append("")
        
        # Ratios
        report.append("## Ratios")
        report.append(f"- Rules per Fragment: {metrics.get('rules_per_fragment', 'N/A'):.2f}")
        report.append(f"- Rules per Activity: {metrics.get('rules_per_activity', 'N/A'):.2f}")
        report.append("")
        
        # Conflicts
        report.append("## Consistency")
        report.append(f"- Conflicts: {metrics.get('conflicts', 'N/A')}")
        report.append("")
        
        # Execution metrics
        if 'execution_metrics' in metrics:
            report.append("## Execution Times")
            for metric, value in metrics['execution_metrics'].items():
                report.append(f"- {metric}: {value:.4f} seconds")
            report.append("")
        
        # Fragment rule distribution
        if 'fragment_rule_counts' in metrics:
            report.append("## Rules per Fragment")
            for fragment_id, count in metrics['fragment_rule_counts'].items():
                report.append(f"- Fragment {fragment_id}: {count} rules")
        
        return "\n".join(report)
    
    def save_metrics_report(self, metrics, output_file):
        """
        Save metrics report to a file.
        
        Args:
            metrics (dict): Metrics dictionary
            output_file (str): Path to output file
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            report = self.generate_metrics_report(metrics)
            with open(output_file, 'w') as f:
                f.write(report)
            return True
        except Exception as e:
            logger.error(f"Error saving metrics report: {str(e)}")
            return False
