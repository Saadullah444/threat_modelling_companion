threat_json_prompts = """
I want you to act like an expert in CyberSecurity. You should perform a threat modeling analysis on the provided threat model JSON file.

1 - Analyze and understand all components, data flows, and security considerations defined in the threat model JSON.
   - For components, focus on their roles, configurations, and vulnerabilities.
   - For data flows, focus on how data moves between components and potential security issues.

2 - Perform a detailed threat modeling analysis on each component and data flow found in the model. Try to extract all the threats based on ISO/OWASP/NIST.

3 - Output the result in a table format, only including columns for:
   <component/dataflow>, <Threat>,  <Type of threat>, <Mitigation Method>, <brief rationale for each mitigation>

NOTE: The following threats have already been identified. You should identify and return ONLY the threats that are NOT present in this list.

Already identified threats: {detected_threats}

The threat model to analyze: {threat_model}
"""