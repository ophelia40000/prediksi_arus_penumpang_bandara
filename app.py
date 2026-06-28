from flask import Flask, render_template, request, redirect, url_for, session
from statsmodels.tsa.holtwinters import ExponentialSmoothing
from sklearn.metrics import r2_score
import pandas as pd
import numpy as np
import os

def get_month_index(month_val):
    month_str = str(month_val).strip().lower()
    
    mapping = {

        "1": 0, "01": 0, "1.0": 0,
        "2": 1, "02": 1, "2.0": 1,
        "3": 2, "03": 2, "3.0": 2,
        "4": 3, "04": 3, "4.0": 3,
        "5": 4, "05": 4, "5.0": 4,
        "6": 5, "06": 5, "6.0": 5,
        "7": 6, "07": 6, "7.0": 6,
        "8": 7, "08": 7, "8.0": 7,
        "9": 8, "09": 8, "9.0": 8,
        "10": 9, "10.0": 9,
        "11": 10, "11.0": 10,
        "12": 11, "12.0": 11,
        
        "jan": 0, "januari": 0, "january": 0,
        "feb": 1, "februari": 1, "february": 1,
        "mar": 2, "maret": 2, "march": 2,
        "apr": 3, "april": 3,
        "mei": 4, "may": 4,
        "jun": 5, "juni": 5, "june": 5,
        "jul": 6, "juli": 6, "july": 6,
        "agu": 7, "agustus": 7, "aug": 7, "august": 7,
        "sep": 8, "september": 8,
        "okt": 9, "oktober": 9, "oct": 9, "october": 9,
        "nov": 10, "november": 10,
        "des": 11, "desember": 11, "dec": 11, "december": 11
    }
    
    return mapping.get(month_str, 0)

app = Flask(__name__)
app.secret_key = "secret123" 

UPLOAD_FOLDER = "uploads"
TEMP_FILE = "uploads/temp_data.csv" 
PREPROCESSED_FILE = "uploads/preprocessed_data.csv" 
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER


os.makedirs(UPLOAD_FOLDER, exist_ok=True)


HOME_DATA_FILE = "target_penumpang_domestik_internasional_2006_2024.xlsx"

FORECAST_PARAMS = {
    "soekarno_hatta_jakarta_domestik": {
        "holt": {"alpha": 0.06, "beta": 0.66, "gamma": 0.31, "s": 12},
        "ma": {"window": 2}
    },
    "ngurah_rai_bali_domestik": {
        "holt": {"alpha": 0.76, "beta": 0.21, "gamma": 0.11, "s": 12},
        "ma": {"window": 13}
    },
    "juanda_surabaya_domestik": {
        "holt": {"alpha": 0.01, "beta": 0.16, "gamma": 0.76, "s": 12},
        "ma": {"window": 19}
    },
    "kualanamu_medan_domestik": {
        "holt": {"alpha": 0.21, "beta": 0.16, "gamma": 0.61, "s": 12},
        "ma": {"window": 3}
    },
    "hasanudin_makassar_domestik": {
        "holt": {"alpha": 0.26, "beta": 0.11, "gamma": 0.31, "s": 12},
        "ma": {"window": 14}
    },
    "soekarno_hatta_jakarta_internasional": {
        "holt": {"alpha": 0.21, "beta": 0.06, "gamma": 0.76, "s": 12},
        "ma": {"window": 2}
    },
    "ngurah_rai_bali_internasional": {
        "holt": {"alpha": 0.41, "beta": 0.76, "gamma": 0.46, "s": 12},
        "ma": {"window": 2}
    },
    "juanda_surabaya_internasional": {
        "holt": {"alpha": 0.71, "beta": 0.06, "gamma": 0.11, "s": 12},
        "ma": {"window": 15}
    },
    "kualanamu_medan_internasional": {
        "holt": {"alpha": 0.31, "beta": 0.01, "gamma": 0.76, "s": 12},
        "ma": {"window": 8}
    }
}

