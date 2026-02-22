"""
Telegram Bot Service untuk Monitoring Kasir Toko Sembako
Fitur:
- Laporan penjualan real-time
- Notifikasi transaksi
- Alert stok rendah
- Monitoring dari mana saja
"""

import os
import asyncio
from datetime import datetime, date
import io
import json
from urllib.parse import quote

import requests
from openpyxl import Workbook
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes
import logging

# Setup logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

class TelegramBotService:
    def __init__(self, bot_token, admin_chat_ids, app_context):
        """
        Initialize Telegram Bot Service
        
        Args:
            bot_token: Token dari @BotFather
            admin_chat_ids: List of admin chat IDs yang bisa akses bot
            app_context: Flask app untuk akses database
        """
        self.bot_token = bot_token
        self.admin_chat_ids = [str(id) for id in admin_chat_ids]
        self.app_context = app_context
        self.application = None
        self.notify_new_transaction = True  # Flag untuk notifikasi transaksi baru
        self.loop = None  # Store event loop reference
        
    def _execute_in_app_context(self, func):
        """Execute a function within Flask app context"""
        with self.app_context.app_context():
            return func()
    
    def is_admin(self, chat_id):
        """Check if user is admin"""
        return str(chat_id) in self.admin_chat_ids

    def _main_menu_markup(self) -> InlineKeyboardMarkup:
        # Simple & elegant: 2-column grid
        keyboard = [
            [
                InlineKeyboardButton("📦 Produk", callback_data='m_total_produk'),
                InlineKeyboardButton("💰 Penjualan", callback_data='m_total_penjualan'),
            ],
            [
                InlineKeyboardButton("⚠️ Stok Alert", callback_data='m_stok'),
                InlineKeyboardButton("📈 Keuntungan", callback_data='m_total_keuntungan'),
            ],
            [
                InlineKeyboardButton("👥 Member", callback_data='m_member'),
                InlineKeyboardButton("🧾 Transaksi", callback_data='m_transaksi'),
            ],
            [
                InlineKeyboardButton("📉 Tren", callback_data='m_tren'),
                InlineKeyboardButton("📊 Laporan Excel", callback_data='m_laporan_excel'),
            ],
            [
                InlineKeyboardButton("🗄️ Backup", callback_data='m_backup'),
                InlineKeyboardButton("🧨 Reset", callback_data='m_reset'),
            ],
        ]
        return InlineKeyboardMarkup(keyboard)

    def _back_menu_markup(self, target: str = 'back_to_menu') -> InlineKeyboardMarkup:
        return InlineKeyboardMarkup([[InlineKeyboardButton("◀️ Menu", callback_data=target)]])

    def _result_edit(self, text: str, reply_markup: InlineKeyboardMarkup | None = None) -> dict:
        return {"kind": "edit", "text": text, "reply_markup": reply_markup}

    def _result_text(self, text: str) -> dict:
        return {"kind": "text", "text": text}

    def _result_document(self, data: bytes, filename: str, caption: str) -> dict:
        return {"kind": "document", "data": data, "filename": filename, "caption": caption}

    def _result_photo(self, data: bytes, caption: str) -> dict:
        return {"kind": "photo", "data": data, "caption": caption}
    
    async def start_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handler untuk /start command"""
        try:
            chat_id = update.effective_chat.id
            logger.info(f"Received /start from chat_id: {chat_id}")
            
            if not self.is_admin(chat_id):
                await update.message.reply_text(
                    "❌ Akses ditolak!\n"
                    "Bot ini hanya untuk admin toko.\n"
                    f"Chat ID Anda: {chat_id}"
                )
                return
            
            reply_markup = self._main_menu_markup()
            
            await update.message.reply_text(
                "🏪 *BOT MONITORING KASIR*\n"
                "Pilih menu:",
                parse_mode='Markdown',
                reply_markup=reply_markup
            )
            logger.info(f"Sent main menu to chat_id: {chat_id}")
        except Exception as e:
            logger.error(f"Error in start_command: {e}", exc_info=True)
            try:
                await update.message.reply_text(f"❌ Error: {str(e)}")
            except:
                pass
    
    async def help_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handler untuk /help command"""
        if not self.is_admin(update.effective_chat.id):
            return

        help_text = """
🤖 *PANDUAN BOT MONITORING*

Gunakan tombol menu (Inline Keyboard) dari `/start`.

Menu yang tersedia:
1) Total Produk
2) Produk habis & hampir habis (+ download Excel)
3) Info Member (total transaksi, total uang, info pribadi)
4) Info Transaksi (riwayat + nota)
5) Total Penjualan (hari ini)
6) Total Keuntungan (hari ini)
7) Tren Penjualan (grafik)
8) Backup (buat backup & download)
9) Laporan Keuangan (Excel seperti menu Laporan)
"""
        await update.message.reply_text(help_text, parse_mode='Markdown')

    async def handle_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handler untuk inline keyboard callbacks"""
        query = update.callback_query
        await query.answer()

        chat_id = query.from_user.id
        callback_data = query.data
        logger.info(f"Received callback '{callback_data}' from chat_id: {chat_id}")

        if not self.is_admin(chat_id):
            await query.edit_message_text("❌ Akses ditolak!")
            return

        try:
            result = self._execute_in_app_context(lambda: self._process_callback(callback_data))
            if not result:
                return

            kind = result.get('kind', 'text')
            if kind in ('text', 'edit'):
                await query.edit_message_text(
                    result.get('text', ''),
                    parse_mode='Markdown',
                    reply_markup=result.get('reply_markup'),
                )
                return

            if kind == 'document':
                bio = io.BytesIO(result['data'])
                bio.name = result['filename']
                await context.bot.send_document(chat_id=chat_id, document=bio, caption=result.get('caption', ''))
                await query.edit_message_text(
                    "✅ File sudah dikirim.",
                    parse_mode='Markdown',
                    reply_markup=self._main_menu_markup(),
                )
                return

            if kind == 'photo':
                bio = io.BytesIO(result['data'])
                await context.bot.send_photo(chat_id=chat_id, photo=bio, caption=result.get('caption', ''))
                await query.edit_message_text(
                    "✅ Grafik sudah dikirim.",
                    parse_mode='Markdown',
                    reply_markup=self._main_menu_markup(),
                )
                return

            await query.edit_message_text("⚠️ Response type tidak dikenal.")
        except Exception as e:
            logger.error(f"Error in handle_callback: {e}", exc_info=True)
            await query.edit_message_text(f"❌ Error: {str(e)}")

    async def omzet_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        await self._reply_from_callback(update, 'omzet_hari_ini')

    async def produk_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        await self._reply_from_callback(update, 'produk_terlaris')

    async def member_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        await self._reply_from_callback(update, 'top_member')

    async def stok_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        await self._reply_from_callback(update, 'stok_rendah')

    async def grafik_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        await self._reply_from_callback(update, 'grafik_penjualan')

    async def members_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        await self._reply_from_callback(update, 'total_member')

    async def settings_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        await self._reply_from_callback(update, 'menu_pengaturan')
    
    def _process_callback(self, callback_data):
        """Process callback and generate response (runs in Flask app context)."""
        from flask import current_app
        from sqlalchemy import func
        from collections import defaultdict

        # Import models/functions from the running app module.
        try:
            from app.app_simple import (
                Produk,
                Member,
                Transaksi,
                TransaksiItem,
                Pengaturan,
                generate_laporan_hari,
                generate_laporan_bulan,
                generate_laporan_tahun,
                backup_database,
            )
        except Exception:
            from app_simple import (  # type: ignore
                Produk,
                Member,
                Transaksi,
                TransaksiItem,
                Pengaturan,
                generate_laporan_hari,
                generate_laporan_bulan,
                generate_laporan_tahun,
                backup_database,
            )

        # Get db session from current_app to ensure proper Flask app context
        db = current_app.extensions['sqlalchemy']
        session = db.session

        logger.info(f"Processing callback: {callback_data}")

        # -------------------- MAIN MENU --------------------
        if callback_data in ('back_to_menu', 'm_menu'):
            return self._result_edit("🏪 *MENU UTAMA*\nPilih menu:", self._main_menu_markup())

        if callback_data == 'm_total_produk':
            total = session.query(func.count(Produk.id)).scalar() or 0
            return self._result_edit(
                f"📦 *TOTAL PRODUK*\n\nTotal produk terdaftar: *{total}*",
                self._back_menu_markup(),
            )

        if callback_data == 'm_stok':
            habis = session.query(Produk).filter(Produk.stok <= 0).order_by(Produk.nama).all()
            hampir = session.query(Produk).filter(Produk.stok > 0, Produk.stok <= Produk.minimal_stok).order_by(Produk.stok.asc()).all()
            text_habis = "\n".join([f"- {p.nama} (stok {p.stok})" for p in habis[:10]]) or "- (tidak ada)"
            text_hampir = "\n".join([f"- {p.nama} (stok {p.stok}, min {p.minimal_stok})" for p in hampir[:10]]) or "- (tidak ada)"
            msg = (
                "⚠️ *PRODUK HABIS & HAMPIR HABIS*\n\n"
                f"🔴 Habis: *{len(habis)}*\n{text_habis}\n\n"
                f"🟡 Hampir habis: *{len(hampir)}*\n{text_hampir}\n\n"
                "Klik tombol di bawah untuk download Excel."
            )
            kb = InlineKeyboardMarkup([
                [InlineKeyboardButton("⬇️ Download Excel", callback_data='stok_download_excel')],
                [InlineKeyboardButton("◀️ Menu", callback_data='back_to_menu')],
            ])
            return self._result_edit(msg, kb)

        if callback_data == 'stok_download_excel':
            habis = session.query(Produk).filter(Produk.stok <= 0).order_by(Produk.nama).all()
            hampir = session.query(Produk).filter(Produk.stok > 0, Produk.stok <= Produk.minimal_stok).order_by(Produk.stok.asc()).all()

            wb = Workbook()
            ws = wb.active
            ws.title = "Stok Alert"
            ws.append(["Status", "Kode", "Nama", "Stok", "Minimal Stok", "Kategori"]) 

            def kategori_name(prod):
                try:
                    return prod.kategori.nama if getattr(prod, 'kategori', None) else ""
                except Exception:
                    return ""

            for p in habis:
                ws.append(["HABIS", getattr(p, 'kode', ''), p.nama, p.stok, getattr(p, 'minimal_stok', ''), kategori_name(p)])
            for p in hampir:
                ws.append(["HAMPIR", getattr(p, 'kode', ''), p.nama, p.stok, getattr(p, 'minimal_stok', ''), kategori_name(p)])

            output = io.BytesIO()
            wb.save(output)
            data = output.getvalue()
            filename = f"stok_alert_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
            caption = "📎 Excel stok habis & hampir habis"
            return self._result_document(data, filename, caption)

        if callback_data == 'm_member':
            # Top 10 member by total spent (all time)
            rows = (
                session.query(
                    Member.id,
                    Member.nama,
                    func.coalesce(func.sum(Transaksi.total), 0).label('total_spent'),
                    func.count(Transaksi.id).label('total_transaksi'),
                )
                .join(Transaksi, Transaksi.member_id == Member.id)
                .group_by(Member.id, Member.nama)
                .order_by(func.coalesce(func.sum(Transaksi.total), 0).desc())
                .limit(10)
                .all()
            )
            if not rows:
                return self._result_edit(
                    "👥 *INFO MEMBER*\n\nBelum ada transaksi member.",
                    self._back_menu_markup(),
                )

            kb_rows = [[InlineKeyboardButton(f"{i+1}. {r.nama}", callback_data=f"member_{r.id}")] for i, r in enumerate(rows)]
            kb_rows.append([InlineKeyboardButton("◀️ Menu", callback_data='back_to_menu')])
            msg = "👥 *INFO MEMBER*\n\nPilih member untuk detail:"
            return self._result_edit(msg, InlineKeyboardMarkup(kb_rows))

        if callback_data.startswith('member_'):
            member_id = int(callback_data.split('_', 1)[1])
            m = session.query(Member).filter(Member.id == member_id).first()
            if not m:
                return self._result_edit("Member tidak ditemukan.", InlineKeyboardMarkup([[InlineKeyboardButton("◀️ Kembali", callback_data='m_member')]]))

            totals = (
                session.query(
                    func.coalesce(func.sum(Transaksi.total), 0),
                    func.count(Transaksi.id),
                )
                .filter(Transaksi.member_id == member_id)
                .first()
            )
            total_spent = float(totals[0] or 0)
            total_trx = int(totals[1] or 0)

            msg = (
                "👤 *DETAIL MEMBER*\n\n"
                f"Nama: *{m.nama}*\n"
                f"No. Telp: `{getattr(m, 'no_telp', '') or '-'}`\n"
                f"Alamat: {getattr(m, 'alamat', '') or '-'}\n\n"
                f"🧾 Total Transaksi: *{total_trx}*\n"
                f"💰 Total Uang Transaksi: *Rp {total_spent:,.0f}*\n"
            )
            kb = InlineKeyboardMarkup([
                [InlineKeyboardButton("◀️ Kembali", callback_data='m_member')],
            ])
            return self._result_edit(msg, kb)

        if callback_data == 'm_transaksi':
            return self._show_transaksi_page(session, Transaksi, page=1)

        if callback_data.startswith('trx_page_'):
            page = int(callback_data.split('_')[-1])
            return self._show_transaksi_page(session, Transaksi, page=page)

        if callback_data.startswith('trx_'):
            trx_id = int(callback_data.split('_', 1)[1])
            t = session.query(Transaksi).filter(Transaksi.id == trx_id).first()
            if not t:
                return self._result_edit("Transaksi tidak ditemukan.", InlineKeyboardMarkup([[InlineKeyboardButton("◀️ Kembali", callback_data='m_transaksi')]]))

            # Build receipt text
            items = session.query(TransaksiItem).filter(TransaksiItem.transaksi_id == trx_id).all()
            lines = []
            for it in items[:30]:
                nama = it.produk.nama if getattr(it, 'produk', None) else getattr(it, 'nama_produk', '-')
                lines.append(f"- {nama} x{it.jumlah} @Rp {it.harga:,.0f} = Rp {it.subtotal:,.0f}")

            nota_url = f"http://<IP-CasaOS>:5000/transaksi/struk/{trx_id}"
            msg = (
                "🧾 *NOTA TRANSAKSI*\n\n"
                f"Kode: *{t.kode_transaksi}*\n"
                f"Tanggal: {t.tanggal.strftime('%d-%m-%Y %H:%M')}\n"
                f"Metode: *{t.payment_method or 'tunai'}*\n"
                f"Kasir: {getattr(getattr(t, 'user', None), 'nama', '-') or '-'}\n\n"
                + "\n".join(lines)
                + f"\n\n💰 Total: *Rp {t.total:,.0f}*\n"
                + f"\n🌐 Link nota (browser): {nota_url}"
            )
            kb = InlineKeyboardMarkup([
                [InlineKeyboardButton("◀️ Kembali", callback_data='m_transaksi')],
            ])
            return self._result_edit(msg, kb)

        if callback_data == 'm_total_penjualan':
            today = date.today()
            transaksi_list = session.query(Transaksi).filter(func.date(Transaksi.tanggal) == today).all()
            total_penjualan = sum(float(t.total or 0) for t in transaksi_list)
            return self._result_edit(
                f"💰 *TOTAL PENJUALAN (HARI INI)*\n\nTanggal: {today.strftime('%d %B %Y')}\nTotal: *Rp {total_penjualan:,.0f}*\nTransaksi: *{len(transaksi_list)}*",
                self._back_menu_markup(),
            )

        if callback_data == 'm_total_keuntungan':
            today = date.today()
            transaksi_list = session.query(Transaksi).filter(func.date(Transaksi.tanggal) == today).all()
            keuntungan = 0.0
            for t in transaksi_list:
                for it in getattr(t, 'items', []) or []:
                    hb = it.produk.harga_beli if getattr(it, 'produk', None) else 0
                    keuntungan += (float(it.harga or 0) - float(hb or 0)) * float(it.jumlah or 0)
            return self._result_edit(
                f"📈 *TOTAL KEUNTUNGAN (HARI INI)*\n\nTanggal: {today.strftime('%d %B %Y')}\nKeuntungan: *Rp {keuntungan:,.0f}*",
                self._back_menu_markup(),
            )

        if callback_data == 'm_tren':
            # 14 days trend
            from datetime import timedelta
            end = date.today()
            start = end - timedelta(days=13)
            sales_by_date = defaultdict(float)
            transaksi_list = session.query(Transaksi).filter(func.date(Transaksi.tanggal) >= start).all()
            for t in transaksi_list:
                key = t.tanggal.strftime('%Y-%m-%d')
                sales_by_date[key] += float(t.total or 0)

            labels = []
            values = []
            for i in range(14):
                d = start + timedelta(days=i)
                k = d.strftime('%Y-%m-%d')
                labels.append(d.strftime('%d/%m'))
                values.append(round(sales_by_date.get(k, 0.0), 2))

            config = {
                "type": "line",
                "data": {
                    "labels": labels,
                    "datasets": [
                        {
                            "label": "Penjualan (Rp)",
                            "data": values,
                            "borderColor": "#2b6ef3",
                            "backgroundColor": "rgba(43,110,243,0.15)",
                            "fill": True,
                            "tension": 0.35,
                            "pointRadius": 3,
                        }
                    ],
                },
                "options": {
                    "plugins": {
                        "legend": {"display": False},
                        "title": {"display": True, "text": "Tren Penjualan 14 Hari"},
                    },
                    "scales": {
                        "y": {
                            "ticks": {
                                "callback": "function(value){return 'Rp ' + value.toLocaleString('id-ID');}",
                            }
                        }
                    },
                },
            }

            try:
                url = "https://quickchart.io/chart"
                params = {
                    "c": json.dumps(config),
                    "format": "png",
                    "width": 900,
                    "height": 450,
                    "backgroundColor": "white",
                }
                r = requests.get(url, params=params, timeout=25)
                r.raise_for_status()
                caption = f"📉 Tren Penjualan {labels[0]} - {labels[-1]}"
                return self._result_photo(r.content, caption)
            except Exception as e:
                total = sum(values)
                return self._result_edit(
                    f"📉 *TREN PENJUALAN*\n\nGagal buat grafik (internet/QuickChart).\nTotal 14 hari: *Rp {total:,.0f}*\nError: {e}",
                    self._back_menu_markup(),
                )

        if callback_data == 'm_backup':
            kb = InlineKeyboardMarkup([
                [InlineKeyboardButton("▶️ Backup Sekarang", callback_data='backup_now')],
                [InlineKeyboardButton("⬇️ Download Backup Terbaru", callback_data='backup_download_latest')],
                [InlineKeyboardButton("◀️ Menu", callback_data='back_to_menu')],
            ])
            return self._result_edit("🗄️ *BACKUP*\n\nPilih aksi:", kb)

        if callback_data == 'backup_now':
            ok = bool(backup_database())
            status = "✅ Backup berhasil" if ok else "❌ Backup gagal"
            return self._result_edit(status, InlineKeyboardMarkup([[InlineKeyboardButton("◀️ Kembali", callback_data='m_backup')]]))

        if callback_data == 'backup_download_latest':
            base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            backup_folder = os.path.join(base_dir, 'backups')
            try:
                files = [
                    f for f in os.listdir(backup_folder)
                    if f.startswith('kasir_backup_') and f.endswith('.db')
                ]
                files.sort(reverse=True)
                if not files:
                    return self._result_edit("Belum ada file backup.", InlineKeyboardMarkup([[InlineKeyboardButton("◀️ Kembali", callback_data='m_backup')]]))
                latest = files[0]
                path = os.path.join(backup_folder, latest)
                with open(path, 'rb') as fh:
                    data = fh.read()
                return self._result_document(data, latest, "🗄️ Backup database terbaru")
            except Exception as e:
                return self._result_edit(f"❌ Gagal ambil backup: {e}", InlineKeyboardMarkup([[InlineKeyboardButton("◀️ Kembali", callback_data='m_backup')]]))

        if callback_data == 'm_laporan_excel':
            kb = InlineKeyboardMarkup([
                [InlineKeyboardButton("⬇️ Export Excel (Hari Ini)", callback_data='lap_excel_hari')],
                [InlineKeyboardButton("⬇️ Export Excel (Bulan Ini)", callback_data='lap_excel_bulan')],
                [InlineKeyboardButton("⬇️ Export Excel (Tahun Ini)", callback_data='lap_excel_tahun')],
                [InlineKeyboardButton("◀️ Menu", callback_data='back_to_menu')],
            ])
            return self._result_edit("📊 *LAPORAN KEUANGAN (EXCEL)*\n\nPilih periode:", kb)

        if callback_data in ('lap_excel_hari', 'lap_excel_bulan', 'lap_excel_tahun'):
            now = datetime.now()
            today = now.date()

            if callback_data == 'lap_excel_hari':
                t1 = t2 = today.strftime('%Y-%m-%d')
                wb = generate_laporan_hari(t1, t2)
                mode = 'hari'
            elif callback_data == 'lap_excel_bulan':
                first = today.replace(day=1)
                t1 = first.strftime('%Y-%m-%d')
                t2 = today.strftime('%Y-%m-%d')
                wb = generate_laporan_bulan(t1, t2)
                mode = 'bulan'
            else:
                first = today.replace(month=1, day=1)
                t1 = first.strftime('%Y-%m-%d')
                t2 = today.strftime('%Y-%m-%d')
                wb = generate_laporan_tahun(t1, t2)
                mode = 'tahun'

            output = io.BytesIO()
            wb.save(output)
            filename = f"laporan_keuangan_{mode}_{now.strftime('%Y%m%d_%H%M%S')}.xlsx"
            caption = f"📊 Laporan keuangan ({mode}) {t1} s/d {t2}"
            return self._result_document(output.getvalue(), filename, caption)

        # -------------------- RESET DATA (SAFE: NO PRODUCT TOUCH) --------------------
        if callback_data == 'm_reset':
            msg = (
                "🧨 *RESET DATA (MODE PERCOBAAN)*\n\n"
                "Menu ini untuk menghapus data *transaksi/member/laporan* yang sifatnya percobaan.\n\n"
                "✅ Aman: *Produk/Kategori/Varian/Harga/Stok tidak disentuh sama sekali.*\n\n"
                "Pilih yang mau di-reset:"
            )
            kb = InlineKeyboardMarkup([
                [InlineKeyboardButton("🧾 Reset Transaksi", callback_data='reset_prepare_transaksi')],
                [InlineKeyboardButton("👥 Reset Member", callback_data='reset_prepare_member')],
                [InlineKeyboardButton("📄 Reset Laporan (hapus file report)", callback_data='reset_prepare_laporan')],
                [InlineKeyboardButton("🧨 Reset SEMUA (Transaksi+Member+Laporan)", callback_data='reset_prepare_all')],
                [InlineKeyboardButton("◀️ Menu", callback_data='back_to_menu')],
            ])
            return self._result_edit(msg, kb)

        def _reset_confirm(action_label: str, do_callback: str) -> dict:
            msg = (
                "⚠️ *KONFIRMASI RESET*\n\n"
                f"Anda akan melakukan: *{action_label}*\n\n"
                "Tindakan ini *tidak bisa dibatalkan*.\n"
                "Produk tidak akan terhapus.\n\n"
                "Lanjutkan?"
            )
            kb = InlineKeyboardMarkup([
                [InlineKeyboardButton("✅ YA, RESET", callback_data=do_callback)],
                [InlineKeyboardButton("❌ Batal", callback_data='m_reset')],
            ])
            return self._result_edit(msg, kb)

        if callback_data == 'reset_prepare_transaksi':
            return _reset_confirm("Reset Transaksi (hapus riwayat + item transaksi)", 'reset_do_transaksi')

        if callback_data == 'reset_prepare_member':
            return _reset_confirm("Reset Member (hapus data member saja)", 'reset_do_member')

        if callback_data == 'reset_prepare_laporan':
            return _reset_confirm("Reset Laporan (hapus file laporan_harian_*.xlsx)", 'reset_do_laporan')

        if callback_data == 'reset_prepare_all':
            return _reset_confirm("Reset SEMUA (Transaksi + Member + Laporan)", 'reset_do_all')

        def _delete_report_files() -> tuple[int, int]:
            # Returns: (deleted_count, total_found)
            reports_dir = os.path.join(current_app.instance_path, 'reports')
            if not os.path.exists(reports_dir):
                return 0, 0
            files = [
                f for f in os.listdir(reports_dir)
                if f.startswith('laporan_harian_') and f.endswith('.xlsx')
            ]
            deleted = 0
            for f in files:
                try:
                    os.remove(os.path.join(reports_dir, f))
                    deleted += 1
                except Exception:
                    pass
            return deleted, len(files)

        if callback_data == 'reset_do_transaksi':
            try:
                # Hapus item dulu, baru transaksi
                items_deleted = session.query(TransaksiItem).delete(synchronize_session=False)
                trx_deleted = session.query(Transaksi).delete(synchronize_session=False)
                session.commit()
                msg = (
                    "✅ *RESET TRANSAKSI SELESAI*\n\n"
                    f"Transaksi dihapus: *{trx_deleted}*\n"
                    f"Item transaksi dihapus: *{items_deleted}*\n\n"
                    "Produk tidak berubah."
                )
                return self._result_edit(msg, InlineKeyboardMarkup([[InlineKeyboardButton("◀️ Kembali", callback_data='back_to_menu')]]))
            except Exception as e:
                session.rollback()
                return self._result_edit(f"❌ Gagal reset transaksi: {e}", InlineKeyboardMarkup([[InlineKeyboardButton("◀️ Kembali", callback_data='m_reset')]]))

        if callback_data == 'reset_do_member':
            try:
                # Supaya aman walaupun transaksi masih ada: putuskan relasi transaksi->member
                session.query(Transaksi).update({Transaksi.member_id: None}, synchronize_session=False)
                members_deleted = session.query(Member).delete(synchronize_session=False)
                session.commit()
                msg = (
                    "✅ *RESET MEMBER SELESAI*\n\n"
                    f"Member dihapus: *{members_deleted}*\n\n"
                    "Produk tidak berubah."
                )
                return self._result_edit(msg, InlineKeyboardMarkup([[InlineKeyboardButton("◀️ Kembali", callback_data='back_to_menu')]]))
            except Exception as e:
                session.rollback()
                return self._result_edit(f"❌ Gagal reset member: {e}", InlineKeyboardMarkup([[InlineKeyboardButton("◀️ Kembali", callback_data='m_reset')]]))

        if callback_data == 'reset_do_laporan':
            deleted, found = _delete_report_files()
            msg = (
                "✅ *RESET LAPORAN SELESAI*\n\n"
                f"File laporan ditemukan: *{found}*\n"
                f"File laporan dihapus: *{deleted}*\n\n"
                "(Hanya file `laporan_harian_*.xlsx` di folder instance/reports)\n"
                "Produk tidak berubah."
            )
            return self._result_edit(msg, InlineKeyboardMarkup([[InlineKeyboardButton("◀️ Kembali", callback_data='back_to_menu')]]))

        if callback_data == 'reset_do_all':
            try:
                session.query(Transaksi).update({Transaksi.member_id: None}, synchronize_session=False)
                items_deleted = session.query(TransaksiItem).delete(synchronize_session=False)
                trx_deleted = session.query(Transaksi).delete(synchronize_session=False)
                members_deleted = session.query(Member).delete(synchronize_session=False)
                session.commit()
            except Exception as e:
                session.rollback()
                return self._result_edit(f"❌ Gagal reset semua: {e}", InlineKeyboardMarkup([[InlineKeyboardButton("◀️ Kembali", callback_data='m_reset')]]))

            deleted, found = _delete_report_files()
            msg = (
                "✅ *RESET SEMUA SELESAI*\n\n"
                f"Transaksi dihapus: *{trx_deleted}*\n"
                f"Item transaksi dihapus: *{items_deleted}*\n"
                f"Member dihapus: *{members_deleted}*\n"
                f"File laporan dihapus: *{deleted}/{found}*\n\n"
                "Produk/Kategori/Varian/Harga/Stok tetap aman (tidak disentuh)."
            )
            return self._result_edit(msg, InlineKeyboardMarkup([[InlineKeyboardButton("◀️ Kembali", callback_data='back_to_menu')]]))

        return self._result_edit(
            "⚠️ Menu tidak dikenali. Silakan kembali ke menu utama.",
            InlineKeyboardMarkup([[InlineKeyboardButton("🏠 Menu Utama", callback_data='back_to_menu')]]),
        )

    def _show_transaksi_page(self, session, Transaksi, page: int) -> dict:
        from sqlalchemy import func

        page = max(1, page)
        page_size = 8
        offset = (page - 1) * page_size
        total = session.query(func.count(Transaksi.id)).scalar() or 0
        rows = (
            session.query(Transaksi)
            .order_by(Transaksi.tanggal.desc())
            .offset(offset)
            .limit(page_size)
            .all()
        )

        if not rows:
            return self._result_edit(
                "🧾 *RIWAYAT TRANSAKSI*\n\nBelum ada transaksi.",
                InlineKeyboardMarkup([[InlineKeyboardButton("◀️ Kembali", callback_data='back_to_menu')]]),
            )

        msg_lines = ["🧾 *RIWAYAT TRANSAKSI*", "(klik untuk lihat nota)", ""]
        kb = []
        for t in rows:
            label = f"{t.kode_transaksi} • Rp {float(t.total or 0):,.0f}"
            kb.append([InlineKeyboardButton(label, callback_data=f"trx_{t.id}")])
            msg_lines.append(f"- {t.kode_transaksi} | {t.tanggal.strftime('%d-%m %H:%M')} | Rp {float(t.total or 0):,.0f}")

        nav = []
        if offset > 0:
            nav.append(InlineKeyboardButton("⬅️ Prev", callback_data=f"trx_page_{page-1}"))
        if offset + page_size < total:
            nav.append(InlineKeyboardButton("Next ➡️", callback_data=f"trx_page_{page+1}"))
        if nav:
            kb.append(nav)
        kb.append([InlineKeyboardButton("◀️ Kembali", callback_data='back_to_menu')])

        return self._result_edit("\n".join(msg_lines), InlineKeyboardMarkup(kb))
        
        if callback_data == 'laporan_hari_ini':
            today = date.today()
            transaksi_list = session.query(Transaksi).filter(
                func.date(Transaksi.tanggal) == today
            ).all()
            
            total_penjualan = sum(t.total for t in transaksi_list)
            total_transaksi = len(transaksi_list)
            
            # Hitung keuntungan
            total_keuntungan = 0
            for t in transaksi_list:
                for item in t.items:
                    harga_beli = item.produk.harga_beli if item.produk else 0
                    total_keuntungan += (item.harga - harga_beli) * item.jumlah
            
            # Payment method breakdown
            payment_count = defaultdict(int)
            for t in transaksi_list:
                payment_count[t.payment_method or 'tunai'] += 1
            
            payment_text = "\n".join([f"  • {k}: {v} transaksi" for k, v in payment_count.items()])
            
            return f"""
