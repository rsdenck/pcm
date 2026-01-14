<?php

use Illuminate\Database\Migrations\Migration;
use Illuminate\Database\Schema\Blueprint;
use Illuminate\Support\Facades\Schema;

return new class extends Migration
{
    public function up(): void
    {
        // PBS Jobs
        Schema::create('pbs_jobs', function (Blueprint $table) {
            $table->uuid('id')->primary();
            $table->foreignUuid('cluster_id')->constrained('proxmox_clusters')->onDelete('cascade');
            $table->string('job_id');
            $table->string('job_type');
            $table->string('schedule')->nullable();
            $table->timestamp('last_run')->nullable();
            $table->timestamp('next_run')->nullable();
            $table->string('status')->nullable();
            $table->timestamps();
        });

        // PMG Accounts
        Schema::create('pmg_accounts', function (Blueprint $table) {
            $table->uuid('id')->primary();
            $table->foreignUuid('cluster_id')->constrained('proxmox_clusters')->onDelete('cascade');
            $table->string('username');
            $table->string('email');
            $table->string('role')->default('user');
            $table->boolean('is_active')->default(true);
            $table->timestamps();
        });

        // PMG Rules (Whitelist/Blacklist)
        Schema::create('pmg_rules', function (Blueprint $table) {
            $table->uuid('id')->primary();
            $table->foreignUuid('cluster_id')->constrained('proxmox_clusters')->onDelete('cascade');
            $table->string('name');
            $table->enum('type', ['whitelist', 'blacklist']);
            $table->string('receiver')->nullable();
            $table->string('sender')->nullable();
            $table->boolean('is_active')->default(true);
            $table->timestamps();
        });

        // SDN Firewall Rules
        Schema::create('sdn_firewall_rules', function (Blueprint $table) {
            $table->uuid('id')->primary();
            $table->foreignUuid('cluster_id')->constrained('proxmox_clusters')->onDelete('cascade');
            $table->string('rule_id')->nullable();
            $table->string('action'); // ACCEPT, DROP, REJECT
            $table->string('direction'); // IN, OUT
            $table->string('source')->nullable();
            $table->string('destination')->nullable();
            $table->string('protocol')->nullable();
            $table->string('dest_port')->nullable();
            $table->boolean('enabled')->default(true);
            $table->text('comment')->nullable();
            $table->timestamps();
        });

        // Add status to pbs_datastores if it doesn't exist
        if (!Schema::hasColumn('pbs_datastores', 'status')) {
            Schema::table('pbs_datastores', function (Blueprint $table) {
                $table->string('status')->default('unknown')->after('usage_percent');
            });
        }
    }

    public function down(): void
    {
        Schema::dropIfExists('sdn_firewall_rules');
        Schema::dropIfExists('pmg_rules');
        Schema::dropIfExists('pmg_accounts');
        Schema::dropIfExists('pbs_jobs');
        
        if (Schema::hasColumn('pbs_datastores', 'status')) {
            Schema::table('pbs_datastores', function (Blueprint $table) {
                $table->dropColumn('status');
            });
        }
    }
};
