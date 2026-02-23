#!/bin/bash

# --- CONFIGURATIE ---
ENVIRONMENTS=("dev" "acc" "prod")

echo "Starten van de Multi-Environment Secret Bootstrap..."

for ENV in "${ENVIRONMENTS[@]}"; do
    NAMESPACE="curity-$ENV"
    U_ENV=${ENV^^}

    echo "---------------------------------------------------"
    if ! kubectl get namespace "$NAMESPACE" &> /dev/null; then
        echo "⏭Namespace $NAMESPACE wordt aangemaakt."
        kubectl create namespace "$NAMESPACE"
        continue
    fi

    # Dynamische variabelen ophalen
    ENV_FILE_VAR="${U_ENV}_ENV_FILE_PATH"
    XML_FILE_VAR="${U_ENV}_XML_CONFIG_PATH"
    TLS_KEY_VAR="${U_ENV}_TLS_KEY_PATH"
    TLS_CRT_VAR="${U_ENV}_TLS_CRT_PATH"
    CLUSTER_PW_VAR="${U_ENV}_CLUSTER_PASSWORD"
    DB_PW_VAR="${U_ENV}_DB_PASSWORD"
    DB_USER_VAR="${U_ENV}_DB_USER"
    TAILSCALE_AUTH_KEY_VAR="${U_ENV}_TAILSCALE_AUTH_KEY"
    DB_SQL_VAR="${U_ENV}_DB_SQL_PATH"

    ENV_FILE="${!ENV_FILE_VAR}"
    XML_FILE="${!XML_FILE_VAR}"
    TLS_KEY="${!TLS_KEY_VAR}"
    TLS_CRT="${!TLS_CRT_VAR}"
    CLUSTER_PW="${!CLUSTER_PW_VAR}"
    DB_PW="${!DB_PW_VAR}"
    DB_USER="${!DB_USER_VAR}"
    TAILSCALE_AUTH_KEY="${!TAILSCALE_AUTH_KEY_VAR}"
    DB_SQL="${!DB_SQL_VAR}"

    # --- UITVOERING ---
    echo "Bootstrapping secrets voor: $ENV"

    if [ -f "$ENV_FILE" ]; then
        kubectl create secret generic curity-vars \
        --from-env-file="$ENV_FILE" \
        -n "$NAMESPACE" --dry-run=client -o yaml | kubectl apply -f -
        echo "Secret 'curity-vars' bijgewerkt."
    else
        echo "FOUT: Env file voor $ENV niet gevonden."
        continue 
    fi

    if [ -f "$XML_FILE" ]; then
        kubectl create secret generic curity-config-secret \
        --from-file=configuration.xml="$XML_FILE" \
        -n "$NAMESPACE" --dry-run=client -o yaml | kubectl apply -f -
        echo "Secret 'curity-config-secret' bijgewerkt."
    else
        echo "FOUT: XML config voor $ENV niet gevonden."
    fi
    if [ ! -z "$DB_USER" ] && [ ! -z "$DB_PW" ]; then
        kubectl create secret generic db-user-creds \
        --from-literal=username="$DB_USER" \
        --from-literal=password="$DB_PW" \
        -n "$NAMESPACE" --dry-run=client -o yaml | kubectl apply -f -
        echo "Secret 'db-user-creds' bijgewerkt."
    else
         echo "FOUT: Database user of password niet ingesteld."
    fi
    if [ -f "$DB_SQL" ]; then
        kubectl create configmap curity-db-init-sql \
        --from-file="$DB_SQL" \
        -n "$NAMESPACE" --dry-run=client -o yaml | kubectl apply -f -
        echo "ConfigMap 'curity-db-init-sql' bijgewerkt."
    fi
    if [ ! -z "$TAILSCALE_AUTH_KEY" ]; then
        kubectl create secret generic tailscale-auth \
        --from-literal=TS_AUTHKEY="$TAILSCALE_AUTH_KEY" \
        -n "$NAMESPACE" --dry-run=client -o yaml | kubectl apply -f -
        echo "Secret 'tailscale-auth' bijgewerkt."
    fi
    if [ ! -z "$CLUSTER_PW" ]; then
        kubectl create secret generic curity-cluster-secret \
        --from-literal=PASSWORD="$CLUSTER_PW" \
        -n "$NAMESPACE" --dry-run=client -o yaml | kubectl apply -f -
        echo "Secret 'curity-cluster-secret' bijgewerkt."
    else
        echo "FOUT: Geen CLUSTER_PASSWORD voor $ENV opgegeven."
    fi

    if [ -f "$TLS_KEY" ] && [ -f "$TLS_CRT" ]; then
        kubectl create secret tls curity-tls-secret \
        --key "$TLS_KEY" \
        --cert "$TLS_CRT" \
        -n "$NAMESPACE" --dry-run=client -o yaml | kubectl apply -f -
        echo "Secret 'curity-tls-secret' bijgewerkt."
    else
        echo "FOUT: TLS bestanden voor $ENV niet gevonden."
    fi

    echo "Alle beschikbare secrets gesynct naar: $NAMESPACE"
done

echo "---------------------------------------------------"
echo "Bootstrap proces voltooid."