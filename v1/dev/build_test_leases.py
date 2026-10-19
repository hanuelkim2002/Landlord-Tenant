"""Build Test Leases: one lease PDF per eval story, so a story never contradicts the lease it is read with (TODO
item 60). Until 2026-10-03 every scenario read the same test lease, lease.pdf (a twelve-month lease from
2026-10-01 at $1,850 with a $1,850 deposit), and the stories said otherwise: a $950 month-to-month duplex, a $900
deposit, a lease that ended 2026-07-31. The model read a rent increase as a decrease and a $1,000 deposit as $1,850.

    python dev/build_test_leases.py        # writes dev/leases/<name>.pdf for every lease in LEASES

Each lease is lease.pdf's text, as PyPDF2 reads it (the way lease.ingest_pdf reads a tenant's lease), with the
story's term, rent, deposit, and clauses changed word for word. A change whose old words are not in the text
exactly once stops the build. The PDF is plain (the text's lines in order, one font), and the build reads it
back to check that its text is the changed text. dev/leases/ is ignored by git, like lease.pdf, since it holds
the lease's text: anyone with lease.pdf can build it again.
"""
import io
import sys
from pathlib import Path

import PyPDF2

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
from config import squash                                  # noqa: E402  (the project's whitespace rule)

SOURCE = ROOT / "lease.pdf"
OUT = ROOT / "dev" / "leases"


# ---- What a lease can change: the term, the rent, the deposit, the pet clause. Each returns (old, new) pairs,
# the old words exactly as PyPDF2 reads lease.pdf (its line breaks included).

def term(start, end, signed):
    """The twelve-month term from `start` to `end`, the lease and its addendum signed on `signed`: each a date as
    the lease prints it, "August 1, 2026"."""
    month_day, year = signed.rsplit(" ", 1)
    return [("commencing on October 1, 2026", f"commencing on {start}"),
            ('on September 30, 2027 (the "Expiration Date")', f'on {end} (the "Expiration Date")'),
            ('as of September 15, \n2026 (the "Effective Date")', f'as of {month_day} \n{year} (the "Effective Date")'),
            ("Residential Lease Agreement dated September 15, \n2026, between",
             f"Residential Lease Agreement dated {month_day} \n{year}, between")]


def rent(words, figure, fee):
    """Monthly rent in words ("NINE HUNDRED FIFTY") and figures ("950.00"), and the early termination fee of the
    addendum's Option 1, two months' rent ("1,900.00"), which 83.595(4) caps at two months."""
    return [("ONE THOUSAND EIGHT HUNDRED FIFTY \nAND 00/100 DOLLARS ($1,850.00) per month",
             f"{words} \nAND 00/100 DOLLARS (${figure}) per month"),
            ("first full month's Rent of $1,850.00", f"first full month's Rent of ${figure}"),
            ("pay $3,700.00 (an amount that does not exceed 2", f"pay ${fee} (an amount that does not exceed 2")]


def deposit(words, figure):
    """The security deposit in words ("NINE HUNDRED") and figures ("900.00")."""
    return [("ONE \nTHOUSAND EIGHT HUNDRED FIFTY AND 00/100 DOLLARS ($1,850.00) as a security deposit",
             f"{words} AND 00/100 DOLLARS (${figure}) as a security deposit")]


NO_PETS = [('10.1. Authorized Pet. Tenant may keep one (1) spayed or neutered domestic dog, currently identified as \n'
            '"Biscuit," a forty -pound (40 lb.) mixed breed, on the Premises. No other animals are permitted without a \n'
            'written Pet Addendum. Tenant shall pay a non -refundable pet fee of $30 0.00 upon execution of this Lease \n'
            'and additional pet rent of $35.00 per month, which is included in the Rent stated in Section 3.1.',
            "10.1. No Pets. No animal of any kind may be kept on the Premises, even for a short time, without a \n"
            "written Pet Addendum signed by Landlord.")]

# A house in a county with no court holiday calendar in calendars/ (TODO item 85): the 3-day notice's period cannot be
# counted there, so whether it has passed is outside the tool.
ORANGE = [("located at 2217 SW 35th Place, Gainesville, Alachua County, Florida 32608",
           "located at 1450 Lake Baldwin Lane, Orlando, Orange County, Florida 32814"),
          ("storm warning for Alachua \nCounty, Tenant shall", "storm warning for Orange \nCounty, Tenant shall"),
          ("exclusively in the courts of Alachua \nCounty, Florida.", "exclusively in the courts of Orange \nCounty, Florida.")]

# A tenancy under way when the stories happen (September 2026): from August 1, 2026, a year.
CURRENT = term("August 1, 2026", "July 31, 2027", "July 15, 2026")


# ---- The leases, by name, and the eval stories that read each (dev/scenarios/eval_*.json, the lease path in
# "start"). Rent and deposit are the story's where it gives them; where it gives one, the other is the same.

