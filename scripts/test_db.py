from datetime import date

from gst_copilot.db import Document, SessionLocal, init_db

# 1. Make sure the table exists
init_db()
print("1. table ready")

with SessionLocal() as session:
    # 2. Add one fake row
    fake = Document(
        doc_no="TEST/01/2025-GST",
        doc_type="circular",
        issue_date=date(2025, 10, 1),
        subject="Fake row to test the database",
        source_url="https://example.com/test.pdf",
    )
    session.add(fake)
    session.commit()
    print("2. inserted, id =", fake.id)

    # 3. Read it back
    row = session.query(Document).filter_by(doc_no="TEST/01/2025-GST").first()
    print("3. read back:", row.doc_no, "|", row.issue_date, "|", row.status)

    # 4. Delete it, so the real data starts clean
    session.delete(row)
    session.commit()
    print("4. deleted, rows left =", session.query(Document).count())