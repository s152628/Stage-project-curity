# Stage-project-curity
## Samenvatting
Dit project is een samenstelling van verschillende kubernetes yaml files en ansible yml files die het uitrollen van Curity Identity Server voorziet op een volledig lege ubuntu server. 

## Prerequisits

- SSH keys zijn gedeeld tussen ubuntu server en host.
- IP van de ubuntu server staat correct aangegeven in "ansible/inventory/hosts.ini".
- Een users.json file met een lijst aan users voor in de ldap indien gewenst.

## Uitvoeren van project
Vanuit de map ansible/ voer je volgend commando uit om de omgeving uit te rollen naar de gewenste omgeving:

```ansible-playbook site.yml -e "env={dev|acc|prod}" --ask-vault-password```

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

Algemene variabelen gebruikt in het playbook.

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

#### ansible/inventory/group_vars/{dev|acc|prod}.yml

Omgevingspecifieke variabelen gebruikt in het playbook. (Overschrijft de algemene variabelen)

| Variabele | Omschrijving | 
| --- | --- |
| testapp_client_id | Client ID van de Curity client waar de testapp naar moet verwijzen. | 
| testapp_client_secret |Client secret van de Curity client waar de testapp naar moet verwijzen. | 
| testapp_app_domain | Domein waar de testapp bereikbaar is. |
| testapp_issuer_url | Issuer URL van de Curity Identity server. | 

### Curity variabelen

#### {{ local_secret_path }}/{dev|acc|prod}/{dev|acc|prod}.env

De variabelen die gebruikt worden om het XML file aan te vullen. Het template voor de curity-config kan worden vervangen door een volledig ingevuld XML file, MAAR deze mag dan niet op GitHub terrecht komen. Als de template wordt vervangen dan kunnen de variabelen worden genegeerd