📊 *LAPORAN HARI INI*
{today.strftime('%d %B %Y')}

💰 Total Penjualan: Rp {total_penjualan:,.0f}
📈 Keuntungan: Rp {total_keuntungan:,.0f}
🧾 Total Transaksi: {total_transaksi}

💳 *Metode Pembayaran:*
{payment_text if payment_text else '  Belum ada transaksi'}

✅ Laporan diupdate real-time
"""
        
        elif callback_data == 'omzet_hari_ini':
            today = date.today()
            transaksi_list = session.query(Transaksi).filter(
                func.date(Transaksi.tanggal) == today
            ).all()
            
            total_penjualan = sum(t.total for t in transaksi_list)
            total_transaksi = len(transaksi_list)
            
            if total_transaksi > 0:
                avg_transaksi = total_penjualan / total_transaksi
            else:
                avg_transaksi = 0
            
            # Group by hour
            sales_by_hour = defaultdict(float)
            for t in transaksi_list:
                hour = t.tanggal.hour
                sales_by_hour[hour] += t.total
            
            # Peak hour
            if sales_by_hour:
                peak_hour = max(sales_by_hour, key=sales_by_hour.get)
                peak_sales = sales_by_hour[peak_hour]
                peak_text = f"Jam {peak_hour}:00 (Rp {peak_sales:,.0f})"
            else:
                peak_text = "-"
            
            return f"""
