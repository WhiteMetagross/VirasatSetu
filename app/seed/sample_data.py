import uuid
from datetime import datetime, timedelta
from app.database import DatabaseSession, Base, engine
from app.models.models import (
    User, Institution, DeceasedPerson, Claimant, FinancialAsset,
    AssetMatch, Claim, Document, Notification, AuditLog
)
from app.utils.auth import hash_password

def seed_all():
    # Re-create tables
    Base.metadata.create_all(bind=engine)
    db = DatabaseSession()

    try:
        # Check if already seeded
        if db.query(User).filter(User.email == "admin@virasatsetu.gov.in").first():
            print("Database already seeded with sample data.")
            return

        print("Seeding Virasat Setu database with realistic prototype data...")

        # 1. Institutions
        institutions = [
            Institution(
                id=str(uuid.uuid4()),
                name="State Bank of India",
                code="SBI",
                category="bank",
                contact_email="unclaimed@sbi.co.in",
                phone="1800-425-3800",
                address="State Bank Bhavan, Madame Cama Road, Nariman Point, Mumbai"
            ),
            Institution(
                id=str(uuid.uuid4()),
                name="Punjab National Bank",
                code="PNB",
                category="bank",
                contact_email="nodal@pnbindia.in",
                phone="1800-180-2222",
                address="Plot No 4, Sector 10, Dwarka, New Delhi"
            ),
            Institution(
                id=str(uuid.uuid4()),
                name="ICICI Bank",
                code="ICICI",
                category="bank",
                contact_email="unclaimedcell@icicibank.com",
                phone="1800-200-3344",
                address="ICICI Bank Towers, Bandra Kurla Complex, Mumbai"
            ),
            Institution(
                id=str(uuid.uuid4()),
                name="Life Insurance Corporation of India (LIC)",
                code="LIC",
                category="insurance",
                contact_email="claims.help@licindia.com",
                phone="022-68276827",
                address="Yogakshema, Jeevan Bima Marg, Nariman Point, Mumbai"
            ),
            Institution(
                id=str(uuid.uuid4()),
                name="Max Life Insurance",
                code="MAXLIFE",
                category="insurance",
                contact_email="claims@maxlifeinsurance.com",
                phone="1860-120-5577",
                address="Max House, 1 Dr Jha Marg, Okhla, New Delhi"
            ),
            Institution(
                id=str(uuid.uuid4()),
                name="HDFC Mutual Fund",
                code="HDFCMF",
                category="mutual_fund",
                contact_email="investor.service@hdfcfund.com",
                phone="1800-3010-6767",
                address="HDFC House, 165-166 Backbay Reclamation, Churchgate, Mumbai"
            ),
            Institution(
                id=str(uuid.uuid4()),
                name="SBI Mutual Fund",
                code="SBIMF",
                category="mutual_fund",
                contact_email="partner@sbimf.com",
                phone="1800-209-3333",
                address="9th Floor, Crescenzo, C-38 and 39, G Block, BKC, Mumbai"
            ),
        ]
        for inst in institutions:
            db.add(inst)
        db.commit()

        # Helper lookup for institutions by code
        inst_map = {inst.code: inst for inst in institutions}

        # 2. Users (Admin, Institution Reps, Family Users)
        users = [
            User(
                id=str(uuid.uuid4()),
                email="admin@virasatsetu.gov.in",
                hashed_password=hash_password("admin123"),
                full_name="Rajiv Nambiar (Govt Administrator)",
                mobile="9811223344",
                role="admin"
            ),
            User(
                id=str(uuid.uuid4()),
                email="sbi@institution.in",
                hashed_password=hash_password("sbi123"),
                full_name="Sanjay Verma (SBI Officer)",
                mobile="9822334455",
                role="institution_rep",
                institution_id=inst_map["SBI"].id
            ),
            User(
                id=str(uuid.uuid4()),
                email="lic@institution.in",
                hashed_password=hash_password("lic123"),
                full_name="Meenakshi Sundaram (LIC Claims Officer)",
                mobile="9833445566",
                role="institution_rep",
                institution_id=inst_map["LIC"].id
            ),
            User(
                id=str(uuid.uuid4()),
                email="hdfcmf@institution.in",
                hashed_password=hash_password("hdfc123"),
                full_name="Arunav Sen (HDFC MF Representative)",
                mobile="9844556677",
                role="institution_rep",
                institution_id=inst_map["HDFCMF"].id
            ),
            User(
                id=str(uuid.uuid4()),
                email="rajesh.family@example.com",
                hashed_password=hash_password("family123"),
                full_name="Ramesh Kumar",
                mobile="9876543210",
                role="family_user"
            ),
            User(
                id=str(uuid.uuid4()),
                email="priya.sharma@example.com",
                hashed_password=hash_password("family123"),
                full_name="Priya Sharma",
                mobile="9988776655",
                role="family_user"
            )
        ]
        for u in users:
            db.add(u)
        db.commit()

        user_map = {u.email: u for u in users}

        # 3. Financial Assets (40+ Bank, 25+ Insurance, 25+ Mutual Fund)
        # Note: Must include the Rajesh Kumar test case (ID: ABCDE1234F, DOB: 1965-04-12)
        financial_records = []

        # --- A. BANK RECORDS (42 records) ---
        bank_data = [
            # Rajesh Kumar (The primary demonstration scenario!)
            ("SBI", "Rajesh Kumar", "1965-04-12", "ABCDE1234F", "SB-4019284102", "Fixed Deposit", "Ramesh Kumar (Son)", 345000.0, "Dormant Term Deposit > 10 Years", "CP Branch, New Delhi (IFSC: SBIN0000691)"),
            ("SBI", "Rajesh Kumar", "1965-04-12", "ABCDE1234F", "SB-1092837461", "Savings Account", "Ramesh Kumar (Son)", 78500.0, "Inoperative Savings Account > 10 Years", "Karol Bagh Branch, New Delhi (IFSC: SBIN0000342)"),
            ("PNB", "Suresh Chandra Gupta", "1958-09-20", "BNKPG9981K", "PNB-99281726", "Savings Account", "Sunita Gupta (Wife)", 182000.0, "Dormant > 10 Yrs", "Civil Lines, Agra"),
            ("ICICI", "Anand Mohan Joshi", "1962-11-05", "AJOPJ4412B", "IC-10293847", "Fixed Deposit", "Aditi Joshi (Daughter)", 520000.0, "Matured Unclaimed FD", "Bandra West, Mumbai"),
            ("SBI", "Gopal Krishna Murthy", "1950-03-15", "GKMPS1122C", "SB-8827163501", "Pension Account", "Saraswati Murthy (Spouse)", 143000.0, "Inoperative > 10 Yrs", "Malleswaram, Bengaluru"),
            ("PNB", "Harpreet Singh Sodhi", "1968-07-22", "HSSPS7788P", "PNB-44112233", "Current Account", "Gurpreet Singh (Son)", 310000.0, "Inoperative > 10 Yrs", "Sector 17, Chandigarh"),
            ("ICICI", "Lakshmi Narayanan", "1954-12-30", "LMNPN6677Q", "IC-99887766", "Special Term Deposit", "Venkatesh L (Son)", 680000.0, "Matured Unclaimed", "T Nagar, Chennai"),
            ("SBI", "Bimal Kanti Ghosh", "1960-01-18", "BKGPG3344R", "SB-7733991100", "Savings Account", "Anindita Ghosh (Wife)", 95000.0, "Inoperative > 10 Yrs", "Salt Lake, Kolkata"),
            ("PNB", "Manorama Devi", "1948-08-14", "MRMDV5566T", "PNB-66554433", "Savings Account", "Rajeshwar Prasad (Son)", 215000.0, "Dormant > 10 Yrs", "Kankarbagh, Patna"),
            ("ICICI", "Devendra Nath Tiwari", "1963-05-10", "DNTPI8899U", "IC-33221100", "Fixed Deposit", "Alok Tiwari (Son)", 410000.0, "Matured Unclaimed", "Hazratganj, Lucknow"),
            ("SBI", "Pushpa Ben Patel", "1952-10-25", "PBPPA2233V", "SB-5566778899", "Recurring Deposit", "Kirit Patel (Son)", 165000.0, "Matured Unclaimed", "Navrangpura, Ahmedabad"),
            ("PNB", "Om Prakash Sharma", "1957-06-03", "OPKPS1199W", "PNB-88776655", "Savings Account", "Neeta Sharma (Wife)", 125000.0, "Dormant > 10 Yrs", "MI Road, Jaipur"),
            ("ICICI", "Kavita Rao", "1970-02-14", "KVRPR9911X", "IC-55443322", "Savings Account", "Siddharth Rao (Son)", 88000.0, "Inoperative > 10 Yrs", "Banjara Hills, Hyderabad"),
            ("SBI", "Subhash Chandra Bose", "1961-04-09", "SCBPS7722Y", "SB-1122334455", "Fixed Deposit", "Anita Bose (Wife)", 720000.0, "Matured Unclaimed", "Gariahat, Kolkata"),
            ("PNB", "Jagdish Chander", "1955-11-28", "JCHPC4433Z", "PNB-22334455", "Pension Account", "Santosh Kumari (Wife)", 150000.0, "Dormant > 10 Yrs", "Ludhiana GT Road"),
            ("ICICI", "Farida Begum", "1964-08-19", "FBGPR8844A", "IC-77889900", "Savings Account", "Tariq Ahmed (Son)", 92000.0, "Inoperative > 10 Yrs", "Charminar, Hyderabad"),
            ("SBI", "Ramesh Chandra Das", "1953-09-07", "RCDPD3322B", "SB-9900112233", "Savings Account", "Pranab Das (Son)", 110000.0, "Inoperative > 10 Yrs", "Saheed Nagar, Bhubaneswar"),
            ("PNB", "Kailash Chand Verma", "1966-12-12", "KCVPA7711C", "PNB-11998877", "Fixed Deposit", "Vimla Verma (Wife)", 390000.0, "Matured Unclaimed", "Dehradun Rajpur Road"),
            ("ICICI", "Vijay Kumar Singhania", "1959-03-31", "VKSPA6655D", "IC-66778899", "Current Account", "Rohit Singhania (Son)", 840000.0, "Dormant > 10 Yrs", "MG Road, Pune"),
            ("SBI", "Parvati Ammal", "1949-05-20", "PAMPA9988E", "SB-4455667788", "Term Deposit", "Muthusamy (Husband)", 290000.0, "Matured Unclaimed", "Madurai Main Branch"),
            ("PNB", "Bhagwan Sahai", "1956-07-16", "BSHPA4422F", "PNB-33445566", "Savings Account", "Kishan Lal (Son)", 75000.0, "Dormant > 10 Yrs", "Ajmer Bus Stand Branch"),
            ("ICICI", "Cyrus Jamshedji Irani", "1961-10-04", "CJIPA1133G", "IC-44556677", "Fixed Deposit", "Roxanne Irani (Daughter)", 610000.0, "Matured Unclaimed", "Colaba, Mumbai"),
            ("SBI", "Shyamal Kanti Sen", "1967-01-23", "SKSPS8822H", "SB-2233114455", "Savings Account", "Sumita Sen (Wife)", 135000.0, "Inoperative > 10 Yrs", "Howrah Station Branch"),
            ("PNB", "Santosh Devi Yadav", "1951-04-17", "SDYPA3311I", "PNB-55664422", "Savings Account", "Ram Avtar Yadav (Son)", 180000.0, "Dormant > 10 Yrs", "Rewari, Haryana"),
            ("ICICI", "Naveen Chand Jain", "1965-06-29", "NCJPA5544J", "IC-88990011", "Special FD", "Arpit Jain (Son)", 480000.0, "Matured Unclaimed", "Indore AB Road"),
            ("SBI", "Hemant Kumar Barua", "1958-02-11", "HKBPA7766K", "SB-6677881122", "Pension Account", "Binita Barua (Wife)", 140000.0, "Dormant > 10 Yrs", "Guwahati Panbazar"),
            ("PNB", "Mahmood Ali Khan", "1960-09-08", "MAKPA9944L", "PNB-77881122", "Savings Account", "Nasreen Khan (Wife)", 115000.0, "Inoperative > 10 Yrs", "Bhopal MP Nagar"),
            ("ICICI", "Sujata Mukherjee", "1969-12-01", "SMKPA2288M", "IC-11229988", "Savings Account", "Debashis Mukherjee (Husband)", 195000.0, "Inoperative > 10 Yrs", "Kolkata Jadavpur"),
            ("SBI", "Girish Chandra Joshi", "1953-11-19", "GCJPA6611N", "SB-8899223344", "Fixed Deposit", "Usha Joshi (Wife)", 330000.0, "Matured Unclaimed", "Nainital Mall Road"),
            ("PNB", "Prakash Rao Deshmukh", "1957-08-25", "PRDPA4499O", "PNB-99112244", "Savings Account", "Kavita Deshmukh (Daughter)", 160000.0, "Dormant > 10 Yrs", "Nagpur Sitabuldi"),
            ("ICICI", "Anthony Francis D'Souza", "1963-03-12", "AFDPA1177P", "IC-33441122", "Term Deposit", "Maria D'Souza (Wife)", 570000.0, "Matured Unclaimed", "Panaji, Goa"),
            ("SBI", "Radha Raman Shukla", "1947-01-30", "RRSPA8833Q", "SB-7711228844", "Pension Account", "Mridula Shukla (Wife)", 190000.0, "Inoperative > 10 Yrs", "Varanasi Cantt"),
            ("PNB", "Gurvinder Kaur", "1964-07-07", "GKRPA3388R", "PNB-22446688", "Savings Account", "Manjit Singh (Son)", 105000.0, "Dormant > 10 Yrs", "Amritsar Hall Gate"),
            ("ICICI", "Balasubramaniam Iyer", "1956-10-18", "BSIER5599S", "IC-99221144", "Fixed Deposit", "Gayatri Iyer (Daughter)", 625000.0, "Matured Unclaimed", "Coimbatore RS Puram"),
            ("SBI", "Dina Nath Bhatt", "1962-05-14", "DNBPA7744T", "SB-3311884422", "Savings Account", "Saroj Bhatt (Wife)", 140000.0, "Inoperative > 10 Yrs", "Shimla Ridge Branch"),
            ("PNB", "Malkiat Singh", "1950-12-05", "MSHPA2255U", "PNB-44881133", "Savings Account", "Paramjit Singh (Son)", 220000.0, "Dormant > 10 Yrs", "Jalandhar Model Town"),
            ("ICICI", "Sudhir Purushottam Kulkarni", "1961-08-21", "SPKPA8811V", "IC-77334411", "Term Deposit", "Meera Kulkarni (Wife)", 430000.0, "Matured Unclaimed", "Nashik Canada Corner"),
            ("SBI", "Geeta Rani Das", "1954-04-03", "GRDPA4466W", "SB-9933557711", "Savings Account", "Subir Das (Son)", 98000.0, "Inoperative > 10 Yrs", "Siliguri Sevoke Road"),
            ("PNB", "Satish Chandra Aggarwal", "1959-06-17", "SCAPA1188X", "PNB-66228844", "Current Account", "Pankaj Aggarwal (Son)", 375000.0, "Inoperative > 10 Yrs", "Delhi Chandni Chowk"),
            ("ICICI", "Tara Chand Meena", "1968-09-11", "TCMPS6622Y", "IC-55118822", "Savings Account", "Kamla Meena (Wife)", 110000.0, "Dormant > 10 Yrs", "Kota Aerodrome Circle"),
            ("SBI", "Madhavan Pillai", "1952-11-23", "MPLPA9933Z", "SB-1144772299", "Pension Account", "Leela Pillai (Wife)", 265000.0, "Inoperative > 10 Yrs", "Thiruvananthapuram MG Road"),
            ("PNB", "Kuldeep Narang", "1965-02-28", "KDNPA3366A", "PNB-88331177", "Fixed Deposit", "Sonia Narang (Daughter)", 310000.0, "Matured Unclaimed", "Faridabad Sector 15"),
        ]

        for inst_code, holder, dob, id_ref, acc_ref, cat, nominee, val, unclaim_st, details in bank_data:
            financial_records.append(FinancialAsset(
                id=str(uuid.uuid4()),
                institution_id=inst_map[inst_code].id,
                asset_type="bank",
                institution_name=inst_map[inst_code].name,
                holder_name=holder,
                date_of_birth=dob,
                sample_identity_ref=id_ref,
                account_ref=acc_ref,
                category=cat,
                nominee_ref=nominee,
                status="Unclaimed",
                unclaimed_status=unclaim_st,
                approximate_value=val,
                details_json=details
            ))

        # --- B. INSURANCE RECORDS (26 records) ---
        insurance_data = [
            # Rajesh Kumar (The primary demonstration scenario!)
            ("LIC", "Rajesh Kumar", "1965-04-12", "ABCDE1234F", "POL-928172635", "Jeevan Anand Endowment Policy", "Ramesh Kumar (Son)", 850000.0, "Matured Unclaimed Payout", "Divisional Office 1, Jeevan Prakash, Kasturba Gandhi Marg, New Delhi"),
            ("MAXLIFE", "Suresh Chandra Gupta", "1958-09-20", "BNKPG9981K", "POL-771234901", "Smart Wealth Plan", "Sunita Gupta (Wife)", 420000.0, "Unclaimed Maturity Proceeds", "Agra Sanjay Place Branch"),
            ("LIC", "Anand Mohan Joshi", "1962-11-05", "AJOPJ4412B", "POL-119283746", "Jeevan Labh Policy", "Aditi Joshi (Daughter)", 650000.0, "Matured Unclaimed", "Mumbai Branch 882"),
            ("LIC", "Gopal Krishna Murthy", "1950-03-15", "GKMPS1122C", "POL-441199223", "Bima Gold Policy", "Saraswati Murthy (Spouse)", 320000.0, "Unclaimed Death Benefit", "Bengaluru City Branch"),
            ("MAXLIFE", "Harpreet Singh Sodhi", "1968-07-22", "HSSPS7788P", "POL-883344112", "Term Life Protection", "Gurpreet Singh (Son)", 1500000.0, "Unclaimed Payout", "Chandigarh Sector 34"),
            ("LIC", "Lakshmi Narayanan", "1954-12-30", "LMNPN6677Q", "POL-662288331", "Jeevan Saral", "Venkatesh L (Son)", 510000.0, "Matured Unclaimed", "Chennai Anna Salai Branch"),
            ("LIC", "Bimal Kanti Ghosh", "1960-01-18", "BKGPG3344R", "POL-339911224", "Jeevan Umang", "Anindita Ghosh (Wife)", 480000.0, "Survival Benefit Unclaimed", "Kolkata Chittaranjan Ave"),
            ("MAXLIFE", "Manorama Devi", "1948-08-14", "MRMDV5566T", "POL-554422998", "Guaranteed Income Plan", "Rajeshwar Prasad (Son)", 370000.0, "Unclaimed Maturity", "Patna Fraser Road"),
            ("LIC", "Devendra Nath Tiwari", "1963-05-10", "DNTPI8899U", "POL-228844115", "Kanyadan Policy", "Alok Tiwari (Son)", 620000.0, "Matured Unclaimed", "Lucknow Alambagh"),
            ("MAXLIFE", "Pushpa Ben Patel", "1952-10-25", "PBPPA2233V", "POL-991133557", "Super Term Plan", "Kirit Patel (Son)", 550000.0, "Unclaimed Proceeds", "Ahmedabad Ashram Road"),
            ("LIC", "Om Prakash Sharma", "1957-06-03", "OPKPS1199W", "POL-447722991", "Money Back Policy 20 Yrs", "Neeta Sharma (Wife)", 290000.0, "Unclaimed Survival Benefit", "Jaipur C-Scheme"),
            ("MAXLIFE", "Kavita Rao", "1970-02-14", "KVRPR9911X", "POL-118833664", "Smart Secure Plus", "Siddharth Rao (Son)", 1200000.0, "Unclaimed Benefit", "Hyderabad Begumpet"),
            ("LIC", "Subhash Chandra Bose", "1961-04-09", "SCBPS7722Y", "POL-773355118", "Jeevan Akshay Pension", "Anita Bose (Wife)", 410000.0, "Unclaimed Annuity Payout", "Kolkata Rashbehari Ave"),
            ("LIC", "Jagdish Chander", "1955-11-28", "JCHPC4433Z", "POL-882266443", "Jeevan Mitra Policy", "Santosh Kumari (Wife)", 350000.0, "Matured Unclaimed", "Ludhiana Ferozepur Road"),
            ("MAXLIFE", "Farida Begum", "1964-08-19", "FBGPR8844A", "POL-331177992", "Savings Advantage Plan", "Tariq Ahmed (Son)", 280000.0, "Unclaimed Payout", "Hyderabad Abids"),
            ("LIC", "Ramesh Chandra Das", "1953-09-07", "RCDPD3322B", "POL-664411885", "Jeevan Rakshak", "Pranab Das (Son)", 230000.0, "Matured Unclaimed", "Bhubaneswar Janpath"),
            ("MAXLIFE", "Kailash Chand Verma", "1966-12-12", "KCVPA7711C", "POL-995522771", "Life Gain Plan", "Vimla Verma (Wife)", 490000.0, "Unclaimed Maturity", "Dehradun Clock Tower"),
            ("LIC", "Vijay Kumar Singhania", "1959-03-31", "VKSPA6655D", "POL-114488339", "Jeevan Shiromani", "Rohit Singhania (Son)", 2100000.0, "Unclaimed Maturity", "Pune Shivajinagar"),
            ("LIC", "Parvati Ammal", "1949-05-20", "PAMPA9988E", "POL-552299663", "Jeevan Tarun", "Muthusamy (Husband)", 270000.0, "Matured Unclaimed", "Madurai Palace Road"),
            ("MAXLIFE", "Bhagwan Sahai", "1956-07-16", "BSHPA4422F", "POL-779933114", "Whole Life Plan", "Kishan Lal (Son)", 310000.0, "Unclaimed Benefit", "Jaipur Tonk Road"),
            ("LIC", "Cyrus Jamshedji Irani", "1961-10-04", "CJIPA1133G", "POL-226611448", "New Endowment Plan", "Roxanne Irani (Daughter)", 780000.0, "Matured Unclaimed", "Mumbai Dadar Branch"),
            ("MAXLIFE", "Shyamal Kanti Sen", "1967-01-23", "SKSPS8822H", "POL-881144772", "Smart Fixed Return", "Sumita Sen (Wife)", 390000.0, "Unclaimed Payout", "Kolkata Park Street"),
            ("LIC", "Santosh Devi Yadav", "1951-04-17", "SDYPA3311I", "POL-443388226", "Jeevan Shanti Annuity", "Ram Avtar Yadav (Son)", 440000.0, "Unclaimed Annuity", "Gurugram Sector 14"),
            ("LIC", "Naveen Chand Jain", "1965-06-29", "NCJPA5544J", "POL-998822551", "Bima Bachat", "Arpit Jain (Son)", 530000.0, "Survival Benefit Unclaimed", "Indore MG Road"),
            ("MAXLIFE", "Hemant Kumar Barua", "1958-02-11", "HKBPA7766K", "POL-336699117", "Life Milestone Plan", "Binita Barua (Wife)", 360000.0, "Unclaimed Maturity", "Guwahati GS Road"),
            ("LIC", "Mahmood Ali Khan", "1960-09-08", "MAKPA9944L", "POL-661133884", "Jeevan Labh 25 Yrs", "Nasreen Khan (Wife)", 680000.0, "Matured Unclaimed", "Bhopal TT Nagar"),
        ]

        for inst_code, holder, dob, id_ref, pol_ref, cat, nominee, val, unclaim_st, details in insurance_data:
            financial_records.append(FinancialAsset(
                id=str(uuid.uuid4()),
                institution_id=inst_map[inst_code].id,
                asset_type="insurance",
                institution_name=inst_map[inst_code].name,
                holder_name=holder,
                date_of_birth=dob,
                sample_identity_ref=id_ref,
                account_ref=pol_ref,
                category=cat,
                nominee_ref=nominee,
                status="Unclaimed",
                unclaimed_status=unclaim_st,
                approximate_value=val,
                details_json=details
            ))

        # --- C. MUTUAL FUND RECORDS (26 records) ---
        mf_data = [
            # Rajesh Kumar (The primary demonstration scenario!)
            ("HDFCMF", "Rajesh Kumar", "1965-04-12", "ABCDE1234F", "FOL-77281903", "HDFC Top 100 Equity Fund (Growth)", "Ramesh Kumar (Son)", 512740.0, "Unclaimed Redemption and Dividends", "Folio: 77281903/81, Units: 4,820.55, NAV: 106.36"),
            ("SBIMF", "Suresh Chandra Gupta", "1958-09-20", "BNKPG9981K", "FOL-33119944", "SBI Bluechip Fund Regular Growth", "Sunita Gupta (Wife)", 310000.0, "Unclaimed Dividend Proceeds", "Folio: 33119944/12, Units: 3,920.10"),
            ("HDFCMF", "Anand Mohan Joshi", "1962-11-05", "AJOPJ4412B", "FOL-99882211", "HDFC Balanced Advantage Fund", "Aditi Joshi (Daughter)", 480000.0, "Unclaimed Redemption", "Folio: 99882211/04, Units: 9,210.00"),
            ("SBIMF", "Gopal Krishna Murthy", "1950-03-15", "GKMPS1122C", "FOL-11447788", "SBI Magnum Equity ESG Fund", "Saraswati Murthy (Spouse)", 240000.0, "Unclaimed Dividends", "Folio: 11447788/90, Units: 2,150.40"),
            ("HDFCMF", "Harpreet Singh Sodhi", "1968-07-22", "HSSPS7788P", "FOL-55228833", "HDFC Flexi Cap Fund", "Gurpreet Singh (Son)", 650000.0, "Unclaimed Redemption", "Folio: 55228833/21, Units: 4,500.00"),
            ("SBIMF", "Lakshmi Narayanan", "1954-12-30", "LMNPN6677Q", "FOL-88331166", "SBI Small Cap Fund Growth", "Venkatesh L (Son)", 890000.0, "Unclaimed Matured Units", "Folio: 88331166/55, Units: 6,100.00"),
            ("HDFCMF", "Bimal Kanti Ghosh", "1960-01-18", "BKGPG3344R", "FOL-22774499", "HDFC Mid-Cap Opportunities Fund", "Anindita Ghosh (Wife)", 380000.0, "Unclaimed Dividend", "Folio: 22774499/19, Units: 3,200.00"),
            ("SBIMF", "Manorama Devi", "1948-08-14", "MRMDV5566T", "FOL-66113377", "SBI Conservative Hybrid Fund", "Rajeshwar Prasad (Son)", 290000.0, "Unclaimed Redemption", "Folio: 66113377/82, Units: 4,400.00"),
            ("HDFCMF", "Devendra Nath Tiwari", "1963-05-10", "DNTPI8899U", "FOL-44992211", "HDFC Hybrid Debt Fund", "Alok Tiwari (Son)", 340000.0, "Unclaimed Payout", "Folio: 44992211/33, Units: 5,600.00"),
            ("SBIMF", "Pushpa Ben Patel", "1952-10-25", "PBPPA2233V", "FOL-77338822", "SBI Healthcare Opportunities", "Kirit Patel (Son)", 410000.0, "Unclaimed Redemption", "Folio: 77338822/01, Units: 1,850.00"),
            ("HDFCMF", "Om Prakash Sharma", "1957-06-03", "OPKPS1199W", "FOL-11884433", "HDFC Large and Mid Cap Fund", "Neeta Sharma (Wife)", 270000.0, "Unclaimed Dividends", "Folio: 11884433/67, Units: 2,900.00"),
            ("SBIMF", "Kavita Rao", "1970-02-14", "KVRPR9911X", "FOL-99226611", "SBI Technology Opportunities", "Siddharth Rao (Son)", 560000.0, "Unclaimed Redemption", "Folio: 99226611/48, Units: 3,120.00"),
            ("HDFCMF", "Subhash Chandra Bose", "1961-04-09", "SCBPS7722Y", "FOL-33661188", "HDFC Taxsaver ELSS Fund", "Anita Bose (Wife)", 490000.0, "Unclaimed Matured Units", "Folio: 33661188/95, Units: 1,200.00"),
            ("SBIMF", "Jagdish Chander", "1955-11-28", "JCHPC4433Z", "FOL-88117722", "SBI Focused Equity Fund", "Santosh Kumari (Wife)", 320000.0, "Unclaimed Dividend", "Folio: 88117722/14, Units: 3,450.00"),
            ("HDFCMF", "Farida Begum", "1964-08-19", "FBGPR8844A", "FOL-55449922", "HDFC Children's Gift Fund", "Tariq Ahmed (Son)", 210000.0, "Unclaimed Redemption", "Folio: 55449922/30, Units: 2,800.00"),
            ("SBIMF", "Ramesh Chandra Das", "1953-09-07", "RCDPD3322B", "FOL-22993388", "SBI Banking and Financial Services", "Pranab Das (Son)", 275000.0, "Unclaimed Dividend", "Folio: 22993388/77, Units: 5,100.00"),
            ("HDFCMF", "Kailash Chand Verma", "1966-12-12", "KCVPA7711C", "FOL-77114466", "HDFC Equity Savings Fund", "Vimla Verma (Wife)", 350000.0, "Unclaimed Payout", "Folio: 77114466/23, Units: 7,800.00"),
            ("SBIMF", "Vijay Kumar Singhania", "1959-03-31", "VKSPA6655D", "FOL-11668833", "SBI Magnum Global Fund", "Rohit Singhania (Son)", 1150000.0, "Unclaimed Redemption", "Folio: 11668833/41, Units: 8,400.00"),
            ("HDFCMF", "Parvati Ammal", "1949-05-20", "PAMPA9988E", "FOL-66331199", "HDFC Low Duration Fund", "Muthusamy (Husband)", 195000.0, "Unclaimed Dividend", "Folio: 66331199/88, Units: 6,500.00"),
            ("SBIMF", "Bhagwan Sahai", "1956-07-16", "BSHPA4422F", "FOL-44882277", "SBI Multi Asset Allocation", "Kishan Lal (Son)", 240000.0, "Unclaimed Redemption", "Folio: 44882277/10, Units: 4,900.00"),
            ("HDFCMF", "Cyrus Jamshedji Irani", "1961-10-04", "CJIPA1133G", "FOL-99337711", "HDFC Corporate Bond Fund", "Roxanne Irani (Daughter)", 620000.0, "Unclaimed Payout", "Folio: 99337711/05, Units: 24,000.00"),
            ("SBIMF", "Shyamal Kanti Sen", "1967-01-23", "SKSPS8822H", "FOL-33884422", "SBI PSU Fund Growth", "Sumita Sen (Wife)", 330000.0, "Unclaimed Dividend", "Folio: 33884422/36, Units: 7,200.00"),
            ("HDFCMF", "Santosh Devi Yadav", "1951-04-17", "SDYPA3311I", "FOL-88221155", "HDFC Banking and PSU Debt Fund", "Ram Avtar Yadav (Son)", 290000.0, "Unclaimed Redemption", "Folio: 88221155/72, Units: 12,000.00"),
            ("SBIMF", "Naveen Chand Jain", "1965-06-29", "NCJPA5544J", "FOL-55117744", "SBI Contra Fund Regular", "Arpit Jain (Son)", 710000.0, "Unclaimed Redemption", "Folio: 55117744/99, Units: 4,100.00"),
            ("HDFCMF", "Hemant Kumar Barua", "1958-02-11", "HKBPA7766K", "FOL-22449911", "HDFC Small Cap Fund", "Binita Barua (Wife)", 430000.0, "Unclaimed Dividend", "Folio: 22449911/64, Units: 3,300.00"),
            ("SBIMF", "Mahmood Ali Khan", "1960-09-08", "MAKPA9944L", "FOL-77992288", "SBI Infrastructure Fund", "Nasreen Khan (Wife)", 360000.0, "Unclaimed Payout", "Folio: 77992288/15, Units: 5,000.00"),
        ]

        for inst_code, holder, dob, id_ref, fol_ref, cat, nominee, val, unclaim_st, details in mf_data:
            financial_records.append(FinancialAsset(
                id=str(uuid.uuid4()),
                institution_id=inst_map[inst_code].id,
                asset_type="mutual_fund",
                institution_name=inst_map[inst_code].name,
                holder_name=holder,
                date_of_birth=dob,
                sample_identity_ref=id_ref,
                account_ref=fol_ref,
                category=cat,
                nominee_ref=nominee,
                status="Unclaimed",
                unclaimed_status=unclaim_st,
                approximate_value=val,
                details_json=details
            ))

        for fa in financial_records:
            db.add(fa)
        db.commit()

        # 4. Pre-seed Deceased Person Records:
        # One verified record for Rajesh Kumar, submitted by user Ramesh Kumar!
        # And one pending record for Priya Sharma's submitted relative.
        deceased_rajesh = DeceasedPerson(
            id=str(uuid.uuid4()),
            user_id=user_map["rajesh.family@example.com"].id,
            full_name="Rajesh Kumar",
            date_of_birth="1965-04-12",
            date_of_death="2023-08-15",
            gender="Male",
            last_known_city="New Delhi",
            last_known_state="Delhi",
            death_cert_ref="DC-DL-2023-88992",
            death_reg_date="2023-08-20",
            issuing_authority="Municipal Corporation of Delhi (MCD)",
            sample_identity_ref="ABCDE1234F",
            status="Verified",
            admin_notes="Death certificate verified with sample civil registrar repository. Record approved for automated asset matching."
        )
        db.add(deceased_rajesh)

        deceased_suresh = DeceasedPerson(
            id=str(uuid.uuid4()),
            user_id=user_map["priya.sharma@example.com"].id,
            full_name="Suresh Chandra Gupta",
            date_of_birth="1958-09-20",
            date_of_death="2022-11-10",
            gender="Male",
            last_known_city="Agra",
            last_known_state="Uttar Pradesh",
            death_cert_ref="DC-UP-2022-44109",
            death_reg_date="2022-11-15",
            issuing_authority="Nagar Nigam Agra",
            sample_identity_ref="BNKPG9981K",
            status="Pending Verification",
            admin_notes="Pending verification by Administrator."
        )
        db.add(deceased_suresh)
        db.commit()

        # Claimant for Rajesh Kumar
        claimant_ramesh = Claimant(
            id=str(uuid.uuid4()),
            user_id=user_map["rajesh.family@example.com"].id,
            deceased_person_id=deceased_rajesh.id,
            name="Ramesh Kumar",
            relationship_to_deceased="Son",
            email="rajesh.family@example.com",
            mobile="9876543210",
            claimant_type="Nominee",
            status="Approved",
            admin_notes="Verified via sample Legal Heir Certificate / Aadhaar identity."
        )
        db.add(claimant_ramesh)
        db.commit()

        # Now, run automated matching for Rajesh Kumar so the initial demonstration already has live results!
        from app.services.matching_service import run_matching_for_deceased
        matches = run_matching_for_deceased(db, deceased_rajesh.id)
        print(f"Generated {len(matches)} initial matches for Rajesh Kumar.")

        # Create one sample claim for demonstration
        if matches:
            first_match = matches[0]
            sample_claim = Claim(
                id=str(uuid.uuid4()),
                claim_reference=f"CLM-2026-{first_match.matching_score}891",
                claimant_id=claimant_ramesh.id,
                asset_match_id=first_match.id,
                deceased_person_id=deceased_rajesh.id,
                financial_asset_id=first_match.financial_asset_id,
                institution_id=first_match.financial_asset.institution_id,
                status="Under Review",
                remarks="Claim submitted by nominee Ramesh Kumar. Under verification by Institution Representative.",
                submission_date=datetime.utcnow() - timedelta(days=2)
            )
            db.add(sample_claim)
            db.commit()

        # Welcome notification for family user
        notif = Notification(
            id=str(uuid.uuid4()),
            user_id=user_map["rajesh.family@example.com"].id,
            title="Welcome to Virasat Setu",
            message="Your account is active. Your submitted record for Rajesh Kumar was verified and potential assets have been matched across Banks, Insurance and Mutual Funds.",
            notification_type="verification",
            link="/dashboard",
            is_read=False,
            email_sent=True,
            email_logs="[Simulated Welcome Email Dispatched to rajesh.family@example.com]"
        )
        db.add(notif)
        db.commit()

        print("Seeding completed successfully!")

    except Exception as e:
        db.rollback()
        print("Error during database seed:", e)
        raise
    finally:
        db.close()

if __name__ == "__main__":
    seed_all()
