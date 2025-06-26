"""
bpmn_validator.py

Provides validation functionality for BPMN files.
"""

import os
import logging
import xml.etree.ElementTree as ET

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class BPMNValidator:
    """Validator for BPMN files."""
    
    def __init__(self):
        """Initialize the BPMN validator."""
        # BPMN namespaces
        self.namespaces = {
            'bpmn': 'http://www.omg.org/spec/BPMN/20100524/MODEL',
            'bpmndi': 'http://www.omg.org/spec/BPMN/20100524/DI',
            'dc': 'http://www.omg.org/spec/DD/20100524/DC',
            'di': 'http://www.omg.org/spec/DD/20100524/DI'
        }
    
    def validate_bpmn_file(self, file_path):
        """
        Validate a BPMN file.
        
        Args:
            file_path (str): Path to the BPMN file
            
        Returns:
            tuple: (is_valid, validation_results)
                is_valid (bool): Whether the file is valid
                validation_results (dict): Validation results with details
        """
        if not os.path.exists(file_path):
            return False, {"overall_valid": False, "messages": ["File does not exist"]}
        
        try:
            # Parse XML
            tree = ET.parse(file_path)
            root = tree.getroot()
            
            validation_messages = []
            
            # Check for process element
            processes = []
            for child in root:
                if child.tag.endswith('}process'):
                    processes.append(child)
            
            if not processes:
                validation_messages.append("No process element found")
                return False, {"overall_valid": False, "messages": validation_messages}
            
            # Check for activities
            process = processes[0]
            tasks = []
            for child in process:
                if child.tag.endswith('}task'):
                    tasks.append(child)
            
            if not tasks:
                validation_messages.append("No tasks found in process")
            
            # Check for sequence flows
            flows = []
            for child in process:
                if child.tag.endswith('}sequenceFlow'):
                    flows.append(child)
            
            if not flows:
                validation_messages.append("No sequence flows found in process")
            
            # Check for start event
            start_events = []
            for child in process:
                if child.tag.endswith('}startEvent'):
                    start_events.append(child)
            
            if not start_events:
                validation_messages.append("No start event found in process")
            
            # Check for end event
            end_events = []
            for child in process:
                if child.tag.endswith('}endEvent'):
                    end_events.append(child)
            
            if not end_events:
                validation_messages.append("No end event found in process")
            
            # If we have validation messages, the file is not fully valid
            is_valid = len(validation_messages) == 0
            
            if is_valid:
                validation_messages.append("BPMN file is valid")
            
            # Return structured validation results
            validation_results = {
                "overall_valid": is_valid,
                "messages": validation_messages,
                "stats": {
                    "tasks": len(tasks),
                    "flows": len(flows),
                    "start_events": len(start_events),
                    "end_events": len(end_events)
                }
            }
            
            return is_valid, validation_results
        except Exception as e:
            logger.error(f"Error validating BPMN file: {str(e)}")
            return False, {"overall_valid": False, "messages": [f"Error validating BPMN file: {str(e)}"]}
    
    def validate_file(self, file_path):
        """
        Validate a BPMN file (alias for validate_bpmn_file).
        
        Args:
            file_path (str): Path to the BPMN file
            
        Returns:
            tuple: (is_valid, validation_results)
        """
        return self.validate_bpmn_file(file_path)
