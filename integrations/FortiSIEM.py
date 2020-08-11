import os
script_path = os.path.abspath(os.path.join(os.path.dirname( __file__ ), "../.."))

import sys
sys.path.append(os.path.join(script_path, "lib"))
sys.path.append(os.path.join(script_path, "bin/integrations"))

import json
import time
import configparser
import requests
import socket
import xmltodict
import argparse
import sys
from datetime import datetime

requests.packages.urllib3.disable_warnings()

config = configparser.ConfigParser()
config.read_file(os.path.join(script_path, "bin/integrations/integration_config.txt"))
FS_HOST = config.get('FortiSIEM', 'FS_HOST').strip('"')
FS_USER = config.get('FortiSIEM', 'FS_USER').strip('"')
FS_PASS = config.get('FortiSIEM', 'FS_PASS').strip('"')
QUERY_DAYS = config.get('FortiSIEM', 'QUERY_DAYS').strip('"')
QUERY_TIMEOUT = int(config.get('FortiSIEM', 'QUERY_TIMEOUT').strip('"'))

QUERYDT = datetime.now().strftime("%m/%d/%Y %H:%M:%S")

def valid_ip(ip):
    if '/' in ip:
        if len(ip.split('/')) == 2:
            if ip.split('/')[1] == '32':
                ip = ip.split('/')[0]
            else:
                return False
        else:
            return False
    try:
        socket.inet_aton(ip)
        return ip
    except socket.error:
        return False


def format_text_events(json_events, ip):
    formatted = 'FortiSIEM event data (past 14 days) for {}:\n'.format(ip)
    formatted = '{}\n    Number of Event Types Returned: {}'.format(formatted, json_events['result_count'])
    if int(json_events['result_count']) > 0:
        formatted = '{}\n\n    Events:'.format(formatted)
        for event in json_events['events']:
            formatted = '{}\n        {}: {}'.format(formatted, event['name'], event['count'])
    formatted = '{}\n\n    Retrieved: {}'.format(formatted, QUERYDT)
    return formatted


def format_text_cmdb(json_data, ip):
    formatted = 'FortiSIEM CMDB data for {}:\n'.format(ip)
    device = json_data['device']
    if 'accessIp' in device.keys():
        formatted = '{}\n    IP: {}'.format(formatted, device['accessIp'])
    if 'name' in device.keys():
        formatted = '{}\n    Name: {}'.format(formatted, device['name'])
    if 'deviceType' in device.keys():
        device_type = device['deviceType']
        if 'vendor' in device_type.keys():
            formatted = '{}\n    Device Vendor: {}'.format(formatted, device_type['vendor'])
        if 'model' in device_type.keys():
            formatted = '{}\n    Device Model: {}'.format(formatted, device_type['model'])
        if 'version' in device_type.keys():
            formatted = '{}\n    Device Version: {}'.format(formatted, device_type['version'])
    if 'hwModel' in device.keys():
        formatted = '{}\n    Hardware Model: {}'.format(formatted, device['hwModel'])
    if 'version' in device.keys():
        formatted = '{}\n    Version: {}'.format(formatted, device['version'])
    if 'unmanaged' in device.keys():
        if device['unmanaged'].lower() == 'false':
            formatted = '{}\n    Managed Device: Yes'.format(formatted)
        else:
            formatted = '{}\n    Managed Device: No'.format(formatted)

    formatted = '{}\n\n    Retrieved: {}'.format(formatted, QUERYDT)
    return formatted.lstrip()


def device_error(code, ip, ret_json):
    if code == 401:
        ret = 'Unable to query FortiSIEM - 401 Not Authorized (check FortiSIEM credentials)'
        if ret_json:
            return {'status': 'Error', 'message': ret, 'returned': QUERYDT}
        else:
            return 'FortiSIEM CMDB data for {}:\n\n    {}'.format(ip, ret)
    elif code == 403:
        ret = 'Unable to query FortiSIEM - 403 Forbidden'
        if ret_json:
            return {'status': 'Error', 'message': ret, 'returned': QUERYDT}
        else:
            return 'FortiSIEM CMDB data for {}:\n\n    {}'.format(ip, ret)
    elif code == 404:
        ret = 'Unable to query FortiSIEM - 404 Not Found'
        if ret_json:
            return {'status': 'Error', 'message': ret, 'returned': QUERYDT}
        else:
            return 'FortiSIEM CMDB data for {}:\n\n    {}'.format(ip, ret)
    elif code == 500:
        ret = 'Unable to query FortiSIEM - 500 Internal Server Error'
        if ret_json:
            return {'status': 'Error', 'message': ret, 'returned': QUERYDT}
        else:
            return 'FortiSIEM CMDB data for {}:\n\n    {}'.format(ip, ret)