💰 *OMZET HARI INI*
{today.strftime('%d %B %Y')}

💵 Total Omzet: Rp {total_penjualan:,.0f}
🧾 Jumlah Transaksi: {total_transaksi}
📊 Rata-rata/Transaksi: Rp {avg_transaksi:,.0f}

🔥 Jam Tersibuk: {peak_text}

✅ Data real-time
"""
        
        elif callback_data == 'produk_terlaris':
            today = date.today()
            transaksi_list = session.query(Transaksi).filter(
                func.date(Transaksi.tanggal) == today
            ).all()
            
            product_sales = Counter()
            product_qty = Counter()
            
            for t in transaksi_list:
                for item in t.items:
                    product_name = item.produk.nama if item.produk else 'Unknown'
                    product_sales[product_name] += item.subtotal
                    product_qty[product_name] += item.jumlah
            
            top_5 = product_sales.most_common(5)
            
            if top_5:
                product_text = ""
                for idx, (name, sales) in enumerate(top_5, 1):
                    qty = product_qty[name]
                    product_text += f"{idx}. {name}\n   💰 Rp {sales:,.0f} | 📦 {qty} pcs\n\n"
            else:
                product_text = "Belum ada penjualan hari ini"
            
            return f"""
📦 *PRODUK TERLARIS HARI INI*
{today.strftime('%d %B %Y')}

