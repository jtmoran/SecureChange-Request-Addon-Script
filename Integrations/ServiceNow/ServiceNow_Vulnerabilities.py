''''
The following configuration parameters should be added to ./bin/integrations/integration_config.txt:
[ServiceNow_Vuln]
# ServiceNow IP or FQDN
SN_HOST = ""
# ServiceNow user name
SN_USER = ""
# ServiceNow password
SN_PASS = ""
# Vulnerability statuses to disregard, in a comma-separated list (Default: "3" (Closed))
SN_VSTAT = "3"
''''

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
SN_HOST = config.get('ServiceNow_Vuln', 'SN_HOST').strip('"')
SN_USER = config.get('ServiceNow_Vuln', 'SN_USER').strip('"')
SN_PASS = config.get('ServiceNow_Vuln', 'SN_PASS').strip('"')
SN_VSTAT = config.get('ServiceNow_Vuln', 'SN_VSTAT').strip('"')

IGNORE_STATUSES = [x.strip() for x in SN_VSTAT.split(',')]

RISK_RATING = {
    "1": "CRITICAL",
    "2": "HIGH",
    "3": "MEDIUM",
    "4": "LOW",
    "5": "NONE",

}

def get_vuln_details(url):
    headers = {
        'accept': 'application/json',
        'content-type': 'application/json',
        'cache-control': 'no-cache'
    }
    try:
        res = requests.get(url, headers=headers, auth=(SN_USER, SN_PASS), verify=False)
        if res.status_code == 200:
            ret = ""
            ret = "{}\n    Summary:     {}".format(ret, res.json()["result"]["summary"])
            ret = "{}\n    Conf Imp:    {}".format(ret, res.json()["result"]["confidentiality_impact"])
            ret = "{}\n    Integ Imp:   {}".format(ret, res.json()["result"]["integrity_impact"])
            ret = "{}\n    Avail Imp:   {}".format(ret, res.json()["result"]["availability_impact"])
            ret = "{}\n    Vector:      {}".format(ret, res.json()["result"]["access_vector"])
            ret = "{}\n    Complexity:  {}".format(ret, res.json()["result"]["access_complexity"])
            return ret
        else:
            print("Not 200")
            return ""
    except Exception as e:
        print(e)
        return ""


def vuln_query (ip, logger):
    headers = {
        'accept': 'application/json',
        'content-type': 'application/json',
        'cache-control': 'no-cache'
    }
    return_data = ""
    try:
        # Query CI
        ci_url = "https://{}/api/now/table/cmdb_ci?sysparm_query=ip_address%3D{}".format(SN_HOST.rstrip("/"), ip)
        ci_res = requests.get(ci_url, headers=headers, auth=(SN_USER, SN_PASS), verify=False)
        # If query was successful
        if ci_res.status_code == 200:
            # Results were found
            try:
                ci_res.json()
            except:
                logger.error("Invalid response recieved from ServiceNow: {}".format(ci_res.text))
                return None
            if len(ci_res.json()["result"]) > 0:
                # For each result
                for ci_result in ci_res.json()["result"]:
                    try:
                        # Query for vulnerabilities
                        vuln_url = "https://{}/api/now/table/sn_vul_vulnerable_item?sysparm_query=cmdb_ci%3D{}^risk_rating%21%3D4".format(SN_HOST.rstrip("/"), ci_result["sys_id"])
                        # Add ignored statuses to URL
                        for status in IGNORE_STATUSES:
                            vuln_url = "{}^risk_rating%21%3D{}".format(vuln_url, status)
                        vuln_url = "{}^ORDERBYDESCrisk_score".format(vuln_url)
                        vuln_res = requests.get(vuln_url, headers=headers, auth=(SN_USER, SN_PASS), verify=False)
                        # If query was successful
                        if vuln_res.status_code == 200:
                            return_data = "{}\nVulnerability results for {}:\n".format(return_data, ci_result["name"])
                            try:
                                vuln_res.json()
                            except:
                                logger.error("Invalid response recieved from ServiceNow: {}".format(vuln_res.text))
                                return None
                            if len(vuln_res.json()["result"]) > 0:
                                for vuln_result in vuln_res.json()["result"]:
                                    return_data = "{}\n    ID:          {}".format(return_data, vuln_result["number"])
                                    return_data = "{}\n    Description: {}".format(return_data, vuln_result["short_description"])
                                    return_data = "{}\n    Risk Score:  {}".format(return_data, vuln_result["risk_score"])
                                    return_data = "{}\n    Risk Rating: {}".format(return_data, RISK_RATING[vuln_result["risk_rating"]])
                                    return_data = "{}\n    First Found: {}".format(return_data, vuln_result["first_found"])
                                    return_data = "{}\n    Last Found:  {}".format(return_data, vuln_result["last_found"])
                                    if "link" in vuln_result["vulnerability"]:
                                        return_data = "{}{}".format(return_data, get_vuln_details(vuln_result["vulnerability"]["link"]))
                                        return_data = "{}\n    Details:     {}".format(return_data, vuln_result["vulnerability"]["link"])
                                    return_data = "{}\n".format(return_data)

                            # No results were found
                            else:
                                return_data = "{}\n\n    No vulnerabilities found".format(return_data)
                        # If query was unsuccessful
                        else:
                            logger.error('Error {} Reaching {}: {}'.format(vuln_res.status_code, vuln_res.url, vuln_res.reason))
                            return None
                    except Exception as e:
                        logger.error("Error: {}".format(e))
                        return None

            # No results were found
            else:
                return_data = "{}\nNo CIs found for {}".format(return_data, ip)
        # If query was unsuccessful
        else:
            logger.error('Error {} Reaching {}: {}'.format(ci_res.status_code, ci_res.url, ci_res.reason))
            return None
        return return_data.rstrip()
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
                    return_str = '{}\n\n{}'.format(return_str, vuln_query(src["Ip"], logger))
            for dst in req['Destinations']:
                if dst['Cidr'] == '32':
                    return_str = '{}\n\n{}'.format(return_str, vuln_query(dst["Ip"], logger))

    except Exception as e:

        # Log the error and return an empty string
        logger.error("Error: {}".format(e))
        return None

    # Log integration completing
    logger.info("{} integration completed".format(__name__))

    # Return comment
    return return_str
