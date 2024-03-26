import logging
from atlassian_doc_builder import load_adf, ADFDoc

# Atlassian Document Format Builder - Python class to build formatted documents for Atlassian products (Jira, Confluence)
class AtlassianDocumentFormatBuilder():

    # AtlassianDocumentFormatBuilder Constructor
    # logger: Logger object
    #
    # Returns: AtlassianDocumentFormatBuilder object
    # Raises: None
    def __init__(self, logger: logging.Logger):
        self.logger = logger

    # Generate a heading in the Atlassian Document Format
    def __add_heading(self, heading_text: str, heading_level: int):
        return {
            'type': 'heading',
            'attrs': {
                'level': heading_level
            },
            'content': [
                {
                    'type': 'text',
                    'text': heading_text
                }
            ]
        }
    
    # Generate a paragraph in the Atlassian Document Format
    def __add_paragraph(self, paragraph_text: str):
        return {
            'type': 'paragraph',
            'content': [
                {
                'type': 'text',
                'text': paragraph_text
                }
            ]
        }
    
    # Generate a divider in the Atlassian Document Format
    def __add_divider(self):
        return {
            'type': 'rule'
        }
    
    # Generate a link in the Atlassian Document Format
    def __add_link(self, link_text: str, link_url: str):
        return {
            'type': 'text',
            'text': link_text,
            'marks': [
                {
                    'type': 'link',
                    'attrs': {
                        'href': link_url
                    }
                }
            ]
        }
    
    # TODO: Needs to be implemented fully but how to generate localId isn't clear
    # Generate a task checklist in the Atlassian Document Format
    def __add_checklist(self, checklist_items: list):
        return {
            'type': 'taskList',
            'attrs': {
                'localId': '7560bb25-7de6-4b35-9e76-b5f6d9371b32'
            },
            'content': [
                {
                    'type': 'taskItem',
                    'attrs': {
                        'localId': 'fa0d6600-dd51-4926-b263-6ad9b360f1f6',
                        'state': 'TODO'
                    }
                }
            ]
        }
    
    # Generate a list item in the Atlassian Document Format
    def __add_list_item(self, list_item_text: str):
        return {
            'type': 'listItem',
            'content': [
                {
                    'type': 'paragraph',
                    'content': [
                        {
                            'type': 'text',
                            'text': list_item_text
                        }
                    ]
                }
            ]
        }
    
    # Generate a numbered list in the Atlassian Document Format
    def __build_numbered_list(self):
        return {
            'type': 'orderedList',
            'attrs': {
                'order': 1
            },
            'content': []
        }
    
    # Generate a bulleted list in the Atlassian Document Format
    def __build_bullet_list(self):
        return {
            'type': 'bulletList',
            'content': []
        }
    
    # Generate a blockquote section in the Atlassian Document Format
    def __add_blockquote(self, blockquote_text: str):
        return {
            'type': 'blockquote',
            'content': [
                {
                'type': 'paragraph',
                'content': [
                    {
                    'type': 'text',
                    'text': blockquote_text
                    }
                ]
                }
            ]
        }
    
    # Generate a codeblock section in the Atlassian Document Format
    def __add_codeblock(self, codeblock_text: str):
        return {
            'type': 'codeBlock',
            'attrs': {
                'language': 'python'
            },
            'content': [
                {
                'type': 'text',
                'text': codeblock_text
                }
            ]
        }
    
    def build_atlassian_document_format_from_SARIF(self, result: dict, index: str = "Unknown") -> tuple[str, ADFDoc]:

        try:
            self.logger.debug("SARIF Issue #" + index + " - " + str(result))

            # Build a content block
            adf_doc = ADFDoc()

            # TODO: Switch each location into a Sub-Task in JIRA instead of adding additional ADF formatted text in the JIRA Issue description 
            for location in result["locations"]:

                self.logger.info(
                    result["ruleId"] + ": " + \
                    result["message"]["text"] + " - " + \
                    location["physicalLocation"]["artifactLocation"]["uri"] + " " + \
                    str(location["physicalLocation"]["region"]["startLine"]) + ":" + \
                    str(location["physicalLocation"]["region"]["startColumn"]) + "-" + \
                    str(location["physicalLocation"]["region"]["endLine"]) + ":" + \
                    str(location["physicalLocation"]["region"]["endColumn"])
                )

                adf_doc.add(
                    load_adf(self.__add_heading(heading_level=4, heading_text=result["ruleId"] + ": " + result["message"]["text"] + " - " + location["physicalLocation"]["artifactLocation"]["uri"]))
                )

                adf_doc.add(
                    load_adf(self.__add_paragraph(paragraph_text="Start Line: #" + str(location["physicalLocation"]["region"]["startLine"]) + ", character " + str(location["physicalLocation"]["region"]["startColumn"]) + "\nEnd Line: #" + str(location["physicalLocation"]["region"]["endLine"]) + ", character " + str(location["physicalLocation"]["region"]["endColumn"])))
                )

            adf_doc.validate()
            return (
                result["ruleId"] + ": " + result["message"]["text"] + " - " + location["physicalLocation"]["artifactLocation"]["uri"],
                adf_doc
            )
        
        except Exception as e:
            self.logger.error(e)
            return None
        
    def build_atlassian_document_format_from_dict(self, sarif_tool_name: str, key: str, results: list, index: str = "Unknown") -> tuple[str, ADFDoc]:

        try:
            self.logger.debug("Issue in " + key + " - " + str(results))

            # Build a content block
            adf_doc = ADFDoc()

            # TODO: Switch each location into a Sub-Task in JIRA instead of adding additional ADF formatted text in the JIRA Issue description 
            for result in results:
                
                self.logger.debug(__name__ + \
                    ": [" + sarif_tool_name + "] " + \
                    result["ruleId"] + ": " + \
                    result["message"] + " - " + \
                    key + " " + \
                    str(result["startLine"]) + ":" + \
                    str(result["startColumn"]) + "-" + \
                    str(result["endLine"]) + ":" + \
                    str(result["endColumn"])
                )

                adf_doc.add(
                    load_adf(self.__add_heading(heading_level=4, heading_text=result["ruleId"] + ": " + result["message"] + " - " + key))
                )

                adf_doc.add(
                    load_adf(self.__add_paragraph(paragraph_text="Start Line: #" + str(result["startLine"]) + ", character " + str(result["startColumn"]) + "\nEnd Line: #" + str(result["endLine"]) + ", character " + str(result["endColumn"])))
                )

            adf_doc.validate()
            return (
                key,
                adf_doc
            )
        
        except Exception as e:
            self.logger.error(e)
            return None