{product_text}

✅ Top 5 produk berdasarkan omzet
"""
        
        elif callback_data == 'top_member':
            from datetime import datetime
            current_date = datetime.now()
            first_day = current_date.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
            
            top_members = session.query(
                Member.nama,
                func.sum(Transaksi.total).label('total_spent'),
                func.count(Transaksi.id).label('total_transaksi')
            ).join(Transaksi, Transaksi.member_id == Member.id
            ).filter(Transaksi.tanggal >= first_day
            ).group_by(Member.nama
            ).order_by(func.sum(Transaksi.total).desc()
            ).limit(10
            ).all()
            
            if top_members:
                member_text = ""
                for idx, m in enumerate(top_members, 1):
                    member_text += f"{idx}. {m.nama}\n   💰 Rp {m.total_spent:,.0f} | 🧾 {m.total_transaksi}x\n\n"
            else:
                member_text = "Belum ada data member bulan ini"
            
            return f"""
👥 *TOP MEMBER BULAN INI*
{current_date.strftime('%B %Y')}

{member_text}

✅ Top 10 member berdasarkan total belanja
"""
        
        elif callback_data == 'stok_rendah':
            # Produk dengan stok < 10
            low_stock_products = session.query(Produk).filter(Produk.stok < 10, Produk.stok > 0).order_by(Produk.stok).limit(10).all()
            
            # Varian dengan stok rendah
            low_stock_variants = session.query(VarianProduk).filter(
                VarianProduk.stok < 10, 
                VarianProduk.stok > 0
            ).order_by(VarianProduk.stok).limit(5).all()
            
            if low_stock_products or low_stock_variants:
                product_text = "*📦 Produk Stok Rendah:*\n"
                for p in low_stock_products:
                    emoji = "🔴" if p.stok < 5 else "🟡"
                    product_text += f"{emoji} {p.nama} - Stok: {p.stok}\n"
                
                if low_stock_variants:
                    product_text += "\n*🏷️ Varian Stok Rendah:*\n"
                    for v in low_stock_variants:
                        emoji = "🔴" if v.stok < 5 else "🟡"
                        product_text += f"{emoji} {v.produk.nama} ({v.nama_varian}) - Stok: {v.stok}\n"
            else:
                product_text = "✅ Semua produk stok aman!"
            
            return f"""
