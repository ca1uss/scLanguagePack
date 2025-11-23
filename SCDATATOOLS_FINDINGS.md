# scdatatools Investigation Results

## Goal
Attempt to use `scdatatools` to extract component data directly from Star Citizen game files (`Data.p4k`) as a "Source of Truth" for the language pack audit.

## Findings

### Installation
- **Status**: ✅ Success (with manual dependency resolution)
- **Issues Encountered**:
  - `pycryptodome` v3.9.0 (required by scdatatools) wouldn't compile (missing C++ tools)
  - **Workaround**: Installed modern `pycryptodome` binary, then used `pip install scdatatools --no-deps`
  - Had to manually install 10+ missing dependencies

### Compatibility with SC 4.4.0
- **Status**: ❌ Failed
- **Root Cause**: scdatatools appears incompatible with Star Citizen 4.4.0-LIVE

#### Errors Encountered:
1. **DataCoreBinary Parser**:
   ```
   AssertionError in DataCoreBinary.__init__()
   assert offset == len(self.raw_data)
   ```
   - Attempted to parse `Data/Game2.dcb`
   - Parser expects a different file structure than what 4.4.0 provides

2. **Localization Manager**:
   ```
   UnicodeDecodeError: 'utf-8' codec can't decode byte 0xa0
   ```
   - Localization files may have changed encoding in 4.4.0
   - Module hardcoded to use UTF-8

### Conclusion
`scdatatools` is likely maintained for an older version of Star Citizen and has not been updated for 4.4.0. The library can successfully:
- Find the SC installation ✅
- Open `Data.p4k` ✅  
- List files in the archive ✅

But fails when attempting to:
- Parse `Game2.dcb` (DataCore) ❌
- Read localization files ❌
- **CLI tool `scdt unforge`** ❌ (completes but produces no output)
- **CLI tool `scdt unp4k`** ❌ (completes but extracts no files)

### User's Valid Points
1. The user correctly identified I should use the `scdt` CLI tool instead of the Python API. However, testing confirmed the CLI tools also fail silently without extracting any data.
2. The user suggested admin privileges might be the issue - testing confirmed we CAN read the P4K file, so permissions are not the problem.
3. The user noted that Erkul likely uses scdatatools - research confirms this is true.

### Patch Attempt
After the user's insights, I discovered the root cause:
- **Bug Found**: `scdatatools` was hardcoded to look for `Data/Game.dcb`
- **Reality**: SC 4.4.0 uses `Data/Game2.dcb`
- **Fix Applied**: Patched the scdatatools source file (lines 175, 251, 252) to use `Game2.dcb`
- **Result**: The file is now found, but the DataCoreBinary parser still fails with `AssertionError`

### Version Compatibility Analysis
- **scdatatools v1.0.4**: Last released **August 2022** (3+ years ago)
- **Star Citizen 4.4.0**: Released **November 2025**
- **Conclusion**: The DCB file format has changed over 3 years, and the parser logic is incompatible

### How Erkul Works
Erkul.games likely uses either:
1. A custom/patched version of scdatatools (not publicly available)
2. A completely different extraction method
3. An unreleased development version with 4.4.0 support

## Final Recommendation
**Return to Erkul.games scraping approach** with the following improvements:
1. Fix the auto-scroll logic to properly load all components
2. Improve parsing robustness for the flat table structure  
3. Add retry logic for network failures

This is more practical than maintaining a fork of scdatatools or waiting for an official update.