| Variabele | Omschrijving | 
| --- | --- |
| RUNTIME_BASE_URL | De URL waar het runtime inteface beschikbaar is. |
| ADMIN_USERNAME | De gebruikersnaam voor de Curity Admin UI en CLI .|
| ADMIN _PASSWORD | Het wachtwoord voor de Curity Admin gebruiker. |
| SYMMETRIC_KEY | Een willekeurige string (min. 32 tekens) gebruikt voor encryptie van data in rust (cookies/sessies). |
| DB_CONNECTION | JDBC connection string voor de standaard/lokale database.| 
| DB_PASSWORD | Wachtwoord voor de standaard database. |
| DB_USERNAME | Gebruikersnaam voor de standaard database. |
| SSL_KEY | De Base64 encoded private key/certificaat voor de HTTPS-interface. |
| SIGNING_KEY | De private key die Curity gebruikt om JWT-tokens digitaal te ondertekenen. |
| VERIFICATION_KEY | De publieke sleutel gebruikt om de handtekeningen van inkomende verzoeken te verifiëren. |
| LICENSE_KEY | De volledige inhoud van het Curity licentie-bestand. |
| CLIENT_1_ID | Unieke ID voor de eerste client (bijv. een interne tool voor introspectie). |
| CLIENT_1_SECRET | Het wachtwoord (secret) voor de eerste client. |
| CLIENT_2_ID | Unieke ID voor de tweede client (code flow). |
| CLIENT_2_SECRET | Het wachtwoord (secret) voor de tweede client. |
| CLIENT_2_REDIRECT_URL | De toegestane URL waar de gebruiker naar teruggestuurd mag worden na login. |
| CLIENT_2_ORIGIN_URL | De toegestane basis-URL (Origin) voor CORS verzoeken van deze client. |
| CLUSTER_KEY | De naam van de keystore die wordt gebruikt voor communicatie tussen nodes in het cluster.  |
| ADMIN_SERVICE_HOST | De interne hostname of IP waar de admin-node op luistert (binnen K8s vaak de service-naam). |
| DATABASE_DRIVER | De Java class name van de JDBC driver (bijv. org.postgresql.Driver). |
| SHARED_DB_CONNECTION | JDBC connection string voor de gedeelde database (gebruikt voor tokens en issuers). |
| SHARED_DB_USERNAME | Gebruikersnaam voor de gedeelde database. |
| SHARED_DB_PASSWORD | Wachtwoord voor de gedeelde database. |
| SHARED_DB_DRIVER | De driver voor de gedeelde database (meestal gelijk aan DATABASE_DRIVER). |
| LDAP_HOSTNAME | Het adres van de OpenLDAP server |
| LDAP_PORT | De poort van de LDAP server. |
| LDAP_CLIENT_ID | De Bind DN die Curity gebruikt om in te loggen op LDAP. |
| LDAP_CLIENT_SECRET | Het wachtwoord van de LDAP admin/bind user. |
| LDAP_DEFAULT_ROOT | De basis van je LDAP-boom waar Curity moet zoeken. |
| GOOGLE_CLIENT_ID | OAuth2 Client ID verkregen uit de Google Cloud Console. |
| GOOGLE_CLIENT_SECRET | OAuth2 Client Secret van Google. |
| SMTP_USERNAME | Gebruikersnaam/API-token voor de SMTP server. |
| SMTP_PASSWORD | Wachtwoord/Secret voor de SMTP server. |
| SMTP_DEFAULT_SENDER | Het e-mailadres dat als afzender verschijnt. |
| SMTP_HOST | Hostnaam van de mailserver. |
| SMTP_PORT | SMTP poort |
| TWILIO_NUMBER | Het telefoonnummer dat Twilio gebruikt om berichten te versturen. |
| TWILIO_SID | Het SID van de Twilio client die gebruikt wordt. |
| TWILIO_TOKEN | Het Auth Token dat de Twilio client gebruikt voor connectie met de API. | 
| THEME_CSS_PROPERTIES | Extra CSS regels of variabelen om de look-and-feel van de loginpagina's aan te passen. |
| EMAIL_LOGO | Het pad naar het logo dat in e-mails gebruikt wordt. |
| LOGO | Het pad naar het logo dat in de browser getoond wordt. |
| LOGO_SOURCE | De bron-URL of Content Security Policy (CSP) instelling voor afbeeldingen (bijv. self). |

#### {{ local_secret_path }}/{dev|acc|prod}/curity.yml

Variabelen die moeten worden ingevuld in de XML-template.

