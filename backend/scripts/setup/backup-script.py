import os
import shutil
import sqlite3
import json
from datetime import datetime
import zipfile

def create_backup():
    """Create a comprehensive backup of the PrevostGO project"""
    
    # Get current timestamp for backup naming
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_name = f"prevostgo_backup_{timestamp}"
    
    # Define paths
    project_root = r"C:\Users\tmcha\Dev\prevostgo"
    backup_root = os.path.join(project_root, "..", "prevostgo_backups", backup_name)
    
    print(f"Creating backup: {backup_name}")
    
    # Create backup directory
    os.makedirs(backup_root, exist_ok=True)
    
    # 1. Backup Frontend
    print("Backing up frontend...")
    frontend_src = os.path.join(project_root, "frontend")
    frontend_dst = os.path.join(backup_root, "frontend")
    
    # Copy frontend, excluding node_modules and build artifacts
    shutil.copytree(
        frontend_src, 
        frontend_dst,
        ignore=shutil.ignore_patterns('node_modules', 'dist', 'build', '.next', '*.log')
    )
    
    # 2. Backup Backend
    print("Backing up backend...")
    backend_src = os.path.join(project_root, "backend")
    backend_dst = os.path.join(backup_root, "backend")
    
    # Copy backend, excluding virtual environment and cache
    shutil.copytree(
        backend_src,
        backend_dst,
        ignore=shutil.ignore_patterns('venv', '__pycache__', '*.pyc', '.pytest_cache', '*.log')
    )
    
    # 3. Create database backup with stats
    print("Backing up database with statistics...")
    db_src = os.path.join(project_root, "backend", "prevostgo.db")
    db_dst = os.path.join(backup_root, "backend", "prevostgo.db")
    
    if os.path.exists(db_src):
        # Copy database
        shutil.copy2(db_src, db_dst)
        
        # Generate database stats
        conn = sqlite3.connect(db_src)
        cursor = conn.cursor()
        
        stats = {
            "backup_date": timestamp,
            "database_stats": {}
        }
        
        # Get coach count by status
        cursor.execute("SELECT status, COUNT(*) FROM coaches GROUP BY status")
        stats["database_stats"]["coaches_by_status"] = dict(cursor.fetchall())
        
        # Get coach count by model
        cursor.execute("SELECT model, COUNT(*) FROM coaches WHERE model IS NOT NULL GROUP BY model")
        stats["database_stats"]["coaches_by_model"] = dict(cursor.fetchall())
        
        # Get coach count by converter
        cursor.execute("SELECT converter, COUNT(*) FROM coaches WHERE converter IS NOT NULL GROUP BY converter")
        stats["database_stats"]["coaches_by_converter"] = dict(cursor.fetchall())
        
        # Total coaches
        cursor.execute("SELECT COUNT(*) FROM coaches")
        stats["database_stats"]["total_coaches"] = cursor.fetchone()[0]
        
        conn.close()
        
        # Save stats
        with open(os.path.join(backup_root, "database_stats.json"), "w") as f:
            json.dump(stats, f, indent=2)
    
    # 4. Copy root level files
    print("Backing up configuration files...")
    root_files = [
        "README.md",
        "QUICKSTART.md",
        "setup.ps1",
        "setup.sh",
        ".gitignore",
        "updatednotes.txt"
    ]
    
    for file in root_files:
        src = os.path.join(project_root, file)
        if os.path.exists(src):
            shutil.copy2(src, os.path.join(backup_root, file))
    
    # 5. Create a state summary
    print("Creating state summary...")
    state_summary = {
        "backup_timestamp": timestamp,
        "working_features": [
            "Frontend running on localhost:3000",
            "Search by keyword (e.g., 'Marathon')",
            "Filter by chassis type (H3-45, XLII, XL, X3)",
            "Filter by converter with fuzzy matching",
            "Filter by price range",
            "Filter by year range",
            "Filter by number of slides",
            "Combined filters working"
        ],
        "known_issues": [
            "Database has 391 coaches instead of 700+",
            "Backend may have Python 3.13 compatibility issues",
            "Need to run scraper_final_v2.py to get all coaches"
        ],
        "recent_fixes": [
            "Fixed chassis filter to use fuzzy matching",
            "Fixed parameter naming consistency (price_min/max)",
            "Updated dropdown values to match database content",
            "Added fuzzy matching for converter filter"
        ],
        "next_steps": [
            "Implement MCP architecture",
            "Create MCP server for search functionality",
            "Fix remaining data population issues"
        ]
    }
    
    with open(os.path.join(backup_root, "PROJECT_STATE.json"), "w") as f:
        json.dump(state_summary, f, indent=2)
    
    # 6. Create ZIP archive
    print("Creating ZIP archive...")
    zip_path = os.path.join(project_root, "..", "prevostgo_backups", f"{backup_name}.zip")
    
    with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, dirs, files in os.walk(backup_root):
            for file in files:
                file_path = os.path.join(root, file)
                arcname = os.path.relpath(file_path, backup_root)
                zipf.write(file_path, arcname)
    
    print(f"\n✅ Backup completed successfully!")
    print(f"📁 Backup location: {backup_root}")
    print(f"🗜️  ZIP archive: {zip_path}")
    print(f"\nBackup includes:")
    print("- Frontend code (without node_modules)")
    print("- Backend code (without venv)")
    print("- Database with current data")
    print("- Configuration files")
    print("- Project state summary")
    
    return backup_root, zip_path

if __name__ == "__main__":
    try:
        backup_dir, zip_file = create_backup()
        print("\n💡 Tip: The ZIP file is perfect for version control or sharing")
        print("💡 Tip: Keep the PROJECT_STATE.json for reference when implementing MCP")
    except Exception as e:
        print(f"\n❌ Backup failed: {e}")
        import traceback
        traceback.print_exc()
