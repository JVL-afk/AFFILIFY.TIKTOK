/**
 * MultiLogin Profile UUID Extractor
 * ==================================
 * This bookmarklet extracts profile UUIDs from the MultiLogin web interface.
 * 
 * HOW TO USE:
 * 
 * Method 1: Browser Console
 * -------------------------
 * 1. Log into your MultiLogin account at https://app.multilogin.com
 * 2. Navigate to your profiles page
 * 3. Open browser DevTools (F12)
 * 4. Go to the Console tab
 * 5. Copy and paste this entire script
 * 6. Press Enter
 * 7. The script will output a CSV-formatted list you can copy
 * 
 * Method 2: Bookmarklet
 * ---------------------
 * 1. Create a new bookmark in your browser
 * 2. Set the URL to: javascript:(function(){...this code...})();
 * 3. Navigate to your MultiLogin profiles page
 * 4. Click the bookmarklet
 * 
 * OUTPUT:
 * The script will generate CSV output in this format:
 * profile_name,profile_uuid
 * TIKTOK1,abc123-def456-ghi789
 * TIKTOK2,bcd234-efg567-hij890
 */

(function() {
    console.log('='.repeat(70));
    console.log('MultiLogin Profile UUID Extractor');
    console.log('='.repeat(70));
    console.log('');
    
    // Try to find profile elements in the DOM
    // Note: This is a generic approach and may need adjustment based on MultiLogin's actual DOM structure
    
    let profiles = [];
    
    // Strategy 1: Look for data attributes
    const profileElements1 = document.querySelectorAll('[data-profile-id], [data-uuid]');
    profileElements1.forEach(el => {
        const uuid = el.getAttribute('data-profile-id') || el.getAttribute('data-uuid');
        const name = el.textContent.trim() || el.getAttribute('data-name') || 'Unknown';
        if (uuid && uuid.length > 10) {
            profiles.push({ name, uuid });
        }
    });
    
    // Strategy 2: Look for profile cards/rows
    const profileElements2 = document.querySelectorAll('.profile-card, .profile-row, [class*="profile"]');
    profileElements2.forEach(el => {
        // Try to find UUID in various attributes
        const allAttributes = Array.from(el.attributes);
        allAttributes.forEach(attr => {
            if (attr.value.match(/^[a-f0-9]{8}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{12}$/i)) {
                const uuid = attr.value;
                const name = el.querySelector('.profile-name, [class*="name"]')?.textContent.trim() || 'Unknown';
                profiles.push({ name, uuid });
            }
        });
    });
    
    // Strategy 3: Check for React/Vue data
    if (window.__REACT_DEVTOOLS_GLOBAL_HOOK__ || window.__VUE_DEVTOOLS_GLOBAL_HOOK__) {
        console.log('Detected React/Vue app. Checking component state...');
        // This would require more specific knowledge of MultiLogin's implementation
    }
    
    // Strategy 4: Check localStorage/sessionStorage
    try {
        const storage = { ...localStorage, ...sessionStorage };
        Object.keys(storage).forEach(key => {
            const value = storage[key];
            if (typeof value === 'string' && value.includes('uuid')) {
                try {
                    const data = JSON.parse(value);
                    if (Array.isArray(data)) {
                        data.forEach(item => {
                            if (item.uuid && item.name) {
                                profiles.push({ name: item.name, uuid: item.uuid });
                            }
                        });
                    } else if (data.uuid && data.name) {
                        profiles.push({ name: data.name, uuid: data.uuid });
                    }
                } catch (e) {
                    // Not JSON, skip
                }
            }
        });
    } catch (e) {
        console.log('Could not access storage:', e);
    }
    
    // Remove duplicates
    const uniqueProfiles = Array.from(
        new Map(profiles.map(p => [p.uuid, p])).values()
    );
    
    // Filter for TikTok profiles
    const tiktokProfiles = uniqueProfiles.filter(p => 
        p.name.toLowerCase().includes('tiktok')
    );
    
    console.log('');
    console.log(`Found ${uniqueProfiles.length} total profiles`);
    console.log(`Found ${tiktokProfiles.length} TikTok profiles`);
    console.log('');
    
    if (tiktokProfiles.length === 0) {
        console.log('⚠️  No profiles found automatically.');
        console.log('');
        console.log('MANUAL EXTRACTION INSTRUCTIONS:');
        console.log('1. Right-click on a profile in the MultiLogin interface');
        console.log('2. Select "Inspect" or "Inspect Element"');
        console.log('3. Look for attributes containing UUID-like strings');
        console.log('4. UUIDs look like: abc123-def456-ghi789-jkl012');
        console.log('');
        console.log('OR:');
        console.log('1. Open the profile settings');
        console.log('2. Look for "Profile ID" or "UUID" field');
        console.log('3. Copy the value');
        return;
    }
    
    // Generate CSV output
    console.log('CSV OUTPUT (copy this):');
    console.log('='.repeat(70));
    console.log('profile_name,profile_uuid');
    
    tiktokProfiles.forEach(profile => {
        console.log(`${profile.name},${profile.uuid}`);
    });
    
    console.log('='.repeat(70));
    console.log('');
    console.log('NEXT STEPS:');
    console.log('1. Copy the CSV output above');
    console.log('2. Paste it into a text editor');
    console.log('3. Add proxy information for each profile');
    console.log('4. Save as profile_mapping.csv');
    console.log('5. Run: python3 pillar1_infrastructure/manual_profile_loader.py');
    console.log('');
    
})();
