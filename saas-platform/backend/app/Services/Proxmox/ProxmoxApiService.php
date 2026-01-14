<?php

namespace App\Services\Proxmox;

use Illuminate\Support\Facades\Http;
use App\Models\Tenant\ProxmoxCluster;

class ProxmoxApiService
{
    public function getResources(ProxmoxCluster $cluster)
    {
        $response = $this->request($cluster, 'get', '/cluster/resources');
        return $response->json('data') ?? [];
    }

    public function getNodes(ProxmoxCluster $cluster)
    {
        $response = $this->request($cluster, 'get', '/nodes');
        return $response->json('data') ?? [];
    }

    public function getNodeStatus(ProxmoxCluster $cluster, string $node)
    {
        $response = $this->request($cluster, 'get', "/nodes/{$node}/status");
        return $response->json('data') ?? [];
    }

    public function getNodeResources(ProxmoxCluster $cluster, string $node)
    {
        // Fetches both qemu and lxc resources for a specific node
        $qemu = $this->request($cluster, 'get', "/nodes/{$node}/qemu")->json('data') ?? [];
        $lxc = $this->request($cluster, 'get', "/nodes/{$node}/lxc")->json('data') ?? [];
        
        return [
            'qemu' => $qemu,
            'lxc' => $lxc
        ];
    }

    public function getDatastores(ProxmoxCluster $cluster)
    {
        if ($cluster->type !== 'pbs') {
            return [];
        }
        // PBS specific endpoint for datastores
        $response = $this->request($cluster, 'get', '/admin/datastore');
        return $response->json('data') ?? [];
    }

    public function getPmgStatistics(ProxmoxCluster $cluster)
    {
        if ($cluster->type !== 'pmg') {
            return [];
        }
        // PMG specific endpoint for statistics
        $response = $this->request($cluster, 'get', '/statistics/recent');
        return $response->json('data') ?? [];
    }

    public function getSdnZones(ProxmoxCluster $cluster)
    {
        $response = $this->request($cluster, 'get', '/cluster/sdn/zones');
        return $response->json('data') ?? [];
    }

    public function getSdnVnets(ProxmoxCluster $cluster)
    {
        $response = $this->request($cluster, 'get', '/cluster/sdn/vnets');
        return $response->json('data') ?? [];
    }

    public function getSdnSubnets(ProxmoxCluster $cluster, string $vnet)
    {
        $response = $this->request($cluster, 'get', "/cluster/sdn/vnets/{$vnet}/subnets");
        return $response->json('data') ?? [];
    }

    public function getSdnFirewallRules(ProxmoxCluster $cluster)
    {
        $response = $this->request($cluster, 'get', '/cluster/firewall/rules');
        return $response->json('data') ?? [];
    }

    public function createSdnFirewallRule(ProxmoxCluster $cluster, array $data)
    {
        $response = $this->request($cluster, 'post', '/cluster/firewall/rules', $data);
        if (!$response->successful()) {
            throw new \Exception("Proxmox API Error: " . ($response->json('errors') ?? $response->body()));
        }
        return $response->json('data');
    }

    public function updateSdnFirewallRule(ProxmoxCluster $cluster, int $pos, array $data)
    {
        $response = $this->request($cluster, 'put', "/cluster/firewall/rules/{$pos}", $data);
        if (!$response->successful()) {
            throw new \Exception("Proxmox API Error: " . ($response->json('errors') ?? $response->body()));
        }
        return $response->json('data');
    }

    public function deleteSdnFirewallRule(ProxmoxCluster $cluster, int $pos)
    {
        $response = $this->request($cluster, 'delete', "/cluster/firewall/rules/{$pos}");
        if (!$response->successful()) {
            throw new \Exception("Proxmox API Error: " . ($response->json('errors') ?? $response->body()));
        }
        return $response->json('data');
    }

    public function getSdnStatus(ProxmoxCluster $cluster)
    {
        $response = $this->request($cluster, 'get', '/cluster/sdn/status');
        return $response->json('data') ?? [];
    }

    public function createSdnZone(ProxmoxCluster $cluster, array $data)
    {
        $response = $this->request($cluster, 'post', '/cluster/sdn/zones', $data);
        if (!$response->successful()) {
            throw new \Exception("Proxmox API Error: " . ($response->json('errors') ?? $response->body()));
        }
        return $response->json('data');
    }

    public function createSdnVnet(ProxmoxCluster $cluster, array $data)
    {
        $response = $this->request($cluster, 'post', '/cluster/sdn/vnets', $data);
        if (!$response->successful()) {
            throw new \Exception("Proxmox API Error: " . ($response->json('errors') ?? $response->body()));
        }
        return $response->json('data');
    }

