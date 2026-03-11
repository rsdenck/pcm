# PCM Development Laboratory

## Proxmox Cluster Configuration

This document contains the configuration details for the development Proxmox cluster used for PCM engineering and testing.

### Cluster Overview

**Cluster Name:** PROXMON  
**Purpose:** Development & Testing Environment  
**Nodes:** 3 (High Availability)

---

## Node Configuration

### PVE-01 (Primary Node)

```yaml
Hostname: proxmon01.local
IP Address: 192.168.130.20
Management URL: https://192.168.130.20:8006

Credentials:
  User: root
  Password: 2020Tra##

API Configuration:
  Token Name: root@pam!pvetoken
  Token UUID: b8e4d593-9fe8-4c10-ae15-881c9873cb63
  Full Token: root@pam!pvetoken=b8e4d593-9fe8-4c10-ae15-881c9873cb63
```

### PVE-02 (Secondary Node)

```yaml
Hostname: proxmon02.local
IP Address: 192.168.130.21
Management URL: https://192.168.130.21:8006

Credentials:
  User: root
  Password: 2020Tra##

API Configuration:
  Token Name: root@pam!pvetoken
  Token UUID: [To be configured]
```

### PVE-03 (Tertiary Node)

```yaml
Hostname: proxmon03.local
IP Address: 192.168.130.22
Management URL: https://192.168.130.22:8006

Credentials:
  User: root
  Password: 2020Tra##

API Configuration:
  Token Name: root@pam!pvetoken
  Token UUID: [To be configured]
```

---

## Network Configuration

### Management Network

```
Network: 192.168.130.0/24
Gateway: 192.168.130.1
DNS: 192.168.130.1

Node IPs:
  - PVE-01: 192.168.130.20
  - PVE-02: 192.168.130.21
  - PVE-03: 192.168.130.22
```

---

## PCM Integration

### Adding Cluster to PCM

#### Via API

```bash
curl -X POST http://localhost:8000/api/v1/clusters \
  -H "Content-Type: application/json" \
  -d '{
    "name": "PROXMON Development Cluster",
    "hostname": "192.168.130.20",
    "port": 8006,
    "cluster_type": "pve",
    "api_token_id": "root@pam!pvetoken",
    "api_token_secret": "b8e4d593-9fe8-4c10-ae15-881c9873cb63",
    "verify_ssl": false,
    "description": "Development and testing cluster for PCM",
    "tenant_id": "your-tenant-id"
  }'
```

#### Via Python SDK

```python
from pcm.sdk.proxmox import ProxmoxClient

client = ProxmoxClient(
    host="192.168.130.20",
    port=8006,
    token_id="root@pam!pvetoken",
    token_secret="b8e4d593-9fe8-4c10-ae15-881c9873cb63",
    verify_ssl=False
)

# Test connection
version = await client.get_version()
print(f"Connected to Proxmox {version}")

# Get cluster status
status = await client.get_cluster_status()
print(f"Cluster status: {status}")
```

---

## Development Workflow

### 1. Initial Setup

```bash
# Configure cluster in PCM
python scripts/add_lab_cluster.py

# Verify connectivity
python scripts/test_cluster_connection.py
```

### 2. Testing Scenarios

- VM provisioning
- Container deployment
- Storage operations
- Network configuration
- Backup/restore operations
- High availability testing
- Failover scenarios

### 3. Monitoring

```bash
# Start monitoring workers
start-workers.bat

# View cluster metrics
curl http://localhost:8000/api/v1/clusters/{cluster_id}/metrics
```

---

## Security Notes

**IMPORTANT:** This is a development environment. Credentials are stored here for convenience.

For production deployments:
- Use secure credential management (HashiCorp Vault, etc.)
- Enable SSL/TLS verification
- Implement proper RBAC
- Use dedicated service accounts
- Rotate API tokens regularly
- Enable audit logging

---

## Cluster Maintenance

### Backup Configuration

```bash
# Backup cluster configuration
pvecm backup /backup/cluster-config-$(date +%Y%m%d).tar.gz

# Backup VMs
vzdump --all --compress zstd --storage local
```

### Updates

```bash
# Update Proxmox packages
apt update && apt dist-upgrade

# Reboot nodes one at a time
# Ensure HA is working before rebooting next node
```

---

## Troubleshooting

### Connection Issues

```bash
# Test network connectivity
ping 192.168.130.20

# Test API endpoint
curl -k https://192.168.130.20:8006/api2/json/version

# Verify token
curl -k -H "Authorization: PVEAPIToken=root@pam!pvetoken=b8e4d593-9fe8-4c10-ae15-881c9873cb63" \
  https://192.168.130.20:8006/api2/json/cluster/status
```

### Common Issues

1. **SSL Certificate Errors**
   - Solution: Set `verify_ssl=false` in development

2. **Token Authentication Failed**
   - Verify token is created in Proxmox
   - Check token permissions
   - Ensure token hasn't expired

3. **Cluster Not Responding**
   - Check node status in Proxmox UI
   - Verify quorum status
   - Check network connectivity

---

## Resources

- [Proxmox VE API Documentation](https://pve.proxmox.com/pve-docs/api-viewer/)
- [Proxmox VE Administration Guide](https://pve.proxmox.com/pve-docs/pve-admin-guide.html)
- [PCM API Documentation](http://localhost:8000/docs)

---

**Last Updated:** 2024-01-14  
**Maintained By:** PCM Development Team
