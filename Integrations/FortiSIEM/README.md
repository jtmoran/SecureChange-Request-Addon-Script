## FortiSIEM
This integration queries FortiSIEM CMBD and events for any /32 IP addresses in the ticket and adds the CMBD and event information to the ticket comments.

**Installer:** FortiSIEM.run

**Code:** FortiSIEM.py

### Configuration

**Header:** `[FortiSIEM]`

**Parameters**
| Name | Type | Description | Example |
| :-------------: | :----------: | :----------- | :----------- |
| FS_HOST | String | FortiSIEM IP address or FQDN | 192.168.1.1 |
| FS_USER | String | FortiSIEM user name | admin |
| FS_PASS | String | FortiSIEM password | Password1! |
| QUERY_DAYS | String | Number of days to query FortiSIEM logs | 14 |
| QUERY_TIMEOUT | String | Query timeout in seconds | 60 |

### Output

    FortiSIEM CMDB data for 10.100.60.254:

        IP: 10.100.60.254
        Name: Firewall_12
        Device Vendor: Fortinet
        Device Model: FortiOS
        Device Version: ANY
        Hardware Model: FGT_VM64KVM
        Version: FortiGate-VM64-KVM v6.4.1,build1637,200604 (GA)
        Managed Device: Yes

        Retrieved: 08/24/2020 13:05:16

    FortiSIEM event data (past 14 days) for 10.100.60.254:

        Number of Event Types Returned: 2

        Events:
            Ping Statistics: 8944
            Host performance monitoring state: 601

        Retrieved: 08/24/2020 13:05:16

### Versions
- 08-12-2020 - Initial upload
