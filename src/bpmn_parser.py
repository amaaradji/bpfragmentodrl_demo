"""
bpmn_parser.py

Parser for BPMN files.
"""

import os
import json
import logging
import xml.etree.ElementTree as ET

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class BPMNParser:
    """Parser for BPMN files."""
    
    def __init__(self):
        """Initialize the BPMN parser."""
        # BPMN namespaces
        self.namespaces = {
            'bpmn': 'http://www.omg.org/spec/BPMN/20100524/MODEL',
            'bpmndi': 'http://www.omg.org/spec/BPMN/20100524/DI',
            'dc': 'http://www.omg.org/spec/DD/20100524/DC',
            'di': 'http://www.omg.org/spec/DD/20100524/DI'
        }
    
    def parse_file(self, file_path):
        """
        Parse a BPMN file.
        
        Args:
            file_path (str): Path to the BPMN file
            
        Returns:
            dict: Parsed BP model
        """
        try:
            # Parse XML
            tree = ET.parse(file_path)
            root = tree.getroot()
            
            # Extract process elements using namespace-aware approach
            processes = []
            for child in root:
                if child.tag.endswith('}process'):
                    processes.append(child)
            
            if not processes:
                logger.error(f"No process found in BPMN file: {file_path}")
                return None
            
            # Use the first process
            process = processes[0]
            process_id = process.get('id')
            process_name = process.get('name', 'Unnamed Process')
            
            # Extract activities
            activities = []
            for task in process:
                if task.tag.endswith('}task'):
                    activity = {
                        'id': task.get('id'),
                        'name': task.get('name', 'Unnamed Task'),
                        'type': 'task'
                    }
                    activities.append(activity)
            
            # Extract gateways
            gateways = []
            for child in process:
                if 'Gateway' in child.tag:
                    gateway_data = {
                        'id': child.get('id'),
                        'name': child.get('name', 'Unnamed Gateway'),
                        'type': child.tag.split('}')[-1]
                    }
                    gateways.append(gateway_data)
            
            # Extract events
            events = []
            for child in process:
                if 'Event' in child.tag:
                    event_data = {
                        'id': child.get('id'),
                        'name': child.get('name', f'Unnamed Event'),
                        'type': child.tag.split('}')[-1]
                    }
                    events.append(event_data)
            
            # Extract sequence flows
            sequence_flows = []
            for child in process:
                if child.tag.endswith('}sequenceFlow'):
                    flow_data = {
                        'id': child.get('id'),
                        'name': child.get('name', ''),
                        'source_ref': child.get('sourceRef'),
                        'target_ref': child.get('targetRef')
                    }
                    sequence_flows.append(flow_data)
            
            # Create BP model
            bp_model = {
                'id': process_id,
                'name': process_name,
                'source_file': os.path.basename(file_path),
                'activities': activities,
                'gateways': gateways,
                'events': events,
                'sequence_flows': sequence_flows
            }
            
            return bp_model
        except Exception as e:
            logger.error(f"Error parsing BPMN file: {str(e)}")
            return None
