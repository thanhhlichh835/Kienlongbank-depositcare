
import streamlit as st
import pandas as pd
from datetime import datetime
from zoneinfo import ZoneInfo

st.set_page_config(
    page_title="KienlongBank DepositCare",
    page_icon="🏦",
    layout="wide"
)

# ===== MÀU THƯƠNG HIỆU =====
ORANGE = "#EF7922"
ORANGE_DARK = "#EF4F25"
BLUE = "#30C2E3"
BLUE_DARK = "#2790CF"
NAVY = "#173B63"
LIGHT_BG = "#F7F9FC"

# ===== CSS =====
st.markdown(f"""
<style>

/* LABEL */
label, .stTextInput label {{
    font-weight: 600 !important;
}}

/* KPI */
div[data-testid="stMetric"] {{
    border: 1px solid rgba(128,128,128,0.20) !important;
    padding: 18px !important;
    border-radius: 14px !important;
    box-shadow: 0 3px 10px rgba(0,0,0,0.04) !important;
}}

div[data-testid="stMetricValue"] {{
    color: #2790CF !important;
    font-weight: 700 !important;
}}

/* ALERT */
div[data-testid="stAlert"] {{
    border-radius: 12px !important;
}}

/* DATAFRAME */
div[data-testid="stDataFrame"] {{
    border-radius: 12px !important;
    overflow: hidden;
}}

/* BRANDING */
.brand-title {{
    color: #2790CF;
    font-weight: 700;
}}

.brand-accent {{
    height: 4px;
    width: 95px;
    border-radius: 4px;
    background: linear-gradient(
        90deg,
        #EF7922,
        #30C2E3
    );
    margin-bottom: 22px;
}}

</style>
""", unsafe_allow_html=True)

# ===== ĐỌC DỮ LIỆU =====
df_cif = pd.read_excel(
    "du_lieu_cap_CIF_ket_qua.xlsx",
    dtype={"Mã CIF": str}
)

df_tk = pd.read_excel(
    "du_lieu_tai_khoan_chi_tiet.xlsx",
    dtype={
        "Mã CIF": str,
        "Số tài khoản": str
    }
)

# ===== TÍNH LẠI SỐ NGÀY ĐẾN HẠN THEO NGÀY HIỆN TẠI =====
df_tk["Ngày đến hạn"] = pd.to_datetime(
    df_tk["Ngày đến hạn"]
)

ngay_hom_nay = pd.Timestamp(
    datetime.now(
        ZoneInfo("Asia/Ho_Chi_Minh")
    ).date()
)

df_tk["songaydenhan"] = (
    df_tk["Ngày đến hạn"] - ngay_hom_nay
).dt.days

# ===== SIDEBAR =====
with st.sidebar:
    st.image(
        "logo KienlongBank.png",
        use_container_width=True
    )

    st.markdown("---")

    menu = st.radio(
        "Chức năng",
        [
            "🔎 Tra cứu khách hàng",
            "⏰ Theo dõi đáo hạn"
        ]
    )
