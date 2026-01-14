<?php

namespace App\Console\Commands;

use App\Models\Tenant as MasterTenant;
use App\Models\Tenant\ProxmoxCluster;
use App\Jobs\SyncProxmoxDataJob;
use App\Services\DatabaseSwitcher;
use Illuminate\Console\Command;

class SyncAllTenantsProxmoxData extends Command
{
    protected $signature = 'proxmon:sync';
    protected $description = 'Sync Proxmox data for all active clusters across all tenants';

    public function handle(DatabaseSwitcher $dbSwitcher)
    {
        $tenants = MasterTenant::all();

        foreach ($tenants as $tenant) {
            $this->info("Processing tenant: {$tenant->name}");
            
            // Switch connection to find clusters for this tenant
            $dbSwitcher->setTenantConnection($tenant->db_name);
            
            $clusters = ProxmoxCluster::where('is_active', true)->get();
            
            foreach ($clusters as $cluster) {
                $this->info("- Syncing cluster: {$cluster->name}");
                SyncProxmoxDataJob::dispatchSync($tenant->db_name, $cluster->id);
            }
        }

        $this->info('All sync jobs dispatched.');
    }
}
