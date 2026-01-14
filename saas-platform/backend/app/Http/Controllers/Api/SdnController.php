<?php

namespace App\Http\Controllers\Api;

use App\Http\Controllers\Controller;
use App\Models\Tenant\ProxmoxCluster;
use App\Services\Proxmox\ProxmoxApiService;
use Illuminate\Http\Request;

class SdnController extends Controller
{
    protected $apiService;

    public function __construct(ProxmoxApiService $apiService)
    {
        $this->apiService = $apiService;
    }

    public function createZone(Request $request)
    {
        $validated = $request->validate([
            'cluster_id' => 'required|exists:proxmox_clusters,id',
            'zone' => 'required|string',
            'type' => 'required|string',
            'mtu' => 'nullable|integer',
            'nodes' => 'nullable|string',
        ]);

        $cluster = ProxmoxCluster::findOrFail($validated['cluster_id']);
        
        try {
            $result = $this->apiService->createSdnZone($cluster, $validated);
            return response()->json(['message' => 'Zone created successfully', 'data' => $result]);
        } catch (\Exception $e) {
            return response()->json(['error' => $e->getMessage()], 500);
        }
    }

    public function createVnet(Request $request)
    {
        $validated = $request->validate([
            'cluster_id' => 'required|exists:proxmox_clusters,id',
            'vnet' => 'required|string',
            'zone' => 'required|string',
            'tag' => 'nullable|integer',
            'alias' => 'nullable|string',
        ]);

        $cluster = ProxmoxCluster::findOrFail($validated['cluster_id']);

        try {
            $result = $this->apiService->createSdnVnet($cluster, $validated);
            return response()->json(['message' => 'VNet created successfully', 'data' => $result]);
        } catch (\Exception $e) {
            return response()->json(['error' => $e->getMessage()], 500);
        }
    }

    public function createSubnet(Request $request)
    {
        $validated = $request->validate([
            'cluster_id' => 'required|exists:proxmox_clusters,id',
            'vnet' => 'required|string',
            'cidr' => 'required|string',
            'gateway' => 'nullable|string',
            'snat' => 'nullable|boolean',
        ]);

        $cluster = ProxmoxCluster::findOrFail($validated['cluster_id']);

        try {
            $result = $this->apiService->createSdnSubnet($cluster, $validated['vnet'], $validated);
            return response()->json(['message' => 'Subnet created successfully', 'data' => $result]);
        } catch (\Exception $e) {
            return response()->json(['error' => $e->getMessage()], 500);
        }
    }

    public function deleteZone(Request $request)
    {
        $validated = $request->validate([
            'cluster_id' => 'required|exists:proxmox_clusters,id',
            'zone' => 'required|string',
        ]);

        $cluster = ProxmoxCluster::findOrFail($validated['cluster_id']);

        try {
            $result = $this->apiService->deleteSdnZone($cluster, $validated['zone']);
            return response()->json(['message' => 'Zone deleted successfully', 'data' => $result]);
        } catch (\Exception $e) {
            return response()->json(['error' => $e->getMessage()], 500);
        }
    }

    public function deleteVnet(Request $request)
    {
        $validated = $request->validate([
            'cluster_id' => 'required|exists:proxmox_clusters,id',
            'vnet' => 'required|string',
        ]);

        $cluster = ProxmoxCluster::findOrFail($validated['cluster_id']);

        try {
            $result = $this->apiService->deleteSdnVnet($cluster, $validated['vnet']);
            return response()->json(['message' => 'VNet deleted successfully', 'data' => $result]);
        } catch (\Exception $e) {
            return response()->json(['error' => $e->getMessage()], 500);
        }
    }

    public function deleteSubnet(Request $request)
    {
        $validated = $request->validate([
            'cluster_id' => 'required|exists:proxmox_clusters,id',
            'vnet' => 'required|string',
            'subnet' => 'required|string',
        ]);

        $cluster = ProxmoxCluster::findOrFail($validated['cluster_id']);

        try {
            $result = $this->apiService->deleteSdnSubnet($cluster, $validated['vnet'], $validated['subnet']);
            return response()->json(['message' => 'Subnet deleted successfully', 'data' => $result]);
        } catch (\Exception $e) {
            return response()->json(['error' => $e->getMessage()], 500);
        }
    }

    public function createFirewallRule(Request $request)
    {
        $validated = $request->validate([
            'cluster_id' => 'required|exists:proxmox_clusters,id',
            'action' => 'required|string',
            'type' => 'required|string', // in/out
            'source' => 'nullable|string',
            'dest' => 'nullable|string',
            'proto' => 'nullable|string',
            'dport' => 'nullable|string',
            'enable' => 'nullable|boolean',
            'comment' => 'nullable|string',
        ]);

        $cluster = ProxmoxCluster::findOrFail($validated['cluster_id']);

        try {
            $result = $this->apiService->createSdnFirewallRule($cluster, $validated);
            return response()->json(['message' => 'Firewall rule created successfully', 'data' => $result]);
        } catch (\Exception $e) {
            return response()->json(['error' => $e->getMessage()], 500);
        }
    }

    public function deleteFirewallRule(Request $request)
    {
        $validated = $request->validate([
            'cluster_id' => 'required|exists:proxmox_clusters,id',
            'pos' => 'required|integer',
        ]);

        $cluster = ProxmoxCluster::findOrFail($validated['cluster_id']);

        try {
            $result = $this->apiService->deleteSdnFirewallRule($cluster, $validated['pos']);
            return response()->json(['message' => 'Firewall rule deleted successfully', 'data' => $result]);
        } catch (\Exception $e) {
            return response()->json(['error' => $e->getMessage()], 500);
        }
    }

    public function apply(Request $request)
    {
        $validated = $request->validate([
            'cluster_id' => 'required|exists:proxmox_clusters,id',
        ]);

        $cluster = ProxmoxCluster::findOrFail($validated['cluster_id']);

        try {
            $result = $this->apiService->applySdn($cluster);
            return response()->json(['message' => 'SDN configuration applied successfully', 'data' => $result]);
        } catch (\Exception $e) {
            return response()->json(['error' => $e->getMessage()], 500);
        }
    }
}