⚠️ *ALERT STOK RENDAH*

{product_text}

💡 Segera restock untuk produk 🔴
"""
        
        elif callback_data == 'grafik_penjualan':
            # 7 hari terakhir
            from datetime import timedelta
            today = date.today()
            seven_days_ago = today - timedelta(days=6)
            
            sales_by_date = defaultdict(float)
            transaksi_list = session.query(Transaksi).filter(
                func.date(Transaksi.tanggal) >= seven_days_ago
            ).all()
            
            for t in transaksi_list:
                date_str = t.tanggal.strftime('%d/%m')
                sales_by_date[date_str] += t.total
            
            # Simple text graph
            if sales_by_date:
                max_sales = max(sales_by_date.values())
                graph_text = ""
                for d in range(7):
                    curr_date = seven_days_ago + timedelta(days=d)
                    date_str = curr_date.strftime('%d/%m')
                    sales = sales_by_date.get(date_str, 0)
                    bar_length = int((sales / max_sales) * 10) if max_sales > 0 else 0
                    bar = "█" * bar_length
                    graph_text += f"{date_str}: {bar} Rp {sales:,.0f}\n"
            else:
                graph_text = "Belum ada data penjualan 7 hari terakhir"
            
            total_7days = sum(sales_by_date.values())
            avg_7days = total_7days / 7 if total_7days > 0 else 0
            
            return f"""
