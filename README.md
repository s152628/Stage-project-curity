# Stage-project-curity
## Samenvatting
Dit project is een samenstelling van verschillende kubernetes yaml files en ansible yml files die het uitrollen van Curity Identity Server voorziet op een volledig lege ubuntu server. 

## Prerequisits

Ssh keys zijn gedeeld tussen ubuntu server en host.
IP van de ubuntu server staat correct aangegeven in "ansible/inventory/hosts.ini".

## Uitvoeren van project
Vanuit de map ansible/ voer je dit commando uit om de omgeving uit te rollen naar de gewenste omgeving.\n
```ansible-playbook site.yml -e "env=...(dev,acc of prod)" --ask-vault-password```

| Env | Omschrijving | 
| --- | --- | 
| dev | Zet de development omgeving op | 
| acc | Zet de acceptatie omgeving op |
| prod | Zet de productie omgeving op | 

## Variabelen

### Ansible variabelen

Al de Ansible variabelen worden neergeschreven volgens deze wijze:

```variabele: "data"```

#### ansible/inventory/group_vars/all.yml

| Variabele | Omschrijving | 
| --- | --- |
| local_secret_path | Het pad naar de map waar de lokaal de secrets staan voor Curity (.env files, database creation script). |
| curity_config_path | Het pad naar de XML file die de configuratie bepaald voor Curity. | 
| github_deploy_key_path | Het pad naar de github deploy key (Niet nodig als GitHub omgeving publiek staat). | 
| db_user | Naam van de user die Curity gebruikt om de database te beheren. | 
| db_password | Wachtwoord van de user die Curity gebruikt om de database te beheren. |
| cluster_password | Wachtwoord dat de Curity runtime pods gebruiken om aan te tonen dat ze tot hetzelfde cluster behoren. | 
| tailscale_auth_key | Key gebruikt door de tailscale pods om zich te authenticeren bij de tailscale omgeving (Type = Reusable, Ephemeral). |
| argo_admin_password | Wachtwoord dat gebruikt wordt om aan te melden met het admin account op de argo webinterface. |
| grafana_link | De URL waar het grafana portaal beschikbaar zou moeten zijn. | 
| grafana_admin_password | Wachtwoord dat gebruikt wordt om aan te meldem met het admin account op de grafan webinterface. |
| openldap_admin_password | Wachtwoord dat gebruikt wordt door openldap om met admin rechten jobs uit te voeren. |