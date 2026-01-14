<?php

namespace App\Jobs;

use App\Models\Tenant\ProxmoxCluster;
use App\Models\Tenant\PveNode;
use App\Models\Tenant\PveResource;
use App\Models\Tenant\PbsDatastore;
use App\Models\Tenant\PmgStat;
use App\Models\Tenant\SdnZone;
use App\Models\Tenant\SdnVnet;
use App\Models\Tenant\SdnSubnet;
use App\Models\Tenant\PbsJob;
use App\Models\Tenant\PmgAccount;
use App\Models\Tenant\PmgRule;
use App\Models\Tenant\SdnFirewallRule;
use App\Services\DatabaseSwitcher;
use App\Services\Proxmox\ProxmoxApiService;
use Illuminate\Bus\Queueable;
use Illuminate\Contracts\Queue\ShouldQueue;
use Illuminate\Foundation\Bus\Dispatchable;

use Illuminate\Queue\InteractsWithQueue;
use Illuminate\Queue\SerializesModels;
use Illuminate\Support\Facades\Log;

class SyncProxmoxDataJob implements ShouldQueue
{
    use Dispatchable, InteractsWithQueue, Queueable, SerializesModels;

    protected $tenantDb;
    protected $clusterId;

    public function __construct(string $tenantDb, string $clusterId)
    {
        $this->tenantDb = $tenantDb;
        $this->clusterId = $clusterId;
    }

    public function handle(ProxmoxApiService $apiService, DatabaseSwitcher $dbSwitcher)
    {
        Log::info("Starting sync for tenant {$this->tenantDb} and cluster {$this->clusterId}");
        // Switch to tenant database
        $dbSwitcher->setTenantConnection($this->tenantDb);

        $cluster = ProxmoxCluster::find($this->clusterId);
        if (!$cluster) {
            Log::warning("Cluster {$this->clusterId} not found in {$this->tenantDb}");
            return;
        }
        
        if (!$cluster->is_active) {
            Log::info("Cluster {$cluster->name} is not active, skipping.");
            return;
        }

        try {
            Log::info("Syncing cluster type: {$cluster->type}");
            switch ($cluster->type) {
                case 'pve':
                    $this->syncPve($cluster, $apiService);
                    $this->syncSdn($cluster, $apiService);
                    break;
                case 'pbs':
                    $this->syncPbs($cluster, $apiService);
                    break;
                case 'pmg':
                    $this->syncPmg($cluster, $apiService);
                    break;
            }

            $cluster->update(['last_sync_at' => now()]);

        } catch (\Exception $e) {
            Log::error("Failed to sync Proxmox cluster {$cluster->id}: " . $e->getMessage());
        }
    }

    protected function syncPve(ProxmoxCluster $cluster, ProxmoxApiService $apiService)
    {
        // Sync Nodes
        $nodes = $apiService->getNodes($cluster);
        foreach ($nodes as $nodeData) {
            // Fetch detailed status for each node
            $status = $apiService->getNodeStatus($cluster, $nodeData['node']);
            
            PveNode::updateOrCreate(
                ['cluster_id' => $cluster->id, 'node_name' => $nodeData['node']],
                [
                    'status' => $nodeData['status'] ?? 'unknown',
                    'uptime' => $nodeData['uptime'] ?? 0,
                    'cpu_usage' => ($nodeData['cpu'] ?? 0) * 100,
                    'memory_used' => $nodeData['mem'] ?? 0,
                    'memory_total' => $nodeData['maxmem'] ?? 0,
                    'disk_used' => $nodeData['disk'] ?? 0,
                    'disk_total' => $nodeData['maxdisk'] ?? 0,
                    'kernel_version' => $status['kversion'] ?? null,
                    'pve_version' => $status['pveversion'] ?? null,
                    'cpu_model' => $status['cpuinfo']['model'] ?? null,
                    'cpu_sockets' => $status['cpuinfo']['sockets'] ?? null,
                    'cpu_cores' => $status['cpuinfo']['cores'] ?? null,
                    'loadavg' => isset($status['loadavg']) ? implode(', ', $status['loadavg']) : null,
                    'swap_total' => $status['swap']['total'] ?? null,
                    'swap_used' => $status['swap']['used'] ?? null,
                ]
            );
        }

        // Sync Resources (VMs/Containers)
        $resources = $apiService->getResources($cluster);
        foreach ($resources as $resData) {
            if (!isset($resData['vmid'])) continue;
            if (!in_array($resData['type'], ['qemu', 'lxc'])) continue;

            PveResource::updateOrCreate(
                ['cluster_id' => $cluster->id, 'vmid' => $resData['vmid']],
                [
                    'name' => $resData['name'] ?? 'unknown',
                    'type' => $resData['type'],
                    'node' => $resData['node'],
                    'status' => $resData['status'] ?? 'unknown',
                    'cpu_usage' => ($resData['cpu'] ?? 0) * 100,
                    'memory_used' => $resData['mem'] ?? 0,
                    'memory_total' => $resData['maxmem'] ?? 0,
                    'disk_used' => $resData['disk'] ?? 0,
                    'disk_total' => $resData['maxdisk'] ?? 0,
                ]
            );
        }
    }

