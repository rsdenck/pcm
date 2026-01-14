<?php

namespace App\Models\Tenant;

use Illuminate\Database\Eloquent\Concerns\HasUuids;
use Illuminate\Database\Eloquent\Model;
use Illuminate\Database\Eloquent\Relations\BelongsTo;

class PveNode extends Model
{
    use HasUuids;

    protected $fillable = [
        'cluster_id',
        'node_name',
        'status',
        'uptime',
        'cpu_usage',
        'memory_used',
        'memory_total',
        'disk_used',
        'disk_total',
        'kernel_version',
        'pve_version',
        'cpu_model',
        'cpu_sockets',
        'cpu_cores',
        'loadavg',
        'swap_total',
        'swap_used',
    ];

    public function cluster(): BelongsTo
    {
        return $this->belongsTo(ProxmoxCluster::class, 'cluster_id');
    }
}
