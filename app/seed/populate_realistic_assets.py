"""
Populate Realistic Financial Assets:
Adds comprehensive assets across banking, insurance, mutual funds,
National Pension System (NPS), EPFO provident funds, Department of Posts (PPF, NSC, SCSS, KVP),
and Demat equity shares for deceased persons in the database.
"""

import sys
import os
sys.path.insert(0, os.path.abspath("."))
import uuid
from datetime import datetime
from sqlalchemy.orm import Session
from app.database import DatabaseSession, engine, Base
from app.models.models import Institution, FinancialAsset, DeceasedPerson, User
from app.services.matching_service import run_matching_for_deceased
from app.utils.auth import hash_password

def populate_realistic_data():
    db: Session = DatabaseSession()
    try:
        print("Checking and registering expanded institutions...")
        new_institutions = [
            {
                "code": "PFRDA",
                "name": "National Pension System (PFRDA / CRA)",
                "category": "pension",
                "contact_email": "cra@pfrda.org.in",
                "phone": "1800-110-069",
                "address": "B-14/A, Chatrapati Shivaji Bhawan, Qutab Institutional Area, New Delhi"
            },
            {
                "code": "EPFO",
                "name": "Employees Provident Fund Organisation (EPFO)",
                "category": "pension",
                "contact_email": "nodal.epf@epfindia.gov.in",
                "phone": "1800-115-811",
                "address": "Bhavishya Nidhi Bhawan, 14, Bhikaiji Cama Place, New Delhi"
            },
            {
                "code": "POST_OFFICE",
                "name": "Department of Posts (India Post Small Savings)",
                "category": "postal_savings",
                "contact_email": "savings@indiapost.gov.in",
                "phone": "1800-266-6868",
                "address": "Dak Bhawan, Sansad Marg, New Delhi"
            },
            {
                "code": "BOB",
                "name": "Bank of Baroda",
                "category": "bank",
                "contact_email": "unclaimed@bankofbaroda.co.in",
                "phone": "1800-258-4455",
                "address": "Baroda Corporate Centre, C-26, G-Block, BKC, Mumbai"
            },
            {
                "code": "CDSL",
                "name": "CDSL Demat and Shares Depository",
                "category": "demat",
                "contact_email": "investor@cdslindia.com",
                "phone": "1800-22-5533",
                "address": "Marathon Futurex, A-Wing, Mafatlal Mills, Lower Parel, Mumbai"
            }
        ]

        inst_map = {}
        for inst_data in new_institutions:
            existing = db.query(Institution).filter(Institution.code == inst_data["code"]).first()
            if not existing:
                inst = Institution(
                    id=str(uuid.uuid4()),
                    code=inst_data["code"],
                    name=inst_data["name"],
                    category=inst_data["category"],
                    contact_email=inst_data["contact_email"],
                    phone=inst_data["phone"],
                    address=inst_data["address"]
                )
                db.add(inst)
                db.commit()
                inst_map[inst_data["code"]] = inst
                print(f"Added institution: {inst_data['name']}")
            else:
                inst_map[inst_data["code"]] = existing

        # Load all institutions
        all_insts = db.query(Institution).all()
        for inst in all_insts:
            inst_map[inst.code] = inst

        # Check and add user xerontitan99@gmail.com if not exists
        xeron_user = db.query(User).filter(User.email == "xerontitan99@gmail.com").first()
        if not xeron_user:
            xeron_user = User(
                id=str(uuid.uuid4()),
                email="xerontitan99@gmail.com",
                hashed_password=hash_password("xeron123"),
                full_name="Xeron Titan",
                mobile="9811998877",
                role="family_user"
            )
            db.add(xeron_user)
            db.commit()
            print("Registered user profile for xerontitan99@gmail.com")

        # Realistic assets for Rajesh Kumar (PAN: ABCDE1234F, DOB: 1965-04-12)
        # Nominee: Ramesh Kumar (Son)
        expanded_assets = [
            # 1. Rajesh Kumar Assets (PFRDA, Post Office, EPFO, BOB, CDSL)
            {
                "inst_code": "PFRDA",
                "holder": "Rajesh Kumar",
                "dob": "1965-04-12",
                "id_ref": "ABCDE1234F",
                "acc_ref": "PRAN-110034928172",
                "category": "National Pension System Tier 1",
                "asset_type": "pension",
                "nominee": "Ramesh Kumar (Son)",
                "val": 1480000.0,
                "status": "Unclaimed",
                "unclaimed_status": "Matured Corpus Unclaimed",
                "details": "PRAN: 110034928172, Nodal Office: Directorate of Education Delhi, CRA: Protean KFintech, Accumulated Corpus: Rs 14,80,000"
            },
            {
                "inst_code": "POST_OFFICE",
                "holder": "Rajesh Kumar",
                "dob": "1965-04-12",
                "id_ref": "ABCDE1234F",
                "acc_ref": "PPF-DEL-401928",
                "category": "Public Provident Fund Scheme",
                "asset_type": "postal_savings",
                "nominee": "Ramesh Kumar (Son)",
                "val": 865000.0,
                "status": "Unclaimed",
                "unclaimed_status": "Matured Account > 15 Years",
                "details": "Head Post Office: Parliament Street Head Post Office New Delhi 110001, Passbook Ref: PPF-401928, Accumulated Balance with Interest: Rs 8,65,000"
            },
            {
                "inst_code": "POST_OFFICE",
                "holder": "Rajesh Kumar",
                "dob": "1965-04-12",
                "id_ref": "ABCDE1234F",
                "acc_ref": "NSC-882910-14",
                "category": "National Savings Certificate (VIII Issue)",
                "asset_type": "postal_savings",
                "nominee": "Ramesh Kumar (Son)",
                "val": 250000.0,
                "status": "Unclaimed",
                "unclaimed_status": "Matured 5 Years Unclaimed",
                "details": "5 Certificates of Rs 50,000 denomination each, Connaught Place Post Office, Total Maturity Proceeds: Rs 2,50,000"
            },
            {
                "inst_code": "EPFO",
                "holder": "Rajesh Kumar",
                "dob": "1965-04-12",
                "id_ref": "ABCDE1234F",
                "acc_ref": "UAN-100928374619",
                "category": "Employees Provident Fund and EPS 95 Arrears",
                "asset_type": "pension",
                "nominee": "Ramesh Kumar (Son)",
                "val": 640000.0,
                "status": "Unclaimed",
                "unclaimed_status": "Inoperative PF Account > 7 Years",
                "details": "Member ID: DLCPM00192830000102, Regional Office: Delhi North Wazirpur, EDLI Life Insurance Cover Applicable"
            },
            {
                "inst_code": "BOB",
                "holder": "Rajesh Kumar",
                "dob": "1965-04-12",
                "id_ref": "ABCDE1234F",
                "acc_ref": "BOB-7711228899",
                "category": "Fixed Deposit",
                "asset_type": "bank",
                "nominee": "Ramesh Kumar (Son)",
                "val": 425000.0,
                "status": "Unclaimed",
                "unclaimed_status": "Dormant Term Deposit > 10 Yrs",
                "details": "Branch: Connaught Circus New Delhi, IFSC: BARB0CONNAU, Principal: Rs 2,50,000, Accrued Interest: Rs 1,75,000"
            },
            {
                "inst_code": "CDSL",
                "holder": "Rajesh Kumar",
                "dob": "1965-04-12",
                "id_ref": "ABCDE1234F",
                "acc_ref": "BO-1203320004918271",
                "category": "Equity Demat Shares",
                "asset_type": "demat",
                "nominee": "Ramesh Kumar (Son)",
                "val": 915000.0,
                "status": "Unclaimed",
                "unclaimed_status": "Inactive Demat Account with Dividends",
                "details": "Depository Participant: Zerodha Broking, Holdings: 150 Reliance Industries, 200 TCS, 400 Infosys, Unclaimed Dividends: Rs 42,500"
            },

            # 2. Suresh Chandra Gupta Assets (PAN: BNKPG9981K, DOB: 1958-09-20)
            {
                "inst_code": "POST_OFFICE",
                "holder": "Suresh Chandra Gupta",
                "dob": "1958-09-20",
                "id_ref": "BNKPG9981K",
                "acc_ref": "SCSS-AGR-9921",
                "category": "Senior Citizen Savings Scheme",
                "asset_type": "postal_savings",
                "nominee": "Sunita Gupta (Wife)",
                "val": 1500000.0,
                "status": "Unclaimed",
                "unclaimed_status": "Matured SCSS Unclaimed",
                "details": "Agra Head Post Office, Quarterly Interest Unclaimed, Total Maturity Value: Rs 15,00,000"
            },
            {
                "inst_code": "POST_OFFICE",
                "holder": "Suresh Chandra Gupta",
                "dob": "1958-09-20",
                "id_ref": "BNKPG9981K",
                "acc_ref": "KVP-551122",
                "category": "Kisan Vikas Patra",
                "asset_type": "postal_savings",
                "nominee": "Sunita Gupta (Wife)",
                "val": 300000.0,
                "status": "Unclaimed",
                "unclaimed_status": "Doubled Maturity Value Unclaimed",
                "details": "Sanjay Place Sub Post Office Agra, 3 Certificates of Rs 1,00,000 each"
            },
            {
                "inst_code": "EPFO",
                "holder": "Suresh Chandra Gupta",
                "dob": "1958-09-20",
                "id_ref": "BNKPG9981K",
                "acc_ref": "UAN-100445566778",
                "category": "EPS 95 Monthly Family Pension Arrears",
                "asset_type": "pension",
                "nominee": "Sunita Gupta (Wife)",
                "val": 385000.0,
                "status": "Unclaimed",
                "unclaimed_status": "Unclaimed Pension Arrears",
                "details": "Regional Office Agra, PPO Ref: UPAGR00049182, Accumulation of monthly pension entitlement"
            },

            # 3. Harpreet Singh Sodhi Assets (PAN: HSSPS7788P, DOB: 1968-07-22)
            {
                "inst_code": "PFRDA",
                "holder": "Harpreet Singh Sodhi",
                "dob": "1968-07-22",
                "id_ref": "HSSPS7788P",
                "acc_ref": "PRAN-110055883311",
                "category": "National Pension System Tier 1",
                "asset_type": "pension",
                "nominee": "Gurpreet Singh (Son)",
                "val": 1850000.0,
                "status": "Unclaimed",
                "unclaimed_status": "Corporate NPS Corpus Unclaimed",
                "details": "Corporate Subscriber: Sodhi Logistics, CRA: Protean, Accumulated Wealth: Rs 18,50,000"
            },
            {
                "inst_code": "POST_OFFICE",
                "holder": "Harpreet Singh Sodhi",
                "dob": "1968-07-22",
                "id_ref": "HSSPS7788P",
                "acc_ref": "PPF-CHD-881122",
                "category": "Public Provident Fund Scheme",
                "asset_type": "postal_savings",
                "nominee": "Gurpreet Singh (Son)",
                "val": 720000.0,
                "status": "Unclaimed",
                "unclaimed_status": "Inoperative Account",
                "details": "Sector 17 General Post Office Chandigarh, Total Accrued Value: Rs 7,20,000"
            },

            # 4. Anand Mohan Joshi Assets (PAN: AJOPJ4412B, DOB: 1962-11-05)
            {
                "inst_code": "CDSL",
                "holder": "Anand Mohan Joshi",
                "dob": "1962-11-05",
                "id_ref": "AJOPJ4412B",
                "acc_ref": "BO-1208160001928374",
                "category": "Equity Demat Holdings",
                "asset_type": "demat",
                "nominee": "Aditi Joshi (Daughter)",
                "val": 1240000.0,
                "status": "Unclaimed",
                "unclaimed_status": "Dormant Demat Account",
                "details": "Depository Participant: HDFC Securities, Bluechip Equities: HDFC Bank, Larsen and Toubro, State Bank of India"
            },
            {
                "inst_code": "POST_OFFICE",
                "holder": "Anand Mohan Joshi",
                "dob": "1962-11-05",
                "id_ref": "AJOPJ4412B",
                "acc_ref": "NSC-BOM-992211",
                "category": "National Savings Certificate",
                "asset_type": "postal_savings",
                "nominee": "Aditi Joshi (Daughter)",
                "val": 300000.0,
                "status": "Unclaimed",
                "unclaimed_status": "Matured Unclaimed",
                "details": "Bandra West Post Office Mumbai 400050, 6 Certificates of Rs 50,000 each"
            },

            # 5. Gopal Krishna Murthy Assets (PAN: GKMPS1122C, DOB: 1950-03-15)
            {
                "inst_code": "POST_OFFICE",
                "holder": "Gopal Krishna Murthy",
                "dob": "1950-03-15",
                "id_ref": "GKMPS1122C",
                "acc_ref": "SCSS-BLR-441199",
                "category": "Senior Citizen Savings Scheme",
                "asset_type": "postal_savings",
                "nominee": "Saraswati Murthy (Spouse)",
                "val": 1200000.0,
                "status": "Unclaimed",
                "unclaimed_status": "Matured SCSS",
                "details": "Malleswaram Sub Post Office Bengaluru 560003, Deposit Date: 2014, Total Claim Value: Rs 12,00,000"
            },
            {
                "inst_code": "BOB",
                "holder": "Gopal Krishna Murthy",
                "dob": "1950-03-15",
                "id_ref": "GKMPS1122C",
                "acc_ref": "BOB-BLR-882233",
                "category": "Savings Account",
                "asset_type": "bank",
                "nominee": "Saraswati Murthy (Spouse)",
                "val": 165000.0,
                "status": "Unclaimed",
                "unclaimed_status": "Dormant > 10 Yrs",
                "details": "Branch: Malleswaram 8th Cross Bengaluru, IFSC: BARB0MALLES, Balance: Rs 1,65,000"
            }
        ]

        added_count = 0
        for item in expanded_assets:
            existing = db.query(FinancialAsset).filter(
                FinancialAsset.account_ref == item["acc_ref"]
            ).first()
            if not existing:
                inst = inst_map.get(item["inst_code"])
                if not inst:
                    continue
                fa = FinancialAsset(
                    id=str(uuid.uuid4()),
                    institution_id=inst.id,
                    asset_type=item["asset_type"],
                    institution_name=inst.name,
                    holder_name=item["holder"],
                    date_of_birth=item["dob"],
                    sample_identity_ref=item["id_ref"],
                    account_ref=item["acc_ref"],
                    category=item["category"],
                    nominee_ref=item["nominee"],
                    status=item["status"],
                    unclaimed_status=item["unclaimed_status"],
                    approximate_value=item["val"],
                    details_json=item["details"]
                )
                db.add(fa)
                added_count += 1

        db.commit()
        print(f"Added {added_count} new realistic financial assets across NPS, PPF, NSC, SCSS, Demat, and Banking.")

        # Re-run matching for all verified deceased persons
        deceased_list = db.query(DeceasedPerson).filter(DeceasedPerson.status == "Verified").all()
        for dec in deceased_list:
            matches = run_matching_for_deceased(db, dec.id)
            print(f"Re-matched {len(matches)} assets for verified deceased: {dec.full_name} ({dec.sample_identity_ref})")

    except Exception as e:
        db.rollback()
        print("Error populating realistic data:", e)
        raise
    finally:
        db.close()

if __name__ == "__main__":
    populate_realistic_data()
