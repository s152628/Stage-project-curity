#!/usr/bin/env python3
"""
Google Sub Hash Service
-----------------------
Ontvangt een Google 'sub' claim van Curity via een webhook,
hasht deze met Argon2id + pepper + salt en schrijft het resultaat
naar OpenLDAP als googleId attribuut.

Omgevingsvariabelen (via Vault Agent injectie):
  LDAP_ADMIN_DN       - bijv. cn=admin,dc=camazotz,dc=me
  LDAP_ADMIN_PASSWORD - LDAP admin wachtwoord
  LDAP_HOST           - bijv. openldap-service
  LDAP_PORT           - bijv. 389
  LDAP_BASE_DN        - bijv. dc=camazotz,dc=me
  GOOGLE_HASH_PEPPER  - geheime pepper, enkel in Vault, nooit in LDAP
"""

import os
import secrets
import base64
import logging
from flask import Flask, request, jsonify
import ldap
import ldap.modlist as modlist
from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)

# Argon2id parameters — bewust zwaarder dan wachtwoordhashing
# omdat dit eenmalig per registratie gebeurt, niet bij elke login
ph = PasswordHasher(
    time_cost=3,        # aantal iteraties
    memory_cost=65536,  # 64MB geheugen
    parallelism=4,      # threads
    hash_len=32,        # output lengte in bytes
    salt_len=16         # salt lengte in bytes (argon2 genereert dit intern)
)

PEPPER = os.environ["GOOGLE_HASH_PEPPER"]
LDAP_HOST = os.environ["LDAP_HOST"]
LDAP_PORT = int(os.environ.get("LDAP_PORT", "389"))
LDAP_ADMIN_DN = os.environ["LDAP_ADMIN_DN"]
LDAP_ADMIN_PASSWORD = os.environ["LDAP_ADMIN_PASSWORD"]
LDAP_BASE_DN = os.environ["LDAP_BASE_DN"]


def get_ldap_connection():
    """Maak een verbinding met OpenLDAP."""
    conn = ldap.initialize(f"ldap://{LDAP_HOST}:{LDAP_PORT}")
    conn.simple_bind_s(LDAP_ADMIN_DN, LDAP_ADMIN_PASSWORD)
    return conn


def hash_google_sub(sub: str) -> tuple[str, str]:
    """
    Hash de Google sub met Argon2id.
    De pepper wordt aan de sub toegevoegd vóór het hashen.
    De salt wordt intern door argon2 gegenereerd en zit in de hash string.
    We slaan een extra externe salt op voor extra bescherming bij databaselek.

    Returns:
        (argon2_hash, external_salt)
    """
    external_salt = secrets.token_hex(32)  # 256-bit externe salt
    peppered_sub = f"{sub}{PEPPER}{external_salt}"
    argon2_hash = ph.hash(peppered_sub)
    return argon2_hash, external_salt


def verify_google_sub(sub: str, stored_hash: str, stored_salt: str) -> bool:
    """Verifieer of een sub overeenkomt met de opgeslagen hash."""
    peppered_sub = f"{sub}{PEPPER}{stored_salt}"
    try:
        return ph.verify(stored_hash, peppered_sub)
    except VerifyMismatchError:
        return False


def find_user_by_email(conn, email: str) -> tuple[str | None, dict | None]:
    """Zoek een gebruiker op via e-mailadres."""
    search_filter = f"(mail={ldap.filter.escape_filter_chars(email)})"
    results = conn.search_s(
        f"ou=people,{LDAP_BASE_DN}",
        ldap.SCOPE_ONELEVEL,
        search_filter,
        ["uid", "googleId", "googleIdSalt", "objectClass"]
    )
    if not results:
        return None, None
    dn, attrs = results[0]
    return dn, attrs


