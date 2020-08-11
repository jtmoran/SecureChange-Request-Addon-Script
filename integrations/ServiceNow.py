import configparser
import requests

requests.packages.urllib3.disable_warnings()

config = configparser.ConfigParser()
config.read_file(open(r'/usr/local/ticket_enrichment/bin/integrations/integration_config.txt'))
SN_HOST = config.get('ServiceNow', 'SN_HOST').strip('"')
SN_USER = config.get('ServiceNow', 'SN_USER').strip('"')
SN_PASS = config.get('ServiceNow', 'SN_PASS').strip('"')

def get_link(url):
    headers = {
        'accept': 'application/json',
        'content-type': 'application/json',
        'cache-control': 'no-cache'
    }
    try:
        res = requests.get(url, headers=headers, auth=(SN_USER, SN_PASS), verify=False)
        if res.status_code == 200:
            return res.json()["result"]["name"]
        else:
            return ""
    except:
        return ""


def ci_query (ip, logger):
    headers = {
        'accept': 'application/json',
        'content-type': 'application/json',
        'cache-control': 'no-cache'
    }
    return_ci = "ServiceNow CI results for {}:".format(ip)
    try:
        # Query CI
        url = "https://{}/api/now/table/cmdb_ci?sysparm_query=ip_address%3D{}".format(SN_HOST.rstrip("/"), ip)
        res = requests.get(url, headers=headers, auth=(SN_USER, SN_PASS), verify=False)
        # If query was successful
        if res.status_code == 200:
            # Results were found
            if len(res.json()["result"]) > 0:
                # For each result
                for result in res.json()["result"]:
                    ci_data = "    IP: {}".format(ip)
                    ci_data = "{}\n    FQDN: {}".format(ci_data, result["fqdn"])
                    ci_data = "{}\n    Name: {}".format(ci_data, result["name"])
                    ci_data = "{}\n    Vendor: {}".format(ci_data, result["vendor"])
                    ci_data = "{}\n    Model: {}".format(ci_data, result["model_number"])
                    ci_data = "{}\n    Category: {}".format(ci_data, result["category"])
                    if "link" in result["assigned_to"]:
                        ci_data = "{}\n    Assigned To: {}".format(ci_data, get_link(result["assigned_to"]["link"]))
                    else:
                        ci_data = "{}\n    Assigned To: ".format(ci_data)
                    if "link" in result["department"]:
                        ci_data = "{}\n    Department: {}".format(ci_data, get_link(result["department"]["link"]))
                    else:
                        ci_data = "{}\n    Department: ".format(ci_data)
                    if "link" in result["location"]:
                        ci_data = "{}\n    Location: {}".format(ci_data, get_link(result["location"]["link"]))
                    else:
                        ci_data = "{}\n    Location: ".format(ci_data)
                    if "link" in result["owned_by"]:
                        ci_data = "{}\n    Owned By: {}".format(ci_data, get_link(result["owned_by"]["link"]))
                    else:
                        ci_data = "{}\n    Owned By: ".format(ci_data)
                    ci_data = "{}\n    Short Desc: {}".format(ci_data, result["short_description"])
                    ci_data = "{}\n    Comments: {}".format(ci_data, result["comments"])
                    ci_data = "{}\n    Link: {}".format(ci_data, "https://{}/nav_to.do?uri=%2F{}.do%3Fsys_id%3D{}".format(SN_HOST, result["sys_class_name"], result["sys_id"]))


                    return_ci = "{}\n\n{}".format(return_ci, ci_data)
            # No results were found
            else:
                return_ci = "{}\n\n    No results found".format(return_ci)
        # If query was unsuccessful
        else:
            logger.error('Error {} Reaching {}: {}'.format(res.status_code, res.url, res.reason))
            return None
        return return_ci
    except Exception as e:
        logger.error("Error: {}".format(e))
        return None


def get_data(ticket_info, logger):
    """ This fucntion accepts the SecureChange access request and will return a string which
    will be added to the SecureChange ticket as a comment.  If an error occurs, return None
    and log the error via the logger.

    :param ticket_info: SecureChange ticket information
    :type ticket_info: dict
    :param logger: Tufin logger
    :type logger: pytos.common.logging.logger
    :return: Comment to be added to SecureChange ticket, or None on error
    :rtype: str | None
    """

    # This string will be returned and added as a comment to the SecureChange ticket
    return_str = ""

    # Log integration starting
    logger.info("Running '{}' integration".format(__name__))

    try:

        for req in ticket_info['Requests']:
            for src in req['Sources']:
                if src['Cidr'] == '32':
                    return_str = '{}\n\n{}'.format(return_str, ci_query(src["Ip"], logger))
            for dst in req['Destinations']:
                if dst['Cidr'] == '32':
                    return_str = '{}\n\n{}'.format(return_str, ci_query(dst["Ip"], logger))

    except Exception as e:

        # Log the error and return an empty string
        logger.error("Error: {}".format(e))
        return None

    # Log integration completing
    logger.info("{} integration completed".format(__name__))

    # Return comment
    return return_str
