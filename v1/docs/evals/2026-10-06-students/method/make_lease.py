"""A made-up Florida student-housing lease (by the bed, individual liability, a managed complex with amenities),
one PDF per student, and the profile a perfect extraction would give. For the student simulation only.

    python make_lease.py <out_dir> "<Resident name>" <unit> <bedroom>

Writes <out_dir>/magnolia_lease.pdf (not lease.pdf, which .gitignore leaves out) and <out_dir>/profile.json. The PDF is written with the repo's own plain PDF writer
(dev/build_test_leases.pdf_bytes) and read back with PyPDF2, as lease.ingest_pdf reads a lease.
"""
import json
import sys
import textwrap
from pathlib import Path

REPO = Path(__file__).resolve().parents[4]                  # the project folder
sys.path.insert(0, str(REPO))
sys.path.insert(0, str(REPO / "dev"))
import PyPDF2                                   # noqa: E402
from build_test_leases import pdf_bytes          # noqa: E402
from config import squash                        # noqa: E402

FOOT = "Magnolia Row Student Housing Lease | Page {n} of {total}"

PAGES = [
"""STUDENT HOUSING LEASE AGREEMENT (INDIVIDUAL LIABILITY)
MAGNOLIA ROW STUDENT APARTMENTS

ARTICLE 1 PARTIES AND PREMISES
1.1. Parties. This Student Housing Lease Agreement ("Lease") is made on July 20, 2026 between MR Gainesville Owner, LLC, by its managing agent, Hartwell Residential Management, LLC, 2600 SW Hartwell Lane, Gainesville, Florida 32608 ("Landlord" or "Management"), and {NAME} ("Resident").
1.2. Premises. Landlord leases to Resident Bedroom {BED} in Unit {UNIT}, a four-bedroom, four-bathroom apartment at Magnolia Row Student Apartments, 2600 SW Hartwell Lane, Unit {UNIT}, Gainesville, Florida 32608, together with the non-exclusive right to use the Unit's shared kitchen, living room, and laundry closet and the Community's common areas and amenities (together, the "Premises").
1.3. Roommates. Resident shares the Unit with up to three other residents, each of whom signs a separate lease with Landlord. Landlord may assign or reassign roommates to fill any vacant bedroom. Resident has no right to choose or approve a roommate assigned by Landlord.

ARTICLE 2 TERM
2.1. Term. The term of this Lease begins on August 15, 2026 and ends at 12:00 noon on July 31, 2027.
2.2. No Early Termination. Resident may not end this Lease before the end of the term except as provided in Article 12 or as required by law.

ARTICLE 3 RENT AND FEES
3.1. Rent. Resident shall pay total rent of $9,468.00 for the term, payable in twelve (12) installments of $789.00 each. The first installment is due on or before August 15, 2026, and each later installment is due on the first day of each month from September 1, 2026 through July 1, 2027. Installments are not prorated. Rent is paid through the online resident portal.
3.2. Late Charge. If any installment is not received by 11:59 p.m. on the fifth (5th) day of the month, Resident shall pay a late charge of $50.00, plus $10.00 for each later day, not to exceed $150.00 in any month.
3.3. Fees. Resident shall pay a non-refundable application fee of $50.00, a non-refundable administrative fee of $200.00, and a non-refundable amenity fee of $150.00, each due at signing. The amenity fee is for access to the Community amenities and is not refundable for any reason, including the closure of any amenity.
3.4. Individual Liability. Resident is responsible only for the Rent and charges under this Lease and is not responsible for the rent of any roommate. However, Resident and all residents of the Unit are jointly and severally liable for damage to the Unit's shared areas (kitchen, living room, laundry closet, and hallways) and its shared appliances when Landlord cannot determine which resident caused the damage, and such charges will be divided equally among the residents of the Unit.
""",
"""ARTICLE 4 SECURITY DEPOSIT
4.1. Security Deposit. Resident shall pay a security deposit of $300.00. Landlord shall hold the security deposit in a separate non-interest-bearing account in a Florida banking institution for the benefit of Resident.
4.2. Deductions. Landlord may deduct from the security deposit unpaid rent, late charges, the cost of repairing damage beyond normal wear and tear to Resident's bedroom and bathroom, Resident's equal share of damage to the shared areas of the Unit under Section 3.4, cleaning charges, and any other amount due under this Lease. Landlord shall return the security deposit, or give notice of its intention to impose a claim on it, as required by Section 83.49, Florida Statutes.
4.3. Guarantor. Resident's parent or guardian shall sign a separate Guaranty of this Lease before Resident moves in.
4.4. Forwarding Address. Resident shall give Landlord a written forwarding address before moving out.

ARTICLE 5 UTILITIES AND SERVICES
5.1. Included Services. Rent includes water, sewer, trash removal, high-speed internet (Wi-Fi), and basic cable television. Electricity is included up to a monthly cap of $100.00 per Unit, and any amount over the cap is divided equally among the residents of the Unit.
5.2. Interruption of Services. Landlord is not liable for any interruption or failure of utilities, internet, or other services caused by a provider, a repair, or anything beyond Landlord's reasonable control, and no such interruption entitles Resident to any reduction or abatement of Rent.

ARTICLE 6 AMENITIES
6.1. Community Amenities. Resident may use the swimming pool, fitness center, study rooms, and clubhouse, subject to the Community Rules and posted hours.
6.2. Closure of Amenities. Landlord may close any amenity, in whole or in part, for maintenance, repair, weather, or safety, for as long as Landlord reasonably determines. The closure of an amenity does not entitle Resident to any reduction of Rent or any refund of the amenity fee.

ARTICLE 7 MAINTENANCE AND REPAIRS
7.1. Landlord's Repairs. Landlord shall maintain in good working order and repair the heating, air-conditioning, plumbing, and electrical systems serving the Unit and the appliances Landlord furnishes, including the refrigerator, range, dishwasher, microwave, washer, and dryer, except for damage caused by Resident, a roommate, or their guests.
7.2. Maintenance Requests. Resident shall report every repair need by submitting a maintenance request through the online resident portal, except in an emergency, which Resident shall report by calling the after-hours emergency line at (352) 555-0147. Loss of air-conditioning when the outside temperature is above 85 degrees, loss of all water, and an active water leak are emergencies. A maintenance request is a request for service and is not by itself a notice under Section 13.1.
7.3. Time for Repairs. Landlord will make repairs within a reasonable time after Resident's request, considering the availability of parts and contractors. Resident is not entitled to any reduction of Rent for inconvenience from a repair or a delay in a repair, except as required by law.
7.4. Resident's Duties. Resident shall keep the Premises clean and sanitary, shall not block air-conditioning vents, shall report any leak, mold, or malfunction promptly, and shall pay for the repair of damage caused by Resident, a roommate, or their guests, including clogged drains and damage to appliances from misuse.
7.5. Permission to Enter. Submitting a maintenance request gives Landlord permission to enter the Unit to make the repair.
""",
"""ARTICLE 8 USE AND CONDUCT
8.1. Use. Resident shall use the Premises only as a private residence for Resident and shall comply with all laws and the Community Rules, which are part of this Lease.
8.2. Guests. A guest may not stay in the Unit more than three (3) nights in any thirty (30) day period without the written consent of Landlord and of every resident of the Unit.

ARTICLE 9 MOVE-OUT
9.1. Move-Out Requirements. At the end of the term Resident shall remove all personal property, clean Resident's bedroom and bathroom, return all keys and access cards to the leasing office, and complete a move-out inspection form. Each key or access card not returned is charged at $75.00.
9.2. Notice Before Vacating. If Resident vacates the Premises before the end of the term, Resident shall give Landlord at least seven (7) days' written notice by certified mail or personal delivery before vacating. If Resident does not give this notice, Resident shall forfeit the security deposit as permitted by Section 83.49(5), Florida Statutes.

ARTICLE 10 DEFAULT
10.1. Default. If Resident fails to pay any installment of Rent when due, or fails to comply with this Lease, Landlord may end this Lease and recover possession of the Premises as provided in Chapter 83, Part II, Florida Statutes.

ARTICLE 11 RELETTING
11.1. Reassignment. Resident may assign this Lease to a replacement resident only with Landlord's written approval and payment of a reassignment fee of $250.00.

ARTICLE 12 EARLY TERMINATION
12.1. Early Termination Option. Resident may end this Lease early by giving Landlord at least sixty (60) days' written notice and paying an early termination fee of $1,578.00, an amount that does not exceed two (2) months' Rent.
12.2. Servicemembers. Resident may end this Lease early as provided in Section 83.682, Florida Statutes.

ARTICLE 13 NOTICES
13.1. Notices to Landlord. Every notice from Resident to Landlord under this Lease or Florida law must be in writing and delivered by hand to the leasing office at 2600 SW Hartwell Lane, Gainesville, Florida 32608, sent by certified mail to that address, or sent by e-mail to office@magnoliarow.example.
13.2. Notices to Resident. Landlord may give notice to Resident by hand delivery, by posting on the door of the Unit, or by e-mail to the address Resident gave on the resident portal.

ARTICLE 14 SIGNATURES
RESIDENT: {NAME} Date: July 20, 2026
LANDLORD: Hartwell Residential Management, LLC, as agent for MR Gainesville Owner, LLC By: Dana Whitfield, Community Manager Date: July 22, 2026
""",
]


