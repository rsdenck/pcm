<?php

namespace App\Models\Tenant;

use Illuminate\Database\Eloquent\Concerns\HasUuids;
use Illuminate\Database\Eloquent\Model;
use Illuminate\Database\Eloquent\Relations\BelongsTo;

class PmgStat extends Model
{
    use HasUuids;

    protected $fillable = [
        'cluster_id',
        'mail_in',
        'mail_out',
        'spam_count',
        'virus_count',
        'stats_date',
    ];

    protected $casts = [
        'stats_date' => 'datetime',
    ];

    public function cluster(): BelongsTo
    {
        return $this->belongsTo(ProxmoxCluster::class, 'cluster_id');
    }
}
