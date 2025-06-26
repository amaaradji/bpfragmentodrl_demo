"""
enhanced_policy_generator_llm_fixed.py

Fixed enhanced policy generator using LLM (Azure OpenAI) for generating policies.
"""

import os
import json
import logging
import time

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
            AzureOpenAI: Azure OpenAI client or None if not available
        """
        try:
            # Try to import and initialize Azure OpenAI
            from openai import AzureOpenAI
            
            api_key = os.getenv("AZURE_OPENAI_API_KEY")
            api_endpoint = os.getenv("AZURE_OPENAI_ENDPOINT", "https://api.azure.com/openai")
            api_version = os.getenv("AZURE_OPENAI_API_VERSION", "2023-05-15")
            
            if not api_key:
                logger.warning("Azure OpenAI API key not found. LLM-based policy generation will use fallback.")
                return None
            
            client = AzureOpenAI(
                api_key=api_key,
                api_version=api_version,
                azure_endpoint=api_endpoint
            )
            
            logger.info("Azure OpenAI client initialized successfully")
            return client
        except ImportError:
            logger.warning("Azure OpenAI library not available. LLM-based policy generation will use fallback.")
            return None
        except Exception as e:
            logger.error(f"Error initializing Azure OpenAI client: {str(e)}")
            return None
    
    def generate_policies(self):
        """
        Generate policies for fragments using LLM or fallback to template-based approach.
        
        Returns:
            tuple: (fragment_activity_policies, fragment_dependency_policies)
        """
        start_time = time.time()
        
        # Generate activity policies
        fragment_activity_policies = self._generate_activity_policies()
        
        # Generate dependency policies
        fragment_dependency_policies = self._generate_dependency_policies()
        
        logger.info(f"LLM-based policy generation completed in {time.time() - start_time:.2f} seconds")
        
        return fragment_activity_policies, fragment_dependency_policies
    
    def _generate_activity_policies(self):
        """
        Generate activity policies for all fragments.
        
        Returns:
            dict: Fragment activity policies
        """
        fragment_activity_policies = {}
        
        for fragment in self.fragments:
            fragment_id = fragment.get('id')
            if self.client:
                # Use LLM-based generation
                policies = self._generate_policies_with_llm(fragment_id, fragment)
            else:
                # Fallback to template-based generation
                policies = self._generate_policies_with_template(fragment_id, fragment)
            
            fragment_activity_policies[fragment_id] = policies
        
        return fragment_activity_policies
    
    def _generate_dependency_policies(self):
        """
        Generate dependency policies for fragment dependencies.
        
        Returns:
            dict: Fragment dependency policies
        """
        # For now, return empty dependency policies
        # This can be enhanced later to generate dependency-specific policies
        return {}
    
    def _generate_policies_with_llm(self, fragment_id, fragment):
        """
        Generate policies for a fragment using LLM.
        
        Args:
            fragment_id (str): Fragment ID
            fragment (dict): Fragment data
            
        Returns:
            list: Generated policies
        """
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
            # Fallback to template-based generation
            return self._generate_policies_with_template(fragment_id, fragment)
    
    def _generate_policies_with_template(self, fragment_id, fragment):
        """
        Generate policies for a fragment using template-based approach (fallback).
        
        Args:
            fragment_id (str): Fragment ID
            fragment (dict): Fragment data
            
        Returns:
            list: Generated policies
        """
        policies = []
        
        for activity in fragment.get('activities', []):
            activity_id = activity.get('id')
            activity_name = activity.get('name', '').lower()
            
            # Generate policies based on activity type
            if 'approve' in activity_name or 'accept' in activity_name:
                policies.extend(self._generate_approval_policies(activity_id))
            elif 'pay' in activity_name or 'payment' in activity_name:
                policies.extend(self._generate_payment_policies(activity_id))
            elif 'verify' in activity_name or 'check' in activity_name or 'review' in activity_name:
                policies.extend(self._generate_verification_policies(activity_id))
            else:
                policies.extend(self._generate_default_policies(activity_id))
        
        return policies
    
    def _prepare_prompt(self, fragment_id, fragment):
        """
        Prepare prompt for LLM policy generation.
        
        Args:
            fragment_id (str): Fragment ID
            fragment (dict): Fragment data
            
        Returns:
            str: Formatted prompt
        """
        activities = fragment.get('activities', [])
        activity_names = [activity.get('name', 'Unnamed') for activity in activities]
        
        prompt = f"""
Generate ODRL policies for business process fragment {fragment_id} containing the following activities:
{', '.join(activity_names)}

For each activity, generate appropriate permissions, prohibitions, and obligations.
Consider typical business roles: Manager, Supervisor, Clerk, Customer.

Return the policies in JSON format with the following structure:
[
  {{
    "target_activity_id": "activity_id",
    "rule_type": "permission|prohibition|obligation",
    "action": "execute|read|write|log",
    "assigner": "SystemPolicy",
    "assignee": "role_name",
    "constraints": []
  }}
]

Focus on realistic business constraints and role-based access control.
"""
        return prompt
    
    def _parse_llm_response(self, response):
        """
        Parse LLM response to extract policies.
        
        Args:
            response: LLM response object
            
        Returns:
            list: Parsed policies
        """
        try:
            content = response.choices[0].message.content
            
            # Try to extract JSON from the response
            start_idx = content.find('[')
            end_idx = content.rfind(']') + 1
            
            if start_idx != -1 and end_idx != -1:
                json_str = content[start_idx:end_idx]
                policies = json.loads(json_str)
                return policies
            else:
                logger.error("Could not find valid JSON in LLM response")
                return []
        except Exception as e:
            logger.error(f"Error parsing LLM response: {str(e)}")
            return []
    
    def _generate_approval_policies(self, activity_id):
        """Generate policies for approval activities."""
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
        """Generate policies for payment activities."""
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
                        "value": "1h"
                    }
                ]
            }
        ]
    
    def _generate_verification_policies(self, activity_id):
        """Generate policies for verification activities."""
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
    
    def _generate_default_policies(self, activity_id):
        """Generate default policies for other activities."""
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