def event_error(code, ip, ret_json):
    if code == 401:
        ret = 'Unable to query FortiSIEM - 401 Not Authorized (check FortiSIEM credentials)'
        if ret_json:
            return {'status': 'Error', 'message': ret, 'returned': QUERYDT}
        else:
            return 'FortiSIEM event data for {}:\n\n    {}'.format(ip, ret)
    elif code == 403:
        ret = 'Unable to query FortiSIEM - 403 Forbidden'
        if ret_json:
            return {'status': 'Error', 'message': ret, 'returned': QUERYDT}
        else:
            return 'FortiSIEM event data for {}:\n\n    {}'.format(ip, ret)
    elif code == 404:
        ret = 'Unable to query FortiSIEM - 404 Not Found'
        if ret_json:
            return {'status': 'Error', 'message': ret, 'returned': QUERYDT}
        else:
            return 'FortiSIEM event data for {}:\n\n    {}'.format(ip, ret)
    elif code == 500:
        ret = 'Unable to query FortiSIEM - 500 Internal Server Error'
        if ret_json:
            return {'status': 'Error', 'message': ret, 'returned': QUERYDT}
        else:
            return 'FortiSIEM event data for {}:\n\n    {}'.format(ip, ret)


def device_query(ip, fmt='text'):
    ret_json = False
    if fmt.lower() == 'json':
        ret_json = True

    if not valid_ip(ip):
        ret = '{} is not a valid, single IPv4 address - nothing to query'.format(ip)
        if ret_json:
            return {'status': 'Error', 'message': ret, 'returned': QUERYDT}
        else:
            return 'FortiSIEM CMDB data :\n\n    {}'.format(ret)
    else:
        ip = valid_ip(ip)

    url = 'https://{}/phoenix/rest/cmdbDeviceInfo/device?ip={}&loadDepend=true'.format(FS_HOST, ip)

    try:
        res = requests.get(url, auth=(FS_USER, FS_PASS), verify=False)
    except Exception as e:
        ret = 'Unable to query FortiSIEM - {}'.format(e)
        if ret_json:
            return {'status': 'Error', 'message': ret, 'returned': QUERYDT}
        else:
            return 'FortiSIEM CMDB data for {}:\n\n    {}'.format(ip, ret)

    # Successful query
    if res.status_code == 200:
        json_data = xmltodict.parse(res.text)

        # Device found
        if 'device' in json_data:
            if ret_json:
                ret = {'status': 'Success', 'message': '', 'returned': QUERYDT}
                json_data.update(ret)
                return json_data
            else:
                return format_text_cmdb(json_data, ip)

        # No device found
        else:
            ret = 'No device matching {} found'.format(ip)
            if ret_json:
                return {'status': 'No Results', 'message': ret, 'returned': QUERYDT}
            else:
                return 'FortiSIEM CMDB data for {}:\n\n    {}'.format(ip, ret)

    # Handle HTTP errors and return
    else:
        return device_error(res.status_code, ip, ret_json)


def parse_events(event_json):
    ret_json = {'status': 'Success', 'message': '', 'returned': QUERYDT}
    ret_json['result_count'] = event_json['queryResult']['@totalCount']
    if event_json['queryResult']['events']:
        events = []
        for event in event_json['queryResult']['events']['event']:
            name = ''
            count = ''
            for attrib in event['attributes']['attribute']:
                if attrib['@name'] == 'eventName':
                    name = attrib['#text']
                if attrib['@name'] == 'COUNT(*)':
                    count = attrib['#text']
            events.append({'name': name, 'count': count})
        ret_json['events'] = events
    return ret_json


