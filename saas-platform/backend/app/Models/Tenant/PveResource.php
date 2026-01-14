<?php

namespace App\Models\Tenant;

use Illuminate\Database\Eloquent\Concerns\HasUuids;
use Illuminate\Database\Eloquent\Model;
use Illuminate\Database\Eloquent\Relations\BelongsTo;

class PveResource extends Model
{
    use HasUuids;

    protected $fillable = [
        'cluster_id',
        'vmid',
        'name',
        'type',
        'node',
        'status',
        'cpu_usage',
        'memory_used',
        'memory_total',
        'disk_used',
        'disk_total',
    ];

    public function cluster(): BelongsTo
    {
        return $this->belongsTo(ProxmoxCluster::class, 'cluster_id');
    }
}
