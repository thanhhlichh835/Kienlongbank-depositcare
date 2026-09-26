import streamlit as st
import pandas as pd
from datetime import datetime
from zoneinfo import ZoneInfo
from io import BytesIO
from pathlib import Path

st.set_page_config(page_title='KienlongBank DepositCare', page_icon='🏦', layout='wide')

DATA_CIF = 'du_lieu_cap_CIF_ket_qua.xlsx'
DATA_TK = 'du_lieu_tai_khoan_chi_tiet.xlsx'
LOGO_FILE = 'logo_KienlongBank.png'

st.markdown('''
<style>
.block-container {padding-top: 1.4rem; padding-bottom: 2rem;}
[data-testid="stMetric"] {background:#fff;border:1px solid #e6e9ef;padding:14px 16px;border-radius:14px;box-shadow:0 2px 8px rgba(0,0,0,.04);}
.main-title {font-size:2rem;font-weight:700;margin-bottom:.25rem;}
.subtle {color:#6b7280;font-size:.95rem;}
.group-box {border:1px solid #e6e9ef;border-radius:14px;padding:14px 16px;margin-bottom:14px;background:#fff;}
</style>
''', unsafe_allow_html=True)

def format_vnd(value):
    if pd.isna(value):
        return '—'
    return f'{value:,.0f}'.replace(',', '.')

def format_pct(value):
    if pd.isna(value):
        return '—'
    return f'{value:.2f}%'

def format_month(value):
    if pd.isna(value):
        return '—'
    return f'{value:.2f} tháng'

def trang_thai_daohan(songay):
    if pd.isna(songay):
        return 'Không xác định'
    songay = int(songay)
    if songay < 0:
        return 'Đã đến hạn'
    if songay == 0:
        return 'Đáo hạn hôm nay'
    if songay <= 7:
        return 'Sắp đến hạn trong 7 ngày'
    if songay <= 15:
        return 'Sắp đến hạn trong 15 ngày'
    if songay <= 30:
        return 'Sắp đến hạn trong 30 ngày'
    return 'Còn hiệu lực'

def to_excel_bytes(df):
    output = BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name='Theo_doi_dao_han')
    return output.getvalue()

@st.cache_data
def load_data():
    df_cif = pd.read_excel(DATA_CIF, dtype={'Mã CIF': str})
    df_tk = pd.read_excel(DATA_TK, dtype={'Mã CIF': str, 'Số tài khoản': str})

    df_cif['Mã CIF'] = df_cif['Mã CIF'].astype(str).str.strip()
    df_tk['Mã CIF'] = df_tk['Mã CIF'].astype(str).str.strip()
    df_tk['Số tài khoản'] = df_tk['Số tài khoản'].astype(str).str.strip()

    df_tk['Ngày mở'] = pd.to_datetime(df_tk['Ngày mở'], errors='coerce')
    df_tk['Ngày đến hạn'] = pd.to_datetime(df_tk['Ngày đến hạn'], errors='coerce')

    ngay_hom_nay = pd.Timestamp(datetime.now(ZoneInfo('Asia/Ho_Chi_Minh')).date())
    df_tk['songaydenhan'] = (df_tk['Ngày đến hạn'] - ngay_hom_nay).dt.days
    df_tk['Trạng thái đáo hạn'] = df_tk['songaydenhan'].apply(trang_thai_daohan)
    return df_cif, df_tk, ngay_hom_nay

missing_files = [f for f in [DATA_CIF, DATA_TK] if not Path(f).exists()]
if missing_files:
    st.error('Không tìm thấy các tệp dữ liệu sau: ' + ', '.join(missing_files) + '. Hãy đặt chúng cùng thư mục với app.py.')
    st.stop()

df_cif, df_tk, ngay_hom_nay = load_data()

with st.sidebar:
    if Path(LOGO_FILE).exists():
        st.image(LOGO_FILE, use_container_width=True)
    st.markdown('### KienlongBank DepositCare')
    st.caption('Ứng dụng thử nghiệm hỗ trợ tra cứu và theo dõi tiền gửi có kỳ hạn')
    menu = st.radio('Chức năng', ['🔎 Tra cứu khách hàng', '⏰ Theo dõi đáo hạn'])
    st.divider()
    st.caption(f"Ngày hệ thống: {ngay_hom_nay.strftime('%d/%m/%Y')}")

