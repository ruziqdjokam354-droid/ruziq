#running: streamlit run "c:/Users/field/Downloads/Compressed/kasir otomatis/kasir.py"
import streamlit as st
try:
    import pandas as pd
    import plotly.express as px
    import plotly.graph_objects as go
except Exception as e:
    st.error("Missing dependency: pandas or plotly or one of its dependencies.\nPlease run: `pip install -r requirements.txt`")
    raise
from datetime import datetime, timedelta
import os

# ========================
# KONFIGURASI FILE
# ========================
MASTER_FILE = "master_barang.xlsx"
TRANSAKSI_FILE = "transaksi.xlsx"
USER_FILE = "user_kasir.xlsx"

# ========================
# PAGE CONFIG
# ========================
st.set_page_config(
    page_title="TOKO BANGUNAN ZUHRI",
    page_icon="🧾",
    layout="centered"
)

# ========================
# LOGIN MULTI KASIR
# ========================
if "login" not in st.session_state:
    st.session_state.login = False
if "nama_kasir" not in st.session_state:
    st.session_state.nama_kasir = ""
if "selected_transactions" not in st.session_state:
    st.session_state.selected_transactions = []
if "barang_dipilih" not in st.session_state:
    st.session_state.barang_dipilih = ""
if "jumlah_input" not in st.session_state:
    st.session_state.jumlah_input = 0.0

if not st.session_state.login:
    st.title("🔐 Login Kasir")

    username = st.text_input("Username")
    password = st.text_input("Password", type="password")

    if st.button("Login"):
        user_df = pd.read_excel(USER_FILE)
        cek = user_df[
            (user_df.username == username) &
            (user_df.password == password)
        ]

        if not cek.empty:
            st.session_state.login = True
            st.session_state.nama_kasir = cek.iloc[0]["nama_kasir"]
            st.success("Login berhasil")
            st.rerun()
        else:
            st.error("Username / Password salah")

    st.stop()

# ========================
# LOAD DATA
# ========================
master_df = pd.read_excel(MASTER_FILE)

# Set default barang_dipilih jika kosong
if st.session_state.barang_dipilih == "" and len(master_df) > 0:
    st.session_state.barang_dipilih = master_df["nama_barang"].iloc[0]

# ========================
# HEADER
# ========================
st.title("🧾 TOKO BANGUNAN ZUHRI")
st.caption(f"Kasir: **{st.session_state.nama_kasir}**")

# ========================
# DASHBOARD OMZET
# ========================
if os.path.exists(TRANSAKSI_FILE):
    df_trx = pd.read_excel(TRANSAKSI_FILE)
    df_trx["tanggal"] = pd.to_datetime(df_trx["tanggal_waktu"]).dt.date
    hari_ini = datetime.now().date()
    today = df_trx[df_trx["tanggal"] == hari_ini]

    col1, col2 = st.columns(2)
    col1.metric("💰 Omzet Hari Ini", f"Rp {today.total_harga.sum():,}")
    col2.metric("🧾 Transaksi Hari Ini", len(today))

# ========================
# TABS
# ========================
tab1, tab2, tab3, tab4 = st.tabs(["📝 Input Transaksi", "📊 Data Transaksi", "🛠️ Manajemen Stok", "📈 Dashboard"])