# ================= DASHBOARD =================
@app.route("/", methods=["GET", "POST"])
def dashboard():
    df_cols = pd.read_excel(HOME_DATA_FILE)
    columns = [c for c in df_cols.columns.tolist() if c not in ["Tahun", "Bulan"]]

    bandara = request.form.get("bandara", "") if request.method == "POST" else ""
    metode = request.form.get("metode", "holt") if request.method == "POST" else "holt"
    n_prediksi = 12
    
    aktual_list, periode_list, hasil_prediksi, periode_prediksi = [], [], [], []

    if bandara and metode:
        df = pd.read_excel(HOME_DATA_FILE)
        
        df = df[~df['Tahun'].isin([2020, 2021, 2022]) & (df['Tahun'] >= 2015)].reset_index(drop=True)
        
        data = df[bandara].values
        periode_list = (df["Tahun"].astype(str) + "-" + df["Bulan"].astype(str)).tolist()
        aktual_list = [float(x) for x in data]


        config = FORECAST_PARAMS[bandara]

        if metode == "ma":
            window = config["ma"]["window"]
            temp_data = list(data)
            for _ in range(n_prediksi):
                pred = round(float(np.mean(temp_data[-window:])), 2)
                hasil_prediksi.append(pred)
                temp_data.append(pred)

        elif metode == "holt":
            c = config["holt"]
            model = ExponentialSmoothing(data, trend="add", seasonal="add", seasonal_periods=c["s"])
            fit = model.fit(smoothing_level=c["alpha"], smoothing_trend=c["beta"], smoothing_seasonal=c["gamma"], optimized=False)
            hasil_prediksi = [round(max(0, float(p)), 2) for p in fit.forecast(n_prediksi)]


        bulan_list = ["Jan","Feb","Mar","Apr","Mei","Jun","Jul","Agu","Sep","Okt","Nov","Des"]
        last_tahun, last_bulan = int(float(df["Tahun"].iloc[-1])), df["Bulan"].iloc[-1]
        try:
            last_bulan_idx = get_month_index(last_bulan)
        except Exception:
            last_bulan_idx = 0

        for _ in range(n_prediksi):
            last_bulan_idx += 1
            if last_bulan_idx >= 12:
                last_bulan_idx = 0
                last_tahun += 1
            periode_prediksi.append(f"{bulan_list[last_bulan_idx]}-{last_tahun}")

    return render_template("home.html", 
        columns=columns,
        bandara=bandara,
        metode=metode,
        aktual_list=aktual_list,
        periode_list=periode_list,
        hasil_prediksi=hasil_prediksi,
        periode_prediksi=periode_prediksi
    )

# ================= INPUT DATA =================
@app.route("/input", methods=["GET", "POST"])
def input_data():
    table_data = None
    columns = None

    if request.method == "GET" and request.args.get("reset"):
        if os.path.exists(TEMP_FILE):
            os.remove(TEMP_FILE)
        if os.path.exists(PREPROCESSED_FILE):
            os.remove(PREPROCESSED_FILE)
        session.clear()
        return redirect(url_for("input_data"))

    if request.method == "POST":
        file = request.files.get("file")

        if file:
            filename = file.filename.lower()
            try:
                if filename.endswith(".csv"):
                    df = pd.read_csv(file)
                elif filename.endswith((".xlsx", ".xls")):
                    df = pd.read_excel(file)
                else:
                    return "<script>alert('Format Tidak Didukung! Harap upload file Excel atau CSV.'); window.location.href='/input';</script>"
                
                if "Tahun" not in df.columns or "Bulan" not in df.columns:
                    return "<script>alert('Kolom wajib Tahun dan Bulan tidak ditemukan!'); window.location.href='/input';</script>"
                
                if len(df.columns) < 3:
                    return "<script>alert('Dataset harus memiliki minimal 3 kolom: Tahun, Bulan, dan minimal 1 variabel buat diramal!'); window.location.href='/input';</script>"
                
                df.to_csv(TEMP_FILE, index=False)
                session["file_uploaded"] = True
                table_data = df.values.tolist()
                columns = df.columns.tolist()
            except Exception as e:
                return f"<script>alert('Gagal membaca file: {str(e)}'); window.location.href='/input';</script>"

    elif os.path.exists(TEMP_FILE) and session.get("file_uploaded"):
        df = pd.read_csv(TEMP_FILE)
        table_data = df.values.tolist()
        columns = df.columns.tolist()

    return render_template("input.html",
        table_data=table_data,
        columns=columns
    )

