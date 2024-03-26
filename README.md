# jira-cloud-ticket-automation
 JIRA Cloud Ticketing Automation based on SARIF files

Project Status: **In Active Development**

## Prerequisites

1. 

## Work items

1. Use rich-text (Atlassian Document Format) in JIRA Issue description.

    > Note: This feature is gated with the config parameter `use_atlassian_document_format` in the config.json file. Set to true to use this feature.
    :warning: **Bug**: Atlassian does not accept ADF rich-text formatted description, rather dumps JSON in the issue description. Needs triage and bug fix.

2. Create sub-tasks instead of multi-lines in the JIRA Issue description.

    > Note: This feature is not implemented yet and will be gated with the config parameter `create_sub_tasks` in the config.json file. Set to true to build and test this feature.

## Usage

1. Copy the `config.json.example` file into `config.json`.
2. Update the configuration values, both `input` and `jira` sections of the `config.json` file.
3. Run this Python script in a directory where the SARIF files are located.
4. The Python script iterates through the SARIF files (files ending with .sarif extension or has the term `.sarif` in the filename) and creates JIRA Issues on your JIRA Cloud instance.

> This script has not been tested with the self-hosted instances of JIRA

## Configuration

| `config.json` | Config Environment variable | Description |
|---------------|-----------------------------|-------------|
| `input["type"]` | `input_type` | Supported SARIF input types: `file`|
| `input["format"]` | `input_format` | Supported SARIF format: `sarif` |
| `jira["cloud_url"]` | `jira_cloud_url` | JIRA Cloud URL: `https://XXXX.atlassian.net/` |
| `jira["project_key"]` | `jira_project_key` | JIRA Project Key: `PROJ-XYZ` |
| `jira["auth_email"]` | `jira_auth_email` | Authentication Email: `test@example.com` |
| `jira["api_token"]` | `jira_api_token` | API token: `<INSERT-YOUR-JIRA-CLOUD-API-TOKEN>` |
| `jira["default_issue_labels"]` | `jira_default_issue_labels` | For config.json - ```["Label1","Label2"]```. For config environment variables, we use comma-separated string like `Label1,Label2` |
| `jira["use_atlassian_document_format"]` | `jira_use_atlassian_document_format` |  Unsupported yet on JIRA Cloud. Defaults to `false`. |
| `jira["create_sub_tasks"]` | `jira_create_sub_tasks` | Placeholder. Feature yet to be developed. Defaults to `false`. |


## GitHub Actions

:construction: Work on publishing a **GitHub Action** is in progress and should be available by end of March 2024

## VSCode Extension

:construction: Plans to build this project into a VSCode extension to submit SARIF output to JIRA direct from the IDE and track progress

## Contribute

If you encounter a bug or think of a useful feature, or find something confusing in the docs, please create a new issue

I ♥️ pull requests. If you'd like to fix a bug or contribute to a feature or simply correct a typo, please feel free to do so.

If you're thinking of adding a new feature, consider opening an issue first to discuss it to ensure it aligns with the direction of the project and potentially save yourself some time.