    protected function syncSdn(ProxmoxCluster $cluster, ProxmoxApiService $apiService)
    {
        // Sync SDN Zones
        $zones = $apiService->getSdnZones($cluster);
        $sdnStatus = $apiService->getSdnStatus($cluster);

        foreach ($zones as $zoneData) {
            $status = collect($sdnStatus)->firstWhere('zone', $zoneData['zone']);
            
            SdnZone::updateOrCreate(
                ['cluster_id' => $cluster->id, 'zone_name' => $zoneData['zone']],
                [
                    'type' => $zoneData['type'] ?? 'unknown',
                    'status' => $status['status'] ?? 'unknown',
                ]
            );
        }

        $vnets = $apiService->getSdnVnets($cluster);
        foreach ($vnets as $vnetData) {
            $zone = SdnZone::where('cluster_id', $cluster->id)->where('zone_name', $vnetData['zone'])->first();
            if (!$zone) continue;

            $vnet = SdnVnet::updateOrCreate(
                ['cluster_id' => $cluster->id, 'zone_id' => $zone->id, 'vnet_name' => $vnetData['vnet']],
                [
                    'tag' => $vnetData['tag'] ?? null,
                    'alias' => $vnetData['alias'] ?? null,
                ]
            );

            // Sync Subnets
            $subnets = $apiService->getSdnSubnets($cluster, $vnetData['vnet']);
            foreach ($subnets as $subnetData) {
                SdnSubnet::updateOrCreate(
                    ['vnet_id' => $vnet->id, 'cidr' => $subnetData['cidr']],
                    [
                        'gateway' => $subnetData['gateway'] ?? null,
                        'snat' => $subnetData['snat'] ?? 0,
                    ]
                );
            }
        }

        // Sync Firewall Rules
        $fwRules = $apiService->getSdnFirewallRules($cluster);
        foreach ($fwRules as $ruleData) {
            SdnFirewallRule::updateOrCreate(
                ['cluster_id' => $cluster->id, 'rule_id' => $ruleData['pos'] ?? null],
                [
                    'action' => $ruleData['action'] ?? 'DROP',
                    'direction' => $ruleData['type'] ?? 'in',
                    'source' => $ruleData['source'] ?? null,
                    'destination' => $ruleData['dest'] ?? null,
                    'protocol' => $ruleData['proto'] ?? null,
                    'dest_port' => $ruleData['dport'] ?? null,
                    'enabled' => $ruleData['enable'] ?? true,
                    'comment' => $ruleData['comment'] ?? null,
                ]
            );
        }
    }

    protected function syncPbs(ProxmoxCluster $cluster, ProxmoxApiService $apiService)
    {
        $datastores = $apiService->getPbsDatastores($cluster);
        foreach ($datastores as $dsData) {
            PbsDatastore::updateOrCreate(
                ['cluster_id' => $cluster->id, 'store_name' => $dsData['store']],
                [
                    'used' => $dsData['used'] ?? 0,
                    'total' => $dsData['total'] ?? 0,
                    'usage_percent' => ($dsData['total'] ?? 0) > 0 ? ($dsData['used'] / $dsData['total']) * 100 : 0,
                    'status' => $dsData['status'] ?? 'unknown',
                ]
            );
        }

        $jobs = $apiService->getPbsJobs($cluster);
        foreach ($jobs as $jobData) {
            PbsJob::updateOrCreate(
                ['cluster_id' => $cluster->id, 'job_id' => $jobData['id']],
                [
                    'job_type' => $jobData['type'] ?? 'unknown',
                    'schedule' => $jobData['schedule'] ?? null,
                    'last_run' => isset($jobData['last_run']) ? date('Y-m-d H:i:s', $jobData['last_run']) : null,
                    'next_run' => isset($jobData['next_run']) ? date('Y-m-d H:i:s', $jobData['next_run']) : null,
                    'status' => $jobData['status'] ?? null,
                ]
            );
        }
    }

    protected function syncPmg(ProxmoxCluster $cluster, ProxmoxApiService $apiService)
    {
        $stats = $apiService->getPmgStats($cluster);
        foreach ($stats as $statData) {
            PmgStat::updateOrCreate(
                ['cluster_id' => $cluster->id, 'stats_date' => date('Y-m-d H:i:s', $statData['time'])],
                [
                    'mail_in' => $statData['count_in'] ?? 0,
                    'mail_out' => $statData['count_out'] ?? 0,
                    'spam_count' => $statData['count_spam'] ?? 0,
                    'virus_count' => $statData['count_virus'] ?? 0,
                ]
            );
        }

        $accounts = $apiService->getPmgAccounts($cluster);
        foreach ($accounts as $accData) {
            PmgAccount::updateOrCreate(
                ['cluster_id' => $cluster->id, 'username' => $accData['userid']],
                [
                    'email' => $accData['email'] ?? '',
                    'role' => $accData['role'] ?? 'user',
                    'is_active' => $accData['enable'] ?? true,
                ]
            );
        }

        $rules = $apiService->getPmgRules($cluster);
        foreach ($rules as $ruleData) {
            PmgRule::updateOrCreate(
                ['cluster_id' => $cluster->id, 'name' => $ruleData['name']],
                [
                    'type' => $ruleData['type'] ?? 'whitelist',
                    'receiver' => $ruleData['to'] ?? null,
                    'sender' => $ruleData['from'] ?? null,
                    'is_active' => $ruleData['active'] ?? true,
                ]
            );
        }
    }
}