if menu == "🔎 Tra cứu khách hàng":
    # ===== HEADER =====
    st.markdown(f"""
    <h1 style="margin-bottom:0;">
        Thông tin khách hàng
    </h1>

    <p style="
        color:#65758B;
        margin-top:4px;
    ">
        Tra cứu và phân tích danh sách tài khoản tiền gửi có kỳ hạn
    </p>

    <div style="
        height:4px;
        width:95px;
        border-radius:4px;
        background:linear-gradient(
            90deg,
            {ORANGE},
            {BLUE}
        );
        margin-bottom:22px;
    "></div>
    """, unsafe_allow_html=True)

    # ===== TRA CỨU =====
    cif_input = st.text_input(
        "Nhập Mã CIF",
        placeholder="Ví dụ: 000100003"
    )

    if cif_input:

        thong_tin_cif = df_cif[
            df_cif["Mã CIF"] == cif_input
        ]

        tai_khoan = df_tk[
            df_tk["Mã CIF"] == cif_input
        ]

        if thong_tin_cif.empty:
            st.warning("Không tìm thấy khách hàng.")

        else:
            st.success("Đã tìm thấy khách hàng.")

            info = thong_tin_cif.iloc[0]

            st.markdown("### 👤 Thông tin khách hàng")

            col1, col2 = st.columns([3, 1])

            with col1:
                st.markdown(
                    f"""
                    **Mã CIF:** {cif_input}  
                    **Nhóm khách hàng:** {info['ten_cum']}
                    """
                )

            with col2:
                st.success(f"Cụm {int(info['cluster'])}")

            c1, c2, c3, c4, c5 = st.columns(5)

            c1.metric(
                "Số tài khoản",
                int(info["soluong_tktg"])
            )

            c2.metric(
                "Tổng số dư",
                f"{info['tongsodutiengui']/1e9:.2f} tỷ"
            )

            c3.metric(
                "Kỳ hạn TB",
                f"{info['kyhantb']:.1f} tháng"
            )

            c4.metric(
                "Lãi suất TB",
                f"{info['laisuattb']:.3f}%"
            )

            if pd.isna(info["tksapdaohangannhat"]):
                ngay_gan_nhat = "Không có"
            else:
                ngay_gan_nhat = (
                    f"{int(info['tksapdaohangannhat'])} ngày"
                )

            c5.metric(
                "Đáo hạn gần nhất",
                ngay_gan_nhat
            )
            st.markdown("### 📊 Phân tích tiền gửi")

            col_chart1, col_chart2 = st.columns(2)

            with col_chart1:
                st.markdown("#### Tổng số dư theo kỳ hạn")

                chart_kyhan = (
                    tai_khoan
                    .groupby("Kỳ hạn (tháng)")["Số dư quy VND"]
                    .sum()
                    .reset_index()
                )

                st.bar_chart(
                    chart_kyhan,
                    x="Kỳ hạn (tháng)",
                    y="Số dư quy VND"
                )

            with col_chart2:
                st.markdown("#### Số dư theo từng tài khoản")

                chart_taikhoan = (
                    tai_khoan[
                        ["Số tài khoản", "Số dư quy VND"]
                    ]
                    .set_index("Số tài khoản")
                )

                st.bar_chart(chart_taikhoan)
            st.markdown("### 📋 Danh sách tài khoản tiền gửi")
            lua_chon = st.selectbox(
                "Lọc tài khoản sắp đến hạn",
                [
                    "Tất cả",
                    "Trong 7 ngày",
                    "Trong 15 ngày",
                    "Trong 30 ngày"
                ]
            )

            def trang_thai_daohan(so_ngay):
                if so_ngay < 0:
                    return "Đã quá hạn"
                elif so_ngay <= 7:
                    return "Sắp đến hạn ≤ 7 ngày"
                elif so_ngay <= 15:
                    return "Sắp đến hạn ≤ 15 ngày"
                elif so_ngay <= 30:
                    return "Sắp đến hạn ≤ 30 ngày"
                else:
                    return "Còn hạn"

            tai_khoan_hienthi = tai_khoan.copy()

            tai_khoan_hienthi["Trạng thái đáo hạn"] = (
                tai_khoan_hienthi["songaydenhan"]
                .apply(trang_thai_daohan)
            )

    # ===== LỌC THEO THỜI GIAN ĐÁO HẠN =====
            if lua_chon == "Trong 7 ngày":
                bang_loc = tai_khoan_hienthi[
                    (tai_khoan_hienthi["songaydenhan"] >= 0) &
                    (tai_khoan_hienthi["songaydenhan"] <= 7)
              ]

            elif lua_chon == "Trong 15 ngày":
                bang_loc = tai_khoan_hienthi[
                    (tai_khoan_hienthi["songaydenhan"] >= 0) &
                    (tai_khoan_hienthi["songaydenhan"] <= 15)
                ]

            elif lua_chon == "Trong 30 ngày":
                bang_loc = tai_khoan_hienthi[
                    (tai_khoan_hienthi["songaydenhan"] >= 0) &
                    (tai_khoan_hienthi["songaydenhan"] <= 30)
                ]

            else:
                bang_loc = tai_khoan_hienthi.copy()

            bang_hienthi = bang_loc[
                [
                    "Số tài khoản",
                    "Ngày mở",
                    "Ngày đến hạn",
                    "Kỳ hạn (tháng)",
                    "Số dư quy VND",
                    "Lãi suất (%/năm)",
                    "songaydenhan",
                    "Trạng thái đáo hạn"
                ]
            ].rename(
                columns={
                    "Số dư quy VND": "Số dư (VND)",
                    "songaydenhan": "Số ngày đến hạn"
                }
            )

            st.dataframe(
                bang_hienthi,
                use_container_width=True,
                hide_index=True
            )