```yaml
# -----------------------------------------------------------------------------
# Admin gebruikers
# -----------------------------------------------------------------------------
admin_users:
  - username: "<ADMIN_USERNAME>"   # Username voor de Curity admin user (bv. admin)
    password: "<ADMIN_PASSWORD>"   # Sterk wachtwoord of via Vault injectie

# -----------------------------------------------------------------------------
# Clients (OAuth/OpenID clients)
# -----------------------------------------------------------------------------
clients:
  - id: "<CLIENT_ID>"              # Unieke identifier van de client (bv. gateway)
    secret: "<CLIENT_SECRET>"      # Secret voor client authenticatie (Vault of env)
    type: "<CLIENT_TYPE>"          # Mogelijke waarden:
                                  # - introspection (machine-to-machine)
                                  # - code (authorization code flow)

  - id: "<WEB_CLIENT_ID>"          # bv. www
    secret: "<WEB_CLIENT_SECRET>"
    type: "code"

    redirect_uris:
      - "<CALLBACK_URL>"           # URL waar de gebruiker na login terugkomt

    allowed_origins:
      - "<FRONTEND_BASE_URL>"      # Frontend origin (CORS)

    scopes:
      - "<SCOPE_NAME>"             # bv. openid, profile, email

    allowed_authenticators:
      - "<AUTHENTICATOR_ID>"       # Moet matchen met authenticators hieronder

    validate_port: "<true|false>"  # Of redirect URI poort moet matchen

# -----------------------------------------------------------------------------
# Authenticators (login methodes)
# -----------------------------------------------------------------------------
authenticators:
  - id: "<AUTH_ID>"                # Unieke naam (bv. username_password)
    type: "<AUTH_TYPE>"            # Mogelijke types:
                                  # - html_form
                                  # - email
                                  # - sms
                                  # - totp
                                  # - passkey
                                  # - google

    enabled: <true|false>          # Of deze authenticator actief is

    account_manager: "<ACCOUNT_MANAGER_ID>"     # bv. ldap-accounts
    credential_manager: "<CREDENTIAL_MANAGER>"  # enkel nodig voor password flows

    email_provider: "<EMAIL_PROVIDER_ID>"       # vereist bij email flows
    throttler: "<THROTTLER_ID>"                 # rate limiting (optioneel)

    mfa_action: "<MFA_ACTION>"                  # bv. MFA
    mfa_second_factor: "<AUTH_ID>"              # tweede factor

    send_otp_as_code: <true|false>              # voor SMS/email
    allow_registration: <true|false>
    auto_login: <true|false>

    data_source: "<DATASOURCE_ID>"              # voor TOTP/passkey
    auto_redirect: <true|false>
    required_authenticator: "<AUTH_ID>"         # chaining van authenticators

# -----------------------------------------------------------------------------
# Scopes en claims (OpenID Connect)
# -----------------------------------------------------------------------------
scopes:
  - id: "<SCOPE_ID>"               # bv. openid, profile, email
    description: "<DESCRIPTION>"   # Beschrijving van de scope

    claims:
      - "<CLAIM_NAME>"             # bv. email, name, given_name

# -----------------------------------------------------------------------------
# Datasources (user storage / DB connecties)
# -----------------------------------------------------------------------------
datasources:
  - id: "<DATASOURCE_ID>"          # bv. LDAP
    type: "ldap"

    account_attributes:
      - "<ATTRIBUTE>"              # bv. uid, mail

    attributes:
      - "<ATTRIBUTE>"

    credential_attributes:
      - "<ATTRIBUTE>"

    account_id_attribute: "<ATTRIBUTE>"   # unieke identifier (bv. uid)
    username_attribute: "<ATTRIBUTE>"     # login veld

    password_encoding: "<ENCODING>"       # bv. ssha

  - id: "<JDBC_DATASOURCE_ID>"
    type: "jdbc"

    connection_string: "<DB_CONNECTION_STRING>"   # bv. jdbc:postgresql://host:5432/db
    driver: "<JDBC_DRIVER_CLASS>"                 # bv. org.postgresql.Driver
    username: "<DB_USERNAME>"
    password: "<DB_PASSWORD>"

# -----------------------------------------------------------------------------
# Providers (email & SMS)
# -----------------------------------------------------------------------------
providers:
  email_providers:
    - id: "<EMAIL_PROVIDER_ID>"    # bv. postmark
      type: "<EMAIL_TYPE>"         # meestal smtp
      tls: <true|false>

  sms_providers:
    - id: "<SMS_PROVIDER_ID>"      # bv. Twilio
      type: "twilio"
      enabled: <true|false>

# -----------------------------------------------------------------------------
# Throttlers (rate limiting)
# -----------------------------------------------------------------------------
throttlers:
  - id: "<THROTTLER_ID>"           # bv. postmark_throttler

    interval: <SECONDS>            # tijdsvenster (bv. 5)
    max_attempts: <NUMBER>         # max aantal pogingen (bv. 3)

    datasource: "<DATASOURCE_ID>"  # DB voor opslag (bv. shared_database)
```


#### users.json formaat
```json
{
  "users": [
    {
      "uid": "Username van de gebruiker",
      "firstName": "Voornaam van de gebruiker",
      "lastName": "Achternaam van de gebruiker",
      "email": "E-mail adress van de gebruiker",
      "telephoneNumber": "Telefoon nummer van de gebruiker in internationaal formaat",
      "password": "Wachtwoord van de gebruiker",
      "active_state": "True/False"
    }
  ]
}
```