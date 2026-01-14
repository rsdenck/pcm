<?php

namespace App\Http\Controllers\Api;

use App\Http\Controllers\Controller;
use App\Models\Tenant\ProxmoxCluster;
use App\Models\Tenant\PveNode;
use App\Models\Tenant\PveResource;
use Illuminate\Http\Request;

class DashboardController extends Controller
{
    public function index()
    {
        $clusters = ProxmoxCluster::with(['nodes' => function($query) {
            $query->select('cluster_id', 'cpu_usage', 'memory_used', 'memory_total', 'disk_used', 'disk_total');
        }])->withCount(['nodes', 'resources'])->get()->map(function($cluster) {
            $cluster->total_cpu = $cluster->nodes->avg('cpu_usage') ?? 0;
            $cluster->total_memory_used = $cluster->nodes->sum('memory_used');
            $cluster->total_memory_max = $cluster->nodes->sum('memory_total');
            $cluster->total_disk_used = $cluster->nodes->sum('disk_used');
            $cluster->total_disk_max = $cluster->nodes->sum('disk_total');
            
            // Remove nodes collection from output to keep it light
            unset($cluster->nodes);
            
            return $cluster;
        });
        
        $stats = [
            'total_nodes' => PveNode::count(),
            'total_vms' => PveResource::where('type', 'qemu')->count(),
            'total_containers' => PveResource::where('type', 'lxc')->count(),
            'online_nodes' => PveNode::where('status', 'online')->count(),
        ];

        return response()->json([
            'clusters' => $clusters,
            'stats' => $stats,
        ]);
    }

    public function clusterDetail($id)
    {
        $cluster = ProxmoxCluster::with(['nodes', 'resources', 'datastores', 'stats'])->findOrFail($id);
        return response()->json($cluster);
    }
}