def event_query(ip, fmt='text'):
    ret_json = False
    if fmt.lower() == 'json':
        ret_json = True

    if not valid_ip(ip):
        ret = '{} is not a valid, single IPv4 address - nothing to query'.format(ip)
        if ret_json:
            return {'status': 'Error', 'message': ret, 'returned': QUERYDT}
        else:
            return 'FortiSIEM CMDB data :\n\n    {}'.format(ret)
    else:
        ip = valid_ip(ip)

    query_url = 'https://{}/phoenix/rest/query/eventQuery'.format(FS_HOST)
    headers = {'Content-Type': 'text/xml'}

    query_dict = {
        'Reports': {
            'Report': {
                '@group': 'report',
                '@id': 'All Incidents',
                'CustomerScope': {
                    '@groupByEachCustomer': 'false',
                    'Include': {
                        '@all': 'true'
                    },
                    'Exclude': None
                },
                'SelectClause': {
                    '@numEntries': 'All',
                    'AttrList': 'eventSeverityCat,incidentLastSeen,eventName,incidentRptDevName,incidentSrc,'
                                'incidentTarget,incidentDetail,incidentStatus,incidentReso,incidentId,eventType,'
                                'incidentTicketStatus, bizService,count,incidentClearedTime,incidentTicketUser,'
                                'incidentNotiRecipients,incidentClearedReason,incidentComments,eventSeverity,'
                                'incidentFirstSeen,incidentRptIp,incidentTicketId,customer,incidentNotiStatus,'
                                'incidentClearedUser,incidentExtUser,incidentExtClearedTime,incidentExtResoTime,'
                                'incidentExtTicketId,incidentExtTicketState,incidentExtTicketType,incidentViewStatus,'
                                'rawEventMsg,phIncidentCategory,phSubIncidentCategory,incidentRptDevStatus'
                },
                'OrderByClause': {
                    'AttrList': 'incidentLastSeen DESC'
                },
                'ReportInterval': {
                    'Window': {
                        '@unit': 'Daily',
                        '@val': QUERY_DAYS
                    }
                },
                'PatternClause': {
                    '@window': '3600',
                    'SubPattern': {
                        '@displayName': 'Incidents',
                        '@name': 'Incidents',
                        'SingleEvtConstr': 'rawEventMsg CONTAIN "{}"'.format(ip),
                        'GroupByAttr': 'eventType'
                    }
                }
            }
        }
    }
    session = requests.session()
    try:
        response_query = session.post(query_url, auth=(FS_USER, FS_PASS), headers=headers,
                                      data=(xmltodict.unparse(query_dict)), verify=False)
    except Exception as e:
        ret = 'Unable to query FortiSIEM - {}'.format(e)
        if ret_json:
            return {'status': 'Error', 'message': ret, 'returned': QUERYDT}
        else:
            return 'FortiSIEM event data for {}:\n\n    {}'.format(ip, ret)

    if 'error code="255"' in response_query.text:
        error_dict = xmltodict.parse(response_query.text)
        ret = 'Unable to query FortiSIEM - {}'.format(error_dict['response']['error']['description'])
        if ret_json:
            return {'status': 'Error', 'message': ret, 'returned': QUERYDT}
        else:
            return 'FortiSIEM event data for {}:\n\n    {}'.format(ip, ret)

    # Successful query
    if response_query.status_code == 200:
        # Check query progress
        headers = {'Content-Type': 'application/json'}
        query_id = response_query.text
        progress_url = 'https://{}/phoenix/rest/query/progress/{}'.format(FS_HOST, query_id)
        try:
            timeout = QUERY_TIMEOUT
            response_progress = session.get(progress_url, auth=(FS_USER, FS_PASS), headers=headers, verify=False)
            if response_progress.status_code != 200:
                return device_error(response_progress.status_code, ip, ret_json)
            while response_progress.text != "100" and timeout > 0:
                response_progress = session.get(progress_url, auth=(FS_USER, FS_PASS), headers=headers, verify=False)
                if response_progress.status_code != 200:
                    return device_error(response_progress.status_code, ip, ret_json)
                timeout = timeout - 1
                if timeout == 0:
                    ret = 'FortiSIEM query timed out'
                    if ret_json:
                        return {'status': 'Error', 'message': ret, 'returned': QUERYDT}
                    else:
                        return 'FortiSIEM event data for {}:\n\n    {}'.format(ip, ret)
                time.sleep(1)
            event_url = 'https://{}/phoenix/rest/query/events/{}/0/25'.format(FS_HOST, query_id)
            response_events = session.get(event_url, auth=(FS_USER, FS_PASS), headers=headers, verify=False)
            if response_events.status_code != 200:
                return device_error(response_events.status_code, ip, ret_json)
            json_events = xmltodict.parse(response_events.text)
            return_json = parse_events(json_events)
            if ret_json:
                return return_json
            else:
                return format_text_events(return_json, ip)
        except Exception as e:
            ret = 'Unable to query FortiSIEM - {}'.format(e)
            if ret_json:
                return {'status': 'Error', 'message': ret, 'returned': QUERYDT}
            else:
                return 'FortiSIEM event data for {}:\n\n    {}'.format(ip, ret)

    # Handle HTTP errors and return
    else:
        return device_error(response_query.status_code, ip, ret_json)

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
                if src['Private'] and src['Cidr'] == '32':
                    return_str = '{}\n\n{}\n\n{}'.format(return_str, device_query(src['Ip'], fmt='text'), event_query(src['Ip'], fmt='text'))
            for dst in req['Destinations']:
                if dst['Private'] and dst['Cidr'] == '32':
                    return_str = '{}\n\n{}\n\n{}'.format(return_str, device_query(dst['Ip'], fmt='text'), event_query(dst['Ip'], fmt='text'))


    except Exception as e:

        # Log the error and return an empty string
        logger.error("Error: {}".format(e))
        return None

    # Log integration completing
    logger.info("{} integration completed".format(__name__))

    # Return comment
    return return_str
