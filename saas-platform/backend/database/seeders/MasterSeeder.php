<?php

namespace Database\Seeders;

use App\Models\Tenant;
use App\Models\Domain;
use Illuminate\Database\Seeder;
use Illuminate\Support\Str;

class MasterSeeder extends Seeder
{
    public function run(): void
    {
        $tenant = Tenant::create([
            'id' => (string) Str::uuid(),
            'name' => 'Proxmon Dev',
            'db_name' => 'tenant_db_1',
            'status' => 'active',
        ]);

        Domain::create([
            'id' => (string) Str::uuid(),
            'tenant_id' => $tenant->id,
            'domain' => 'localhost',
            'is_primary' => true,
        ]);
    }
}
