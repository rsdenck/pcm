<?php

namespace App\Models\Tenant;

use Illuminate\Database\Eloquent\Concerns\HasUuids;
use Illuminate\Database\Eloquent\Model;
use Illuminate\Database\Eloquent\Relations\BelongsTo;
use Illuminate\Database\Eloquent\Relations\HasMany;

class SdnVnet extends Model
{
    use HasUuids;

    protected $fillable = [
        'cluster_id',
        'zone_id',
        'vnet_name',
        'tag',
        'alias',
    ];

    public function cluster(): BelongsTo
    {
        return $this->belongsTo(ProxmoxCluster::class, 'cluster_id');
    }

    public function zone(): BelongsTo
    {
        return $this->belongsTo(SdnZone::class, 'zone_id');
    }

    public function subnets(): HasMany
    {
        return $this->hasMany(SdnSubnet::class, 'vnet_id');
    }
}