# ================= PREPROCESSING =================
@app.route("/preprocessing", methods=["GET", "POST"])
def preprocessing():
    if not os.path.exists(TEMP_FILE):
        return "<script>alert('Harap upload dataset Anda terlebih dahulu sebelum memulai proses!'); window.location.href='/input';</script>"

    columns, preview_data, missing_info = None, None, None
    jumlah_data, jumlah_kolom = "-", "-"
    periode_awal_list = []
    
    df = pd.read_csv(TEMP_FILE)
    columns, jumlah_data, jumlah_kolom = df.columns.tolist(), len(df), len(df.columns)
    if "Tahun" in df.columns and "Bulan" in df.columns:
        periode_awal_list = (df["Tahun"].astype(str) + " - " + df["Bulan"].astype(str)).tolist()

    # Ambil input form
    kolom_target = request.form.get("kolom_target")
    metode_missing = request.form.get("metode_missing")
    buang_covid = request.form.get("buang_covid")
    periode_awal = request.form.get("periode_awal")
    periode_akhir = request.form.get("periode_akhir")
    persen_training = int(request.form.get("persen_training", 80))
    persen_testing = int(request.form.get("persen_testing", 20))

    if request.method == "POST" and kolom_target in df.columns:


        full_periods = (df["Tahun"].astype(str) + " - " + df["Bulan"].astype(str))
        start_idx = df.index[full_periods == periode_awal].tolist()[0] if periode_awal in full_periods.values else 0
        end_idx = df.index[full_periods == periode_akhir].tolist()[-1] if periode_akhir in full_periods.values else len(df)-1
        df = df.loc[start_idx:end_idx].reset_index(drop=True)


        df[kolom_target] = pd.to_numeric(df[kolom_target], errors='coerce')
        total_missing = int(df[kolom_target].isna().sum())

        
        def apply_cleaning(data, method):
            if method == "Hapus Data Kosong": return data.dropna(subset=[kolom_target])
            if method == "Interpolasi Linear": data[kolom_target] = data[kolom_target].interpolate(method='linear')
            elif method == "Forward Fill": data[kolom_target] = data[kolom_target].ffill()
            elif method == "Mean": data[kolom_target] = data[kolom_target].fillna(data[kolom_target].mean())
            return data

        action = request.form.get("action")
        if action == "cek_missing":
            if total_missing > 0:
                if metode_missing and metode_missing != "-- Pilih Metode --":
                    df_cleaned = apply_cleaning(df.copy(), metode_missing)
                    sisa = int(df_cleaned[kolom_target].isna().sum())
                    missing_info = f"Ditemukan {total_missing} data hilang. Jika metode '{metode_missing}' diterapkan, sisa: {sisa} ✅"
                else:
                    missing_info = f"Ditemukan {total_missing} data hilang. Silakan pilih metode penanganan."
            else:
                missing_info = "Data lengkap, tidak ada missing value ✅"

        elif action == "proses":
            df = apply_cleaning(df, metode_missing)
            if buang_covid == "yes" and "Tahun" in df.columns:
                df = df[~df["Tahun"].astype(int).isin([2020, 2021])]
            
            
            n_train = int(len(df) * persen_training / 100)

            df_hasil = pd.DataFrame({
                "periode": (df["Tahun"].astype(str) + " - " + df["Bulan"].astype(str)).values,
                "tahun": df["Tahun"],
                "bulan": df["Bulan"],
                "nilai": df[kolom_target].values,
                "set": ["Training" if i < n_train else "Testing" for i in range(len(df))]
            })
            
            df_hasil.to_csv(PREPROCESSED_FILE, index=False)
            session.update({"kolom_target": kolom_target, "persen_training": persen_training, "persen_testing": persen_testing})
            preview_data = df_hasil.to_dict(orient="records")

    return render_template("preprocessing.html", columns=columns, jumlah_data=jumlah_data, jumlah_kolom=jumlah_kolom,
        missing_info=missing_info, preview_data=preview_data, kolom_target=kolom_target, metode_missing=metode_missing,
        buang_covid=buang_covid, periode_awal=periode_awal, periode_akhir=periode_akhir, periode_awal_list=periode_awal_list,
        persen_training=persen_training, persen_testing=persen_testing)


