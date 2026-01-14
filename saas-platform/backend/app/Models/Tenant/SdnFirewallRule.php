<?php

namespace App\Models\Tenant;

use Illuminate\Database\Eloquent\Factories\HasFactory;
use Illuminate\Database\Eloquent\Model;
use App\Traits\HasUuid;

class SdnFirewallRule extends Model
{
    use HasFactory, HasUuid;

    protected $fillable = [
        'cluster_id',
        'rule_id',
        'action',
        'direction',
        'source',
        'destination',
        'protocol',
        'dest_port',
        'enabled',
        'comment',
    ];

    public function cluster()
    {
        return $this->belongsTo(ProxmoxCluster::class, 'cluster_id');
    }
}
