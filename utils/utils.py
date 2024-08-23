import logging
import os

class Utils:

    # Utils Constructor
    # logger: Logger object
    #
    # Returns: Utils object
    # Raises: None
    def __init__(self, logger: logging.Logger):
        self.logger = logger

    # Check if a finding attribute exists, returns True 
    def check_if_finding_attribute_exists(self, source: any, key_str: str) -> bool:

        if type(source) == type([]) or type(source) == type({}):
            return key_str in source
        
    # Serializes attributes into a string of findings, returns str 
    def serialize_finding_attributes(self, finding_file_key: str, findings: dict) -> str:

        result_str = ''
        for attribute in findings.keys():

            if attribute == "ruleId":
                result_str = findings[attribute] + ': ' + result_str

            if attribute == "message":
                result_str += findings[attribute] + ' - ' + finding_file_key + "\n"

        for attribute in findings.keys():

            if attribute not in [ "ruleId", "message" ]:
                result_str += attribute + ' = ' + str(findings[attribute]) + "\n"

        if result_str[-2:] == ', ':
            return result_str[:-2]
        return result_str