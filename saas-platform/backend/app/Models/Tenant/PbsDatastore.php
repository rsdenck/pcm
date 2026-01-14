<?php

namespace App\Models\Tenant;

use Illuminate\Database\Eloquent\Concerns\HasUuids;
use Illuminate\Database\Eloquent\Model;
use Illuminate\Database\Eloquent\Relations\BelongsTo;

class PbsDatastore extends Model
{
    use HasUuids;

    protected $fillable = [
        'cluster_id',
        'store_name',
        'used',
        'total',
        'usage_percent',
    ];

    public function cluster(): BelongsTo
    {
        return $this->belongsTo(ProxmoxCluster::class, 'cluster_id');
    }
}