def find_user_by_google_hash(conn, sub: str) -> tuple[str | None, dict | None]:
    """
    Zoek een gebruiker op via zijn Google sub.
    Omdat we niet direct kunnen filteren op de hash,
    halen we alle gebruikers op met een googleId en verifiëren we.
    In grote directories gebruik je een index op googleId.
    """
    search_filter = "(googleId=*)"
    results = conn.search_s(
        f"ou=people,{LDAP_BASE_DN}",
        ldap.SCOPE_ONELEVEL,
        search_filter,
        ["uid", "googleId", "googleIdSalt"]
    )
    for dn, attrs in results:
        stored_hash = attrs.get("googleId", [b""])[0].decode()
        stored_salt = attrs.get("googleIdSalt", [b""])[0].decode()
        if stored_hash and stored_salt and verify_google_sub(sub, stored_hash, stored_salt):
            return dn, attrs
    return None, None


@app.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "ok"})


@app.route("/link-google", methods=["POST"])
def link_google():
    """
    Koppel een Google account aan een bestaand LDAP-account.
    Verwacht JSON body:
    {
        "sub": "Google sub claim",
        "email": "gebruiker@voorbeeld.com"
    }
    Curity roept dit aan via een custom authenticatie action na Google login.
    """
    data = request.get_json()
    if not data or "sub" not in data or "email" not in data:
        return jsonify({"error": "sub en email zijn verplicht"}), 400

    sub = data["sub"]
    email = data["email"]

    try:
        conn = get_ldap_connection()

        # Zoek gebruiker op via email
        dn, attrs = find_user_by_email(conn, email)
        if not dn:
            logger.warning(f"Geen LDAP gebruiker gevonden voor email: {email}")
            return jsonify({"error": "Gebruiker niet gevonden in LDAP"}), 404

        # Controleer of er al een Google ID gekoppeld is
        existing_hash = attrs.get("googleId")
        if existing_hash:
            # Verifieer of het dezelfde Google sub is
            existing_salt = attrs.get("googleIdSalt", [b""])[0].decode()
            if verify_google_sub(sub, existing_hash[0].decode(), existing_salt):
                logger.info(f"Google account al correct gekoppeld voor {dn}")
                return jsonify({"status": "already_linked", "dn": dn}), 200
            else:
                logger.warning(f"Poging tot koppelen van ander Google account voor {dn}")
                return jsonify({"error": "Ander Google account al gekoppeld"}), 409

        # Hash de sub en sla op in LDAP
        argon2_hash, external_salt = hash_google_sub(sub)

        # Voeg googleIdentity auxiliary objectclass toe indien nodig
        current_classes = [c.decode() for c in attrs.get("objectClass", [])]
        mod_list = []

        if "googleIdentity" not in current_classes:
            mod_list.append((ldap.MOD_ADD, "objectClass", [b"googleIdentity"]))

        mod_list.extend([
            (ldap.MOD_ADD, "googleId", [argon2_hash.encode()]),
            (ldap.MOD_ADD, "googleIdSalt", [external_salt.encode()])
        ])

        conn.modify_s(dn, mod_list)
        logger.info(f"Google account succesvol gekoppeld aan {dn}")
        return jsonify({"status": "linked", "dn": dn}), 200

    except ldap.LDAPError as e:
        logger.error(f"LDAP fout: {e}")
        return jsonify({"error": "LDAP fout"}), 500


@app.route("/verify-google", methods=["POST"])
def verify_google():
    """
    Verifieer of een Google sub gekoppeld is aan een LDAP-account.
    Verwacht JSON body:
    {
        "sub": "Google sub claim"
    }
    Curity roept dit aan bij elke Google login om de LDAP-koppeling te verifiëren.
    """
    data = request.get_json()
    if not data or "sub" not in data:
        return jsonify({"error": "sub is verplicht"}), 400

    sub = data["sub"]

    try:
        conn = get_ldap_connection()
        dn, attrs = find_user_by_google_hash(conn, sub)

        if not dn:
            logger.info("Geen LDAP gebruiker gevonden voor deze Google sub")
            return jsonify({"status": "not_found"}), 404

        uid = attrs.get("uid", [b""])[0].decode()
        logger.info(f"Google sub geverifieerd voor gebruiker: {uid}")
        return jsonify({"status": "verified", "uid": uid, "dn": dn}), 200

    except ldap.LDAPError as e:
        logger.error(f"LDAP fout: {e}")
        return jsonify({"error": "LDAP fout"}), 500


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
