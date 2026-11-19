import os
import sys
import uvicorn

if __name__ == "__main__":
    root_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(root_dir)
    sys.path.insert(0, root_dir)

    print("=" * 70)
    print("      VIRASAT SETU (Virasat Setu) - SERVER ENGINE")
    print("      National Digital Inheritance and Asset Discovery Platform")
    print("=" * 70)
    print("\n[+] Initializing database and verifying sample records...")

    try:
        from app.seed.sample_data import seed_all
        seed_all()
    except Exception as e:
        print(f"[-] Note on seed: {e}")

    print("\n[+] SYSTEM IS READY FOR LIVE PRESENTATION AND EVALUATION")
    print("-" * 70)
    print("  >> Web Application URL  : http://127.0.0.1:8000")
    print("  >> Swagger API Docs URL : http://127.0.0.1:8000/docs")
    print("-" * 70)
    print("  DEMO PRESET CREDENTIALS (1-Click Login available in header):")
    print("  1. Family Member (Son)  : rajesh.family@example.com  /  family123")
    print("  2. Govt Administrator   : admin@virasatsetu.gov.in   /  admin123")
    print("  3. SBI Bank Officer     : sbi@institution.in         /  sbi123")
    print("  4. LIC Claims Officer   : lic@institution.in         /  lic123")
    print("  5. HDFC Fund Manager    : hdfcmf@institution.in      /  hdfc123")
    print("-" * 70)
    print("  PRIMARY DEMO SCENARIO:")
    print("  Rajesh Kumar (Deceased) has 17,86,240 INR across 3 financial sectors:")
    print("  - SBI Bank Fixed Deposit (3,45,000 INR) and Savings (78,500 INR)")
    print("  - LIC Jeevan Anand Policy (8,50,000 INR)")
    print("  - HDFC Top 100 Equity Mutual Fund (5,12,740 INR)")
    print("=" * 70 + "\n")

    uvicorn.run("app.main:app", host="127.0.0.1", port=8000, reload=False)
