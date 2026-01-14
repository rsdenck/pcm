<?php

use Illuminate\Database\Migrations\Migration;
use Illuminate\Database\Schema\Blueprint;
use Illuminate\Support\Facades\Schema;

return new class extends Migration
{
    public function up(): void
    {
        // Cluster / Server Configuration
        Schema::create('proxmox_clusters', function (Blueprint $table) {
            $table->uuid('id')->primary();
            $table->string('name');
            $table->enum('type', ['pve', 'pbs', 'pmg']);
            $table->string('hostname');
            $table->integer('port')->default(8006);
            $table->string('username');
            $table->text('api_token'); // Encrypted
            $table->string('api_secret')->nullable(); // Encrypted
            $table->boolean('is_active')->default(true);
            $table->timestamp('last_sync_at')->nullable();
            $table->timestamps();
        });

        // PVE Nodes
        Schema::create('pve_nodes', function (Blueprint $table) {
            $table->uuid('id')->primary();
            $table->foreignUuid('cluster_id')->constrained('proxmox_clusters')->onDelete('cascade');
            $table->string('node_name');
            $table->string('status');
            $table->bigInteger('uptime');
            $table->decimal('cpu_usage', 5, 2);
            $table->bigInteger('memory_used');
            $table->bigInteger('memory_total');
            $table->bigInteger('disk_used');
            $table->bigInteger('disk_total');
            $table->timestamps();
        });

        // PVE VMs / Containers
        Schema::create('pve_resources', function (Blueprint $table) {
            $table->uuid('id')->primary();
            $table->foreignUuid('cluster_id')->constrained('proxmox_clusters')->onDelete('cascade');
            $table->string('vmid');
            $table->string('name');
            $table->enum('type', ['qemu', 'lxc']);
            $table->string('node');
            $table->string('status');
            $table->decimal('cpu_usage', 5, 2);
            $table->bigInteger('memory_used');
            $table->bigInteger('memory_total');
            $table->bigInteger('disk_used');
            $table->bigInteger('disk_total');
            $table->timestamps();
        });

        // PBS Datastores
        Schema::create('pbs_datastores', function (Blueprint $table) {
            $table->uuid('id')->primary();
            $table->foreignUuid('cluster_id')->constrained('proxmox_clusters')->onDelete('cascade');
            $table->string('store_name');
            $table->bigInteger('used');
            $table->bigInteger('total');
            $table->decimal('usage_percent', 5, 2);
            $table->timestamps();
        });

        // PMG Statistics (Simplified for now)
        Schema::create('pmg_stats', function (Blueprint $table) {
            $table->uuid('id')->primary();
            $table->foreignUuid('cluster_id')->constrained('proxmox_clusters')->onDelete('cascade');
            $table->integer('mail_in');
            $table->integer('mail_out');
            $table->integer('spam_count');
            $table->integer('virus_count');
            $table->timestamp('stats_date');
            $table->timestamps();
        });
    }

    public function down(): void
    {
        Schema::dropIfExists('pmg_stats');
        Schema::dropIfExists('pbs_datastores');
        Schema::dropIfExists('pve_resources');
        Schema::dropIfExists('pve_nodes');
        Schema::dropIfExists('proxmox_clusters');
    }
};