📈 *GRAFIK PENJUALAN 7 HARI*

{graph_text}

📊 Total 7 Hari: Rp {total_7days:,.0f}
📊 Rata-rata/Hari: Rp {avg_7days:,.0f}

✅ Data diupdate setiap hari
"""
        
        elif callback_data == 'total_member':
            total_members = session.query(func.count(Member.id)).scalar() or 0
            active_members = session.query(func.count(Member.id)).filter(
                Member.last_purchase.isnot(None)
            ).scalar() or 0
            
            total_points = session.query(
                func.coalesce(func.sum(Member.points), 0)
            ).scalar() or 0
            
            # Get member levels breakdown
            bronze = session.query(func.count(Member.id)).filter(Member.level == 'Bronze').scalar() or 0
            silver = session.query(func.count(Member.id)).filter(Member.level == 'Silver').scalar() or 0
            gold = session.query(func.count(Member.id)).filter(Member.level == 'Gold').scalar() or 0
            
            return f"""
👥 *DATA MEMBER*

👤 Total Member: {total_members}
✅ Member Aktif: {active_members}

💎 *Level Breakdown:*
  🥉 Bronze: {bronze}
  🥈 Silver: {silver}
  🏆 Gold: {gold}

⭐ Total Points: {total_points:,}

📊 Rata-rata/Member: {int(total_points/total_members) if total_members > 0 else 0} pts
"""
        
        elif callback_data == 'performa_minggu':
            from datetime import timedelta
            today = date.today()
            week_ago = today - timedelta(days=6)
            
            # Get this week's data
            week_transaksi = session.query(Transaksi).filter(
                func.date(Transaksi.tanggal) >= week_ago
            ).all()
            
            week_total = sum(t.total for t in week_transaksi)
            week_trans_count = len(week_transaksi)
            week_avg = week_total / week_trans_count if week_trans_count > 0 else 0
            
            # Get last week's data for comparison
            last_week_start = week_ago - timedelta(days=7)
            last_week_transaksi = session.query(Transaksi).filter(
                func.date(Transaksi.tanggal) >= last_week_start,
                func.date(Transaksi.tanggal) < week_ago
            ).all()
            
            last_week_total = sum(t.total for t in last_week_transaksi)
            
            # Calculate growth
            if last_week_total > 0:
                growth = ((week_total - last_week_total) / last_week_total) * 100
                growth_text = f"📈 +{growth:.1f}%" if growth > 0 else f"📉 {growth:.1f}%"
            else:
                growth_text = "🔄 N/A"
            
            # Best day
            sales_by_date = defaultdict(float)
            for t in week_transaksi:
                date_str = t.tanggal.strftime('%d %B')
                sales_by_date[date_str] += t.total
            
            best_day = max(sales_by_date, key=sales_by_date.get) if sales_by_date else "-"
            best_day_sales = sales_by_date.get(best_day, 0) if best_day != "-" else 0
            
            return f"""
