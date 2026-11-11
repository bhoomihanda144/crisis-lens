"""CrisisLens Supabase Database Connectivity & Health Test.

Member 2: Backend, Database and Integration Lead.

Run this script to verify:
1. Presence of SUPABASE_URL and SUPABASE_SERVICE_ROLE_KEY in backend/.env.
2. Active connection to the Supabase PostgreSQL database.
3. Successful insertion and retrieval of synthetic test reports.
"""

import sys
import json
from pathlib import Path

# Add backend directory to sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent))

from app.database.supabase_client import (
    get_config,
    test_connection,
    insert_sample_report,
    get_sample_reports,
    ENV_PATH,
)


def run_diagnostics():
    print("=" * 70)
    print(" CRISISLENS: SUPABASE POSTGRESQL CONNECTIVITY DIAGNOSTIC")
    print(" Member 2: Backend, Database and Integration Lead")
    print("=" * 70)

    # Step 1: Configuration check
    print(f"\n[Step 1] Inspecting environment file: {ENV_PATH}")
    try:
        config = get_config()
        print(f"  [OK] SUPABASE_URL: {config['url']}")
        key_preview = config['active_key'][:10] + "..." + config['active_key'][-6:] if len(config['active_key']) > 20 else "***"
        print(f"  [OK] Server API Key Loaded: {key_preview}")
    except ValueError as err:
        print("\n  [STOPPED] Configuration Missing or Incomplete:")
        print(f"  {err}")
        print("\n  Required Actions:")
        print("  1. Log into your team's Supabase Dashboard: https://supabase.com/dashboard")
        print("  2. Open your project -> Project Settings -> API")
        print("  3. Copy 'Project URL' into SUPABASE_URL in backend/.env")
        print("  4. Copy 'service_role secret' into SUPABASE_SERVICE_ROLE_KEY in backend/.env")
        print("  5. Re-run: python test_database.py\n")
        sys.exit(1)

    # Step 2: Connection test
    print("\n[Step 2] Pinging Supabase PostgreSQL database...")
    result = test_connection()
    if result["status"] == "error":
        print(f"  [FAILED] {result['message']}")
        print("\n  Troubleshooting Tips:")
        print("  - Did you execute the SQL schema in the Supabase SQL Editor?")
        print("    File: backend/app/database/schema.sql")
        print("  - Ensure the 'reports' table exists.")
        print("  - Verify your project is not paused in the Supabase dashboard.")
        sys.exit(2)
    else:
        print(f"  [SUCCESS] {result['message']}")
        print(f"  Current rows in 'reports' table: {result['data_count']}")

    # Step 3: Insert sample synthetic report
    print("\n[Step 3] Demonstrating sample report insertion (Synthetic/Non-emergency data)...")
    try:
        sample = insert_sample_report()
        print(f"  [SUCCESS] Inserted test report UUID: {sample.get('id')}")
        print(f"  Title: {sample.get('title')}")
        print(f"  Status: {sample.get('status')}")
    except Exception as exc:
        print(f"  [ERROR] Insertion failed: {str(exc)}")
        sys.exit(3)

    # Step 4: Retrieve reports
    print("\n[Step 4] Retrieving recent reports from Supabase...")
    try:
        reports = get_sample_reports(limit=3)
        print(f"  [SUCCESS] Retrieved {len(reports)} report(s):")
        for r in reports:
            print(f"    - ID: {r.get('id')} | Title: {r.get('title')} | Created: {r.get('created_at')}")
    except Exception as exc:
        print(f"  [ERROR] Retrieval failed: {str(exc)}")
        sys.exit(4)

    print("\n" + "=" * 70)
    print(" ALL DATABASE CONNECTIVITY CHECKS PASSED SUCCESSFULLY!")
    print("=" * 70)


if __name__ == "__main__":
    run_diagnostics()
