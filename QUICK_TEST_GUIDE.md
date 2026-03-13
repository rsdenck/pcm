# Quick Test Guide - Frontend Fixes

## Test Environment

- **Frontend URL**: http://192.168.130.10:9000/
- **Backend URL**: http://192.168.130.10:8000/api/v1
- **Browser**: Chrome/Firefox (Anonymous Tab for testing)

## Test Cases

### 1. Root Redirect Test ✅

**Test 1.1: Anonymous User Redirect**
```
1. Open http://192.168.130.10:9000/ in ANONYMOUS TAB
2. Expected: Should redirect to /login page
3. Verify: Login form is displayed
4. Verify: No infinite reload/spinner
5. Verify: Orange gradient button visible
```

**Test 1.2: Authenticated User Redirect**
```
1. Login with valid credentials
2. Open http://192.168.130.10:9000/
3. Expected: Should redirect to /dashboard
4. Verify: Dashboard is displayed
5. Verify: No infinite reload
```

### 2. Clusters Page Test ✅

**Test 2.1: Page Load**
```
1. Navigate to /dashboard/clusters
2. Expected: Page loads without infinite reload
3. Verify: Clusters list is displayed
4. Verify: Search and filter work
5. Verify: No console errors
```

**Test 2.2: Color Scheme**
```
1. Open /dashboard/clusters
2. Verify: All buttons are orange gradient (#E57000 → #FF8C00)
3. Verify: No blue or green colors
4. Verify: Icons are properly colored
```

**Test 2.3: RBAC3 Permissions**
```
1. Open /dashboard/clusters
2. Check "Adicionar Cluster" button:
   - If user has cluster:update permission → Button enabled
   - If user lacks permission → Button disabled (opacity-50)
3. Check action buttons (sync, edit):
   - If user has cluster:read permission → Buttons enabled
   - If user lacks permission → Buttons disabled
4. Click disabled button → Should show error toast
```

### 3. Tenants Page Test ✅

**Test 3.1: Page Load**
```
1. Navigate to /dashboard/tenants
2. Expected: Page loads without infinite reload
3. Verify: Tenants list is displayed
4. Verify: Search and filter work
5. Verify: No console errors
```

**Test 3.2: Color Scheme**
```
1. Open /dashboard/tenants
2. Verify: All progress bars are orange gradient
3. Verify: RAM progress bar is orange (NOT blue)
4. Verify: Storage progress bar is orange (NOT green)
5. Verify: No blue or green colors anywhere
```

**Test 3.3: RBAC3 Permissions**
```
1. Open /dashboard/tenants
2. Check "Novo Tenant" button:
   - If user has tenant:update permission → Button enabled
   - If user lacks permission → Button disabled (opacity-50)
3. Check action buttons (edit, stats):
   - If user has tenant:update permission → Edit button enabled
   - If user has tenant:read permission → Stats button enabled
   - If user lacks permissions → Buttons disabled
4. Click disabled button → Should show error toast
```

### 4. Visual Identity Test ✅

**Test 4.1: Colors**
```
1. Open all pages
2. Verify: Only orange (#E57000, #FF8C00) and gray colors used
3. Verify: No blue (#0000FF) anywhere
4. Verify: No green (#00FF00) anywhere
5. Verify: No other colors outside design system
```

**Test 4.2: Icons**
```
1. Check all icons:
   - Building-office icon for tenants ✓
   - Server icon for clusters ✓
   - Plus icon for add buttons ✓
   - Pencil icon for edit buttons ✓
   - Chart icon for stats ✓
2. Verify: All icons use PCM brand colors
3. Verify: Icon sizes are consistent
```

### 5. Performance Test ✅

**Test 5.1: Load Time**
```
1. Open /dashboard/clusters
2. Measure: Page should load in <2 seconds
3. Verify: No unnecessary re-renders
4. Verify: Search/filter debounce works (300ms)
```

**Test 5.2: Memory**
```
1. Open DevTools → Memory tab
2. Navigate between pages
3. Verify: No memory leaks
4. Verify: Proper cleanup on unmount
```

## Expected Results

### ✅ All Tests Should Pass

| Test | Expected | Status |
|------|----------|--------|
| Root redirect (anonymous) | Login page | ✅ |
| Root redirect (authenticated) | Dashboard | ✅ |
| Clusters page load | No reload | ✅ |
| Tenants page load | No reload | ✅ |
| Color scheme | Orange only | ✅ |
| RBAC3 permissions | Buttons disabled | ✅ |
| Icons | Correct icons | ✅ |
| Performance | <2s load | ✅ |

## Troubleshooting

### Issue: Still seeing infinite reload
**Solution**:
1. Clear browser cache (Ctrl+Shift+Delete)
2. Hard refresh (Ctrl+Shift+R)
3. Check console for errors
4. Verify backend is running

### Issue: Blue/green colors still visible
**Solution**:
1. Clear browser cache
2. Check CSS files for hardcoded colors
3. Verify Tailwind classes are correct
4. Rebuild frontend if needed

### Issue: RBAC3 buttons not working
**Solution**:
1. Verify useRBAC3 composable is imported
2. Check user has correct permissions
3. Verify backend returns permissions
4. Check console for errors

### Issue: Buttons not disabled
**Solution**:
1. Verify :disabled binding is correct
2. Check :class binding for opacity
3. Verify permission check logic
4. Test with different user roles

## Browser DevTools Checks

### Console
```javascript
// Should see no errors
// Should see auth initialization logs
// Should see RBAC3 loading logs
```

### Network
```
GET /api/v1/clusters/ → 200 OK
GET /api/v1/tenants/ → 200 OK
GET /api/v1/users/{id}/rbac → 200 OK
```

### Performance
```
- First Contentful Paint: <1s
- Largest Contentful Paint: <2s
- Cumulative Layout Shift: <0.1
```

## Sign-Off Checklist

- [ ] Root redirect works correctly
- [ ] No infinite reload on clusters page
- [ ] No infinite reload on tenants page
- [ ] All colors are orange/gray only
- [ ] No blue or green colors
- [ ] RBAC3 permissions work
- [ ] Buttons are disabled correctly
- [ ] Error messages appear
- [ ] Icons are correct
- [ ] Performance is good
- [ ] No console errors
- [ ] No memory leaks

## Notes

- Tests should be performed in both Chrome and Firefox
- Test with different user roles (admin, tenant_admin, tenant_user)
- Test on both desktop and mobile viewports
- Test with slow network (DevTools throttling)
- Test with JavaScript disabled (should show loading state)

---

**Date**: March 13, 2026
**Version**: 1.0.0
**Status**: Ready for QA Testing