📊 *PERFORMA MINGGU INI*

💰 Total Omzet: Rp {week_total:,.0f}
🧾 Total Transaksi: {week_trans_count}
📊 Rata-rata/Transaksi: Rp {week_avg:,.0f}

📈 *Growth vs Minggu Lalu:*
{growth_text}

🔥 *Hari Terbaik:*
{best_day} (Rp {best_day_sales:,.0f})

✅ Data minggu: {week_ago.strftime('%d')} - {today.strftime('%d %B %Y')}
"""
        
        elif callback_data == 'target_penjualan':
            today = date.today()
            transaksi_today = session.query(Transaksi).filter(
                func.date(Transaksi.tanggal) == today
            ).all()
            
            sales_today = sum(t.total for t in transaksi_today)
            
            # Default target (bisa dikonfigurasi)
            daily_target = 5000000  # Rp 5 juta per hari
            
            progress = (sales_today / daily_target) * 100 if daily_target > 0 else 0
            progress_bar = "█" * int(progress / 10) + "░" * (10 - int(progress / 10))
            
            remaining = max(0, daily_target - sales_today)
            
            status = "✅ TARGET TERCAPAI!" if sales_today >= daily_target else "⏳ SEDANG BERJALAN"
            
            return f"""
🎯 *TARGET PENJUALAN HARIAN*
{today.strftime('%d %B %Y')}

💰 Omzet Sekarang: Rp {sales_today:,.0f}
🎯 Target Harian: Rp {daily_target:,.0f}

📊 Progress: {progress:.1f}%
[{progress_bar}]

💵 Kurang: Rp {remaining:,.0f}

{status}

⏰ Update real-time
"""
        
        elif callback_data == 'menu_pengaturan':
            keyboard = [
                [InlineKeyboardButton("🔔 Notifikasi Transaksi", callback_data='toggle_notif')],
                [InlineKeyboardButton("◀️ Kembali ke Menu", callback_data='back_to_menu')],
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            notif_status = "✅ ON" if self.notify_new_transaction else "❌ OFF"
            
            settings_text = f"""
⚙️ *PENGATURAN BOT*

