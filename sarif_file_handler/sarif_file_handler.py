import logging
from sarif import loader
import os

from utils.utils import Utils

# SARIF - class to handle Static Analysis Results Interchange Format (SARIF)
class SARIFFileHandler:

    # SARIFFileHandler Constructor
    # logger: Logger object
    #
    # Returns: SARIFFileHandler object
    # Raises: None
    def __init__(self, logger: logging.Logger, utils: Utils):
        self.logger = logger
        self.utils = utils
        self.__region_optional_fields = [ "startLine", "startColumn", "endLine", "endColumn" ] # TODO: `snippet` is not supported at this time.

    # Check for SARIF files in project root directory, using SARIF file naming convention. Refer to SARIF specification for more details: https://docs.oasis-open.org/sarif/sarif/v2.0/csprd02/sarif-v2.0-csprd02.html#_Toc9244200
    def check_for_sarif_files_in_project_root_directory(self) -> list[str]:

        sarif_files_list = []

        local_directory = os.getcwd()
        if 'GITHUB_ACTIONS' in os.environ.keys():

            self.logger.debug("Running inside GitHub Actions")
            local_directory = os.environ.get("GITHUB_WORKSPACE")

        for file in os.listdir(local_directory):

            if file.__contains__('.sarif'):

                sarif_files_list.append(os.path.join(local_directory, file))

        self.logger.debug("SARIF Files List - " + str(sarif_files_list))
        return sarif_files_list

    def load_sarif_data(self, sarif_file_path: dict) -> tuple[str, loader.SarifFile]:

        sarif_data = loader.load_sarif_file(file_path = sarif_file_path)

        self.logger.debug("SARIF file - " + str(sarif_file_path) + " - " + str(type(sarif_data)))

        sarif_tool = sarif_data.get_distinct_tool_names()[0] if len(sarif_data.get_distinct_tool_names()) > 0 else None

        return sarif_tool, sarif_data
    
    def build_sarif_findings_dict(self, sarif_tool_name: str, sarif_data: loader.SarifFile) -> dict:

        sarif_findings = {}
        results = sarif_data.get_results()

        unique_file_findings = []

        # Build empty filename dictionaries so we can document the findings inside them later
        for result in results:

            self.logger.debug("[" + sarif_tool_name + "]: " + str(result))

            if self.utils.check_if_finding_attribute_exists(source=result, key_str='locations'):

                if self.utils.check_if_finding_attribute_exists(source=result['locations'][0], key_str='physicalLocation'):

                    if self.utils.check_if_finding_attribute_exists(source=result['locations'][0]['physicalLocation'], key_str='artifactLocation'):

                        if self.utils.check_if_finding_attribute_exists(source=result['locations'][0]['physicalLocation']['artifactLocation'], key_str='uri'):

                            if result["locations"][0]["physicalLocation"]["artifactLocation"]["uri"] not in unique_file_findings:

                                self.logger.debug("Finding is unique")                                
                                unique_file_findings.append(result["locations"][0]["physicalLocation"]["artifactLocation"]["uri"])

        self.logger.debug("[" + sarif_tool_name + "]: Total file(s) with findings - " + str(len(unique_file_findings)))

        # This is a unique list of file names with findings
        self.logger.debug("Unique findings list - " + str(unique_file_findings))

        for unique_file_finding in unique_file_findings:

            finding_counter = 0

            sarif_findings.update({unique_file_finding: []})

            for result in results:

                if self.utils.check_if_finding_attribute_exists(source=result, key_str='locations'):

                    if self.utils.check_if_finding_attribute_exists(source=result['locations'][0], key_str='physicalLocation'):

                        if self.utils.check_if_finding_attribute_exists(source=result['locations'][0]['physicalLocation'], key_str='artifactLocation'):
                
                            if result["locations"][0]["physicalLocation"]["artifactLocation"]["uri"] == unique_file_finding:

                                finding_attrs = {}

                                finding_attrs.update({
                                    "ruleId": result["ruleId"],
                                    "message": result["message"]["text"]                        
                                })

                                if self.utils.check_if_finding_attribute_exists(source=result['locations'][0]['physicalLocation'], key_str='region'):

                                    for optional_field in self.__region_optional_fields:
                                        if self.utils.check_if_finding_attribute_exists(
                                            source = result["locations"][0]["physicalLocation"]["region"],
                                            key_str = optional_field
                                        ):
                                            finding_attrs.update({
                                                optional_field: result["locations"][0]["physicalLocation"]["region"][optional_field]
                                            })

                                sarif_findings[unique_file_finding].append(finding_attrs)

                    finding_counter += 1

            self.logger.debug("Finding counter for file - " + str(unique_file_finding) + " - " + str(finding_counter))

        return sarif_findings