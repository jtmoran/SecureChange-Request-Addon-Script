## ServiceNow
This integration queries ServiceNow CIs for any /32 IP addresses in the ticket and adds the CI information to the ticket comments.

**Installer:** ServiceNow.run

**Code:** ServiceNow.py

### Configuration

**Header:** `[ServiceNow]`

**Parameters**
| Name | Type | Description | Example |
| :-------------: | :----------: | :----------- | :----------- |
| SN_HOST | String | ServiceNow IP address or FQDN | 192.168.1.1 |
| SN_USER | String | ServiceNow user name | admin |
| SN_PASS | String | ServiceNow password | Password1! |

### Output

    ServiceNow CI results for 172.16.20.30:

        IP: 172.16.20.30
        FQDN: Firewall_36.example.net
        Name: Firewall_36
        Vendor: Fortinet
        Model: FG300
        Category: Hardware
        Assigned To: Kevin Gallows
        Department: Sales
        Location: Boston
        Owned By: Tyler Jackson
        Short Desc: Fortinet FG300 Firewall
        Comments: Server room, third floow
        Link: https://example.service-now.com/nav_to.do?uri=%2Fcmdb_ci_appl.do%3Fsys_id%1234567890abcdef1234567890abcdef

### Versions
- 08-12-2020 - Initial upload
