<?php

namespace Database\Seeders;

use Illuminate\Database\Seeder;
use App\Models\Tenant\ProxmoxCluster;
use App\Models\Tenant\PveNode;
use App\Models\Tenant\PveResource;
use Illuminate\Support\Str;

class TenantDummyDataSeeder extends Seeder
{
    public function run(): void
    {
        $cluster = ProxmoxCluster::create([
            'id' => (string) Str::uuid(),
            'name' => 'Main Datacenter',
            'type' => 'pve',
            'hostname' => 'pve.proxmon.local',
            'port' => 8006,
            'username' => 'root@pam',
            'api_token' => 'dummy-token',
            'api_secret' => 'dummy-secret',
            'is_active' => true,
        ]);

        $node1 = PveNode::create([
            'id' => (string) Str::uuid(),
            'cluster_id' => $cluster->id,
            'node_name' => 'pve-01',
            'status' => 'online',
            'uptime' => 86400 * 5,
            'cpu_usage' => 15.5,
            'memory_used' => 1024 * 1024 * 1024 * 8,
            'memory_total' => 1024 * 1024 * 1024 * 32,
            'disk_used' => 1024 * 1024 * 1024 * 100,
            'disk_total' => 1024 * 1024 * 1024 * 500,
        ]);

        PveResource::create([
            'id' => (string) Str::uuid(),
            'cluster_id' => $cluster->id,
            'vmid' => '100',
            'name' => 'web-server-01',
            'type' => 'qemu',
            'node' => 'pve-01',
            'status' => 'running',
            'cpu_usage' => 5.2,
            'memory_used' => 1024 * 1024 * 1024 * 2,
            'memory_total' => 1024 * 1024 * 1024 * 4,
            'disk_used' => 1024 * 1024 * 1024 * 20,
            'disk_total' => 1024 * 1024 * 1024 * 50,
        ]);

        PveResource::create([
            'id' => (string) Str::uuid(),
            'cluster_id' => $cluster->id,
            'vmid' => '101',
            'name' => 'db-primary',
            'type' => 'qemu',
            'node' => 'pve-01',
            'status' => 'running',
            'cpu_usage' => 12.8,
            'memory_used' => 1024 * 1024 * 1024 * 6,
            'memory_total' => 1024 * 1024 * 1024 * 8,
            'disk_used' => 1024 * 1024 * 1024 * 80,
            'disk_total' => 1024 * 1024 * 1024 * 200,
        ]);
    }
}