def clause(quote, page, section):
    return {"present": True, "quote": quote, "page": page, "section": section}


def profile(name, unit, bed):
    return {
        "landlord_name_and_address": clause("MR Gainesville Owner, LLC, by its managing agent, Hartwell Residential Management, LLC, 2600 SW Hartwell Lane, Gainesville, Florida 32608", 1, "1.1"),
        "tenant_names": clause(f'{name} ("Resident")', 1, "1.1"),
        "premises_address": clause(f"Bedroom {bed} in Unit {unit}, a four-bedroom, four-bathroom apartment at Magnolia Row Student Apartments, 2600 SW Hartwell Lane, Unit {unit}, Gainesville, Florida 32608", 1, "1.2"),
        "term_start": clause("The term of this Lease begins on August 15, 2026", 1, "2.1"),
        "term_end": clause("ends at 12:00 noon on July 31, 2027", 1, "2.1"),
        "rent": clause("Resident shall pay total rent of $9,468.00 for the term, payable in twelve (12) installments of $789.00 each.", 1, "3.1"),
        "security_deposit": clause("Resident shall pay a security deposit of $300.00.", 2, "4.1"),
        "deposit_deductions": clause("Landlord may deduct from the security deposit unpaid rent, late charges, the cost of repairing damage beyond normal wear and tear to Resident's bedroom and bathroom, Resident's equal share of damage to the shared areas of the Unit under Section 3.4, cleaning charges, and any other amount due under this Lease.", 2, "4.2"),
        "nonrefundable_fees": clause("Resident shall pay a non-refundable application fee of $50.00, a non-refundable administrative fee of $200.00, and a non-refundable amenity fee of $150.00, each due at signing. The amenity fee is for access to the Community amenities and is not refundable for any reason, including the closure of any amenity.", 1, "3.3"),
        "move_out_requirements": clause("At the end of the term Resident shall remove all personal property, clean Resident's bedroom and bathroom, return all keys and access cards to the leasing office, and complete a move-out inspection form. Each key or access card not returned is charged at $75.00.", 3, "9.1"),
        "forwarding_address_requirement": clause("Resident shall give Landlord a written forwarding address before moving out.", 2, "4.4"),
        "notices_to_landlord": clause("Every notice from Resident to Landlord under this Lease or Florida law must be in writing and delivered by hand to the leasing office at 2600 SW Hartwell Lane, Gainesville, Florida 32608, sent by certified mail to that address, or sent by e-mail to office@magnoliarow.example.", 3, "13.1"),
        "joint_and_several_liability": clause("Resident is responsible only for the Rent and charges under this Lease and is not responsible for the rent of any roommate. However, Resident and all residents of the Unit are jointly and severally liable for damage to the Unit's shared areas (kitchen, living room, laundry closet, and hallways) and its shared appliances when Landlord cannot determine which resident caused the damage, and such charges will be divided equally among the residents of the Unit.", 1, "3.4"),
        "signatures": clause(f"RESIDENT: {name} Date: July 20, 2026 LANDLORD: Hartwell Residential Management, LLC, as agent for MR Gainesville Owner, LLC By: Dana Whitfield, Community Manager Date: July 22, 2026", 3, "ARTICLE 14"),
        "notice_before_vacating": clause("If Resident vacates the Premises before the end of the term, Resident shall give Landlord at least seven (7) days' written notice by certified mail or personal delivery before vacating. If Resident does not give this notice, Resident shall forfeit the security deposit as permitted by Section 83.49(5), Florida Statutes.", 3, "9.2"),
        "maintenance_and_repairs": clause("7.1. Landlord's Repairs. Landlord shall maintain in good working order and repair the heating, air-conditioning, plumbing, and electrical systems serving the Unit and the appliances Landlord furnishes, including the refrigerator, range, dishwasher, microwave, washer, and dryer, except for damage caused by Resident, a roommate, or their guests. 7.2. Maintenance Requests. Resident shall report every repair need by submitting a maintenance request through the online resident portal, except in an emergency, which Resident shall report by calling the after-hours emergency line at (352) 555-0147.", 2, "7.1"),
    }


def page_text(i, name, unit, bed):
    body = PAGES[i].replace("{NAME}", name).replace("{UNIT}", unit).replace("{BED}", bed)
    lines = []
    for para in body.split("\n"):
        lines += textwrap.wrap(para, 150) or [""]
    lines.append(FOOT.format(n=i + 1, total=len(PAGES)))
    return "\n".join(lines)


def main(out_dir, name, unit, bed):
    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)
    pages = [page_text(i, name, unit, bed) for i in range(len(PAGES))]
    (out / "magnolia_lease.pdf").write_bytes(pdf_bytes(pages))
    back = [p.extract_text() or "" for p in PyPDF2.PdfReader(out / "magnolia_lease.pdf").pages]
    assert [squash(t) for t in back] == [squash(t) for t in pages], "the PDF does not read back as written"
    (out / "profile.json").write_text(json.dumps(profile(name, unit, bed), indent=2))
    print("wrote", out / "magnolia_lease.pdf", "and profile.json")


if __name__ == "__main__":
    main(*sys.argv[1:5])