LEASES = {
    "current": CURRENT,                                                   # entry_shower, noise_neighbors,
                                                                          # repair_mold_apt, nc_mixed_heater,
                                                                          # nc_roommate, nc_towing,
                                                                          # know_violation_waterbed,
                                                                          # know_violation_guest, know_repair_mold_code
    "current_no_pets": CURRENT + NO_PETS,                                 # violation_dog, cases_retaliation
    "current_orange": CURRENT + ORANGE,                                   # know_nonpayment_orange
    "cash_1300": CURRENT + rent("ONE THOUSAND THREE HUNDRED", "1,300.00", "2,600.00")
                 + deposit("ONE THOUSAND THREE HUNDRED", "1,300.00"),     # cases_3day_cash
    "taped_1100": CURRENT + rent("ONE THOUSAND ONE HUNDRED", "1,100.00", "2,200.00")
                  + deposit("ONE THOUSAND ONE HUNDRED", "1,100.00"),      # nonpayment_taped
    "family_1050": CURRENT + rent("ONE THOUSAND FIFTY", "1,050.00", "2,100.00")
                   + deposit("ONE THOUSAND FIFTY", "1,050.00"),           # leave_early_family
    "ended_2026-06-30": term("July 1, 2025", "June 30, 2026", "June 15, 2025")
                        + rent("ONE THOUSAND", "1,000.00", "2,000.00")
                        + deposit("ONE THOUSAND", "1,000.00"),            # cases_late_claim
    "ended_2026-07-31": term("August 1, 2025", "July 31, 2026", "July 15, 2025")
                        + rent("NINE HUNDRED", "900.00", "1,800.00")
                        + deposit("NINE HUNDRED", "900.00"),              # deposit_ghosted, know_deposit_unsure
    "ended_2026-08-31": term("September 1, 2025", "August 31, 2026", "August 15, 2025")
                        + rent("ONE THOUSAND TWO HUNDRED", "1,200.00", "2,400.00")
                        + deposit("ONE THOUSAND TWO HUNDRED", "1,200.00"),  # claim_carpet
    "ends_2026-12-31": term("January 1, 2026", "December 31, 2026", "December 15, 2025"),  # lease_end_renewal,
                                                                          # know_lease_holdover
    # a year's term that ended on 2025-09-30: month to month since, under the lease's own Section 2.4
    "month_to_month_950": term("October 1, 2024", "September 30, 2025", "September 15, 2024")
                          + rent("NINE HUNDRED FIFTY", "950.00", "1,900.00")
                          + deposit("NINE HUNDRED FIFTY", "950.00"),      # rent_hike_duplex
}


# ---- The PDF: the text's lines in order, in Helvetica, one page per page of lease.pdf.

def escaped(line):
    """A line as a PDF string: Windows-1252 bytes (the font's encoding), with \\, (, and ) escaped."""
    return b"(" + line.encode("cp1252").replace(b"\\", b"\\\\").replace(b"(", b"\\(").replace(b")", b"\\)") + b")"


def pdf_bytes(pages):
    """A plain PDF of the pages' text: numbered objects (the catalog, the page list, the font, then each page
    and its text), then the table of where each object starts, which a PDF reader uses to find them."""
    out = io.BytesIO()
    out.write(b"%PDF-1.4\n")
    starts = []

    def add(body):                                         # the next object, numbered from 1 in order
        starts.append(out.tell())
        out.write(f"{len(starts)} 0 obj\n".encode() + body + b"\nendobj\n")

    count = len(pages)
    add(b"<< /Type /Catalog /Pages 2 0 R >>")
    add(f"<< /Type /Pages /Kids [{' '.join(f'{4 + 2 * i} 0 R' for i in range(count))}] /Count {count} >>".encode())
    add(b"<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica /Encoding /WinAnsiEncoding >>")
    for i, text in enumerate(pages):
        lines = b" Tj T*\n".join(escaped(line) for line in text.split("\n")) + b" Tj"
        stream = b"BT /F1 6 Tf 8 TL 30 770 Td\n" + lines + b"\nET"
        add(f"<< /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792] /Resources << /Font << /F1 3 0 R >> >> "
            f"/Contents {5 + 2 * i} 0 R >>".encode())
        add(f"<< /Length {len(stream)} >>\nstream\n".encode() + stream + b"\nendstream")
    table = out.tell()
    out.write(f"xref\n0 {len(starts) + 1}\n0000000000 65535 f \n".encode())
    out.write(b"".join(f"{start:010d} 00000 n \n".encode() for start in starts))
    out.write(f"trailer\n<< /Size {len(starts) + 1} /Root 1 0 R >>\nstartxref\n{table}\n%%EOF\n".encode())
    return out.getvalue()


def build(name, changes, pages):
    """Make each change, once, in the pages' text; write the PDF; read it back and check it. Returns the path."""
    pages = list(pages)
    for old, new in changes:
        holding = [i for i, text in enumerate(pages) if old in text]
        found = sum(text.count(old) for text in pages)
        if found != 1:
            sys.exit(f"{name}: {old[:60]!r} is in lease.pdf's text {found} times, not once")
        pages[holding[0]] = pages[holding[0]].replace(old, new)
    path = OUT / f"{name}.pdf"
    path.write_bytes(pdf_bytes(pages))
    back = [page.extract_text() or "" for page in PyPDF2.PdfReader(path).pages]
    if [squash(t) for t in back] != [squash(t) for t in pages]:
        sys.exit(f"{name}: the PDF does not read back as the changed text")
    return path


if __name__ == "__main__":
    if not SOURCE.exists():
        sys.exit("lease.pdf is not in the project folder; the test leases are built from it")
    OUT.mkdir(exist_ok=True)
    source_pages = [page.extract_text() or "" for page in PyPDF2.PdfReader(SOURCE).pages]
    for lease_name, lease_changes in LEASES.items():
        print("wrote", build(lease_name, lease_changes, source_pages).relative_to(ROOT), f"({len(lease_changes)} changes)")
