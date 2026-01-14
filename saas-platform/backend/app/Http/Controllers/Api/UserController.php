<?php

namespace App\Http\Controllers\Api;

use App\Http\Controllers\Controller;
use App\Models\User;
use Illuminate\Http\Request;
use Illuminate\Support\Facades\Hash;
use Illuminate\Support\Facades\Log;
use Illuminate\Validation\Rule;

class UserController extends Controller
{
    public function index()
    {
        Log::info('Fetching all users for tenant: ' . config('database.connections.tenant.database'));
        return response()->json(User::all());
    }

    public function store(Request $request)
    {
        Log::info('Storing new user', $request->except('password'));
        $validated = $request->validate([
            'name' => 'required|string|max:255',
            'email' => 'required|string|email|max:255|unique:users',
            'password' => 'required|string|min:8',
            'role' => ['required', Rule::in(['admin', 'editor', 'viewer'])],
        ]);

        $user = User::create([
            'name' => $validated['name'],
            'email' => $validated['email'],
            'password' => Hash::make($validated['password']),
            'role' => $validated['role'],
        ]);

        Log::info('User created with ID: ' . $user->id);

        return response()->json($user, 201);
    }

    public function update(Request $request, $id)
    {
        Log::info('Updating user ID: ' . $id, $request->except('password'));
        $user = User::findOrFail($id);

        $validated = $request->validate([
            'name' => 'sometimes|required|string|max:255',
            'email' => ['sometimes', 'required', 'string', 'email', 'max:255', Rule::unique('users')->ignore($user->id)],
            'role' => ['sometimes', 'required', Rule::in(['admin', 'editor', 'viewer'])],
            'password' => 'sometimes|nullable|string|min:8',
        ]);

        if (isset($validated['password']) && $validated['password']) {
            $validated['password'] = Hash::make($validated['password']);
        } else {
            unset($validated['password']);
        }

        $user->update($validated);
        
        Log::info('User updated successfully');

        return response()->json($user);
    }

    public function destroy($id)
    {
        Log::info('Deleting user ID: ' . $id);
        $user = User::findOrFail($id);
        
        $user->delete();

        Log::info('User deleted successfully');

        return response()->json(null, 204);
    }
}