    public function createSdnSubnet(ProxmoxCluster $cluster, string $vnet, array $data)
    {
        $response = $this->request($cluster, 'post', "/cluster/sdn/vnets/{$vnet}/subnets", $data);
        if (!$response->successful()) {
            throw new \Exception("Proxmox API Error: " . ($response->json('errors') ?? $response->body()));
        }
        return $response->json('data');
    }

    public function deleteSdnZone(ProxmoxCluster $cluster, string $zone)
    {
        $response = $this->request($cluster, 'delete', "/cluster/sdn/zones/{$zone}");
        if (!$response->successful()) {
            throw new \Exception("Proxmox API Error: " . ($response->json('errors') ?? $response->body()));
        }
        return $response->json('data');
    }

    public function deleteSdnVnet(ProxmoxCluster $cluster, string $vnet)
    {
        $response = $this->request($cluster, 'delete', "/cluster/sdn/vnets/{$vnet}");
        if (!$response->successful()) {
            throw new \Exception("Proxmox API Error: " . ($response->json('errors') ?? $response->body()));
        }
        return $response->json('data');
    }

    public function deleteSdnSubnet(ProxmoxCluster $cluster, string $vnet, string $subnet)
    {
        $response = $this->request($cluster, 'delete', "/cluster/sdn/vnets/{$vnet}/subnets/{$subnet}");
        if (!$response->successful()) {
            throw new \Exception("Proxmox API Error: " . ($response->json('errors') ?? $response->body()));
        }
        return $response->json('data');
    }

    public function applySdn(ProxmoxCluster $cluster)
    {
        $response = $this->request($cluster, 'put', '/cluster/sdn');
        if (!$response->successful()) {
            throw new \Exception("Proxmox API Error: " . ($response->json('errors') ?? $response->body()));
        }
        return $response->json('data');
    }

    public function getPbsJobs(ProxmoxCluster $cluster)
    {
        if ($cluster->type !== 'pbs') return [];
        $response = $this->request($cluster, 'get', '/admin/jobstate');
        return $response->json('data') ?? [];
    }

    public function getPmgAccounts(ProxmoxCluster $cluster)
    {
        if ($cluster->type !== 'pmg') return [];
        $response = $this->request($cluster, 'get', '/access/users');
        return $response->json('data') ?? [];
    }

    public function getPmgRules(ProxmoxCluster $cluster)
    {
        if ($cluster->type !== 'pmg') return [];
        // Combined whitelist/blacklist mock logic
        $response = $this->request($cluster, 'get', '/config/rules');
        return $response->json('data') ?? [];
    }

    public function executeResourceAction(ProxmoxCluster $cluster, string $node, string $type, int $vmid, string $action)
    {
        // Proxmox resource action endpoint: /nodes/{node}/{type}/{vmid}/status/{action}
        // Type is usually 'qemu' for VMs or 'lxc' for containers
        $endpoint = "/nodes/{$node}/{$type}/{$vmid}/status/{$action}";
        
        $response = $this->request($cluster, 'post', $endpoint);
        
        if (!$response->successful()) {
            throw new \Exception("Proxmox API Error: " . ($response->json('errors') ?? $response->body()));
        }

        return $response->json('data');
    }

    public function migrateResource(ProxmoxCluster $cluster, string $node, string $type, int $vmid, string $targetNode)
    {
        $endpoint = "/nodes/{$node}/{$type}/{$vmid}/migrate";
        
        $response = $this->request($cluster, 'post', $endpoint, [
            'target' => $targetNode,
            'online' => 1, // Live migration
        ]);

        if (!$response->successful()) {
            throw new \Exception("Proxmox API Error: " . ($response->json('errors') ?? $response->body()));
        }

        return $response->json('data');
    }

    protected function request(ProxmoxCluster $cluster, string $method, string $endpoint, array $data = [])
    {
        // Development Mock for .local domains
        if (str_ends_with($cluster->hostname, '.local')) {
            return $this->mockResponse($endpoint, $method, $data);
        }

        $url = "https://{$cluster->hostname}:{$cluster->port}/api2/json" . $endpoint;

        $headers = [
            'Authorization' => "PVEAPIToken={$cluster->username}!{$cluster->api_token}={$cluster->api_secret}",
            'Accept' => 'application/json',
        ];

        $request = Http::withHeaders($headers)
            ->withoutVerifying()
            ->timeout(10);

        if ($method === 'post') {
            return $request->asForm()->post($url, $data);
        }

        return $request->send($method, $url);
    }

