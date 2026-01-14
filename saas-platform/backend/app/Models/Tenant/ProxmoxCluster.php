<?php

namespace App\Models\Tenant;

use Illuminate\Database\Eloquent\Concerns\HasUuids;
use Illuminate\Database\Eloquent\Model;
use Illuminate\Database\Eloquent\Relations\HasMany;
use Illuminate\Support\Facades\Crypt;

class ProxmoxCluster extends Model
{
    use HasUuids;

    protected $fillable = [
        'name',
        'type',
        'hostname',
        'port',
        'username',
        'api_token',
        'api_secret',
        'is_active',
        'last_sync_at',
    ];

    protected $casts = [
        'is_active' => 'boolean',
        'last_sync_at' => 'datetime',
    ];

    public function setApiTokenAttribute($value)
    {
        $this->attributes['api_token'] = Crypt::encryptString($value);
    }

    public function getApiTokenAttribute($value)
    {
        return Crypt::decryptString($value);
    }

    public function setApiSecretAttribute($value)
    {
        if ($value) {
            $this->attributes['api_secret'] = Crypt::encryptString($value);
        }
    }

    public function getApiSecretAttribute($value)
    {
        return $value ? Crypt::decryptString($value) : null;
    }

    public function nodes(): HasMany
    {
        return $this->hasMany(PveNode::class, 'cluster_id');
    }

    public function resources(): HasMany
    {
        return $this->hasMany(PveResource::class, 'cluster_id');
    }

    public function datastores(): HasMany
    {
        return $this->hasMany(PbsDatastore::class, 'cluster_id');
    }

    public function stats(): HasMany
    {
        return $this->hasMany(PmgStat::class, 'cluster_id');
    }
}
