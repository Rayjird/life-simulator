import streamlit as st
import matplotlib.pyplot as plt
import numpy as np

# -------------------
# ページ設定
# -------------------
st.set_page_config(page_title="老後資産シミュレーター（iDeCo＋NISA版）", layout="wide")
st.title("老後資産シミュレーター（iDeCo＋NISA版）")

# -------------------
# 基本入力
# -------------------
start_age = 50
st.write(f"シミュレーション開始年齢: {start_age}歳")
age = start_age
end_age = st.number_input("想定寿命", 70, 110, 90)
assets = st.number_input("現在の資産（万円）", 0, 20000, 2000)
monthly_cost = st.number_input("毎月の生活費（万円）", 0, 100, 20)
inflation = st.number_input("生活費の物価上昇率（％）", 0.0, 5.0, 1.0)
extra_cost = st.number_input("臨時支出（年間、万円）", 0, 500, 0)

# -------------------
# 投資・運用
# -------------------
annual_return = st.number_input("期待運用利回り（％）", 0.0, 10.0, 1.0)
volatility = st.number_input("利回りの変動幅（％）", 0.0, 10.0, 2.0)
simulations = st.number_input("シミュレーション回数", 100, 5000, 1000)

# -------------------
# 年金関連
# -------------------
annual_pension = st.number_input("年金受給額（年間、万円）", 0, 500, 120)
pension_start_age = st.number_input("年金受給開始年齢", age, end_age, 65)

# -------------------
# 給与収入
# -------------------
salary_start_age = st.number_input("給与受給開始年齢", age, end_age, 50)
retirement_age = st.number_input("退職年齢（給与終了）", salary_start_age, end_age, 65)
annual_salary = st.number_input("給与収入（年間、万円）", 0, 3000, 300)
reduction_threshold = st.number_input("年金減額開始給与額（万円）", 0, 3000, 280)
reduction_rate = st.number_input("年金減額率（％）", 0.0, 100.0, 50.0) / 100

# -------------------
# iDeCo / NISA
# -------------------
ideco_start_age = st.number_input("iDeCo拠出開始年齢", age, end_age, 50)
ideco_end_age = st.number_input("iDeCo拠出終了年齢", ideco_start_age, end_age, 70)
ideco_annual = st.number_input("iDeCo年間拠出額（万円）", 0, 500, 24)
ideco_initial = st.number_input("iDeCo初期残高（万円）", 0, 2000, 0)
ideco_return = st.number_input("iDeCo期待利回り（％）", 0.0, 10.0, 2.0)
ideco_volatility = st.number_input("iDeCo利回りの変動幅（％）", 0.0, 10.0, 2.0)

nisa_return = st.number_input("NISA期待利回り（％）", 0.0, 10.0, 3.0)
nisa_volatility = st.number_input("NISA利回りの変動幅（％）", 0.0, 10.0, 2.0)

# -------------------
# シミュレーション
# -------------------
if st.button("シミュレーション実行"):
    years = end_age - age
    all_histories = []

    for _ in range(simulations):
        balance = assets   # 現金資産（生活費・給与・年金の計算用）
        history = []
        cost = monthly_cost * 12
        ideco_balance = ideco_initial
        nisa_balance = 0

        for year in range(years):
            current_age = age + year

            # -------------------
            # 給与・年金・生活費・臨時支出
            # -------------------
            total_balance = balance

            # 給与収入
            if salary_start_age <= current_age < retirement_age:
                total_balance += annual_salary

            # 年金（在職老齢年金減額）
            if current_age >= pension_start_age:
                pension_reduction = 0
                if salary_start_age <= current_age < retirement_age:
                    pension_reduction = max(0, annual_salary - reduction_threshold) * reduction_rate
                total_balance += max(0, annual_pension - pension_reduction)

            # 生活費・臨時支出
            cost = cost * (1 + inflation / 100)
            total_balance -= cost
            total_balance -= extra_cost

            # -------------------
            # 余剰金をNISAに積立
            # -------------------
            surplus = max(0, total_balance)
            nisa_balance += surplus

            # iDeCo拠出（年齢判定後）
            if ideco_start_age <= current_age <= ideco_end_age:
                ideco_balance += ideco_annual
                total_balance -= ideco_annual  # 拠出分は現金から差し引く

            # -------------------
            # 運用利回り（モンテカルロ） ※拠出後に反映
            # -------------------
            rand_return = np.random.normal(annual_return, volatility) / 100
            balance = total_balance * (1 + rand_return)

            # iDeCo運用
            ideco_balance = ideco_balance * (1 + np.random.normal(ideco_return, ideco_volatility)/100)

            # NISA運用（余剰金積立分）
            nisa_balance = nisa_balance * (1 + np.random.normal(nisa_return, nisa_volatility)/100)

            # iDeCo終了後はNISAから取り崩し（生活費補填）※簡易モデル
            if current_age > ideco_end_age:
                # NISAから不足分を取り崩す
                needed = max(0, cost + extra_cost - balance)
                withdrawal = min(needed, nisa_balance)
                balance += withdrawal
                nisa_balance -= withdrawal

            # 合計残高
            total_assets = balance + ideco_balance + nisa_balance
            history.append(total_assets)

        all_histories.append(history)

    all_histories = np.array(all_histories)

    # -------------------
    # 統計処理
    # -------------------
    median = np.median(all_histories, axis=0)
    p10 = np.percentile(all_histories, 10, axis=0)
    p90 = np.percentile(all_histories, 90, axis=0)

    # -------------------
    # 結果表示
    # -------------------
    st.subheader("結果（iDeCo＋NISAモデル）")
    st.write(f"最終残高の中央値：{int(median[-1])} 万円")
    st.write(f"10％下振れ時：{int(p10[-1])} 万円")
    st.write(f"90％上振れ時：{int(p90[-1])} 万円")

    if p10[-1] < 0:
        st.error("⚠ 老後資金が途中で尽きる可能性があります（下振れシナリオ）")
    else:
        st.success("✅ 老後資金は持ちそうです（下振れシナリオでも安心）")

    # -------------------
    # グラフ表示
    # -------------------
    fig, ax = plt.subplots(figsize=(10,5))
    ax.plot(range(age, end_age), median, color='blue', label='中央値')
    ax.fill_between(range(age, end_age), p10, p90, color='gray', alpha=0.3, label='10-90%範囲')
    ax.set_xlabel("年齢")
    ax.set_ylabel("資産（万円）")
    ax.set_title("資産推移（給与・年金・iDeCo・NISA・生活費込み）")
    ax.grid(True)
    ax.legend()

    st.pyplot(fig=fig)
