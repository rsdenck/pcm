<?php

use Illuminate\Database\Migrations\Migration;
use Illuminate\Database\Schema\Blueprint;
use Illuminate\Support\Facades\Schema;

return new class extends Migration
{
    /**
     * Run the migrations.
     */
    public function up(): void
    {
        Schema::table('pve_nodes', function (Blueprint $table) {
            $table->string('kernel_version')->nullable()->after('status');
            $table->string('pve_version')->nullable()->after('kernel_version');
            $table->string('cpu_model')->nullable()->after('cpu_usage');
            $table->integer('cpu_sockets')->nullable()->after('cpu_model');
            $table->integer('cpu_cores')->nullable()->after('cpu_sockets');
            $table->string('loadavg')->nullable()->after('cpu_cores');
            $table->bigInteger('swap_total')->nullable()->after('memory_total');
            $table->bigInteger('swap_used')->nullable()->after('swap_total');
        });
    }

    /**
     * Reverse the migrations.
     */
    public function down(): void
    {
        Schema::table('pve_nodes', function (Blueprint $table) {
            $table->dropColumn([
                'kernel_version',
                'pve_version',
                'cpu_model',
                'cpu_sockets',
                'cpu_cores',
                'loadavg',
                'swap_total',
                'swap_used'
            ]);
        });
    }
};