with tab1:
    st.subheader("➕ Transaksi Baru")

    # ========================
    # PILIH BARANG (DI LUAR FORM - UPDATE REAL-TIME)
    # ========================
    # Reload master_df fresh saat tab1 diakses
    master_df_fresh = pd.read_excel(MASTER_FILE)
    
    st.session_state.barang_dipilih = st.selectbox(
        "Nama Barang",
        master_df_fresh["nama_barang"],
        index=list(master_df_fresh["nama_barang"]).index(st.session_state.barang_dipilih) if st.session_state.barang_dipilih in list(master_df_fresh["nama_barang"]) else 0,
        key="barang_selectbox"
    )
    
    # Ambil data barang yang dipilih dari fresh data
    barang_terpilih = master_df_fresh[master_df_fresh["nama_barang"] == st.session_state.barang_dipilih].iloc[0]
    
    # Debug: tampilkan kolom yang tersedia
    # st.write("Debug - Kolom master_df:", master_df_fresh.columns.tolist())
    
    # Coba ambil satuan dari berbagai nama kolom yang mungkin
    if "satuan" in master_df_fresh.columns:
        satuan = barang_terpilih["satuan"]
    elif "Satuan" in master_df_fresh.columns:
        satuan = barang_terpilih["Satuan"]
    else:
        satuan = "pcs"  # Default
    
    # Strip whitespace jika ada
    satuan = str(satuan).strip() if pd.notna(satuan) else "pcs"
    
    harga_satuan = float(barang_terpilih["harga"])
    stok_barang = float(barang_terpilih["stok"])
    
    # Tampilkan info barang (UPDATE REAL-TIME)
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("💵 Harga/Satuan", f"Rp {harga_satuan:,.0f}")
    with col2:
        st.metric("📦 Satuan", satuan)
    with col3:
        st.metric("📊 Stok", f"{stok_barang:.0f} {satuan}")
    
    st.divider()
    
    # ========================
    # INPUT JUMLAH (DI LUAR FORM - BISA MANUAL)
    # ========================
    st.write("**Input Jumlah:**")
    
    # Input dengan placeholder dan validasi
    jumlah_str = st.text_input(
        "Jumlah (support desimal: 0.25, 0.5, 1, dll)",
        value=str(st.session_state.jumlah_input) if st.session_state.jumlah_input > 0 else "",
        placeholder="masukkan angka",
        key="jumlah_input_text"
    )
    
    # Validasi input - cek apakah ada karakter non-numerik
    if jumlah_str:
        try:
            jumlah_value = float(jumlah_str)
            if jumlah_value < 0:
                st.warning("⚠️ Masukkan angka yang lebih besar dari 0")
                st.session_state.jumlah_input = 0.0
            else:
                st.session_state.jumlah_input = jumlah_value
        except ValueError:
            st.error("❌ Hanya terima angka (desimal atau bulat). Contoh: 1, 0.5, 2.25")
            st.session_state.jumlah_input = 0.0
    else:
        st.session_state.jumlah_input = 0.0
    
    # Hitung harga total (UPDATE REAL-TIME) - hanya tampil jika jumlah > 0
    if st.session_state.jumlah_input > 0:
        total_harga = harga_satuan * st.session_state.jumlah_input
        st.metric("💰 Total Harga", f"Rp {total_harga:,.0f}")
    else:
        st.metric("💰 Total Harga", "Rp 0")
    
    st.divider()
    
    # ========================
    # FORM SUBMIT (HANYA TOMBOL SIMPAN)
    # ========================
    with st.form("form_transaksi"):
        simpan = st.form_submit_button("💾 Simpan Transaksi", use_container_width=True)

    # ========================
    # PROSES TRANSAKSI
    # ========================
    if simpan:
        # Validasi jumlah harus > 0
        if st.session_state.jumlah_input <= 0:
            st.error("❌ Silakan input jumlah terlebih dahulu")
            st.stop()
        
        # Reload data fresh saat submit untuk memastikan data terkini
        master_df_submit = pd.read_excel(MASTER_FILE)
        barang = master_df_submit[master_df_submit["nama_barang"] == st.session_state.barang_dipilih].iloc[0]

        harga = float(barang["harga"])
        stok = float(barang["stok"])
        
        # Ambil satuan dengan handling yang sama seperti di atas
        if "satuan" in master_df_submit.columns:
            satuan_barang = barang["satuan"]
        elif "Satuan" in master_df_submit.columns:
            satuan_barang = barang["Satuan"]
        else:
            satuan_barang = "pcs"
        
        satuan_barang = str(satuan_barang).strip() if pd.notna(satuan_barang) else "pcs"
        jumlah = st.session_state.jumlah_input

        if stok == 0:
            st.error("❌ STOK HABIS")
            st.stop()

        if jumlah > stok:
            st.error(f"❌ Stok tidak mencukupi (stok: {stok} {satuan_barang})")
            st.stop()

        total = harga * jumlah
        waktu = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        data_baru = pd.DataFrame([{
            "kasir": st.session_state.nama_kasir,
            "nama_barang": st.session_state.barang_dipilih,
            "jumlah": jumlah,
            "satuan": satuan_barang,
            "harga": harga,
            "total_harga": total,
            "tanggal_waktu": waktu
        }])

        # Simpan transaksi
        if os.path.exists(TRANSAKSI_FILE):
            lama = pd.read_excel(TRANSAKSI_FILE)
            df_trx = pd.concat([lama, data_baru], ignore_index=True)
        else:
            df_trx = data_baru

        df_trx.to_excel(TRANSAKSI_FILE, index=False)

        # Update stok - reload fresh master_df sebelum update
        master_df_update = pd.read_excel(MASTER_FILE)
        master_df_update.loc[
            master_df_update["nama_barang"] == st.session_state.barang_dipilih, "stok"
        ] = stok - jumlah
        master_df_update.to_excel(MASTER_FILE, index=False)

        st.success("✅ Transaksi berhasil disimpan")
        st.metric("Total Bayar", f"Rp {total:,}")
        
        # Reset jumlah untuk transaksi berikutnya
        st.session_state.jumlah_input = 0.0

    # ========================
    # MONITORING STOK
    # ========================
    st.subheader("📦 Monitoring Stok")

    # Reload data fresh untuk monitoring stok
    master_df_monitoring = pd.read_excel(MASTER_FILE)
    stok_kritis = master_df_monitoring[master_df_monitoring["stok"] <= 5]

    if not stok_kritis.empty:
        st.warning("⚠️ Ada stok hampir habis")
        st.dataframe(stok_kritis)
    else:
        st.success("✅ Semua stok aman")

