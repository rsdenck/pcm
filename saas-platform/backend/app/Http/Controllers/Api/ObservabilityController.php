<?php

namespace App\Http\Controllers\Api;

use App\Http\Controllers\Controller;
use App\Models\Tenant\SdnZone;
use App\Models\Tenant\SdnVnet;
use App\Models\Tenant\SdnFirewallRule;
use App\Models\Tenant\PbsDatastore;
use App\Models\Tenant\PbsJob;
use App\Models\Tenant\PmgStat;
use App\Models\Tenant\PmgAccount;
use App\Models\Tenant\PmgRule;
use App\Models\Tenant\ProxmoxCluster;
use App\Models\Tenant\PveNode;
use App\Models\Tenant\PveResource;
use Illuminate\Http\Request;

class ObservabilityController extends Controller
{
    public function pve()
    {
        $nodes = PveNode::with('cluster')->get();
        $resources = PveResource::with('cluster')->get();

        return response()->json([
            'nodes' => $nodes,
            'resources' => $resources,
            'summary' => [
                'total_nodes' => $nodes->count(),
                'online_nodes' => $nodes->where('status', 'online')->count(),
                'total_vms' => $resources->where('type', 'qemu')->count(),
                'total_containers' => $resources->where('type', 'lxc')->count(),
                'running_resources' => $resources->where('status', 'running')->count(),
            ]
        ]);
    }

    public function sdn()
    {
        $zones = SdnZone::with(['vnets.subnets', 'cluster'])->get();
        $firewallRules = SdnFirewallRule::with('cluster')->get();
        
        return response()->json([
            'zones' => $zones,
            'firewall_rules' => $firewallRules,
            'total_vnets' => SdnVnet::count(),
            'total_zones' => SdnZone::count(),
        ]);
    }

    public function pbs()
    {
        $datastores = PbsDatastore::with('cluster')->get();
        $jobs = PbsJob::with('cluster')->get();
        
        return response()->json([
            'datastores' => $datastores,
            'jobs' => $jobs,
            'total_usage' => $datastores->sum('used'),
            'total_capacity' => $datastores->sum('total'),
        ]);
    }

    public function pmg()
    {
        $stats = PmgStat::with('cluster')
            ->orderBy('stats_date', 'desc')
            ->limit(30)
            ->get();
            
        $accounts = PmgAccount::with('cluster')->get();
        $rules = PmgRule::with('cluster')->get();

        return response()->json([
            'stats' => $stats,
            'accounts' => $accounts,
            'rules' => $rules,
            'summary' => [
                'total_mail_in' => $stats->sum('mail_in'),
                'total_mail_out' => $stats->sum('mail_out'),
                'total_spam' => $stats->sum('spam_count'),
                'total_virus' => $stats->sum('virus_count'),
                'total_accounts' => $accounts->count(),
            ]
        ]);
    }
}
