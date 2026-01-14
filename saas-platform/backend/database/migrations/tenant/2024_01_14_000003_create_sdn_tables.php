<?php

use Illuminate\Database\Migrations\Migration;
use Illuminate\Database\Schema\Blueprint;
use Illuminate\Support\Facades\Schema;

return new class extends Migration
{
    public function up(): void
    {
        // SDN Zones
        Schema::create('sdn_zones', function (Blueprint $table) {
            $table->uuid('id')->primary();
            $table->foreignUuid('cluster_id')->constrained('proxmox_clusters')->onDelete('cascade');
            $table->string('zone_name');
            $table->string('type');
            $table->string('mtu')->nullable();
            $table->string('nodes')->nullable();
            $table->string('ipam')->nullable();
            $table->timestamps();
        });

        // SDN VNets
        Schema::create('sdn_vnets', function (Blueprint $table) {
            $table->uuid('id')->primary();
            $table->foreignUuid('cluster_id')->constrained('proxmox_clusters')->onDelete('cascade');
            $table->foreignUuid('zone_id')->constrained('sdn_zones')->onDelete('cascade');
            $table->string('vnet_name');
            $table->string('tag')->nullable();
            $table->string('alias')->nullable();
            $table->timestamps();
        });

        // SDN Subnets
        Schema::create('sdn_subnets', function (Blueprint $table) {
            $table->uuid('id')->primary();
            $table->foreignUuid('vnet_id')->constrained('sdn_vnets')->onDelete('cascade');
            $table->string('cidr');
            $table->string('gateway')->nullable();
            $table->string('snat')->default('0');
            $table->timestamps();
        });
    }

    public function down(): void
    {
        Schema::dropIfExists('sdn_subnets');
        Schema::dropIfExists('sdn_vnets');
        Schema::dropIfExists('sdn_zones');
    }
};
