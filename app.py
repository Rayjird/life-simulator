import streamlit as st
import matplotlib.pyplot as plt

st.set_page_config(page_title="老後資産シミュレーター")

st.title("老後資産シミュレーター")

# 入力
age = st.number_input("現在の年齢", 40, 90, 65)
end_age = st.number_input("想定寿命", 70, 110, 90)
assets = st.number_input("現在の資産（万円）", 0, 20000, 2000)
monthly_cost = st.number_input("毎月の生活費（万円）", 0, 100, 20)
annual_return = st.number_input("運用利回り（％）", 0.0, 10.0, 1.0)

if st.button("シミュレーション実行"):
    years = end_age - age
    balance = assets
    history = []

    for i in range(years):
        balance = balance * (1 + annual_return / 100)
        balance -= monthly_cost * 12
        history.append(balance)

    st.subheader("結果")
    st.write(f"最終残高：{int(balance)} 万円")

    if balance < 0:
        st.error("⚠ 老後資金が途中で尽きます")
    else:
        st.success("✅ 老後資金は持ちそうです")

    # グラフ
    fig, ax = plt.subplots()
    ax.plot(range(age + 1, end_age + 1), history)
    ax.set_xlabel("年齢")
    ax.set_ylabel("資産（万円）")
    ax.set_title("資産推移")

    st.pyplot(fig)
