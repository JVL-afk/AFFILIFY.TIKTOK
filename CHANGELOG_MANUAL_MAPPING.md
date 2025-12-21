# Changelog: Manual Profile Mapping Support

## Version 2.1 - December 2024

### Summary

Added comprehensive support for **manual profile mapping** using CSV files. This enhancement addresses the security requirement of users who have profiles split across multiple MultiLogin accounts and prefer not to provide API access to all accounts.

The manual mapping approach provides maximum security and flexibility by allowing users to specify profile UUIDs and proxy assignments directly in a CSV file, eliminating the need for API-based profile discovery.

---

## Key Features

### 1. CSV-Based Profile Configuration

The system now supports loading profile configurations from a simple CSV file format. This approach provides several advantages over API-based methods:

**Security Benefits:**
- No API credentials required for profile discovery
- Works with profiles across multiple MultiLogin accounts
- Reduces attack surface by eliminating unnecessary API access
- User maintains full control over profile data

**Operational Benefits:**
- Simple, human-readable format
- Easy to edit in spreadsheet applications
- Version control friendly
- Portable across systems

### 2. Automated CSV Template Generation

A new tool (`build_csv_mapping.py`) automatically generates a CSV template pre-populated with proxy credentials from the existing Nodemaven proxy list. This eliminates manual data entry and reduces errors.

**Features:**
- Reads existing proxy credentials
- Generates profile entries with placeholder UUIDs
- Handles proxy cycling for cases where profiles outnumber proxies
- Produces ready-to-edit CSV file

### 3. Manual Profile Loader

A dedicated loader script (`manual_profile_loader.py`) validates and imports CSV-based profile mappings into the system database. The loader includes comprehensive validation and error handling.

**Validation Features:**
- CSV format validation
- Required field checking
- Duplicate detection
- Detailed error reporting

### 4. UUID Extraction Tools

Multiple methods and tools are provided to help users extract profile UUIDs from their MultiLogin accounts:

**JavaScript Bookmarklet:**
- Runs in browser console
- Attempts automatic UUID extraction from MultiLogin web interface
- Generates CSV-formatted output
- Includes fallback instructions for manual extraction

**Documentation:**
- Step-by-step extraction guide
- Multiple extraction methods
- Screenshots and examples
- Troubleshooting tips

---

## New Files

### Core Functionality
- **`pillar1_infrastructure/manual_profile_loader.py`** - CSV-based profile loader with validation
- **`data/profile_mapping_template.csv`** - Example CSV template showing correct format

### Helper Tools
- **`tools/build_csv_mapping.py`** - Automated CSV template generator
- **`tools/multilogin_uuid_extractor.js`** - JavaScript bookmarklet for UUID extraction
- **`tools/extract_profile_uuid.md`** - Comprehensive UUID extraction guide

### Documentation
- **`MANUAL_SETUP_GUIDE.md`** - Complete setup guide for manual mapping workflow
- **`CHANGELOG_MANUAL_MAPPING.md`** - This file

---

## Modified Files

### Configuration
- **`.env.template`** - Added `MULTILOGIN_PROFILE_MODE=manual` option and `PROFILE_MAPPING_CSV` setting

### Documentation
- **`README.md`** - Updated to prominently feature manual mapping as the recommended approach for multi-account setups

---

## CSV File Format

The manual mapping CSV file uses the following structure:

```csv
profile_name,profile_uuid,proxy_host,proxy_port,proxy_username,proxy_password,multilogin_account,notes
TIKTOK1,abc123-def456-ghi789,gate.nodemaven.com,8080,session_id_1,password_1,account1@example.com,US proxy
```

**Required Fields:**
- `profile_name` - Profile identifier (e.g., TIKTOK1, TIKTOK2)
- `profile_uuid` - MultiLogin profile UUID
- `proxy_host` - Proxy server hostname
- `proxy_port` - Proxy server port
- `proxy_username` - Proxy authentication username
- `proxy_password` - Proxy authentication password

**Optional Fields:**
- `multilogin_account` - Which MultiLogin account owns this profile (for user reference)
- `notes` - Any additional notes about the profile

---

## Workflow Comparison

### Old Workflow (API-Based)
1. Provide API credentials for MultiLogin account
2. System searches for profiles via API
3. System extracts UUIDs automatically
4. Profiles loaded into database

**Limitations:**
- Requires API access to all accounts
- Security risk if credentials compromised
- Doesn't work with profiles split across accounts

