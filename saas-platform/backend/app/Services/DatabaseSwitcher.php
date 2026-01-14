<?php

namespace App\Services;

use Illuminate\Support\Facades\Config;
use Illuminate\Support\Facades\DB;

class DatabaseSwitcher
{
    /**
     * Switch to a tenant database.
     *
     * @param string $dbName
     * @return void
     */
    public static function setTenantConnection(string $dbName): void
    {
        // Purge existing connection
        DB::purge('tenant');

        // Set the new connection configuration
        Config::set('database.connections.tenant.database', $dbName);

        // Reconnect
        DB::reconnect('tenant');

        // Set as default for the request
        DB::setDefaultConnection('tenant');
    }

    /**
     * Reset to the master database connection.
     *
     * @return void
     */
    public static function resetToMaster(): void
    {
        DB::purge('tenant');
        DB::setDefaultConnection(config('database.default_master', 'mysql'));
    }
}