# ================= METHOD =================
@app.route("/method", methods=["GET", "POST"])
def method():
    if not os.path.exists(PREPROCESSED_FILE):
        return "<script>alert('Harap selesaikan proses Pra-pemrosesan terlebih dahulu!'); window.location.href='/preprocessing';</script>"

    if request.method == "POST":
        metode = request.form.get("metode")
        session["metode"] = metode
        
        if metode == "sma":
            session["sma_window"] = int(request.form.get("sma_window"))

        elif metode == "holt":
            session["holt_mode"] = request.form.get("holt_mode")
            if request.form.get("holt_mode") == "manual":
                session["alpha"] = float(request.form.get("alpha"))
                session["beta"] = float(request.form.get("beta"))
                session["gamma"] = float(request.form.get("gamma"))
                session["seasonal_period"] = int(request.form.get("seasonal_period"))
            else:
                session["seasonal_period"] = 12

        return redirect(url_for("evaluation"))

    return render_template("method.html")

# ================= EVALUASI =================
@app.route("/evaluation")
def evaluation():
    if not os.path.exists(PREPROCESSED_FILE):
        return "<script>alert('Harap selesaikan proses Pra-pemrosesan terlebih dahulu!'); window.location.href='/preprocessing';</script>"

    df = pd.read_csv(PREPROCESSED_FILE)
    metode = session.get("metode")

    if not metode:
        return render_template("evaluation.html", show_error_modal=True, error_message="Harap pilih metode peramalan terlebih dahulu sebelum melihat hasil evaluasi!")

    df_train = df[df["set"] == "Training"]["nilai"].values
    df_test = df[df["set"] == "Testing"]
    aktual = df_test["nilai"].values
    
    periode_test = (df_test["tahun"].astype(str) + "-" + df_test["bulan"].astype(str)).tolist()

    prediksi = []

    if metode == "sma":
        window = session.get("sma_window", 3)
        for i in range(len(aktual)):
        
            if i == 0:
                window_data = df_train[-window:]
            else:
                window_data = np.append(df_train, aktual[:i])[-window:]
            prediksi.append(round(float(np.mean(window_data)), 2))

    elif metode == "holt":
        holt_mode = session.get("holt_mode", "otomatis")
        s = session.get("seasonal_period", 12)

        if holt_mode == "manual":
            model = ExponentialSmoothing(df_train, trend="add", seasonal="add", seasonal_periods=s)
            fit = model.fit(
                smoothing_level=session.get("alpha"),
                smoothing_trend=session.get("beta"),
                smoothing_seasonal=session.get("gamma"),
                optimized=False
            )
        else:
         
            best_mape = np.inf
            best_alpha, best_beta, best_gamma = None, None, None
            best_fit = None
            values = np.arange(0.01, 0.81, 0.05) 
            
            for a in values:
                for b in values:
                    for g in values:
                        try:
                           
                            model = ExponentialSmoothing(df_train, trend="add", seasonal="add", seasonal_periods=s)
                            fit = model.fit(
                                smoothing_level=a,
                                smoothing_trend=b,
                                smoothing_seasonal=g,
                                optimized=False
                            )
                            forecast = fit.forecast(len(aktual))
                            
                            
                            mape = np.mean(np.abs((aktual - forecast) / aktual)) * 100
                            
                            if mape < best_mape: 
                                best_mape = mape
                                best_alpha, best_beta, best_gamma = a, b, g
                                best_fit = fit
                        except:
                            pass
            
            if best_fit is None:
               
                return "<script>alert('Optimasi gagal menemukan model yang valid. Coba gunakan metode manual.'); window.location.href='/method';</script>"
            
            session["alpha_opt"] = float(best_alpha)
            session["beta_opt"] = float(best_beta)
            session["gamma_opt"] = float(best_gamma)
            
            fit = best_fit

        prediksi = [round(float(p), 2) for p in fit.forecast(len(aktual))]

  
    aktual_arr = np.array(aktual, dtype=float)
    prediksi_arr = np.array(prediksi, dtype=float)

   
    errors = [round(abs(a - p) / a * 100, 2) if a != 0 else 0 for a, p in zip(aktual_arr, prediksi_arr)]
    mae = round(float(np.mean(np.abs(aktual_arr - prediksi_arr))), 2)
    rmse = round(float(np.sqrt(np.mean((aktual_arr - prediksi_arr) ** 2))), 2)
    mape = round(float(np.mean(errors)), 2)
    r2 = round(float(r2_score(aktual_arr, prediksi_arr)), 4)

    hasil = []
    for i in range(len(aktual)):
        hasil.append({
            "periode": periode_test[i],
            "aktual": round(float(aktual[i]), 2),
            "prediksi": prediksi[i],
            "error": errors[i]
        })


    kolom_target = session.get("kolom_target", "Tidak Diketahui")
    alpha, beta, gamma = None, None, None
    sma_window = None
    
    if metode == "holt":
        holt_mode = session.get("holt_mode", "otomatis")
        if holt_mode == "manual":
            alpha = session.get("alpha")
            beta = session.get("beta")
            gamma = session.get("gamma")
        else:
            alpha = session.get("alpha_opt")
            beta = session.get("beta_opt")
            gamma = session.get("gamma_opt")
    elif metode == "sma":
        sma_window = session.get("sma_window", 3)

    return render_template("evaluation.html",
        hasil=hasil,
        mae=mae,
        rmse=rmse,
        mape=mape,
        r2=r2,
        periode_list=periode_test,
        aktual_list=aktual_arr.tolist(),
        prediksi_list=prediksi,
        metode=metode,
        kolom_target=kolom_target,
        alpha=alpha,
        beta=beta,
        gamma=gamma,
        sma_window=sma_window
    )


