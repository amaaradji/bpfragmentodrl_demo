"""
enhanced_policy_generator_llm.py

Enhanced policy generator using LLM (Azure OpenAI) for generating policies.
"""

import os
import json
import logging
import time
from openai import AzureOpenAI

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class EnhancedPolicyGeneratorLLM:
    """Enhanced policy generator using LLM for generating policies."""
    
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
        
        # Initialize Azure OpenAI client
        self.client = self._initialize_azure_openai()
    
    def _initialize_azure_openai(self):
        """
        Initialize Azure OpenAI client.
        
        Returns:
            AzureOpenAI: Azure OpenAI client
        """
        try:
            api_key = os.getenv("AZURE_OPENAI_API_KEY")
            api_endpoint = os.getenv("AZURE_OPENAI_ENDPOINT", "https://api.azure.com/openai")
            api_version = os.getenv("AZURE_OPENAI_API_VERSION", "2023-05-15")
            deployment_name = os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME", "gpt-4")
            
            if not api_key:
                logger.error("Azure OpenAI API key not found")
                return None
            
            client = AzureOpenAI(
                api_key=api_key,
                api_version=api_version,
                azure_endpoint=api_endpoint
            )
            
            return client
        except Exception as e:
            logger.error(f"Error initializing Azure OpenAI client: {str(e)}")
            return None
    
    def generate_policies_with_llm(self, fragment_id, fragment):
        """
        Generate policies for a fragment using LLM.
        
        Args:
            fragment_id (str): Fragment ID
            fragment (dict): Fragment data
            
        Returns:
            list: Generated policies
        """
        if not self.client:
            logger.error("Azure OpenAI client not initialized")
            return []
        
        try:
            # Prepare prompt for LLM
            prompt = self._prepare_prompt(fragment_id, fragment)
            
            # Call Azure OpenAI API
            start_time = time.time()
            response = self.client.chat.completions.create(
                model=os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME", "gpt-4"),
                messages=[
                    {"role": "system", "content": "You are an expert in ODRL and business process management."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.2,
                max_tokens=2000
            )
            logger.info(f"LLM API call took {time.time() - start_time:.2f} seconds")
            
            # Parse response
            policies = self._parse_llm_response(response)
            
            return policies
        except Exception as e:
            logger.error(f"Error generating policies with LLM: {str(e)}")
            return []
    
    def _prepare_prompt(self, fragment_id, fragment):
        """
        Prepare prompt for LLM.
        
        Args:
            fragment_id (str): Fragment ID
            fragment (dict): Fragment data
            
        Returns:
            str: Prompt for LLM
        """
        # Extract fragment information
        activities = fragment.get('activities', [])
        activity_names = [activity.get('name', 'Unknown Activity') for activity in activities]
        
        # Construct prompt
        prompt = f"""
Generate ODRL policies for a business process fragment with the following details:

Fragment ID: {fragment_id}
Activities: {', '.join(activity_names)}

For each activity in the fragment, generate policies that include:
1. Permissions: What roles are allowed to execute the activity
2. Prohibitions: What roles are not allowed to execute the activity
3. Obligations: What must be done before or after executing the activity

Consider the activity names and their semantic meaning when generating policies.
For example:
- Approval activities should require manager or supervisor roles
- Payment activities should have financial department permissions
- Verification activities should have quality control permissions

Output Format:
Return a JSON object with a "policies" array containing policy objects with the following structure:
{{
  "policies": [
    {{
      "target_activity_id": "activity_id",
      "rule_type": "permission|prohibition|obligation",
      "action": "execute|access|modify|etc",
      "assigner": "role_or_system",
      "assignee": "role_that_policy_applies_to",
      "constraints": [
        {{
          "constraint_type": "temporal|spatial|role|etc",
          "operator": "eq|gt|lt|etc",
          "value": "constraint_value"
        }}
      ]
    }}
  ]
}}

Example:
{{
  "policies": [
    {{
      "target_activity_id": "Activity_1",
      "rule_type": "permission",
      "action": "execute",
      "assigner": "SystemPolicy",
      "assignee": "Manager",
      "constraints": [
        {{
          "constraint_type": "temporal",
          "operator": "lteq",
          "value": "24h"
        }}
      ]
    }}
  ]
}}

Generate policies that are business-relevant and security-focused.
"""
        
        return prompt
    
    def _parse_llm_response(self, response):
        """
        Parse LLM response.
        
        Args:
            response: LLM response
            
        Returns:
            list: Parsed policies
        """
        try:
            # Extract content from response
            content = response.choices[0].message.content
            
            # Try to parse JSON from content
            # First, find JSON block if it's embedded in text
            json_start = content.find('{')
            json_end = content.rfind('}') + 1
            
            if json_start >= 0 and json_end > json_start:
                json_content = content[json_start:json_end]
                data = json.loads(json_content)
                
                # Extract policies
                policies = data.get('policies', [])
                
                return policies
            else:
                logger.error("No JSON found in LLM response")
                return []
        except Exception as e:
            logger.error(f"Error parsing LLM response: {str(e)}")
            return []
    
    def _generate_rule_based_dependency_policies(self, fragment_dependencies):
        """
        Generate dependency policies using rule-based approach.
        
        Args:
            fragment_dependencies (dict): Fragment dependencies
            
        Returns:
            dict: Generated dependency policies
        """
        dependency_policies = {}
        
        for dependency_key, dependency in fragment_dependencies.items():
            source_fragment_id = dependency.get('source_fragment_id')
            target_fragment_id = dependency.get('target_fragment_id')
            
            # Create a simple dependency policy
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
                }
            ]
            
            dependency_policies[dependency_key] = policies
        
        return dependency_policies
