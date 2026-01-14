<?php

use Illuminate\Http\Request;
use Illuminate\Support\Facades\Route;

/*
|--------------------------------------------------------------------------
| API Routes
|--------------------------------------------------------------------------
|
| Here is where you can register API routes for your application. These
| routes are loaded by the RouteServiceProvider within a group which
| is assigned the "api" middleware group. Enjoy building your API!
|
*/

Route::middleware(['tenant'])->group(function () {
    Route::get('/health', function() { return response()->json(['status' => 'ok']); });
    
    Route::get('/tenant-info', function (Request $request) {
        return response()->json([
            'tenant' => $request->tenant,
            'database' => config('database.connections.tenant.database')
        ]);
    });

    Route::get('/dashboard', [App\Http\Controllers\Api\DashboardController::class, 'index']);
    Route::get('/dashboard/cluster/{id}', [App\Http\Controllers\Api\DashboardController::class, 'clusterDetail']);

    // Cluster Resource Actions
    Route::post('/cluster/{id}/resource/{vmid}/{action}', [App\Http\Controllers\Api\ClusterController::class, 'executeAction']);
    Route::post('/cluster/{id}/resource/{vmid}/migrate', [App\Http\Controllers\Api\ClusterController::class, 'migrate']);

    // User Management
    Route::get('/users', [App\Http\Controllers\Api\UserController::class, 'index']);
    Route::post('/users', [App\Http\Controllers\Api\UserController::class, 'store']);
    Route::put('/users/{id}', [App\Http\Controllers\Api\UserController::class, 'update']);
    Route::delete('/users/{id}', [App\Http\Controllers\Api\UserController::class, 'destroy']);

    // Settings
    Route::get('/settings', [\App\Http\Controllers\Api\SettingsController::class, 'index']);
    Route::post('/settings', [\App\Http\Controllers\Api\SettingsController::class, 'update']);

    // Observability
    Route::get('/observability/pve', [\App\Http\Controllers\Api\ObservabilityController::class, 'pve']);
    Route::get('/observability/sdn', [\App\Http\Controllers\Api\ObservabilityController::class, 'sdn']);
    Route::get('/observability/pbs', [\App\Http\Controllers\Api\ObservabilityController::class, 'pbs']);
    Route::get('/observability/pmg', [\App\Http\Controllers\Api\ObservabilityController::class, 'pmg']);

    // SDN Management
    Route::post('/sdn/zones', [\App\Http\Controllers\Api\SdnController::class, 'createZone']);
    Route::delete('/sdn/zones', [\App\Http\Controllers\Api\SdnController::class, 'deleteZone']);
    Route::post('/sdn/vnets', [\App\Http\Controllers\Api\SdnController::class, 'createVnet']);
    Route::delete('/sdn/vnets', [\App\Http\Controllers\Api\SdnController::class, 'deleteVnet']);
    Route::post('/sdn/subnets', [\App\Http\Controllers\Api\SdnController::class, 'createSubnet']);
    Route::delete('/sdn/subnets', [\App\Http\Controllers\Api\SdnController::class, 'deleteSubnet']);
    Route::post('/sdn/firewall', [\App\Http\Controllers\Api\SdnController::class, 'createFirewallRule']);
    Route::delete('/sdn/firewall', [\App\Http\Controllers\Api\SdnController::class, 'deleteFirewallRule']);
    Route::post('/sdn/apply', [\App\Http\Controllers\Api\SdnController::class, 'apply']);

    Route::post('/login', [App\Http\Controllers\Auth\LoginController::class, 'login']);
    Route::post('/logout', [App\Http\Controllers\Auth\LoginController::class, 'logout']);
});
