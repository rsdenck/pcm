<?php

namespace App\Http\Controllers\Api;

use App\Http\Controllers\Controller;
use App\Models\Tenant\ProxmoxCluster;
use App\Models\Tenant\PveResource;
use App\Services\Proxmox\ProxmoxApiService;
use Illuminate\Http\Request;

class ClusterController extends Controller
{
    protected $proxmoxApi;

    public function __construct(ProxmoxApiService $proxmoxApi)
    {
        $this->proxmoxApi = $proxmoxApi;
    }

    public function executeAction(Request $request, $clusterId, $vmid, $action)
    {
        $cluster = ProxmoxCluster::findOrFail($clusterId);
        $resource = PveResource::where('cluster_id', $clusterId)->where('vmid', $vmid)->firstOrFail();

        try {
            $result = $this->proxmoxApi->executeResourceAction(
                $cluster,
                $resource->node,
                $resource->type,
                $resource->vmid,
                $action
            );

            return response()->json([
                'status' => 'success',
                'message' => "Ação {$action} enviada com sucesso para {$resource->name}",
                'data' => $result
            ]);
        } catch (\Exception $e) {
            return response()->json([
                'status' => 'error',
                'message' => $e->getMessage()
            ], 500);
        }
    }

    public function migrate(Request $request, $clusterId, $vmid)
    {
        $request->validate([
            'target_node' => 'required|string'
        ]);

        $cluster = ProxmoxCluster::findOrFail($clusterId);
        $resource = PveResource::where('cluster_id', $clusterId)->where('vmid', $vmid)->firstOrFail();

        try {
            $result = $this->proxmoxApi->migrateResource(
                $cluster,
                $resource->node,
                $resource->type,
                $resource->vmid,
                $request->target_node
            );

            return response()->json([
                'status' => 'success',
                'message' => "Migração iniciada para {$resource->name}",
                'data' => $result
            ]);
        } catch (\Exception $e) {
            return response()->json([
                'status' => 'error',
                'message' => $e->getMessage()
            ], 500);
        }
    }
}
