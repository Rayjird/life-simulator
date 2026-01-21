import streamlit as st
import matplotlib.pyplot as plt
import numpy as np

# ページ設定
st.set_page_config(page_title="老後資産シミュレーター（本格版）", layout="wide")
st.title("老後資産シミュレーター（本格版）")

# -------------------
# 入力
# -------------------
age = st.number_input("現在の年齢", 40, 90, 65)
end_age = st.number_input("想定寿命", 70, 110, 90)
assets = st.number_input("現在の資産（万円）", 0, 20000, 2000)
monthly_cost = st.number_input("毎月の生活費（万円）", 0, 100, 20)

# 投資
annual_return = st.number_input("期待運用利回り（％）", 0.0, 10.0, 1.0)
volatility = st.number_input("利回りの変動幅（％）", 0.0, 10.0, 2.0)
simulations = st.number_input("シミュレーション回数", 100, 5000, 1000)

# 年金
annual_pension = st.number_input("年金受給額（年間、万円）", 0, 500, 120)

# 物価上昇
inflation = st.number_input("生活費の物価上昇率（％）", 0.0, 5.0, 1.0)

# 臨時支出
extra_cost = st.number_input("臨時支出（年間、万円）", 0, 500, 0)

# -------------------
# シミュレーション実行
# -------------------
if st.button("シミュレーション実行"):
    years = end_age - age
    all_histories = []

    for _ in range(simulations):
        balance = assets
        history = []
        cost = monthly_cost * 12  # 初期年間生活費

        for _ in range(years):
            # 年ごとのランダム利回り
            rand_return = np.random.normal(annual_return, volatility) / 100
            balance = balance * (1 + rand_return)

            # 物価上昇で生活費増加
            cost = cost * (1 + inflation / 100)

            # 年間収支
            balance += annual_pension  # 年金受給
            balance -= cost  # 生活費
            balance -= extra_cost  # 臨時支出

            history.append(balance)
        all_histories.append(history)

    all_histories = np.array(all_histories)

    # 年ごとの統計
    median = np.median(all_histories, axis=0)
    p10 = np.percentile(all_histories, 10, axis=0)
    p90 = np.percentile(all_histories, 90, axis=0)

    # -------------------
    # 結果表示
    # -------------------
    st.subheader("結果（モンテカルロシミュレーション）")
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
    ax.plot(range(age, end_age)_
