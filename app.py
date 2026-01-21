import streamlit as st
import matplotlib.pyplot as plt
import numpy as np

# -------------------
# ページ設定
# -------------------
st.set_page_config(page_title="老後資産シミュレーター（簡易版）", layout="wide")
st.title("老後資産シミュレーター（簡易版）")

# -------------------
# 基本入力
# -------------------
start_age = st.number_input("シミュレーション開始年齢", 40, 70, 50)
end_age = st.number_input("想定寿命", 70, 110, 90)
assets = st.number_input("現在の資産（万円）", 0, 20000, 2000)
monthly_cost = st.number_input("毎月の生活費（万円）", 0, 100, 20)
ideco_annual = st.number_input("iDeCo年間拠出額（万円）", 0, 500, 24)

# -------------------
# 運用条件（固定値で簡易化）
# -------------------
annual_return = 3.0  # 運用利回り中央値％
volatility = 2.0     # 年ごとのブレ％
simulations = 1000

# -------------------
# シンプル年金・給与（固定値）
# -------------------
annual_pension = 120
pension_start_age = 65

# iDeCo期間固定
ideco_start_age = start_age
ideco_end_age = ideco_start_age + 20  # 例：20年積立

# -------------------
# シミュレーション
# -------------------
if st.button("シミュレーション実行"):
    years = end_age - start_age
    all_histories = []

    for _ in range(simulations):
        balance = assets
        history = []
        ideco_balance = 0
        nisa_balance = 0

        cost = monthly_cost * 12

        for year in range(years):
            current_age = start_age + year

            # -------------------
            # 年金受給
            # -------------------
            total_balance = balance
            if current_age >= pension_start_age:
                total_balance += annual_pension

            # 生活費
            total_balance -= cost

            # -------------------
            # 余剰金をNISAに積立
            # -------------------
            surplus = max(0, total_balance)
            nisa_balance += surplus

            # iDeCo拠出
            if ideco_start_age <= current_age <= ideco_end_age:
                ideco_balance += ideco_annual
                total_balance -= ideco_annual  # 拠出分を差し引く

            # -------------------
            # 運用利回り（モンテカルロ）
            # -------------------
            rand_return = np.random.normal(annual_return, volatility)/100
            balance = total_balance * (1 + rand_return)

            # iDeCo運用
            ideco_balance *= (1 + np.random.normal(annual_return, volatility)/100)

            # NISA運用
            nisa_balance *= (1 + np.random.normal(annual_return, volatility)/100)

            # iDeCo終了後はNISAから取り崩し
            if current_age > ideco_end_age:
                needed = max(0, cost - balance)
                withdrawal = min(needed, nisa_balance)
                balance += withdrawal
                nisa_balance -= withdrawal

            # 合計資産
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
    st.subheader("結果（簡易版）")
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
    ax.plot(range(start_age, end_age), median, color='blue', label='中央値')
    ax.fill_between(range(start_age, end_age), p10, p90, color='gray', alpha=0.3, label='10-90%範囲')
    ax.set_xlabel("年齢")
    ax.set_ylabel("資産（万円）")
    ax.set_title("資産推移（iDeCo＋NISA＋生活費）")
    ax.grid(True)
    ax.legend()
    st.pyplot(fig)
