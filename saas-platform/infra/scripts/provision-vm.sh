#!/bin/bash
# Provisioning script for Hetzner VM

set -e

echo "Updating system..."
apt-get update && apt-get upgrade -y

echo "Installing dependencies..."
apt-get install -y apt-transport-https ca-certificates curl software-properties-common gnupg nginx git

echo "Installing Docker..."
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | apt-key add -
add-apt-repository "deb [arch=amd64] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable"
apt-get update
apt-get install -y docker-ce docker-ce-cli containerd.io docker-compose-plugin

echo "Configuring Nginx..."
rm /etc/nginx/sites-enabled/default || true
# Copy configs from repo to /etc/nginx/

echo "Setting up Firewall (UFW)..."
ufw allow OpenSSH
ufw allow 'Nginx Full'
ufw --force enable

echo "Provisioning complete!"