with tab2:
    st.subheader("📊 Data Transaksi")

    # Reload transaksi display after inventory forms
    if os.path.exists(TRANSAKSI_FILE):
        df_transaksi = pd.read_excel(TRANSAKSI_FILE)
        
        if not df_transaksi.empty:
            # Tambah kolom index untuk reference
            df_display = df_transaksi.copy()
            df_display.insert(0, 'No', range(1, len(df_display) + 1))
            
            # Tampilkan dataframe
            st.dataframe(df_display, use_container_width=True)
            
            # Kolom untuk delete action
            col1, col2, col3 = st.columns([2, 1, 1])
            
            with col1:
                selected_row = st.number_input(
                    "Nomor transaksi yang ingin dihapus",
                    min_value=1,
                    max_value=len(df_transaksi),
                    step=1
                )
            
            with col2:
                if st.button("🗑️ Hapus Transaksi"):
                    # Hapus baris yang dipilih
                    df_transaksi_updated = df_transaksi.drop(selected_row - 1).reset_index(drop=True)
                    df_transaksi_updated.to_excel(TRANSAKSI_FILE, index=False)
                    
                    # Reload master file untuk update stok
                    master_reload = pd.read_excel(MASTER_FILE)
                    st.success("✅ Transaksi berhasil dihapus")
                    st.rerun()
            
            # Filter dan statistik
            st.divider()
            st.subheader("🔍 Filter Transaksi")
            
            col1, col2, col3 = st.columns(3)
            
            with col1:
                filter_kasir = st.selectbox(
                    "Filter Kasir",
                    ["Semua"] + df_transaksi["kasir"].unique().tolist()
                )
            
            with col2:
                filter_barang = st.selectbox(
                    "Filter Barang",
                    ["Semua"] + df_transaksi["nama_barang"].unique().tolist()
                )
            
            with col3:
                filter_tanggal = st.date_input("Filter Tanggal", datetime.now().date())
            
            # Terapkan filter
            df_filtered = df_transaksi.copy()
            
            if filter_kasir != "Semua":
                df_filtered = df_filtered[df_filtered["kasir"] == filter_kasir]
            
            if filter_barang != "Semua":
                df_filtered = df_filtered[df_filtered["nama_barang"] == filter_barang]
            
            # Filter tanggal
            df_filtered["tanggal"] = pd.to_datetime(df_filtered["tanggal_waktu"]).dt.date
            df_filtered = df_filtered[df_filtered["tanggal"] == filter_tanggal]
            
            if not df_filtered.empty:
                st.write(f"**Total Transaksi:** {len(df_filtered)}")
                st.write(f"**Total Penjualan:** Rp {df_filtered['total_harga'].sum():,}")
                st.dataframe(df_filtered, use_container_width=True)
            else:
                st.info("Tidak ada transaksi untuk filter yang dipilih")
        else:
            st.info("Belum ada transaksi")
    else:
        st.info("File transaksi belum ada")

