#!/bin/bash

# --- CONFIGURATIE ---
ENVIRONMENTS=("dev" "acc" "prod")
NAMESPACE="curity" 

echo "IP-adressen ophalen uit Kubernetes..."

get_ip() {
    local env=$1
    local ip=$(kubectl get ingress -n "$NAMESPACE" -l "app.kubernetes.io/instance=curity-$env" -o jsonpath='{.items[0].status.loadBalancer.ingress[0].ip}' 2>/dev/null)
    if [ -z "$ip" ] || [ "$ip" == "localhost" ]; then
        ip="127.0.0.1"
    fi
    echo "$ip"
}

# --- UITVOERING ---

for ENV in "${ENVIRONMENTS[@]}"; do
    IP=$(get_ip "$ENV")
    
    if [ -z "$IP" ]; then
        echo "Kon geen IP vinden voor $ENV. Staat 'minikube tunnel' aan en is de Ingress gesynct?"
        continue
    fi
    DOMAINS=("$ENV.curity.local" "$ENV.curity-admin.local")

    for DOMAIN in "${DOMAINS[@]}"; do
        echo "Koppelen: $DOMAIN -> $IP"
        sudo sed -i.bak "/$DOMAIN/d" /etc/hosts 2>/dev/null || sudo sed -i "/$DOMAIN/d" /etc/hosts
        echo "$IP $DOMAIN" | sudo tee -a /etc/hosts > /dev/null
    done
done

sudo rm /etc/hosts.bak 2>/dev/null

echo "/etc/hosts is bijgewerkt voor alle omgevingen."