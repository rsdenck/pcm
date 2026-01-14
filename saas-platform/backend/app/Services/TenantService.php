<?php

namespace App\Services;

use App\Models\Tenant;
use App\Models\Domain;
use Illuminate\Support\Facades\DB;
use Illuminate\Support\Facades\Artisan;
use Illuminate\Support\Str;

class TenantService
{
    /**
     * Create a new tenant with its own database.
     */
    public function createTenant(string $name, string $domainName): Tenant
    {
        $uuid = (string) Str::uuid();
        $dbName = 'tenant_' . str_replace('-', '_', $uuid);

        // 1. Create Tenant record in Master
        $tenant = Tenant::create([
            'id' => $uuid,
            'name' => $name,
            'db_name' => $dbName,
        ]);

        // 2. Create Domain record
        Domain::create([
            'tenant_id' => $tenant->id,
            'domain' => $domainName,
        ]);

        // 3. Create Physical Database
        DB::statement("CREATE DATABASE `{$dbName}` CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;");

        // 4. Run Tenant Migrations
        DatabaseSwitcher::setTenantConnection($dbName);
        Artisan::call('migrate', [
            '--path' => 'database/migrations/tenant',
            '--force' => true,
        ]);
        DatabaseSwitcher::resetToMaster();

        return $tenant;
    }
}
