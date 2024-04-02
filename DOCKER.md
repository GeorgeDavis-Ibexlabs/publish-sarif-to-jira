# publish-sarif-to-jira

Python project to push SARIF output to JIRA Cloud and track progress of personal projects in JIRA

Project Status: **In Active Development**

## Prerequisites

1. Requires a JIRA Cloud account
    - Access to the Authentication Email and API token

## Work items

1. Use rich-text (Atlassian Document Format) in JIRA Issue description

    > **Note**: This feature is gated with the config parameter `use_atlassian_document_format` in the config.json file. Set to true to use this feature.
    **Bug**: Atlassian does not accept ADF rich-text formatted description, rather dumps JSON in the issue description. Needs triage and bug fix.

2. Create sub-tasks instead of multi-lines in the JIRA Issue description

    > **Note**: This feature is not implemented yet and will be gated with the config parameter `create_sub_tasks` in the config.json file. Set to true to build and test this feature.

## Usage

1. Copy the `.env.example` file into `.env`
2. Update the configuration values, both `input` and `jira` values on the `.env` file
3. Run Docker container using
`docker run --network host -itd --env-file .env publish-sarif-to-jira:latest`

4. The Python script within the Docker container iterates through the SARIF files (files ending with `.sarif` extension or has the term `.sarif` in the filename) and creates JIRA Issues on your JIRA Cloud instance

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
| `jira["default_issue_labels"]` | `jira_default_issue_labels` | For config.json - `["Label1","Label2"]`. For config environment variables, we use comma-separated string like `Label1,Label2` |
| `jira["use_atlassian_document_format"]` | `jira_use_atlassian_document_format` |  Unsupported yet on JIRA Cloud. Defaults to `false`. |
| `jira["create_sub_tasks"]` | `jira_create_sub_tasks` | Placeholder. Feature yet to be developed. Defaults to `false`. |

## Tool Compatibility

| Tools | Link | Status |
|-------|------|--------|
| `cfn-lint` | [aws-cloudformation/cfn-lint](https://github.com/aws-cloudformation/cfn-lint) | √ |
| `trivy` | [aquasecurity/trivy](https://github.com/aquasecurity/trivy) | √ |

## GitHub Actions

```
    - name: Create JIRA tickets from SARIF
      uses: GeorgeDavis-Ibexlabs/publish-sarif-to-jira@v0.0.6
```
Refer to [Create JIRA tickets from SARIF using GitHub Actions](https://github.com/marketplace/actions/create-jira-tickets-from-sarif)

## Work in progress 

- #### VSCode Extension

    Plans to build this project into a VSCode extension to submit SARIF output to JIRA direct from the IDE and track progress

## Upcoming features

Feature requests are currently tracked by the original author within the source code. Clone this repository, run a search for the term "TODO" to find the list of new features being tracked.

1. Create sub-tasks instead of multi-lines in the JIRA Issue description
2. Fully support Atlassian Document Format (ADF). Currently, a bug is limiting the ADF from appearing formatted when visiting the JIRA Issue on JIRA Cloud 
3. Create a JIRA Project if the project does not exist (Nice to have so it can be deployed per project all from CI/CD without the need to access JIRA Cloud)

## Contribute

If you encounter a bug or think of a useful feature, or find something confusing in the docs, please create a new issue.

I ♥️ pull requests. If you'd like to fix a bug or contribute to a feature or simply correct a typo, please feel free to do so.

If you're thinking of adding a new feature, consider opening an issue first to discuss it to ensure it aligns with the direction of the project and potentially save yourself some time.

## Development

```sh
docker login
```

```sh
docker build --no-cache --progress=plain . -f Dockerfile -t publish-sarif-to-jira:latest 2>&1 | tee build.log
```

```sh
docker run --network host -itd \
--env-file .env \
-e LOG_LEVEL='DEBUG' \
publish-sarif-to-jira:latest
```