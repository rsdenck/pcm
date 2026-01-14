<?php

namespace App\Models\Tenant;

use Illuminate\Database\Eloquent\Factories\HasFactory;
use Illuminate\Database\Eloquent\Model;
use App\Traits\HasUuid;

class PmgRule extends Model
{
    use HasFactory, HasUuid;

    protected $fillable = [
        'cluster_id',
        'name',
        'type',
        'receiver',
        'sender',
        'is_active',
    ];

    public function cluster()
    {
        return $this->belongsTo(ProxmoxCluster::class, 'cluster_id');
    }
}
