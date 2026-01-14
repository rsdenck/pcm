<?php

namespace App\Http\Middleware;

use Closure;
use App\Models\Domain;
use App\Services\DatabaseSwitcher;
use Illuminate\Http\Request;
use Symfony\Component\HttpFoundation\Response;

class ResolveTenant
{
    /**
     * Handle an incoming request.
     *
     * @param  \Closure(\Illuminate\Http\Request): (\Symfony\Component\HttpFoundation\Response)  $next
     */
    public function handle(Request $request, Closure $next): Response
    {
        $host = $request->getHost();

        // Check if it's the master domain or localhost
        if ($host === config('app.master_domain')) {
            return $next($request);
        }

        // Development helper: auto-resolve first tenant if on localhost
        if ($host === 'localhost' || $host === '127.0.0.1') {
            $tenant = \App\Models\Tenant::first();
            if ($tenant) {
                \App\Services\DatabaseSwitcher::setTenantConnection($tenant->db_name);
                $request->merge(['tenant' => $tenant]);
                return $next($request);
            }
        }

        // Resolve tenant by domain
        $domain = Domain::where('domain', $host)->with('tenant')->first();

        if (!$domain || !$domain->tenant) {
            return response()->json(['error' => 'Tenant not found.'], 404);
        }

        // Switch database
        DatabaseSwitcher::setTenantConnection($domain->tenant->db_name);

        // Add tenant info to request
        $request->merge(['tenant' => $domain->tenant]);

        return $next($request);
    }
}