with tab3:
    st.subheader("🛠️ Manajemen Stok & Produk")
    master_inv = pd.read_excel(MASTER_FILE)
    # Pastikan kolom yang dibutuhkan ada
    if "kode" not in master_inv.columns:
        master_inv["kode"] = ""
    if "modal" not in master_inv.columns:
        master_inv["modal"] = 0.0

    # Helper: parsing angka dari teks (mendukung koma sebagai desimal)
    def _parse_number(s):
        try:
            if s is None:
                return None
            ss = str(s).strip()
            if ss == "":
                return None
            return float(ss.replace(",", "."))
        except Exception:
            return None

    # Form: Tambah Stok untuk produk existing
    with st.form("form_tambah_stok"):
        pilih_barang = st.selectbox("Pilih Barang untuk Tambah Stok", master_inv["nama_barang"], key="pilih_barang_tambah")
        tambah_qty = st.text_input("Jumlah yang ditambahkan (support desimal)", value="", placeholder="Contoh: 10", key="tambah_qty")
        submit_tambah = st.form_submit_button("➕ Tambah Stok")

    if submit_tambah:
        tambah_qty_val = _parse_number(tambah_qty)
        if tambah_qty_val is None or tambah_qty_val <= 0:
            st.warning("Masukkan jumlah yang valid (lebih dari 0)")
        else:
            master_inv = pd.read_excel(MASTER_FILE)
            idx = master_inv[master_inv["nama_barang"] == pilih_barang].index
            if len(idx) == 0:
                st.error("Barang tidak ditemukan di master. Gunakan form Tambah Produk jika belum ada.")
            else:
                master_inv.loc[idx, "stok"] = master_inv.loc[idx, "stok"] + tambah_qty_val
                master_inv.to_excel(MASTER_FILE, index=False)
                st.success(f"✅ Stok untuk {pilih_barang} berhasil ditambahkan sebanyak {tambah_qty_val}")
                st.rerun()

    st.divider()

    # Form: Tambah Produk Baru
    with st.form("form_tambah_produk"):
        st.write("**Tambah Produk Baru**")
        nama_baru = st.text_input("Nama Barang Baru", key="nama_baru")
        satuan_baru = st.text_input("Satuan", value="pcs", key="satuan_baru")
        harga_baru = st.text_input("Harga Jual per Satuan", value="", placeholder="Contoh: 10000", key="harga_baru")
        modal_baru = st.text_input("Harga Modal per Satuan", value="", placeholder="Contoh: 7000", key="modal_baru")
        stok_awal = st.text_input("Stok Awal", value="", placeholder="Contoh: 10", key="stok_awal")
        submit_produk = st.form_submit_button("🆕 Tambah Produk")

    if submit_produk:
        nama_strip = str(nama_baru).strip()
        if nama_strip == "":
            st.warning("Masukkan nama produk")
        else:
            # parsing angka dari input teks
            harga_val = _parse_number(harga_baru)
            modal_val = _parse_number(modal_baru) or 0.0
            stok_val = _parse_number(stok_awal) or 0.0

            if harga_val is None:
                st.warning("Masukkan harga jual yang valid")
            else:
                master_inv = pd.read_excel(MASTER_FILE)
                # Cek duplikasi nama
                if nama_strip in master_inv["nama_barang"].values:
                    st.error("Produk dengan nama ini sudah ada di master. Gunakan form Tambah Stok.")
                else:
                    # generate kode otomatis
                    import re
                    existing_codes = master_inv[master_inv["kode"].notna() & (master_inv["kode"] != "")]["kode"].astype(str).tolist()
                    nums = []
                    for c in existing_codes:
                        m = re.search(r"(\d+)$", c)
                        if m:
                            try:
                                nums.append(int(m.group(1)))
                            except:
                                pass
                    next_n = max(nums) + 1 if nums else 1
                    kode_baru = f"P{next_n:04d}"

                    new_row = {
                        "kode": kode_baru,
                        "nama_barang": nama_strip,
                        "satuan": satuan_baru if satuan_baru else "pcs",
                        "harga": float(harga_val),
                        "modal": float(modal_val),
                        "stok": float(stok_val)
                    }
                    # Pastikan kolom exist in master_inv, append missing keys with defaults
                    for k in new_row.keys():
                        if k not in master_inv.columns:
                            master_inv[k] = 0 if k in ["harga", "modal", "stok"] else ""

                    master_inv = pd.concat([master_inv, pd.DataFrame([new_row])], ignore_index=True)
                    master_inv.to_excel(MASTER_FILE, index=False)
                    st.success(f"✅ Produk '{nama_strip}' berhasil ditambahkan dengan kode {kode_baru}")
                    st.experimental_rerun()

    st.markdown("---")

