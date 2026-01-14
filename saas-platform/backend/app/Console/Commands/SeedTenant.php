<?php

namespace App\Console\Commands;

use Illuminate\Console\Command;
use App\Models\Tenant;
use App\Services\DatabaseSwitcher;
use Illuminate\Support\Facades\Artisan;

class SeedTenant extends Command
{
    protected $signature = 'tenant:seed {class} {tenant_id?}';
    protected $description = 'Run a seeder for a specific tenant or all tenants';

    public function handle()
    {
        $tenantId = $this->argument('tenant_id');
        $class = $this->argument('class');

        if ($tenantId) {
            $tenants = Tenant::where('id', $tenantId)->get();
        } else {
            $tenants = Tenant::all();
        }

        foreach ($tenants as $tenant) {
            $this->info("Seeding tenant: {$tenant->name} ({$tenant->db_name})");
            
            DatabaseSwitcher::setTenantConnection($tenant->db_name);

            Artisan::call('db:seed', [
                '--class' => $class,
                '--force' => true,
            ]);

            $this->info(Artisan::output());
        }

        $this->info('Tenant seeding completed.');
    }
}