    protected function mockResponse(string $endpoint, string $method, array $data = [])
    {
        $mockData = [];

        if (str_contains($endpoint, '/cluster/resources')) {
            $mockData = [
                ['vmid' => 100, 'name' => 'web-server-01', 'type' => 'qemu', 'node' => 'pve-01', 'status' => 'running', 'cpu' => 0.05, 'mem' => 2147483648, 'maxmem' => 4294967296, 'disk' => 21474836480, 'maxdisk' => 53687091200],
                ['vmid' => 101, 'name' => 'db-primary', 'type' => 'qemu', 'node' => 'pve-01', 'status' => 'running', 'cpu' => 0.12, 'mem' => 6442450944, 'maxmem' => 8589934592, 'disk' => 85899345920, 'maxdisk' => 214748364800],
            ];
        } elseif (str_contains($endpoint, '/nodes') && str_contains($endpoint, '/status')) {
            $mockData = [
                'kversion' => 'Linux 6.2.16-3-pve #1 SMP PREEMPT_DYNAMIC PMX 6.2.16-3',
                'pveversion' => '8.0.3',
                'cpuinfo' => [
                    'model' => 'Intel(R) Xeon(R) Gold 6130 CPU @ 2.10GHz',
                    'sockets' => 2,
                    'cores' => 32,
                ],
                'loadavg' => ['0.45', '0.32', '0.28'],
                'swap' => [
                    'total' => 8589934592,
                    'used' => 1073741824,
                    'free' => 7516192768,
                ]
            ];
        } elseif (str_contains($endpoint, '/nodes') && !str_contains($endpoint, '/status')) {
            $mockData = [
                ['node' => 'pve-01', 'status' => 'online', 'uptime' => 432000, 'cpu' => 0.15, 'mem' => 8589934592, 'maxmem' => 34359738368, 'disk' => 107374182400, 'maxdisk' => 536870912000],
            ];
        } elseif (str_contains($endpoint, '/cluster/sdn/zones')) {
            $mockData = [
                ['zone' => 'local-vxlan', 'type' => 'vxlan', 'status' => 'active'],
            ];
        } elseif (str_contains($endpoint, '/cluster/sdn/vnets')) {
            $mockData = [
                ['vnet' => 'vnet10', 'zone' => 'local-vxlan', 'tag' => 10, 'alias' => 'Production Net'],
            ];
        } elseif (str_contains($endpoint, '/subnets')) {
            $mockData = [
                ['cidr' => '10.0.10.0/24', 'gateway' => '10.0.10.1', 'snat' => 1],
            ];
        } elseif (str_contains($endpoint, '/admin/datastore')) {
            $mockData = [
                ['store' => 'backup-01', 'total' => 1099511627776, 'used' => 549755813888, 'avail' => 549755813888, 'status' => 'up'],
            ];
        } elseif (str_contains($endpoint, '/statistics/recent')) {
            $mockData = [
                ['time' => now()->subHours(1)->timestamp, 'count_in' => 150, 'count_out' => 45, 'count_spam' => 12, 'count_virus' => 1],
                ['time' => now()->timestamp, 'count_in' => 200, 'count_out' => 60, 'count_spam' => 15, 'count_virus' => 0],
            ];
        } elseif (str_contains($endpoint, '/cluster/firewall/rules')) {
            $mockData = [
                ['pos' => 0, 'enable' => 1, 'action' => 'ACCEPT', 'type' => 'in', 'source' => '10.0.0.0/24', 'proto' => 'tcp', 'dport' => '80', 'comment' => 'Allow HTTP'],
                ['pos' => 1, 'enable' => 1, 'action' => 'DROP', 'type' => 'in', 'source' => 'any', 'proto' => 'tcp', 'dport' => '22', 'comment' => 'Block SSH'],
            ];
        } elseif (str_contains($endpoint, '/admin/jobstate')) {
            $mockData = [
                ['id' => 'backup-01', 'type' => 'backup', 'schedule' => 'daily', 'last_run' => now()->subDay()->timestamp, 'next_run' => now()->addDay()->timestamp, 'status' => 'OK'],
            ];
        } elseif (str_contains($endpoint, '/access/users')) {
            $mockData = [
                ['userid' => 'admin@pmg', 'email' => 'admin@proxmon.local', 'role' => 'admin', 'enable' => 1],
                ['userid' => 'user01@pmg', 'email' => 'user01@proxmon.local', 'role' => 'user', 'enable' => 1],
            ];
        } elseif (str_contains($endpoint, '/config/rules')) {
            $mockData = [
                ['name' => 'Whitelist Google', 'type' => 'whitelist', 'from' => 'google.com', 'active' => 1],
                ['name' => 'Blacklist Spam', 'type' => 'blacklist', 'from' => 'spammer.com', 'active' => 1],
            ];
        }

        return new class($mockData) {
            private $data;
            public function __construct($data) { $this->data = $data; }
            public function json($key = null) { return $key === 'data' ? $this->data : ['data' => $this->data]; }
            public function successful() { return true; }
        };
    }
}
