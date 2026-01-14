<?php

namespace App\Models\Tenant;

use Illuminate\Database\Eloquent\Factories\HasFactory;
use Illuminate\Database\Eloquent\Model;
use App\Traits\HasUuid;

class PbsJob extends Model
{
    use HasFactory, HasUuid;

    protected $fillable = [
        'cluster_id',
        'job_id',
        'job_type',
        'schedule',
        'last_run',
        'next_run',
        'status',
    ];

    public function cluster()
    {
        return $this->belongsTo(ProxmoxCluster::class, 'cluster_id');
    }
}
