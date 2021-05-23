
from xml.etree.ElementTree import parse

def parseXml(xmlFilePath):
    tree = parse(xmlFilePath)
    return getRules(tree.getroot(), {})

def remove_whitespace_if_has_comma(value):
    if(value.find(",") != -1):
        return "".join(value.split())
    return value

def translateSeverity(checkstyle_severity):
    return {
        "ERROR":"BLOCKER",
        "WARNING":"MAJOR",
        "INFO":"INFO",
        "IGNORE":"INFO"
    }[checkstyle_severity.upper()]

def getParams(root, parentParams):
    children = root.getchildren()
    list_of_dict = sum(list(
        map(lambda prop: [{prop.get('name'): prop.get('value')}],
            filter(lambda child: child.tag=='property', children)
        )), []
    )
    params = {k: remove_whitespace_if_has_comma(v) for d in list_of_dict for k, v in d.items()}
    return {**parentParams, **params}
    
def getRules(root, parentParams):
    if(root.tag != 'module'):
        return []

    name = root.get('name') # Checker, FileTabCharacter, TreeWalker, ...
    if(name in ["Checker", "TreeWalker"]):
        children = root.getchildren()
        params = getParams(root, parentParams)
        return sum(list(map(lambda child: getRules(child, params), children)), [])
    elif(name.endswith('Filter')):
        return [] # Ignore filters
    else:
        rule = {
            'name': root.get('name'),
            'params': getParams(root, parentParams),
            'markdown_description': 'Auto generated rule from template rule. Please refer to original template rule\'s description'
        }
        if(rule['params'].get('severity') is not None):
            rule['severity'] = translateSeverity(rule['params'].get('severity'))
        return [rule]
