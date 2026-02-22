"""Reset semua transaksi dan poin/total belanja member.

Cara pakai:
    python tools/reset_transaksi.py
"""

from pathlib import Path
import sys

BASE_DIR = Path(__file__).resolve().parents[1]
APP_DIR = BASE_DIR / "app"

sys.path.insert(0, str(APP_DIR))

from app_simple import app, db, Member, Transaksi, TransaksiItem  # noqa: E402


def main() -> None:
    print("PERINGATAN: Ini akan menghapus semua transaksi dan item transaksi,")
    print("serta mereset poin dan total belanja semua member ke 0.")
    konfirmasi = input("Ketik 'YA' untuk melanjutkan: ").strip()
    if konfirmasi != "YA":
        print("Dibatalkan.")
        return

    with app.app_context():
        db.session.query(TransaksiItem).delete(synchronize_session=False)
        db.session.query(Transaksi).delete(synchronize_session=False)
        db.session.query(Member).update(
            {Member.points: 0, Member.total_spent: 0},
            synchronize_session=False
        )
        db.session.commit()

    print("Selesai: transaksi dihapus, poin/total belanja member direset.")


if __name__ == "__main__":
    main()