if menu == '🔎 Tra cứu khách hàng':
    st.markdown('<div class="main-title">🔎 Tra cứu khách hàng</div>', unsafe_allow_html=True)
    st.markdown('<div class="subtle">Tra cứu thông tin tổng hợp theo Mã CIF và xem nhóm K-Means.</div>', unsafe_allow_html=True)

    danh_sach_cif = sorted(df_cif['Mã CIF'].dropna().astype(str).unique().tolist())
    ma_cif = st.text_input('Nhập Mã CIF', value=danh_sach_cif[0] if danh_sach_cif else '', placeholder='Ví dụ: 000100012').strip()

    if ma_cif:
        kh = df_cif[df_cif['Mã CIF'] == ma_cif]
        if kh.empty:
            st.warning('Không tìm thấy Mã CIF trong dữ liệu tổng hợp.')
        else:
            info = kh.iloc[0]
            st.success('Đã tìm thấy khách hàng.')

            ten_cum = info['ten_cum'] if 'ten_cum' in info.index else 'Chưa có tên cụm'
            cluster = info['cluster'] if 'cluster' in info.index else None
            cum_html = f"<br><b>Cụm:</b> {int(cluster)}" if pd.notna(cluster) else ''
            st.markdown(f'''<div class="group-box"><b>Mã CIF:</b> {ma_cif}<br><b>Nhóm khách hàng:</b> {ten_cum}{cum_html}</div>''', unsafe_allow_html=True)

            c1, c2, c3, c4, c5 = st.columns(5)
            c1.metric('Số tài khoản còn hiệu lực', int(info['soluong_tktg']) if 'soluong_tktg' in info.index and pd.notna(info['soluong_tktg']) else '—')
            if 'tongsodutiengui' in info.index and pd.notna(info['tongsodutiengui']):
                tong_sodu = info['tongsodutiengui']

                if tong_sodu >= 1_000_000_000:
                    sodu_hienthi = f"{tong_sodu / 1_000_000_000:.2f} tỷ VND"
                elif tong_sodu >= 1_000_000:
                    sodu_hienthi = f"{tong_sodu / 1_000_000:.2f} triệu VND"
                else:
                    sodu_hienthi = f"{format_vnd(tong_sodu)} VND"
            else:
                sodu_hienthi = "—"

            c2.metric("Tổng số dư", sodu_hienthi)
            c3.metric('Kỳ hạn TB', format_month(info['kyhantb']) if 'kyhantb' in info.index else '—')
            c4.metric('Lãi suất TB', format_pct(info['laisuattb']) if 'laisuattb' in info.index else '—')
            c5.metric('Đáo hạn gần nhất', f"{int(info['tksapdaohangannhat'])} ngày" if 'tksapdaohangannhat' in info.index and pd.notna(info['tksapdaohangannhat']) else '—')

            st.divider()
            tk_kh = df_tk[(df_tk['Mã CIF'] == ma_cif) & (df_tk['songaydenhan'] >= 0)].copy()
            st.subheader('📊 Phân tích tiền gửi')

            if tk_kh.empty:
                st.info('Khách hàng không còn tài khoản tiền gửi hiệu lực tại ngày hiện tại.')
            else:
                if 'Kỳ hạn (tháng)' in tk_kh.columns and 'Số dư quy VND' in tk_kh.columns:
                    chart_kyhan = tk_kh.groupby('Kỳ hạn (tháng)', as_index=False)['Số dư quy VND'].sum().sort_values('Kỳ hạn (tháng)').set_index('Kỳ hạn (tháng)')
                    st.markdown('**Tổng số dư theo kỳ hạn**')
                    st.bar_chart(chart_kyhan)

                if 'Số tài khoản' in tk_kh.columns and 'Số dư quy VND' in tk_kh.columns:
                    chart_tk = tk_kh[['Số tài khoản', 'Số dư quy VND']].set_index('Số tài khoản')
                    st.markdown('**Số dư theo từng tài khoản**')
                    st.bar_chart(chart_tk)

                st.subheader('📋 Danh sách tài khoản tiền gửi còn hiệu lực')
                cols = ['Số tài khoản','Ngày mở','Ngày đến hạn','Kỳ hạn (tháng)','Số dư quy VND','Lãi suất (%/năm)','songaydenhan','Trạng thái đáo hạn']
                cols = [c for c in cols if c in tk_kh.columns]
                tk_show = tk_kh[cols].copy()
                if 'Ngày mở' in tk_show.columns:
                    tk_show['Ngày mở'] = pd.to_datetime(tk_show['Ngày mở']).dt.strftime('%d/%m/%Y')
                if 'Ngày đến hạn' in tk_show.columns:
                    tk_show['Ngày đến hạn'] = pd.to_datetime(tk_show['Ngày đến hạn']).dt.strftime('%d/%m/%Y')
                if 'Số dư quy VND' in tk_show.columns:
                    tk_show['Số dư quy VND'] = tk_show['Số dư quy VND'].apply(format_vnd)
                tk_show = tk_show.rename(columns={'songaydenhan':'Số ngày đến hạn'})
                st.dataframe(tk_show, use_container_width=True, hide_index=True)

