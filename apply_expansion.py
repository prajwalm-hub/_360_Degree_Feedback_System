"""
Quick Update Script: Apply RSS Feeds & Keywords Expansion
Run this after reviewing the implementation guide
"""

import shutil
import os
from datetime import datetime

# Backup existing files
def backup_files():
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backups = [
        ("backend/app/feeds.yaml", f"backend/app/feeds_backup_{timestamp}.yaml"),
        ("backend/app/goi_filter.py", f"backend/app/goi_filter_backup_{timestamp}.py"),
        ("backend/app/resources/gazetteers.py", f"backend/app/resources/gazetteers_backup_{timestamp}.py"),
    ]
    
    print("📦 Creating backups...")
    for src, dst in backups:
        if os.path.exists(src):
            shutil.copy2(src, dst)
            print(f"✅ Backed up: {src} -> {dst}")
        else:
            print(f"⚠️  File not found: {src}")
    
    print("\n✅ Backups completed!")

# Apply RSS feeds expansion
def apply_feeds_expansion():
    print("\n📡 Applying RSS Feeds Expansion...")
    src = "backend/app/feeds_expanded.yaml"
    dst = "backend/app/feeds.yaml"
    
    if os.path.exists(src):
        shutil.copy2(src, dst)
        print(f"✅ Updated {dst} with 55+ RSS feeds")
    else:
        print(f"❌ Error: {src} not found. Please create it first.")

# Instructions for manual updates
def print_manual_update_instructions():
    print("\n" + "="*70)
    print("📝 MANUAL UPDATES REQUIRED")
    print("="*70)
    
    print("""
STEP 1: Update backend/app/resources/gazetteers.py
----------------------------------------
Add the comprehensive lists from IMPLEMENTATION_GUIDE_GOI_EXPANSION.md:
- MINISTRIES (expand to 200+ entries with all language translations)
- SCHEMES (expand to 150+ entries with translations)
- GOVERNMENT_OFFICIALS (add 50+ current officials)
- INSTITUTIONS (add 40+ government bodies)

STEP 2: Update backend/app/goi_filter.py
----------------------------------------
Expand the GOI_KEYWORDS dictionary:
- Each language should have 500+ keywords (currently ~10-20)
- Include all categories: govt terms, parliament, officials, ministries, schemes

STEP 3: Test the Changes
----------------------------------------
Run: python test_feeds.py  (create this to test RSS feeds)
Run: python test_keywords.py  (create this to test keyword matching)

STEP 4: Restart Backend
----------------------------------------
cd backend
py -3.10 -m uvicorn app.main:app --host 0.0.0.0 --port 8000

STEP 5: Monitor Collection
----------------------------------------
Watch logs: tail -f logs/collector.log
Check dashboard: http://localhost:5173/
Verify article counts increase 3-4x within 24 hours

See IMPLEMENTATION_GUIDE_GOI_EXPANSION.md for complete details.
""")

if __name__ == "__main__":
    print("🚀 GoI News Filtering Expansion - Quick Update Script")
    print("="*70)
    
    # Step 1: Backup
    backup_files()
    
    # Step 2: Apply feeds expansion
    apply_feeds_expansion()
    
    # Step 3: Manual update instructions
    print_manual_update_instructions()
    
    print("\n✅ Automated steps completed!")
    print("⚠️  Please complete manual updates before restarting the backend.")
    print("📖 Full guide: IMPLEMENTATION_GUIDE_GOI_EXPANSION.md")