elif menu == "⏰ Theo dõi đáo hạn":

    st.markdown("## ⏰ Theo dõi tài khoản sắp đáo hạn")

    st.caption(
        "Lọc toàn bộ tài khoản tiền gửi sắp đến hạn "
        "để hỗ trợ nhân viên chăm sóc khách hàng."
    )

    # ===== KPI TỔNG QUAN ĐÁO HẠN =====
    so_tk_7ng = len(
        df_tk[
            (df_tk["songaydenhan"] >= 0) &
            (df_tk["songaydenhan"] <= 7)
        ]
    )

    so_tk_15ng = len(
        df_tk[
            (df_tk["songaydenhan"] >= 0) &
            (df_tk["songaydenhan"] <= 15)
        ]
    )

    so_tk_30ng = len(
        df_tk[
            (df_tk["songaydenhan"] >= 0) &
            (df_tk["songaydenhan"] <= 30)
        ]
    )

    tong_du_30ng = df_tk[
        (df_tk["songaydenhan"] >= 0) &
        (df_tk["songaydenhan"] <= 30)
    ]["Số dư quy VND"].sum()

    k1, k2, k3, k4 = st.columns(4)

    k1.metric(
        "Đáo hạn ≤ 7 ngày",
        so_tk_7ng
    )

    k2.metric(
        "Đáo hạn ≤ 15 ngày",
        so_tk_15ng
    )

    k3.metric(
        "Đáo hạn ≤ 30 ngày",
        so_tk_30ng
    )

    k4.metric(
        "Tổng số dư ≤ 30 ngày",
        f"{tong_du_30ng/1e9:.2f} tỷ"
    )

    nguong_ngay = st.selectbox(
        "Khoảng thời gian đáo hạn",
        [7, 15, 30]
    )

    df_daohan = df_tk.copy()

    df_daohan = df_daohan[
        (df_daohan["songaydenhan"] >= 0) &
        (df_daohan["songaydenhan"] <= nguong_ngay)
    ]

    df_daohan = df_daohan.sort_values(
        "songaydenhan"
    )

    def trang_thai_theodoi(so_ngay):
        if so_ngay == 0:
            return "Đáo hạn hôm nay"
        elif so_ngay <= 7:
            return "Ưu tiên cao"
        elif so_ngay <= 15:
            return "Theo dõi gần"
        else:
            return "Theo dõi"

    df_daohan["Trạng thái theo dõi"] = (
        df_daohan["songaydenhan"]
        .apply(trang_thai_theodoi)
    )

    # ===== THỐNG KÊ DANH SÁCH ĐANG LỌC =====
    so_tai_khoan_loc = len(df_daohan)

    so_khach_hang_loc = (
        df_daohan["Mã CIF"]
        .nunique()
    )

    tong_so_du_loc = (
        df_daohan["Số dư quy VND"]
        .sum()
    )

    m1, m2, m3 = st.columns(3)

    m1.metric(
        f"Tài khoản trong {nguong_ngay} ngày",
        so_tai_khoan_loc
    )

    m2.metric(
        "Khách hàng cần chăm sóc",
        so_khach_hang_loc
    )

    m3.metric(
        "Tổng số dư đang theo dõi",
        f"{tong_so_du_loc/1e9:.2f} tỷ"
    )

    ds_daohan_hienthi = df_daohan[
        [
            "Mã CIF",
            "Tên khách hàng",
            "Số tài khoản",
            "Ngày đến hạn",
            "songaydenhan",
            'Trạng thái theo dõi',
            "Số dư quy VND",
            "Lãi suất (%/năm)"
        ]
    ].copy()

    ds_daohan_hienthi = ds_daohan_hienthi.rename(
        columns={
            "songaydenhan": "Số ngày đến hạn",
            "Số dư quy VND": "Số dư (VND)"
        }
    )

    ds_daohan_hienthi["Ngày đến hạn"] = pd.to_datetime(
        ds_daohan_hienthi["Ngày đến hạn"]
    ).dt.strftime("%d/%m/%Y")

    st.dataframe(
        ds_daohan_hienthi,
        use_container_width=True,
        hide_index=True,
        column_config={
            'Số dư (VND)': st.column_config.NumberColumn(
                'Số dư (VND)',
                format='%,d'
            ),
            'Lãi suất (%/năm)': st.column_config.NumberColumn(
                'Lãi suất (%/năm)',
                format='%.2f%%'
            )
        }
    )
    from io import BytesIO

    # ===== XUẤT EXCEL =====
    output = BytesIO()

    with pd.ExcelWriter(
        output,
        engine="openpyxl"
    ) as writer:
        ds_daohan_hienthi.to_excel(
            writer,
            index=False,
            sheet_name="Danh_sach_sap_daohan"
        )

    excel_data = output.getvalue()

    st.download_button(
        label="📥 Xuất danh sách Excel",
        data=excel_data,
        file_name=f"danh_sach_sap_daohan_{nguong_ngay}_ngay.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
