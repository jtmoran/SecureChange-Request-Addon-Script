## Tenable Security Center
This integration queries Tenable Security Center with any /32 IP addresses in the ticket for vulnerabilites of severity LOW or higher.  For **source** IP addresses, the integration will query Tenable Security Center for any vulnerabilities matching the IP address.  For **destination** IP addresses, the integration will query Tenable Security Center for any vulnerabilities matching the IP address and port combinations.  

**Installer:** TenableSC.run

**Code:** TenableSC.py

### Configuration

**Header:** `[Tenable_SC]`

**Parameters**
| Name | Type | Description | Example |
| :-------------: | :----------: | :----------- | :----------- |
| TSC_HOST | String | Tenable IP address or FQDN | 192.168.1.1 |
| TSC_USER | String | Tenable user name | admin |
| TSC_PASS | String | Tenable password | Password1! |

### Output

    Tenable.sc results for Source 10.0.0.1 :

        Name:      SSL Certificate Cannot Be Trusted
        Family:    General
        Plugin ID: 51192
        Severity:  Medium
        VPR Score: 

        Name:      VMware vCenter Server 5.5.x < 5.5U3g / 6.0.x < 6.0U3d / 6.5.x < 6.5U1e Hypervisor-Assisted Guest Remediation (VMSA-2018-0004) (Spectre)
        Family:    Misc.
        Plugin ID: 105784
        Severity:  Medium
        VPR Score: 7.9

        Name:      VMware vCenter Server 6.5.x < 6.5u1f Multiple Vulnerabilities (VMSA-2018-0007) (Spectre-1) (Meltdown)
        Family:    Misc.
        Plugin ID: 106950
        Severity:  Medium
        VPR Score: 8.4

        Name:      VMware vCenter Server 5.5.x / 6.0.x / 6.5.x / 6.7.x Speculative Execution Side Channel Vulnerability (Foreshadow) (VMSA-2018-0020)
        Family:    Misc.
        Plugin ID: 111760
        Severity:  Medium
        VPR Score: 6.0

    Tenable.sc results for Destination 192.168.1.1:443 :

        Name:      SSL Certificate Signed Using Weak Hashing Algorithm
        Family:    General
        Plugin ID: 35291
        Severity:  Medium
        VPR Score: 4.2

        Name:      SSL Medium Strength Cipher Suites Supported (SWEET32)
        Family:    General
        Plugin ID: 42873
        Severity:  Medium
        VPR Score: 4.4

        Name:      SSL Certificate Cannot Be Trusted
        Family:    General
        Plugin ID: 51192
        Severity:  Medium
        VPR Score: 

        Name:      SSL Self-Signed Certificate
        Family:    General
        Plugin ID: 57582
        Severity:  Medium
        VPR Score:

    Tenable.sc results for Destination 192.168.1.1:22 :

        Name:      SSH Weak Algorithms Supported
        Family:    Misc.
        Plugin ID: 90317
        Severity:  Medium
        VPR Score: 

        Name:      SSH Server CBC Mode Ciphers Enabled
        Family:    Misc.
        Plugin ID: 70658
        Severity:  Low
        VPR Score: 2.5

        Name:      SSH Weak MAC Algorithms Enabled
        Family:    Misc.
        Plugin ID: 71049
        Severity:  Low
        VPR Score:
        
    No Tenable.sc results found for 10.0.0.2
    No Tenable.sc results found for 192.168.1.1:80
    No Tenable.sc results found for 192.168.1.2:443

### Versions
- 08-28-2020 - Initial upload
