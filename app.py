import streamlit as st
import matplotlib.pyplot as plt
import numpy as np

# -------------------
# ページ設定
# -------------------
st.set_page_config(page_title="老後資産シミュレーター（フル版）", layout="wide")
st.title("老後資産シミュレーター（フル版）")

# -------------------
# 基本入力
# -------------------
age = st.number_input("現在の年齢", 40, 90, 65)
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
salary_start_age = st.number_input("給与受給開始年齢", age, end_age, 65)
annual_salary = st.number_input("給与収入（年間、万円）", 0, 3000, 300)
# 在職老齢年金の減額パラメータ（簡易）
reduction_threshold = st.number_input("年金減額開始給与額（万円）", 0, 3000, 280)
reduction_rate = st.number_input("年金減額率（％）", 0.0, 100.0, 50.0) / 100

# -------------------
# iDeCo / 個人年金
# -------------------
ideco_start_age = st.number_input("iDeCo拠出開始年齢", age, end_age, 65)
ideco_annual = st.number_input("iDeCo年間拠出額（万円）", 0, 500, 24)
ideco_return = st.number_input("iDeCo期待利回り（％）", 0.0, 10.0, 2.0)
ideco_volatility = st.number_input("iDeCo利回りの変動幅（％）", 0.0, 10.0, 2.0)

# -------------------
# シミュレーション
# -------------------
if st.button("シミュレーション実行"):
    years = end_age - age
    all_histories = []

    for _ in range(simulations):
        balance = assets
        history = []
        cost = monthly_cost * 12
        ideco_balance = 0  # iDeCo専用残高

        for year in range(years):
            current_age = age + year

            # -------------------
            # 運用利回り（モンテカルロ）
            # -------------------
            rand_return = np.random.normal(annual_return, volatility) / 100
            balance = balance * (1 + rand_return)

            # iDeCo運用
            if current_age >= ideco_start_age:
                ideco_balance = ideco_balance * (1 + np.random.normal(ideco_return, ideco_volatility)/100)
                ideco_balance += ideco_annual
            total_balance = balance + ideco_balance

            # -------------------
            # 生活費・物価上昇・臨時支出
            # -------------------
            cost = cost * (1 + inflation / 100)
            total_balance -= cost
            total_balance -= extra_cost

            # -------------------
            # 給与収入・在職老齢年金
            # -------------------
            if current_age >= salary_start_age:
                total_balance += annual_salary
                # 在職老齢年金減額（簡易モデル）
                pension_reduction = max(0, annual_salary - reduction_threshold) * reduction_rate
                if current_age >= pension_start_age:
                    total_balance += annual_pension - pension_reduction
            else:
                if current_age >= pension_start_age:
                    total_balance += annual_pension

            history.append(total_balance)

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
    st.subheader("結果（フル版モンテカルロシミュレーション）")
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
    ax.set_title("資産推移（給与・年金・iDeCo・生活費込み）")
    ax.grid(True)
    ax.legend()

    st.pyplot(fig=fig)
