from os import environ, getcwd, listdir
import re
import logging
import traceback
from python_json_config import ConfigBuilder, config_node
from mergedeep import merge

ConfigKeyValuePair = {
    'input_type': 'input.type',
    'input_format': 'input.format',
    'jira_cloud_url': 'jira.cloud_url',
    'jira_project_key': 'jira.project_key',
    'jira_auth_email': 'jira.auth_email',
    'jira_api_token': 'jira.api_token',
    'jira_default_issue_labels': 'jira.default_issue_labels',
    'jira_use_atlassian_document_format': 'jira.use_atlassian_document_format',
    'jira_create_sub_tasks': 'jira.create_sub_tasks'
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
    
    # # If JSON config variable exists
    # def check_if_json_key_value_exists(self, key: str, config: dict, existing_value):

    #     if key in config.keys(): # Only works for flat JSON files
    #         if key != 'default_issue_labels':
    #             return config[key]
    #         else:
    #             if environ[key] == '':
    #                 return []
    #             else:
    #                 environ[key].split(',')
    #     else:
    #         return existing_value
    
    # # If environment variable exists
    # def check_if_env_var_exists(self, env_key: str, existing_value):

    #     if env_key in environ:
    #         if env_key != 'default_issue_labels':
    #             return environ[env_key]
    #         else:
    #             if environ[env_key] == '':
    #                 return []
    #             else:
    #                 environ[env_key].split(',')
    #     else:
    #         return existing_value

    # Load the config.json file from the current working directory, or from the GITHUB_WORKSPACE environment variable if running inside GitHub Actions
    def load_config_file(self) -> dict:

        try:
            local_directory = getcwd()
            if 'GITHUB_ACTIONS' in environ.keys():

                # self.logger.debug("Running inside GitHub Actions")
                local_directory = environ.get("GITHUB_WORKSPACE")

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

                    # self.builder.validate_field_type('config.input.type', str)
                    # self.builder.validate_field_type('config.input.format', str)
                    # self.builder.validate_field_type('config.jira.cloud_url', str)
                    # self.builder.validate_field_type('config.jira.project_key', str)
                    # self.builder.validate_field_type('config.jira.auth_email', int)
                    # self.builder.validate_field_type('config.jira.api_token', str)
                    # self.builder.validate_field_type('config.jira.default_issue_labels', list)
                    # self.builder.validate_field_type('config.jira.use_atlassian_document_format', bool)
                    # self.builder.validate_field_type('config.jira.create_sub_tasks', bool)
                    
            self.logger.debug("Config from the config.json file - " + str(self.config))
            return self.config.to_dict() if isinstance(self.config, config_node.Config) else self.config
        
        except Exception as e:
            self.logger.error("Error loading config.json file: " + str(traceback.print_tb(e.__traceback__)))

    # Load the config.json file from environment variables instead if running inside GitHub Actions. Environment variables override config.json values to enable CI workflows.
    def load_config_env(self) -> dict:

        try:
            config = {}

            temp_list = []
            for config_key, config_value in ConfigKeyValuePair.items():
                if config_key in environ.keys():
                    temp_list.append(config_value)

            unique_parent_list = []
            for item in temp_list:
                if item.split('.')[0] not in unique_parent_list:
                    unique_parent_list.append(item.split('.')[0])

            for parent_item in unique_parent_list:

                temp_config_dict = {}
                for list_item in [x for x in temp_list if re.match(parent_item+".*", x)]:
                    item_path = list_item.split('.')
                    for item in reversed(item_path):
                        # temp_config_dict.update({item: environ[list_item.replace('.', '_')]})
                        # break
                        if list_item == "jira.default_issue_labels":
                            temp_config_dict.update({item: environ[list_item.replace('.', '_')].split(",")})
                        else:
                            if list_item in ['jira.use_atlassian_document_format', 'jira.create_sub_tasks']:
                                temp_config_dict.update({item: self.get_boolean(environ[list_item.replace('.', '_')])})
                            else:
                                temp_config_dict.update({item: environ[list_item.replace('.', '_')]})
                        break
                    config.update({list_item.split('.')[0]: temp_config_dict})
            self.logger.debug("Config from environment variables - " + str(config))
            return config
        
        except Exception as e:
            self.logger.error("Error loading environment variables: " + str(traceback.print_tb(e.__traceback__)))
        
        # self.input_type = self.check_if_env_var_exists(env_key="input_type", existing_value=self.input_type)
        # self.input_format = self.check_if_env_var_exists(env_key="input_format", existing_value=self.input_format)
        # self.jira_cloud_url = self.check_if_env_var_exists(env_key="jira_cloud_url", existing_value=self.jira_cloud_url)
        # self.jira_project_key = self.check_if_env_var_exists(env_key="jira_project_key", existing_value=self.jira_project_key)
        # self.auth_email = self.check_if_env_var_exists(env_key="jira_auth_email", existing_value=self.auth_email)
        # self.api_token = self.check_if_env_var_exists(env_key="jira_api_token", existing_value=self.api_token)
        # self.default_issue_labels = self.check_if_env_var_exists(env_key="jira_default_issue_labels", existing_value=self.default_issue_labels)
        # self.use_atlassian_document_format = self.check_if_env_var_exists(env_key="jira_use_atlassian_document_format", existing_value=self.use_atlassian_document_format)
        # self.create_sub_tasks = self.check_if_env_var_exists(env_key="jira_create_sub_tasks", existing_value=self.create_sub_tasks)
            
    def get_combined_config(self, config_file: dict, config_env: dict) -> dict:

        try:
            # merged_config = config_env | config_file
            # self.logger.debug("Final Config Object - " + str(merged_config))
            # return merged_config

            # for k in set(config_file.keys()).union(config_env.keys()):
            #     if k in config_file and k in config_env:
            #         if isinstance(config_file[k], dict) and isinstance(config_env[k], dict):
            #             yield (k, dict(self.get_combined_config(config_file[k], config_env[k])))
            #         else:
            #             # If one of the values is not a dict, you can't continue merging it.
            #             # Value from second dict overrides one in first and we move on.
            #             yield (k, config_env[k])
            #             # Alternatively, replace this with exception raiser to alert you of value conflicts
            #     elif k in config_file:
            #         yield (k, config_file[k])
            #     else:
            #         yield (k, config_env[k])

            return merge(config_file, config_env)

        except Exception as e:
            self.logger.error("Error merging config: " + str(traceback.print_tb(e.__traceback__)))
        