### New Workflow (Manual Mapping)
1. Generate CSV template from proxy list
2. Extract profile UUIDs manually from MultiLogin UI
3. Fill in UUIDs in CSV file
4. Load CSV into system database

**Advantages:**
- No API credentials required
- Works with any number of MultiLogin accounts
- Maximum security and control
- Simple, transparent process

---

## Use Cases

This feature is specifically designed for:

### Multi-Account Security Architecture
Users who distribute their 60 profiles across 6 different MultiLogin accounts for security isolation. Each account breach would only compromise 10 profiles instead of all 60.

### Air-Gapped Operations
Users who operate the system in environments where API access is restricted or prohibited for security reasons.

### Compliance Requirements
Organizations with strict data handling policies that prohibit storing API credentials or require manual approval for profile assignments.

### Temporary or Testing Setups
Users who want to quickly test the system with a subset of profiles without setting up full API integration.

---

## Security Considerations

The manual mapping approach provides several security advantages:

**Credential Isolation:**
- MultiLogin API credentials not stored in the system
- Each account's credentials remain separate
- Reduced risk from credential theft

**Audit Trail:**
- CSV file provides clear record of profile assignments
- Easy to review and verify configurations
- Version control enables change tracking

**Principle of Least Privilege:**
- System only receives information it needs (UUIDs and proxy data)
- No unnecessary API access
- Reduced attack surface

---

## Migration Path

### From API-Based Setup to Manual Mapping

If you previously used API-based profile loading:

1. **Export Existing Data:**
   ```bash
   sqlite3 data/affilify_system.db "SELECT profile_name, profile_id, proxy_host, proxy_port, proxy_username, proxy_password FROM multilogin_profiles;" -csv -header > data/profile_mapping.csv
   ```

2. **Update Configuration:**
   ```bash
   # Edit .env file
   MULTILOGIN_PROFILE_MODE=manual
   PROFILE_MAPPING_CSV=data/profile_mapping.csv
   ```

3. **Continue Operations:**
   The system will now use the CSV file instead of API calls.

---

## Best Practices

### CSV File Management

**Version Control:**
Store your `profile_mapping.csv` in a secure version control system (e.g., private Git repository) to track changes over time.

**Backup Strategy:**
Maintain multiple backups of your CSV file in secure locations. This file is critical for system operation.

**Access Control:**
Restrict access to the CSV file as it contains sensitive proxy credentials. Use file system permissions or encryption.

### UUID Extraction

**Batch Processing:**
Extract UUIDs for 10 profiles at a time to maintain accuracy and avoid fatigue.

**Verification:**
After extracting UUIDs, verify a sample by launching test profiles before loading all 60.

**Documentation:**
Keep notes about which MultiLogin account owns which profiles for future reference.

---

## Troubleshooting

### Common Issues

**"CSV file missing required columns"**
- Ensure your CSV has all required headers
- Check for typos in column names
- Use the template generator to create a correct starting point

**"Profile UUID not found"**
- Verify you copied the complete UUID
- Check for extra spaces or line breaks
- Ensure the UUID format is correct (includes dashes)

**"Profile won't launch"**
- Confirm the MultiLogin account owning this profile is logged in
- Verify MultiLogin application is running
- Check that the UUID matches the profile

**"Wrong proxy being used"**
- Double-check the proxy credentials in your CSV
- Verify the session ID matches what was configured in the profile
- Ensure no duplicate profile entries exist

---

## Future Enhancements

Potential improvements for future versions:

- [ ] GUI-based CSV editor with validation
- [ ] Automated UUID extraction via browser extension
- [ ] Bulk profile testing tool
- [ ] CSV import/export for different formats
- [ ] Profile health check dashboard
- [ ] Automated backup and versioning

---

## Support

For questions or issues with manual mapping:

1. Review **`MANUAL_SETUP_GUIDE.md`** for complete setup instructions
2. Check **`tools/extract_profile_uuid.md`** for UUID extraction help
3. Verify CSV format matches the template in `data/profile_mapping_template.csv`
4. Test with a single profile first using `test_profile_launch.py`

---

## Credits

This enhancement was developed in response to user feedback regarding the security implications of providing API access to multiple MultiLogin accounts. The manual mapping approach provides maximum security while maintaining full system functionality.

---

**Version:** 2.1  
**Date:** December 2024  
**Status:** Production Ready  
**Recommended For:** Users with profiles across multiple accounts
