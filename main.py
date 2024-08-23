# from __future__ import annotations
import logging
import traceback
from os import environ
from jira import JIRA
from projects.projects import Projects
from issues.issues import Issues
from sarif_file_handler.sarif_file_handler import SARIFFileHandler
from config_handler.config_handler import ConfigHandler
from atlassian_doc_builder import load_adf, ADFDoc
from atlassian.adf import AtlassianDocumentFormatBuilder
from utils.utils import Utils

logging.basicConfig()
logger = logging.getLogger(__name__)
logger.setLevel(environ['LOG_LEVEL'] if 'LOG_LEVEL' in environ.keys() else 'INFO')

def main():

    try:
        logger.debug("Environment variables - " + str(environ))
        configHandlerObj = ConfigHandler(logger=logger)
        utilsObj = Utils(logger=logger)

        # Build a config file using config.json if it exists
        config_file = configHandlerObj.load_config_file()
        logger.debug("Config File Object - " + str(config_file))

        # Override config.json if exists, with Environment variables for GitHub Actions and CI purposes
        config_env = configHandlerObj.load_config_env()
        logger.debug("Config Env Object - " + str(config_env))

        # Merge both config objects
        configHandlerObj.config = configHandlerObj.get_combined_config(config_file=config_file, config_env=config_env)
        logger.debug("Final Config Object - " + str(configHandlerObj.config))

        # Create a JIRA Object
        jira = JIRA(
            server=configHandlerObj.config["jira"]["cloud_url"],
            basic_auth=(configHandlerObj.config["jira"]["auth_email"],
            configHandlerObj.config["jira"]["api_token"])
        )

        # Create an Projects Object
        projectsObj = Projects(jira_credentials=jira, logger=logger)

        # Returns bool and project ID
        project_info = projectsObj.does_project_exist(configHandlerObj.config["jira"]["project_key"])

        if project_info[0]:

            sarifObj = SARIFFileHandler(logger=logger, utils=utilsObj)
            sarif_files_list = sarifObj.check_for_sarif_files_in_project_root_directory()

            # Iterate through the SARIF results file in the project root directory that ends with .sarif or contains the term ".sarif" in the filename
            for sarif_file_path in sarif_files_list:

                sarif_tool_name, sarif_data = sarifObj.load_sarif_data(sarif_file_path=sarif_file_path)

                logger.info("[" + sarif_tool_name + "]: Total no. of issues found in SARIF report - " + str(sarif_data.get_result_count()))

                if sarif_data.get_result_count() > 0:

                    sarif_findings = sarifObj.build_sarif_findings_dict(
                        sarif_tool_name=sarif_tool_name,
                        sarif_data=sarif_data
                    )

                    # with open(sarif_tool_name + '_findings.json', 'w') as sarif_findings_file:
                    #     sarif_findings_file.write(json.dumps(sarif_findings))

                    # Create an Issues Object
                    issueObj = Issues(
                        logger=logger,
                        jira_credentials=jira,
                        project_key=configHandlerObj.config["jira"]["project_key"],
                        project_id=project_info[1],
                        email_domain="@" + str(configHandlerObj.config["jira"]["auth_email"].split('@')[1]),
                        default_issue_labels=configHandlerObj.config["jira"]["default_issue_labels"],
                    )

                    for sarif_per_file_key in sarif_findings.keys():

                        logger.info("[" + sarif_tool_name + "]: " + str(sarif_findings[sarif_per_file_key]))
                        
                        # Building a list of findings 

                        issue_summary = issue_desc = ''

                        if configHandlerObj.config["jira"]["use_atlassian_document_format"]:
                            # Build an Atlassian Document Format
                            adf_builder = AtlassianDocumentFormatBuilder(logger=logger)

                            issue_summary, issue_desc = adf_builder.build_atlassian_document_format_from_dict(sarif_tool_name=sarif_tool_name, key=sarif_per_file_key, results=sarif_findings[sarif_per_file_key])
                        else:
                            issue_summary = sarif_per_file_key

                            for issue in sarif_findings[sarif_per_file_key]:

                                logger.debug(str(issue))

                                if issue_desc != '':
                                    issue_desc = utilsObj.serialize_finding_attributes(
                                        finding_file_key = sarif_per_file_key,
                                        findings = issue
                                    ) + "\n___\n\n" 
                                else:
                                    issue_desc += utilsObj.serialize_finding_attributes(
                                        finding_file_key = sarif_per_file_key,
                                        findings = issue
                                    ) + "\n___\n\n" 
                                
                                # issue_desc += "[" + sarif_tool_name + "] " + issue["ruleId"] + ": " + issue["message"] + " - " + sarif_per_file_key + "\nStart Line #: " + str(issue["startLine"]) + ", character " + str(issue["startColumn"]) + "\nEnd Line #: " + str(issue["endLine"]) + ", character " + str(issue["endColumn"]) + "\n___\n\n"                

                        logger.debug("JIRA Issue Summary: " + str(issue_summary))
                        logger.debug("JIRA Issue Description: %s", str(issue_desc.validate()) if isinstance(issue_desc, ADFDoc) else issue_desc)

                        # Update or Insert a JIRA issue. If the issue exists, then update it. If the issue doesn't exist, then create a new issue.
                        issueObj.upsert_jira_issue(
                            issue_summary = issue_summary,
                            issue_desc = issue_desc,
                            issue_type = "Task"
                        )
                else:
                    logger.error("[" + sarif_tool_name + "]: No results found.")
                
            logger.info("Success.")

        else:
            raise Exception("JIRA Cloud Project does not exist.")

    except Exception as e:
        logger.error("Error. Exception: " + str(traceback.print_tb(e.__traceback__)))
        exit(1)

if __name__ == "__main__":
    main()