## ServiceNow CIs
This integration queries ServiceNow CIs for any /32 IP addresses in the ticket and adds the CI information to the ticket comments.

**Installer:** ServiceNow_CIs.run

**Code:** ServiceNow_CIs.py

### Configuration

**Header:** `[ServiceNow_CIs]`

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

## ServiceNow Vulnerabilities
This integration queries ServiceNow for vulnerabilies related to any /32 IP addresses in the ticket and adds the vulnerability information to the ticket comments.  Vulnerabilities of a certain status (for example, Closed (ID: 3)) can be omitted by adding these statuses to the `SN_VSTAT` configuration parameter.

**Installer:** ServiceNow_Vulnerabilities.run

**Code:** ServiceNow_Vulnerabilities.py

### Configuration

**Header:** `[ServiceNow_Vuln]`

**Parameters**
| Name | Type | Description | Example |
| :-------------: | :----------: | :----------- | :----------- |
| SN_HOST | String | ServiceNow IP address or FQDN | 192.168.1.1 |
| SN_USER | String | ServiceNow user name | admin |
| SN_PASS | String | ServiceNow password | Password1! |
| SN_VSTAT | String | Vulnerability statuses to disregard, in a comma-separated list | 3, 101 |

### Output

        Vulnerability results for LOAD-SF-2445:

            ID:          VIT0010234
            Description: CVE-2013-0074 detected on LOAD-SF-2445
            Risk Score:  100
            Risk Rating: CRITICAL
            First Found: 2021-06-28
            Last Found:  2021-06-28
            Summary:     Microsoft Silverlight 5, and 5 Developer Runtime, before 5.1.20125.0 does not properly validate pointers during HTML object rendering, which allows remote attackers to execute arbitrary code via a crafted Silverlight application, aka "Silverlight Double Dereference Vulnerability."
            Conf Imp:    COMPLETE
            Integ Imp:   COMPLETE
            Avail Imp:   COMPLETE
            Vector:      NETWORK
            Complexity:  MEDIUM
            Details:     https://dev52177.service-now.com/api/now/table/sn_vul_entry/a5b3b65edb5873005daef4eabf9619e9

            ID:          VIT0010851
            Description: CVE-2013-3906 detected on LOAD-SF-2445
            Risk Score:  100
            Risk Rating: CRITICAL
            First Found: 2021-06-18
            Last Found:  2021-06-18
            Summary:     GDI+ in Microsoft Windows Vista SP2 and Server 2008 SP2; Office 2003 SP3, 2007 SP3, and 2010 SP1 and SP2; Office Compatibility Pack SP3; and Lync 2010, 2010 Attendee, 2013, and Basic 2013 allows remote attackers to execute arbitrary code via a crafted TIFF image, as demonstrated by an image in a Word document, and exploited in the wild in October and November 2013.
            Conf Imp:    COMPLETE
            Integ Imp:   COMPLETE
            Avail Imp:   COMPLETE
            Vector:      NETWORK
            Complexity:  MEDIUM
            Details:     https://dev52177.service-now.com/api/now/table/sn_vul_entry/b204fa52db9873005daef4eabf9619a1

            ID:          VIT0001684
            Description: CVE-2014-6332 detected on LOAD-SF-2445
            Risk Score:  80
            Risk Rating: HIGH
            First Found: 2019-05-31
            Last Found:  2019-05-31
            Summary:     OleAut32.dll in OLE in Microsoft Windows Server 2003 SP2, Windows Vista SP2, Windows Server 2008 SP2 and R2 SP1, Windows 7 SP1, Windows 8, Windows 8.1, Windows Server 2012 Gold and R2, and Windows RT Gold and 8.1 allows remote attackers to execute arbitrary code via a crafted web site, as demonstrated by an array-redimensioning attempt that triggers improper handling of a size value in the SafeArrayDimen function, aka "Windows OLE Automation Array Remote Code Execution Vulnerability."
            Conf Imp:    COMPLETE
            Integ Imp:   COMPLETE
            Avail Imp:   COMPLETE
            Vector:      NETWORK
            Complexity:  MEDIUM
            Details:     https://dev52177.service-now.com/api/now/table/sn_vul_entry/31a5b656dbd873005daef4eabf961982
            
            ...

### Versions
- 08-12-2020 - Initial upload
- 08-31-2020 - ServiceNow Vulnerabilities added
