"""
bp_policy_generator.py

Business Process level policy generator for creating ODRL-compliant policies
that govern the entire business process before fragmentation.
"""

import logging
import json
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class BPPolicyGenerator:
    """Generator for BP-level policies using predefined templates."""
    
    def __init__(self):
        """Initialize the BP policy generator."""
        self.policy_templates = {
            'standard': self._get_standard_template(),
            'financial': self._get_financial_template(),
            'healthcare': self._get_healthcare_template(),
            'manufacturing': self._get_manufacturing_template(),
            'custom': self._get_custom_template()
        }
    
    def generate_bp_policy(self, template='standard'):
        """
        Generate a BP-level policy using the specified template.
        
        Args:
            template (str): Policy template to use
            
        Returns:
            dict: Generated BP-level policy
        """
        try:
            if template not in self.policy_templates:
                logger.warning(f"Unknown template '{template}', using 'standard'")
                template = 'standard'
            
            policy = self.policy_templates[template].copy()
            
            # Add metadata
            policy['metadata'] = {
                'generated_at': datetime.now().isoformat(),
                'generator': 'BPFragmentODRL',
                'template': template,
                'version': '1.0.0'
            }
            
            logger.info(f"Generated BP-level policy using '{template}' template")
            return policy
            
        except Exception as e:
            logger.error(f"Error generating BP policy: {str(e)}")
            return self._get_default_policy()
    
    def _get_standard_template(self):
        """Standard business process policy template."""
        return {
            "@context": "http://www.w3.org/ns/odrl/2/",
            "@type": "Policy",
            "uid": "bp-policy-standard",
            "profile": "http://example.org/bp-policies",
            "permission": [
                {
                    "target": "bp:process",
                    "action": "execute",
                    "assignee": "role:process-owner",
                    "constraint": [
                        {
                            "leftOperand": "dateTime",
                            "operator": "gteq",
                            "rightOperand": "business-hours"
                        }
                    ]
                },
                {
                    "target": "bp:activities",
                    "action": "read",
                    "assignee": "role:participant"
                }
            ],
            "prohibition": [
                {
                    "target": "bp:process",
                    "action": "modify",
                    "assignee": "role:external-user"
                }
            ],
            "obligation": [
                {
                    "target": "bp:process",
                    "action": "log",
                    "assignee": "system:audit",
                    "constraint": [
                        {
                            "leftOperand": "event",
                            "operator": "eq",
                            "rightOperand": "process-start"
                        }
                    ]
                }
            ]
        }
    
    def _get_financial_template(self):
        """Financial process policy template with compliance requirements."""
        return {
            "@context": "http://www.w3.org/ns/odrl/2/",
            "@type": "Policy",
            "uid": "bp-policy-financial",
            "profile": "http://example.org/financial-policies",
            "permission": [
                {
                    "target": "bp:financial-process",
                    "action": "execute",
                    "assignee": "role:financial-officer",
                    "constraint": [
                        {
                            "leftOperand": "amount",
                            "operator": "lteq",
                            "rightOperand": "approval-limit"
                        }
                    ]
                }
            ],
            "prohibition": [
                {
                    "target": "bp:sensitive-data",
                    "action": "export",
                    "assignee": "role:external-auditor"
                },
                {
                    "target": "bp:financial-process",
                    "action": "execute",
                    "assignee": "role:unauthorized",
                    "constraint": [
                        {
                            "leftOperand": "location",
                            "operator": "neq",
                            "rightOperand": "approved-jurisdiction"
                        }
                    ]
                }
            ],
            "obligation": [
                {
                    "target": "bp:transaction",
                    "action": "audit-log",
                    "assignee": "system:compliance"
                },
                {
                    "target": "bp:approval",
                    "action": "notify",
                    "assignee": "role:supervisor",
                    "constraint": [
                        {
                            "leftOperand": "amount",
                            "operator": "gt",
                            "rightOperand": "10000"
                        }
                    ]
                }
            ]
        }
    
    def _get_healthcare_template(self):
        """Healthcare process policy template with privacy requirements."""
        return {
            "@context": "http://www.w3.org/ns/odrl/2/",
            "@type": "Policy",
            "uid": "bp-policy-healthcare",
            "profile": "http://example.org/healthcare-policies",
            "permission": [
                {
                    "target": "bp:patient-data",
                    "action": "access",
                    "assignee": "role:healthcare-provider",
                    "constraint": [
                        {
                            "leftOperand": "purpose",
                            "operator": "eq",
                            "rightOperand": "treatment"
                        }
                    ]
                }
            ],
            "prohibition": [
                {
                    "target": "bp:patient-data",
                    "action": "share",
                    "assignee": "role:third-party",
                    "constraint": [
                        {
                            "leftOperand": "consent",
                            "operator": "eq",
                            "rightOperand": "false"
                        }
                    ]
                }
            ],
            "obligation": [
                {
                    "target": "bp:patient-data",
                    "action": "encrypt",
                    "assignee": "system:security"
                },
                {
                    "target": "bp:access-log",
                    "action": "maintain",
                    "assignee": "system:audit",
                    "constraint": [
                        {
                            "leftOperand": "retention-period",
                            "operator": "eq",
                            "rightOperand": "7-years"
                        }
                    ]
                }
            ]
        }
    
    def _get_manufacturing_template(self):
        """Manufacturing process policy template with safety requirements."""
        return {
            "@context": "http://www.w3.org/ns/odrl/2/",
            "@type": "Policy",
            "uid": "bp-policy-manufacturing",
            "profile": "http://example.org/manufacturing-policies",
            "permission": [
                {
                    "target": "bp:production-line",
                    "action": "operate",
                    "assignee": "role:operator",
                    "constraint": [
                        {
                            "leftOperand": "certification",
                            "operator": "eq",
                            "rightOperand": "valid"
                        }
                    ]
                }
            ],
            "prohibition": [
                {
                    "target": "bp:safety-system",
                    "action": "override",
                    "assignee": "role:operator"
                },
                {
                    "target": "bp:production-line",
                    "action": "operate",
                    "constraint": [
                        {
                            "leftOperand": "safety-check",
                            "operator": "eq",
                            "rightOperand": "failed"
                        }
                    ]
                }
            ],
            "obligation": [
                {
                    "target": "bp:quality-check",
                    "action": "perform",
                    "assignee": "role:quality-inspector",
                    "constraint": [
                        {
                            "leftOperand": "frequency",
                            "operator": "eq",
                            "rightOperand": "every-batch"
                        }
                    ]
                }
            ]
        }
    
    def _get_custom_template(self):
        """Custom policy template for LLM-based generation."""
        return {
            "@context": "http://www.w3.org/ns/odrl/2/",
            "@type": "Policy",
            "uid": "bp-policy-custom",
            "profile": "http://example.org/custom-policies",
            "permission": [
                {
                    "target": "bp:process",
                    "action": "execute",
                    "assignee": "role:authorized-user"
                }
            ],
            "prohibition": [
                {
                    "target": "bp:process",
                    "action": "bypass",
                    "assignee": "role:any"
                }
            ],
            "obligation": [
                {
                    "target": "bp:process",
                    "action": "monitor",
                    "assignee": "system:monitoring"
                }
            ]
        }
    
    def _get_default_policy(self):
        """Default fallback policy."""
        return {
            "@context": "http://www.w3.org/ns/odrl/2/",
            "@type": "Policy",
            "uid": "bp-policy-default",
            "profile": "http://example.org/default-policies",
            "permission": [
                {
                    "target": "bp:process",
                    "action": "execute",
                    "assignee": "role:user"
                }
            ],
            "metadata": {
                "generated_at": datetime.now().isoformat(),
                "generator": "BPFragmentODRL",
                "template": "default",
                "version": "1.0.0"
            }
        }