# ================= VISUALISASI =================
@app.route("/visualization", methods=["GET", "POST"])
def visualization():
    if not os.path.exists(PREPROCESSED_FILE):
        return "<script>alert('Harap selesaikan proses Pra-pemrosesan terlebih dahulu!'); window.location.href='/preprocessing';</script>"

    df = pd.read_csv(PREPROCESSED_FILE)
    metode = session.get("metode")

    if not metode:
        return render_template("visualization.html", show_error_modal=True, error_message="Harap lakukan pemodelan pada menu 'Metode' terlebih dahulu untuk melihat visualisasi peramalan!")

    df_full = df["nilai"].values

    n_prediksi = 12
    hasil_prediksi = []
    periode_prediksi = []

    if request.method == "POST":
        n_prediksi = int(request.form.get("n_prediksi", 12))

        if metode == "sma":
            window = session.get("sma_window", 3)
            data = df["nilai"].values.tolist()
            for i in range(n_prediksi):
                pred = round(float(np.mean(data[-window:])), 2)
                hasil_prediksi.append(pred)
                data.append(pred)

        elif metode == "holt":
            holt_mode = session.get("holt_mode", "otomatis")
            s = session.get("seasonal_period", 12)

            if holt_mode == "manual":
                model = ExponentialSmoothing(df_full, trend="add", seasonal="add", seasonal_periods=s)
                fit = model.fit(
                    smoothing_level=session.get("alpha"),
                    smoothing_trend=session.get("beta"),
                    smoothing_seasonal=session.get("gamma"),
                    optimized=False
                )
            else:
                model = ExponentialSmoothing(df_full, trend="add", seasonal="add", seasonal_periods=s)
                fit = model.fit(
                    smoothing_level=session.get("alpha_opt"),
                    smoothing_trend=session.get("beta_opt"),
                    smoothing_seasonal=session.get("gamma_opt"),
                    optimized=False
                )

            hasil_prediksi = [round(float(p), 2) for p in fit.forecast(n_prediksi)]
        bulan_list = ["Jan","Feb","Mar","Apr","Mei","Jun","Jul","Agu","Sep","Okt","Nov","Des"]
        
        tahun = int(float(df["tahun"].iloc[-1]))
        last_bulan = df["bulan"].iloc[-1]
        try:
            last_bulan_idx = get_month_index(last_bulan)
        except Exception:
            last_bulan_idx = 0

        for i in range(n_prediksi):
            last_bulan_idx += 1
            if last_bulan_idx >= 12:
                last_bulan_idx = 0
                tahun += 1
            periode_prediksi.append(f"{bulan_list[last_bulan_idx]}-{tahun}")

    return render_template("visualization.html",
        n_prediksi=n_prediksi,
        hasil_prediksi=hasil_prediksi,
        periode_prediksi=periode_prediksi
    )

if __name__ == "__main__":
    app.run(debug=True)