else:
    st.markdown('<div class="main-title">⏰ Theo dõi tài khoản sắp đáo hạn</div>', unsafe_allow_html=True)
    st.markdown('<div class="subtle">Danh sách được tính tự động theo ngày hệ thống và chỉ lấy các tài khoản chưa đến hạn.</div>', unsafe_allow_html=True)

    so_7 = int(df_tk['songaydenhan'].between(0, 7, inclusive='both').sum())
    so_15 = int(df_tk['songaydenhan'].between(0, 15, inclusive='both').sum())
    so_30 = int(df_tk['songaydenhan'].between(0, 30, inclusive='both').sum())

    c1, c2, c3 = st.columns(3)
    c1.metric('Đáo hạn trong 7 ngày', so_7)
    c2.metric('Đáo hạn trong 15 ngày', so_15)
    c3.metric('Đáo hạn trong 30 ngày', so_30)

    st.divider()
    moc_ngay = st.selectbox('Khoảng thời gian theo dõi', [7,15,30], index=0, format_func=lambda x: f'Trong {x} ngày')

    df_loc = df_tk[df_tk['songaydenhan'].between(0, moc_ngay, inclusive='both')].copy()
    df_loc = df_loc.sort_values(by=['songaydenhan','Mã CIF'], ascending=[True,True])
    tong_so_du = df_loc['Số dư quy VND'].sum() if 'Số dư quy VND' in df_loc.columns else 0

    c4, c5 = st.columns(2)
    c4.metric(f'Số tài khoản trong {moc_ngay} ngày', len(df_loc))
    c5.metric(f'Tổng số dư trong {moc_ngay} ngày', f'{format_vnd(tong_so_du)} VND')

    st.subheader('📋 Danh sách tài khoản cần theo dõi')
    cols = ['Mã CIF','Tên khách hàng','Số tài khoản','Ngày đến hạn','songaydenhan','Số dư quy VND','Lãi suất (%/năm)','Trạng thái đáo hạn']
    cols = [c for c in cols if c in df_loc.columns]
    df_show = df_loc[cols].copy()
    if 'Ngày đến hạn' in df_show.columns:
        df_show['Ngày đến hạn'] = pd.to_datetime(df_show['Ngày đến hạn']).dt.strftime('%d/%m/%Y')
    if 'Số dư quy VND' in df_show.columns:
        df_show['Số dư quy VND'] = df_show['Số dư quy VND'].apply(format_vnd)
    df_show = df_show.rename(columns={'songaydenhan':'Số ngày đến hạn'})
    st.dataframe(df_show, use_container_width=True, hide_index=True)

    export_cols = ['Mã CIF','Tên khách hàng','Số tài khoản','Ngày đến hạn','songaydenhan','Số dư quy VND','Lãi suất (%/năm)','Trạng thái đáo hạn']
    export_cols = [c for c in export_cols if c in df_loc.columns]
    df_export = df_loc[export_cols].copy().rename(columns={'songaydenhan':'Số ngày đến hạn'})
    st.download_button(
        '📥 Xuất danh sách Excel',
        data=to_excel_bytes(df_export),
        file_name=f"theo_doi_dao_han_{moc_ngay}_ngay_{ngay_hom_nay.strftime('%Y%m%d')}.xlsx",
        mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )
