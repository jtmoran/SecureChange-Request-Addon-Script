import os
script_path = os.path.abspath(os.path.join(os.path.dirname( __file__ ), "../.."))

import sys
sys.path.append(os.path.join(script_path, "lib"))
sys.path.append(os.path.join(script_path, "bin/integrations"))

import configparser
import requests

requests.packages.urllib3.disable_warnings()

# './integration_config.txt' can be used to store configuration parameters for your
# integration.  The example below sets two variables based on the parameters in the
# configuration file for the example integration named 'YOUR_INTEGRATION_NAME'.

config = configparser.ConfigParser()
config.read(os.path.join(script_path, "bin/integrations/integration_config.txt"))
IB_HOST = config.get('Infoblox', 'IB_HOST').strip('"')
IB_USER = config.get('Infoblox', 'IB_USER').strip('"')
IB_PASS = config.get('Infoblox', 'IB_PASS').strip('"')
IB_APIV = config.get('Infoblox', 'IB_APIV').strip('"')


def search_ip(ip, logger):
    result = "Infoblox results for {}:\n".format(ip)

    # Get IP address information
    ip_url = "https://{}/wapi/v{}/ipv4address?ip_address={}".format(IB_HOST, IB_APIV, ip)
    try:
        res = requests.get(ip_url, auth=(IB_USER, IB_PASS), verify=False)
        if res.status_code == 200:
            try:
                res.json()
            except:
                logger.error("Recieved data in invalid format: {}".format(res.text))
                return None
            result = "{}\n    IP Address Information:\n".format(result)
            for item in res.json():
                if "status" in item:
                    result = "{}\n        Status: {}".format(result, item["status"])
                if "names" in item:
                    if len(item["types"]) > 0:
                        result = "{}\n        Types: {}".format(result, ", ".join(item["types"]))
                if "lease_state" in item:
                    result = "{}\n        Lease State: {}".format(result, item["lease_state"])
                if "is_conflict" in item:
                    result = "{}\n        Conflict: {}".format(result, item["is_conflict"])
                if "names" in item:
                    if len(item["names"]) > 0:
                        result = "{}\n        Names: {}".format(result, ", ".join(item["names"]))
                if "network" in item:
                    result = "{}\n        Network: {}".format(result, item["network"])
        elif res.status_code == 400:
            result = "{}\n        No results found: {}".format(result, res.json()["text"])
        else:
            result = "{}\n        Error {}: {}".format(result, res.status_code, res.reason)
    except Exception as e:
        logger.error("Error: {}".format(e))
        return None

    # Get IP search results
    ip_url = "https://{}/wapi/v{}/search?address={}".format(IB_HOST, IB_APIV, ip)
    try:
        res = requests.get(ip_url, auth=(IB_USER, IB_PASS), verify=False)
        if res.status_code == 200:
            try:
                res.json()
            except:
                logger.error("Recieved data in invalid format: {}".format(res.text))
                return None
            result = "{}\n\n    IP Search Results:\n".format(result)
            hosts = ""
            if len(res.json()) < 1:
                result = "{}\n        No results found".format(result)
            for item in res.json():
                if "range" in item["_ref"]:
                    result = "{}\n        Range:".format(result)
                    result = "{}\n        - Network: {}".format(result, item["network"])
                    result = "{}\n        - Start: {}".format(result, item["start_addr"])
                    result = "{}\n        - End: {}".format(result, item["end_addr"])
                if "network" in item["_ref"]:
                    result = "{}\n        Network:".format(result)
                    result = "{}\n        - Network: {}".format(result, item["network"])
                    result = "{}\n        - Comment: {}".format(result, item["comment"])
                if "record:host" in item["_ref"]:
                    for host in item["ipv4addrs"]:
                        hosts = "{}\n        - '{}' ({}) DHCP: {}".format(hosts, host["host"], host["ipv4addr"], host["configure_for_dhcp"])
            if len(hosts) > 0:
                result = "{}\n        Hosts:{}".format(result, hosts)
        elif res.status_code == 400:
            result = "{}\n        No results found: {}".format(result, res.json()["text"])
        else:
            result = "{}\n        Error {}: {}".format(result, res.status_code, res.reason)
    except Exception as e:
        logger.error("Error: {}".format(e))
        return None

    return result


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
                    return_str = '{}\n\n{}'.format(return_str, search_ip(src["Ip"], logger))
            for dst in req['Destinations']:
                if dst['Cidr'] == '32':
                    return_str = '{}\n\n{}'.format(return_str, search_ip(dst["Ip"], logger))

    except Exception as e:

        # Log the error and return an empty string
        logger.error("Error: {}".format(e))
        return None

    # Log integration completing
    logger.info("{} integration completed".format(__name__))

    # Return comment
    return return_str
