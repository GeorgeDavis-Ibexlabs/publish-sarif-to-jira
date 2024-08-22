from os import environ, getcwd, listdir
import re
import logging
import traceback
from python_json_config import ConfigBuilder, config_node
from mergedeep import merge

# The ConfigMap - Mapping between runtime environment variable keys and JSON Config keys. Will need to append 'INPUT_' when looking to map within GitHub Actions environment
ConfigKeyValuePair = {
    'INPUT_TYPE': 'input.type',
    'INPUT_FORMAT': 'input.format',
    'JIRA_CLOUD_URL': 'jira.cloud_url',
    'JIRA_PROJECT_KEY': 'jira.project_key',
    'JIRA_AUTH_EMAIL': 'jira.auth_email',
    'JIRA_API_TOKEN': 'jira.api_token',
    'JIRA_DEFAULT_ISSUE_LABELS': 'jira.default_issue_labels',
    'JIRA_USE_ATLASSIAN_DOCUMENT_FORMAT': 'jira.use_atlassian_document_format',
    'JIRA_CREATE_SUB_TASKS': 'jira.create_sub_tasks'
}

# SARIF - class to handle Static Analysis Results Interchange Format (SARIF)
class ConfigHandler():

    # ConfigHandler Constructor
    # input_type: str
    # input_format: str
    # jira_cloud_url: str
    # jira_project_key: str
    # jira_auth_email: str
    # jira_api_token: str
    # jira_default_issue_labels: list
    # jira_use_atlassian_document_format: bool
    # jira_create_sub_tasks: bool
    #
    # Returns: ConfigHandler object
    # Raises: None
    def __init__(self, logger: logging.Logger):

        # Create a JSON Config parser
        self.logger = logger
        self.builder = ConfigBuilder()
        self.input_type = 'file'
        self.input_format = 'sarif'
        self.jira_cloud_url = self.jira_project_key = self.jira_auth_email = self.jira_api_token = ''
        self.jira_default_issue_labels = []
        self.jira_use_atlassian_document_format = self.jira_create_sub_tasks = False
        self.config = self.build_config()

    # Get Boolean
    def get_boolean(self, key: str):
        return True if str(key).lower() == 'true' and key != '' else False

    # Build the Config object
    def build_config(self) -> dict:
        return {
            'input': {
                'type': self.input_type,
                'format': self.input_format,
            },
            'jira': {
                'cloud_url': self.jira_cloud_url,
                'project_key': self.jira_project_key,
                'auth_email': self.jira_auth_email,
                'api_token': self.jira_api_token,
                'default_issue_labels': self.jira_default_issue_labels,
                'use_atlassian_document_format': self.jira_use_atlassian_document_format if isinstance(self.jira_use_atlassian_document_format, bool) else self.get_boolean(self.jira_use_atlassian_document_format),
                'create_sub_tasks': self.jira_create_sub_tasks if isinstance(self.jira_create_sub_tasks, bool) else self.get_boolean(self.jira_create_sub_tasks)
            }
        }

    # Load the config.json file from the current working directory, or from the GITHUB_WORKSPACE environment variable if running inside GitHub Actions
    def load_config_file(self) -> dict:

        try:
            local_directory = getcwd()
            if 'GITHUB_ACTIONS' in environ.keys():

                self.logger.debug('Running inside GitHub Actions')
                local_directory = environ.get('GITHUB_WORKSPACE')

            for file in listdir(local_directory):
                if file == 'config.json':

                    # Parse JSON Config
                    # required means an error is thrown if a non-existing field is accessed 
                    self.builder.set_field_access_required()
                    # self.builder.add_required_fields(field_names=['jira.cloud_url','jira.project_key','jira.auth_email','jira.api_token'])
                    self.builder.add_optional_fields(field_names=['input.type','input.format','jira.default_issue_labels','jira.use_atlassian_document_format','jira.create_sub_tasks'])

                    self.config = self.builder.parse_config('config.json')

                    # Set default values for optional fields if they are not set in the config.json file.
                    if self.config.input.type == None:
                        self.config.input.type = 'file' # Default is file

                    if self.config.input.format == None:
                        self.config.input.format = 'sarif' # Default is SARIF format

                    if self.config.jira.default_issue_labels == None:
                        self.config.jira.default_issue_labels = []

                    if self.config.jira.use_atlassian_document_format == None:
                        self.config.jira.use_atlassian_document_format = False # Default is false

                    if self.config.jira.create_sub_tasks == None:
                        self.config.jira.create_sub_tasks = False # Default is false
                    
            self.logger.debug('Config from the config.json file - ' + str(self.config))
            return self.config.to_dict() if isinstance(self.config, config_node.Config) else self.config
        
        except Exception as e:
            self.logger.error('Error loading config.json file: ' + str(traceback.print_tb(e.__traceback__)))

    # Load the config.json file from environment variables instead if running inside GitHub Actions. Environment variables override config.json values to enable CI workflows.
    def load_config_env(self) -> dict:

        try:
            config = {}

            temp_list = []
            for config_key, config_value in ConfigKeyValuePair.items():
        
                if 'GITHUB_ACTIONS' in environ.keys():
                        if environ['GITHUB_ACTIONS']:
                            config_key = 'INPUT_' + config_key

                if config_key in environ.keys():
                    self.logger.debug('Config found within environment variables - ' + str(config_key) + ' - ' + str(config_value))
                    temp_list.append(config_value)

            self.logger.debug('ConfigMap JSON key values found within environment variables - ' + str(temp_list))

            unique_parent_list = []
            for item in temp_list:
                if item.split('.')[0] not in unique_parent_list:
                    unique_parent_list.append(item.split('.')[0])

            self.logger.debug('Parent config attributes found within environment variables - ' + str(unique_parent_list))

            for parent_item in unique_parent_list:

                temp_config_dict = {}
                for list_item in [x for x in temp_list if re.match(parent_item+'.*', x)]:

                    if 'GITHUB_ACTIONS' in environ.keys():
                        if environ['GITHUB_ACTIONS']:
                            list_item = 'INPUT_' + list_item

                    self.logger.debug('Config `' + str(list_item) + '` within parent `' + str(parent_item) + '` - ' + str(environ[list_item.replace('.', '_').upper()]))

                    item_path = list_item.split('.')
                    for item in reversed(item_path):
                        # temp_config_dict.update({item: environ[list_item.replace('.', '_').upper()]})
                        # break
                        if 'GITHUB_ACTIONS' in environ.keys():
                            if environ['GITHUB_ACTIONS']:
                                if list_item == 'INPUT_jira.default_issue_labels':
                                    temp_config_dict.update({
                                        item: environ[list_item.replace('.', '_').upper()].split(',')
                                    })
                                else:
                                    if list_item in ['INPUT_jira.use_atlassian_document_format', 'INPUT_jira.create_sub_tasks']:
                                        temp_config_dict.update({
                                            item: self.get_boolean(environ[list_item.replace('.', '_').upper()])
                                        })
                                    else:
                                        temp_config_dict.update({
                                            item: environ[list_item.replace('.', '_').upper()]
                                        })
                                config.update({list_item.split('.')[0].replace('INPUT_',''): temp_config_dict})
                                break
                        else:
                            if list_item == 'jira.default_issue_labels':
                                temp_config_dict.update({
                                    item: environ[list_item.replace('.', '_').upper()].split(',')
                                })
                            else:
                                if list_item in ['jira.use_atlassian_document_format', 'jira.create_sub_tasks']:
                                    temp_config_dict.update({
                                        item: self.get_boolean(environ[list_item.replace('.', '_').upper()])
                                    })
                                else:
                                    temp_config_dict.update({
                                        item: environ[list_item.replace('.', '_').upper()]
                                    })
                            config.update({list_item.split('.')[0]: temp_config_dict})
                            break
            self.logger.debug('Config from environment variables - ' + str(config))
            return config
        
        except Exception as e:
            self.logger.error('Error loading environment variables: ' + str(traceback.print_tb(e.__traceback__)))
            
    def get_combined_config(self, config_file: dict, config_env: dict) -> dict:

        try:
            return merge(config_file, config_env)

        except Exception as e:
            self.logger.error('Error merging config: ' + str(traceback.print_tb(e.__traceback__)))
        