with tab4:
    st.subheader("📈 Dashboard Penjualan")
    
    if os.path.exists(TRANSAKSI_FILE):
        df_dash = pd.read_excel(TRANSAKSI_FILE)
        
        if not df_dash.empty:
            # Persiapkan data
            df_dash["tanggal"] = pd.to_datetime(df_dash["tanggal_waktu"]).dt.date
            df_dash["tanggal_waktu"] = pd.to_datetime(df_dash["tanggal_waktu"])
            
            # Pilih range tanggal
            col1, col2 = st.columns(2)
            with col1:
                start_date = st.date_input("Tanggal Mulai", datetime.now().date() - timedelta(days=7))
            with col2:
                end_date = st.date_input("Tanggal Akhir", datetime.now().date())
            
            # Filter data berdasarkan range tanggal
            df_filtered_dash = df_dash[(df_dash["tanggal"] >= start_date) & (df_dash["tanggal"] <= end_date)]
            
            # Hitung modal & keuntungan (profit)
            # Ambil modal dari master data (cari nama kolom yang umum)
            master_for_modal = pd.read_excel(MASTER_FILE)
            modal_col = None
            for c in ["modal", "Modal", "harga_modal", "harga_beli", "cost"]:
                if c in master_for_modal.columns:
                    modal_col = c
                    break
            if modal_col is None:
                # jika tidak ada kolom modal, default 0
                master_for_modal["modal"] = 0.0
                modal_col = "modal"

            modal_map = master_for_modal.set_index("nama_barang")[modal_col].to_dict()
            df_filtered_dash["modal_unit"] = df_filtered_dash["nama_barang"].map(modal_map).fillna(0).astype(float)
            # Profit per unit = harga - modal_unit; total profit = profit_unit * jumlah
            df_filtered_dash["harga"] = df_filtered_dash["harga"].astype(float)
            df_filtered_dash["profit_unit"] = df_filtered_dash["harga"] - df_filtered_dash["modal_unit"]
            df_filtered_dash["profit"] = df_filtered_dash["profit_unit"] * df_filtered_dash["jumlah"]

            # KPI Cards (termasuk keuntungan)
            st.divider()
            kpi_col1, kpi_col2, kpi_col3, kpi_col4, kpi_col5 = st.columns(5)

            with kpi_col1:
                st.metric(
                    "💰 Total Penjualan",
                    f"Rp {df_filtered_dash['total_harga'].sum():,.0f}"
                )

            with kpi_col2:
                st.metric(
                    "🧾 Total Transaksi",
                    len(df_filtered_dash)
                )

            with kpi_col3:
                st.metric(
                    "📦 Total Unit Terjual",
                    int(df_filtered_dash['jumlah'].sum())
                )

            with kpi_col4:
                st.metric(
                    "📈 Total Keuntungan",
                    f"Rp {df_filtered_dash['profit'].sum():,.0f}"
                )

            with kpi_col5:
                if len(df_filtered_dash) > 0:
                    avg_transaksi = df_filtered_dash['total_harga'].sum() / len(df_filtered_dash)
                    st.metric(
                        "📊 Rata-rata Transaksi",
                        f"Rp {avg_transaksi:,.0f}"
                    )

            # Chart 1: Tren Jumlah Terjual (pilihan periode)
            st.subheader("📅 Tren Jumlah Terjual")
            periode = st.radio(
                "Pilih Periode Tampilan:",
                ["Harian", "Mingguan", "Bulanan"],
                horizontal=True
            )

            # Persiapkan data berdasarkan periode untuk jumlah
            df_chart = df_filtered_dash.copy()

            if periode == "Harian":
                chart_data = df_chart.groupby("tanggal")["jumlah"].sum().reset_index()
                chart_data.columns = ["tanggal", "jumlah_terjual"]
                chart_data = chart_data.sort_values("tanggal")
                x_label = "Tanggal"
                title = "Jumlah Terjual (Harian)"

            elif periode == "Mingguan":
                df_chart["minggu"] = df_chart["tanggal_waktu"].dt.isocalendar().week
                df_chart["tahun"] = df_chart["tanggal_waktu"].dt.year
                chart_data = df_chart.groupby(["tahun", "minggu"])["jumlah"].sum().reset_index()
                chart_data["periode_label"] = "Minggu " + chart_data["minggu"].astype(str) + " (" + chart_data["tahun"].astype(str) + ")"
                chart_data.columns = ["tahun", "minggu", "jumlah_terjual", "periode_label"]
                x_label = "Minggu"
                title = "Jumlah Terjual (Mingguan)"

            else:  # Bulanan
                df_chart["bulan_tahun"] = df_chart["tanggal_waktu"].dt.to_period("M")
                chart_data = df_chart.groupby("bulan_tahun")["jumlah"].sum().reset_index()
                chart_data["bulan_label"] = chart_data["bulan_tahun"].astype(str)
                chart_data.columns = ["bulan_tahun", "jumlah_terjual", "bulan_label"]
                x_label = "Bulan"
                title = "Jumlah Terjual (Bulanan)"

            if not chart_data.empty:
                if periode == "Harian":
                    fig_daily = px.line(
                        chart_data,
                        x="tanggal",
                        y="jumlah_terjual",
                        title=title,
                        markers=True,
                        labels={"tanggal": x_label, "jumlah_terjual": "Jumlah Terjual (unit)"}
                    )
                elif periode == "Mingguan":
                    fig_daily = px.bar(
                        chart_data,
                        x="periode_label",
                        y="jumlah_terjual",
                        title=title,
                        labels={"periode_label": x_label, "jumlah_terjual": "Jumlah Terjual (unit)"}
                    )
                else:  # Bulanan
                    fig_daily = px.bar(
                        chart_data,
                        x="bulan_label",
                        y="jumlah_terjual",
                        title=title,
                        labels={"bulan_label": x_label, "jumlah_terjual": "Jumlah Terjual (unit)"}
                    )

                fig_daily.update_layout(height=400)
                fig_daily.update_yaxes(title_text="Jumlah Terjual (unit)")
                st.plotly_chart(fig_daily, use_container_width=True)

            # Chart Profit: Tren Keuntungan sesuai periode
            st.subheader("💹 Tren Keuntungan")
            df_profit_chart = df_filtered_dash.copy()
            if periode == "Harian":
                profit_by_date = df_profit_chart.groupby("tanggal")["profit"].sum().reset_index()
                fig_profit = px.line(profit_by_date, x="tanggal", y="profit", title="Keuntungan Per Hari", markers=True,
                                     labels={"tanggal": "Tanggal", "profit": "Keuntungan (Rp)"})
            elif periode == "Mingguan":
                profit_by_week = df_profit_chart.groupby([df_profit_chart["tanggal_waktu"].dt.isocalendar().year, df_profit_chart["tanggal_waktu"].dt.isocalendar().week])["profit"].sum().reset_index()
                profit_by_week["label"] = profit_by_week["week"].astype(str) + " (" + profit_by_week["year"].astype(str) + ")"
                fig_profit = px.bar(profit_by_week, x="label", y="profit", title="Keuntungan Per Minggu", labels={"label": "Minggu", "profit": "Keuntungan (Rp)"})
            else:
                profit_by_month = df_profit_chart.groupby(df_profit_chart["tanggal_waktu"].dt.to_period("M"))["profit"].sum().reset_index()
                profit_by_month["label"] = profit_by_month["tanggal_waktu"].astype(str)
                fig_profit = px.bar(profit_by_month, x="label", y="profit", title="Keuntungan Per Bulan", labels={"label": "Bulan", "profit": "Keuntungan (Rp)"})

            fig_profit.update_layout(height=350)
            st.plotly_chart(fig_profit, use_container_width=True)
            
            # Chart 2: Penjualan per Barang
            st.subheader("🏆 Penjualan Per Barang")
            sales_by_item = df_filtered_dash.groupby("nama_barang").agg({
                "total_harga": "sum",
                "jumlah": "sum"
            }).reset_index().sort_values("total_harga", ascending=False)
            
            if not sales_by_item.empty:
                fig_item = px.bar(
                    sales_by_item,
                    x="nama_barang",
                    y="total_harga",
                    title="Total Penjualan Per Barang",
                    labels={"nama_barang": "Barang", "total_harga": "Penjualan (Rp)"},
                    color="total_harga"
                )
                fig_item.update_layout(height=400)
                st.plotly_chart(fig_item, use_container_width=True)
            
            # Chart 3: Penjualan per Kasir
            st.subheader("👤 Penjualan Per Kasir")
            sales_by_kasir = df_filtered_dash.groupby("kasir").agg({
                "total_harga": "sum",
                "jumlah": "count"
            }).reset_index()
            sales_by_kasir.columns = ["kasir", "total_penjualan", "jumlah_transaksi"]
            
            if not sales_by_kasir.empty:
                fig_kasir = px.pie(
                    sales_by_kasir,
                    values="total_penjualan",
                    names="kasir",
                    title="Distribusi Penjualan Per Kasir"
                )
                st.plotly_chart(fig_kasir, use_container_width=True)
            
            # Tabel Detail Penjualan per Barang
            st.subheader("📋 Detail Penjualan Per Barang")
            detail_item = df_filtered_dash.groupby("nama_barang").agg({
                "total_harga": ["sum", "count"],
                "jumlah": "sum",
                "harga": "first"
            }).reset_index()
            detail_item.columns = ["Barang", "Total Revenue", "Jumlah Transaksi", "Unit Terjual", "Harga Satuan"]
            st.dataframe(detail_item, use_container_width=True)
        else:
            st.info("Tidak ada data transaksi untuk periode yang dipilih")
    else:
        st.info("File transaksi belum ada")

# ========================
# LOGOUT
# ========================
if st.button("🚪 Logout"):
    st.session_state.login = False
    st.session_state.nama_kasir = ""
    st.rerun()
