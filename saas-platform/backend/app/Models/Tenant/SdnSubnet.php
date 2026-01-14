<?php

namespace App\Models\Tenant;

use Illuminate\Database\Eloquent\Concerns\HasUuids;
use Illuminate\Database\Eloquent\Model;
use Illuminate\Database\Eloquent\Relations\BelongsTo;

class SdnSubnet extends Model
{
    use HasUuids;

    protected $fillable = [
        'vnet_id',
        'cidr',
        'gateway',
        'snat',
    ];

    public function vnet(): BelongsTo
    {
        return $this->belongsTo(SdnVnet::class, 'vnet_id');
    }
}