🔔 Notifikasi Transaksi: {notif_status}
📊 Notifikasi Stok: ✅ ON
📈 Laporan Harian: ✅ ON (05:00)

Pilih pengaturan yang ingin diubah:
"""
            return settings_text
        
        elif callback_data == 'toggle_notif':
            self.notify_new_transaction = not self.notify_new_transaction
            status = "✅ DIAKTIFKAN" if self.notify_new_transaction else "❌ DINONAKTIFKAN"
            
            return f"""
🔔 *NOTIFIKASI TRANSAKSI*

Status: {status}

Notifikasi transaksi baru akan {
    'dikirim ke Telegram' if self.notify_new_transaction else 'tidak dikirim ke Telegram'
}

Pengaturan tersimpan ✓
"""
        
        elif callback_data == 'back_to_menu':
            return f"""
🏪 *KASIR TOKO SEMBAKO - BOT MONITORING*

📱 Dashboard lengkap untuk monitoring toko Anda

✅ Kembali ke menu utama
Pilih menu di atas untuk melanjutkan
"""
        
        return None
    
    async def send_notification(self, message):
        """Send notification to all admin"""
        if self.application is None:
            return
        
        for chat_id in self.admin_chat_ids:
            try:
                await self.application.bot.send_message(
                    chat_id=int(chat_id),
                    text=message,
                    parse_mode='Markdown'
                )
            except Exception as e:
                logger.error(f"Failed to send notification to {chat_id}: {e}")
    
    async def notify_new_transaction(self, transaksi_data):
        """Notify admin about new transaction"""
        if not self.notify_new_transaction:
            return
        
        message = f"""
🔔 *TRANSAKSI BARU*

💰 Total: Rp {transaksi_data['total']:,.0f}
💳 Metode: {transaksi_data['payment_method']}
👤 Kasir: {transaksi_data['kasir']}
📦 Items: {transaksi_data['item_count']} produk

⏰ {transaksi_data['waktu']}
"""
        await self.send_notification(message)
    
    async def notify_low_stock(self, produk_name, stok):
        """Notify admin about low stock"""
        message = f"""
⚠️ *ALERT STOK RENDAH*

📦 Produk: {produk_name}
📊 Stok Tersisa: {stok} pcs

💡 Segera lakukan restock!
"""
        await self.send_notification(message)
    
    # Synchronous wrappers for calling from Flask routes
    def notify_new_transaction_sync(self, kode_transaksi, total, payment_method, kasir, member_name=None):
        """Synchronous wrapper for notifying new transaction"""
        if not self.application or not self.loop:
            return
        
        transaksi_data = {
            'kode': kode_transaksi,
            'total': total,
            'payment_method': payment_method,
            'kasir': kasir,
            'member': member_name or '-',
            'waktu': datetime.now().strftime('%H:%M:%S')
        }
        
        message = f"""
🔔 *TRANSAKSI BARU*

🧾 Kode: {transaksi_data['kode']}
💰 Total: Rp {transaksi_data['total']:,.0f}
💳 Metode: {transaksi_data['payment_method']}
👤 Kasir: {transaksi_data['kasir']}
👥 Member: {transaksi_data['member']}

⏰ {transaksi_data['waktu']}
"""
        
        # Schedule coroutine in bot's event loop
        asyncio.run_coroutine_threadsafe(
            self._send_message_to_admins(message),
            self.loop
        )
    
    def notify_low_stock_sync(self, produk_nama, stok, kategori=None):
        """Synchronous wrapper for notifying low stock"""
        if not self.application or not self.loop:
            return
        
        message = f"""
⚠️ *PERINGATAN STOK RENDAH!*

📦 Produk: {produk_nama}
📊 Stok Tersisa: {stok} pcs
📁 Kategori: {kategori or '-'}

💡 Segera lakukan restock!
"""
        
        # Schedule coroutine in bot's event loop
        asyncio.run_coroutine_threadsafe(
            self._send_message_to_admins(message),
            self.loop
        )
    
    async def _send_message_to_admins(self, message):
        """Helper to send message to all admins"""
        if not self.application:
            return
        
        for chat_id in self.admin_chat_ids:
            try:
                await self.application.bot.send_message(
                    chat_id=int(chat_id),
                    text=message,
                    parse_mode='Markdown'
                )
            except Exception as e:
                logger.error(f"Failed to send message to {chat_id}: {e}")
    
    def start_bot(self):
        """Start the Telegram bot"""
        try:
            # Create new event loop for this thread
            self.loop = asyncio.new_event_loop()
            asyncio.set_event_loop(self.loop)
            
            # Create application
            self.application = Application.builder().token(self.bot_token).build()
            
            # Add handlers
            self.application.add_handler(CommandHandler("start", self.start_command))
            self.application.add_handler(CommandHandler("help", self.help_command))
            self.application.add_handler(CallbackQueryHandler(self.handle_callback))
            
            # Start bot with drop_pending_updates to avoid conflicts
            logger.info("🤖 Telegram Bot started successfully!")
            self.application.run_polling(
                allowed_updates=Update.ALL_TYPES,
                drop_pending_updates=True,  # Ignore old pending updates
                # IMPORTANT: running in a background thread; don't install signal handlers.
                # In python-telegram-bot v20+, stop_signals=None uses defaults (installs signal handlers)
                # and will crash with: set_wakeup_fd only works in main thread.
                stop_signals=(),
            )
            
        except Exception as e:
            logger.error(f"Failed to start Telegram bot: {e}")
        finally:
            if self.loop:
                self.loop.close()
    
    def start_bot_async(self):
        """Start bot in background thread"""
        import threading
        bot_thread = threading.Thread(target=self.start_bot, daemon=True)
        bot_thread.start()
        logger.info("🤖 Telegram Bot thread started")

# Global bot instance
telegram_bot = None

def initialize_telegram_bot(bot_token, admin_chat_ids, app_context):
    """Initialize global telegram bot instance"""
    global telegram_bot
    if bot_token and admin_chat_ids:
        telegram_bot = TelegramBotService(bot_token, admin_chat_ids, app_context)
        return telegram_bot
    return None

def get_telegram_bot():
    """Get global telegram bot instance"""
    return telegram_bot
