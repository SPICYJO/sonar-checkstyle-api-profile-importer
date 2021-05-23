import requests
import logging
import sys
import argparse
from xml_parser import loader, module_name_mapper
from utils import util

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Import checkstyle xml configuration files into Sonarqube profile via Sonarqube Web API.')
    parser.add_argument('--xml_path', required=True, help='Path of the xml file which configures checkstyle rules')
    parser.add_argument('--profile_name', required=True, help='Name of quality profile that being imported')
    parser.add_argument('--username', required=True, help='Username which has privilege to manage quality profile')
    parser.add_argument('--password', required=True, help='Password that corresponds to username')
    parser.add_argument('--server_url', required=False, default='http://localhost:9000', help='URL of Sonarqube server. Default value is http://localhost:9000.')
    args = parser.parse_args()

    # Environment settings
    SERVER_URL = args.server_url
    ADMIN_ID = args.username
    ADMIN_PASSWORD = args.password
    XML_FILE_PATH = args.xml_path
    CUSTOM_KEY_PREFIX = util.string_generator(10) # Randomly generated string
    PLUGIN_NAME = "checkstyle"
    PROFILE_NAME = args.profile_name
    SERVER_URL_AUTH = util.URLWithAuthentication(SERVER_URL, ADMIN_ID, ADMIN_PASSWORD)

    # Logger settings
    logger = logging.getLogger("sonar_checkstyle_profile_importer")
    logger.setLevel(logging.INFO)
    logging.basicConfig(stream=sys.stdout, level=logging.INFO)
    
    logger.info("Start import")
    logger.info(f"Server URL: {SERVER_URL}")
    logger.info(f"XML file path: {XML_FILE_PATH}")

    ## Step00: Parse XML file
    rules = loader.parseXml(XML_FILE_PATH)

    #########################################################################
    ## Step01: Define custom template rules
    logger.info("[Step01 started] Define custom template rules")
    num_defined_rules = 0
    num_define_error_rules = 0
    num_not_template_rules = 0
    rules_to_activate = []
    for rule in rules:
        data={**{
            'custom_key': CUSTOM_KEY_PREFIX+str(num_defined_rules),
            'template_key': PLUGIN_NAME+':' + module_name_mapper.moduleNameToKey(rule['name']),
            'name': rule['name'] + " generated custom template rule",
            'markdown_description': rule['markdown_description'],
            'params': util.serializeParams(rule['params']),
        }, **({'severity': rule.get('severity')} if rule.get('severity') is not None else {})}

        res = requests.post(
            f'{SERVER_URL_AUTH}/api/rules/create',
            data=data
        )

        if(res.status_code!=200):
            logger.debug(f"Failed to define custom rule : {rule['name']}")
            rules_to_activate.append({**{
                'key': (PLUGIN_NAME+':' + module_name_mapper.moduleNameToKey(rule['name'])),
                'name': rule['name'],
                'params': rule['params']
            }, **({'severity': rule.get('severity')} if rule.get('severity') is not None else {})})
            error_msg = ""
            try:
                error_msg = res.json().get('errors')[0].get('msg')
            except Exception:
                error_msg = "Failed to parse error message"
            if(error_msg.startswith("This rule is not a template rule")):
                num_not_template_rules += 1
            else:
                num_define_error_rules += 1
        else:
            #logger.debug(f"Success to define custom rule : {rule['name']}")
            rules_to_activate.append({**{
                'key': PLUGIN_NAME+':'+CUSTOM_KEY_PREFIX+str(num_defined_rules),
                'name': rule['name'] + " generated custom template rule",
                'params': rule['params']
            }, **({'severity': rule.get('severity')} if rule.get('severity') is not None else {})})
            num_defined_rules += 1
        logger.debug(res.json())
    logger.info(f"[Step01 finished] Result: Defined custom template rules: {num_defined_rules}, Not template rules: {num_not_template_rules}, Error: {num_define_error_rules}")
    if num_define_error_rules != 0:
        logger.debug("Error occured while defining custom template rules. Please set the log level to debug and figure out what is going wrong.")
    #########################################################################

    #########################################################################
    ## Step02: Create quality profile
    logger.info("[Step02 started] Create quality profile")

    res = requests.post(
        f"{SERVER_URL_AUTH}/api/qualityprofiles/create",
        data={
            'language': 'java',
            'name': PROFILE_NAME
        }
    )
    
    logger.debug(res.json())
    if(res.status_code!=200):
        logger.error("[Step02 failed] Failed to create quality profile")
        sys.exit(-1)
    profile_key = res.json()['profile']['key']
    logger.info("[Step02 finished] Created quality profile")
    #########################################################################
    
    #########################################################################
    ## Step03: Activate rules in the quality profile
    num_activated_rules = 0
    num_not_activated_rules = 0
    rules_not_activated = []
    logger.info("[Step03 started] Activate rules in the quality profile")
    for rule in rules_to_activate:
        data={**{
            'key': profile_key,
            'rule': rule['key'],
            'params': util.serializeParams(rule['params'])  
        }, **({'severity': rule.get('severity')} if rule.get('severity') is not None else {})}

        res = requests.post(
            f"{SERVER_URL_AUTH}/api/qualityprofiles/activate_rule",
            data=data
        )

        if(res.status_code != 204):
            logger.debug(f"Failed to activate rule : {rule['name']}")
            rules_not_activated.append(rule['name'])
            num_not_activated_rules += 1
        else:
            num_activated_rules += 1
    logger.info(f"[Step03 finished] Result: Activated rules: {num_activated_rules}, Failed to activate: {num_not_activated_rules}")
    if num_not_activated_rules != 0:
        logger.error(f"Following rules were not activated properly. Please manually define or activate following rules: {rules_not_activated}")
    else:
        logger.info("Import Profile Success!")
    #########################################################################    
