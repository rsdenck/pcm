<?php

namespace App\Console\Commands;

use Illuminate\Console\Command;
use App\Models\Tenant;
use App\Services\DatabaseSwitcher;
use Illuminate\Support\Facades\Artisan;

class MigrateTenant extends Command
{
    protected $signature = 'tenant:migrate {tenant_id?}';
    protected $description = 'Run migrations for a specific tenant or all tenants';

    public function handle()
    {
        $tenantId = $this->argument('tenant_id');

        if ($tenantId) {
            $tenants = Tenant::where('id', $tenantId)->get();
        } else {
            $tenants = Tenant::all();
        }

        foreach ($tenants as $tenant) {
            $this->info("Migrating tenant: {$tenant->name} ({$tenant->db_name})");
            
            DatabaseSwitcher::setTenantConnection($tenant->db_name);

            Artisan::call('migrate', [
                '--database' => 'tenant',
                '--path' => 'database/migrations/tenant',
                '--force' => true,
            ]);

            $this->info(Artisan::output());
        }

        $this->info('Tenant migrations completed.');
    }
}
