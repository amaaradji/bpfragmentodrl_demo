"""
enhanced_fragmenter.py

Enhanced fragmenter for fragmenting business processes.
"""

import logging
import time

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class EnhancedFragmenter:
    """Enhanced fragmenter for fragmenting business processes."""
    
    def __init__(self, bp_model):
        """
        Initialize the enhanced fragmenter.
        
        Args:
            bp_model (dict): Business process model
        """
        self.bp_model = bp_model
    
    def fragment_process(self, strategy='activity'):
        """
        Fragment the business process.
        
        Args:
            strategy (str): Fragmentation strategy ('activity', 'gateway', 'hybrid')
            
        Returns:
            tuple: (fragments, fragment_dependencies)
        """
        start_time = time.time()
        
        if strategy == 'activity':
            fragments, fragment_dependencies = self._fragment_by_activity()
        elif strategy == 'gateway':
            fragments, fragment_dependencies = self._fragment_by_gateway()
        elif strategy == 'hybrid':
            fragments, fragment_dependencies = self._fragment_hybrid()
        else:
            logger.error(f"Unknown fragmentation strategy: {strategy}")
            return [], {}
        
        # Ensure we have valid data structures
        if not fragments:
            fragments = []
        if not fragment_dependencies:
            fragment_dependencies = {}
            
        logger.info(f"Process fragmented into {len(fragments)} fragments using {strategy} strategy in {time.time() - start_time:.2f} seconds")
        
        return fragments, fragment_dependencies
    
    def _fragment_by_activity(self):
        """
        Fragment the process by activity.
        
        Returns:
            tuple: (fragments, fragment_dependencies)
        """
        fragments = []
        fragment_dependencies = {}
        
        # Get activities and sequence flows
        activities = self.bp_model.get('activities', [])
        sequence_flows = self.bp_model.get('sequence_flows', [])
        
        # Create one fragment per activity
        for i, activity in enumerate(activities):
            fragment_id = str(i + 1)
            fragment = {
                'id': fragment_id,
                'activities': [activity],
                'entry_points': [],
                'exit_points': []
            }
            fragments.append(fragment)
        
        # Create dependencies based on sequence flows
        dependency_id = 1
        for flow in sequence_flows:
            source_ref = flow.get('source_ref')
            target_ref = flow.get('target_ref')
            
            # Find source and target fragments
            source_fragment = None
            target_fragment = None
            
            for fragment in fragments:
                for act in fragment['activities']:
                    if act['id'] == source_ref:
                        source_fragment = fragment
                    if act['id'] == target_ref:
                        target_fragment = fragment
            
            # Create dependency if both fragments are found
            if source_fragment and target_fragment and source_fragment['id'] != target_fragment['id']:
                dependency_key = f"{source_fragment['id']}-{target_fragment['id']}"
                
                if dependency_key not in fragment_dependencies:
                    fragment_dependencies[dependency_key] = {
                        'id': str(dependency_id),
                        'source_fragment_id': source_fragment['id'],
                        'target_fragment_id': target_fragment['id'],
                        'flows': []
                    }
                    dependency_id += 1
                
                fragment_dependencies[dependency_key]['flows'].append(flow)
                
                # Update entry and exit points
                if flow['id'] not in source_fragment['exit_points']:
                    source_fragment['exit_points'].append(flow['id'])
                
                if flow['id'] not in target_fragment['entry_points']:
                    target_fragment['entry_points'].append(flow['id'])
        
        # Log the results for debugging
        logger.debug(f"Created {len(fragments)} fragments and {len(fragment_dependencies)} dependencies")
        
        return fragments, fragment_dependencies
    
    def _fragment_by_gateway(self):
        """
        Fragment the process by gateway.
        
        Returns:
            tuple: (fragments, fragment_dependencies)
        """
        fragments = []
        fragment_dependencies = {}
        
        # Get activities, gateways, and sequence flows
        activities = self.bp_model.get('activities', [])
        gateways = self.bp_model.get('gateways', [])
        sequence_flows = self.bp_model.get('sequence_flows', [])
        
        # Create gateway-based fragments
        if not gateways:
            # If no gateways, create a single fragment with all activities
            fragment = {
                'id': '1',
                'activities': activities,
                'entry_points': [],
                'exit_points': []
            }
            fragments.append(fragment)
        else:
            # Create fragments based on gateways
            # This is a simplified implementation for the demo
            # In a real implementation, this would be more sophisticated
            
            # Create a fragment for each gateway and its connected activities
            for i, gateway in enumerate(gateways):
                fragment_id = str(i + 1)
                
                # Find activities connected to this gateway
                connected_activities = []
                for flow in sequence_flows:
                    if flow['source_ref'] == gateway['id'] or flow['target_ref'] == gateway['id']:
                        # Find the activity on the other end
                        activity_id = flow['target_ref'] if flow['source_ref'] == gateway['id'] else flow['source_ref']
                        
                        # Check if it's an activity
                        for activity in activities:
                            if activity['id'] == activity_id:
                                if activity not in connected_activities:
                                    connected_activities.append(activity)
                
                fragment = {
                    'id': fragment_id,
                    'activities': connected_activities,
                    'gateway': gateway,
                    'entry_points': [],
                    'exit_points': []
                }
                fragments.append(fragment)
            
            # If there are activities not connected to any gateway, create a separate fragment
            unconnected_activities = []
            for activity in activities:
                is_connected = False
                for fragment in fragments:
                    if activity in fragment['activities']:
                        is_connected = True
                        break
                
                if not is_connected:
                    unconnected_activities.append(activity)
            
            if unconnected_activities:
                fragment_id = str(len(fragments) + 1)
                fragment = {
                    'id': fragment_id,
                    'activities': unconnected_activities,
                    'entry_points': [],
                    'exit_points': []
                }
                fragments.append(fragment)
        
        # Create dependencies based on sequence flows
        dependency_id = 1
        for flow in sequence_flows:
            source_ref = flow.get('source_ref')
            target_ref = flow.get('target_ref')
            
            # Find source and target fragments
            source_fragment = None
            target_fragment = None
            
            for fragment in fragments:
                # Check if source is in this fragment
                for act in fragment['activities']:
                    if act['id'] == source_ref:
                        source_fragment = fragment
                
                # Check if gateway is in this fragment
                if 'gateway' in fragment and fragment['gateway']['id'] == source_ref:
                    source_fragment = fragment
                
                # Check if target is in this fragment
                for act in fragment['activities']:
                    if act['id'] == target_ref:
                        target_fragment = fragment
                
                # Check if gateway is in this fragment
                if 'gateway' in fragment and fragment['gateway']['id'] == target_ref:
                    target_fragment = fragment
            
            # Create dependency if both fragments are found
            if source_fragment and target_fragment and source_fragment['id'] != target_fragment['id']:
                dependency_key = f"{source_fragment['id']}-{target_fragment['id']}"
                
                if dependency_key not in fragment_dependencies:
                    fragment_dependencies[dependency_key] = {
                        'id': str(dependency_id),
                        'source_fragment_id': source_fragment['id'],
                        'target_fragment_id': target_fragment['id'],
                        'flows': []
                    }
                    dependency_id += 1
                
                fragment_dependencies[dependency_key]['flows'].append(flow)
                
                # Update entry and exit points
                if flow['id'] not in source_fragment['exit_points']:
                    source_fragment['exit_points'].append(flow['id'])
                
                if flow['id'] not in target_fragment['entry_points']:
                    target_fragment['entry_points'].append(flow['id'])
        
        # Log the results for debugging
        logger.debug(f"Created {len(fragments)} fragments and {len(fragment_dependencies)} dependencies")
        
        return fragments, fragment_dependencies
    
    def _fragment_hybrid(self):
        """
        Fragment the process using a hybrid approach.
        
        Returns:
            tuple: (fragments, fragment_dependencies)
        """
        # For the demo, we'll use a simple hybrid approach that combines activity and gateway fragmentation
        # In a real implementation, this would be more sophisticated
        
        # First, fragment by gateway
        gateway_fragments, gateway_dependencies = self._fragment_by_gateway()
        
        # Then, for large fragments (more than 3 activities), further fragment by activity
        fragments = []
        fragment_dependencies = gateway_dependencies.copy() if gateway_dependencies else {}
        
        fragment_id = len(gateway_fragments) + 1
        dependency_id = len(gateway_dependencies) + 1
        
        for gf in gateway_fragments:
            if len(gf['activities']) <= 3:
                # Keep small fragments as is
                fragments.append(gf)
            else:
                # Further fragment large fragments
                for i, activity in enumerate(gf['activities']):
                    sub_fragment_id = str(fragment_id)
                    fragment_id += 1
                    
                    sub_fragment = {
                        'id': sub_fragment_id,
                        'activities': [activity],
                        'parent_fragment_id': gf['id'],
                        'entry_points': [],
                        'exit_points': []
                    }
                    fragments.append(sub_fragment)
                    
                    # Create dependencies between sub-fragments
                    if i > 0:
                        prev_sub_fragment_id = str(fragment_id - 2)
                        dependency_key = f"{prev_sub_fragment_id}-{sub_fragment_id}"
                        
                        fragment_dependencies[dependency_key] = {
                            'id': str(dependency_id),
                            'source_fragment_id': prev_sub_fragment_id,
                            'target_fragment_id': sub_fragment_id,
                            'flows': []
                        }
                        dependency_id += 1
        
        # Log the results for debugging
        logger.debug(f"Created {len(fragments)} fragments and {len(fragment_dependencies)} dependencies")
        
        return fragments, fragment_dependencies
