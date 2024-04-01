import logging
from sarif import loader
import os

# SARIF - class to handle Static Analysis Results Interchange Format (SARIF)
class SARIFFileHandler:

    # SARIFFileHandler Constructor
    # logger: Logger object
    #
    # Returns: SARIFFileHandler object
    # Raises: None
    def __init__(self, logger: logging.Logger):
        self.logger = logger

    # Check for SARIF files in project root directory, using SARIF file naming convention. Refer to SARIF specification for more details: https://docs.oasis-open.org/sarif/sarif/v2.0/csprd02/sarif-v2.0-csprd02.html#_Toc9244200
    def check_for_sarif_files_in_project_root_directory(self) -> list[str]:

        sarif_files_list = []

        local_directory = os.getcwd()
        if 'GITHUB_ACTIONS' in os.environ.keys():

            self.logger.debug("Running inside GitHub Actions")
            local_directory = os.environ.get("GITHUB_WORKSPACE")

        for file in os.listdir(local_directory):
            if file.__contains__('.sarif'):
                self.logger.debug(local_directory)
                sarif_files_list.append(os.path.join(local_directory, file))

        self.logger.debug("SARIF Files List - " + str(sarif_files_list))
        return sarif_files_list

    def load_sarif_data(self, sarif_file_path: dict) -> tuple[str, dict]:
        sarif_data = loader.load_sarif_file(sarif_file_path)
        self.logger.debug("SARIF file - " + str(sarif_file_path) + " - " + str(type(sarif_data)))

        sarif_tool = sarif_data.get_distinct_tool_names()[0] if len(sarif_data.get_distinct_tool_names()) > 0 else None

        return sarif_tool, sarif_data
    
    def build_sarif_findings_dict(self, sarif_tool_name: str, sarif_data: dict) -> dict:

        sarif_findings = {}

        results = sarif_data.get_results()

        unique_file_findings = []

        for result in results:

            self.logger.debug("[" + sarif_tool_name + "]: " + str(result))

            if result["locations"][0]["physicalLocation"]["artifactLocation"]["uri"] not in unique_file_findings:
                unique_file_findings.append(result["locations"][0]["physicalLocation"]["artifactLocation"]["uri"])

        self.logger.debug("[" + sarif_tool_name + "]: Total file(s) with findings - " + str(len(unique_file_findings)))

        for unique_file_finding in unique_file_findings:

            finding_counter = 0

            sarif_findings.update({unique_file_finding: []})

            for result in results:
                if result["locations"][0]["physicalLocation"]["artifactLocation"]["uri"] == unique_file_finding:

                    sarif_findings[unique_file_finding].append({
                        "ruleId": result["ruleId"],
                        "message": result["message"]["text"],
                        "startLine": result["locations"][0]["physicalLocation"]["region"]["startLine"],
                        "startColumn": result["locations"][0]["physicalLocation"]["region"]["startColumn"],
                        "endLine": result["locations"][0]["physicalLocation"]["region"]["endLine"],
                        "endColumn": result["locations"][0]["physicalLocation"]["region"]["endColumn"]
                    })

                    finding_counter += 1

            self.logger.debug("Finding counter for file - " + str(unique_file_finding) + " - " + str(finding_counter))

        return sarif_findings