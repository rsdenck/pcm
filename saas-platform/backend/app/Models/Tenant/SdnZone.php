<?php

namespace App\Models\Tenant;

use Illuminate\Database\Eloquent\Concerns\HasUuids;
use Illuminate\Database\Eloquent\Model;
use Illuminate\Database\Eloquent\Relations\BelongsTo;
use Illuminate\Database\Eloquent\Relations\HasMany;

class SdnZone extends Model
{
    use HasUuids;

    protected $fillable = [
        'cluster_id',
        'zone_name',
        'type',
        'status',
        'mtu',
        'nodes',
        'ipam',
    ];

    public function cluster(): BelongsTo
    {
        return $this->belongsTo(ProxmoxCluster::class, 'cluster_id');
    }

    public function vnets(): HasMany
    {
        return $this->hasMany(SdnVnet::class, 'zone_id');
    }
}
