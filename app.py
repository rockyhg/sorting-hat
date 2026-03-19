import streamlit as st

from grouping import assign_groups
from storage import delete_record, load_history, save_result

st.set_page_config(page_title="組み分け帽子", page_icon="🎩", layout="centered")
st.title("🎩 組み分け帽子")

# --- メンバー入力 ---
st.subheader("メンバー入力")
members_text = st.text_area(
    "メンバー名を1行に1人ずつ入力してください",
    height=200,
    placeholder="田中\n佐藤\n鈴木\n高橋\n...",
)

members = [name.strip() for name in members_text.strip().splitlines() if name.strip()]

if members:
    st.caption(f"{len(members)} 人のメンバーが入力されています")

# --- パラメータ設定 ---
st.subheader("グループ設定")
mode = st.radio("指定方法", ["グループの人数を指定", "グループの数を指定"], horizontal=True)

group_size = None
num_groups = None

if mode == "グループの人数を指定":
    group_size = st.number_input("1グループあたりの人数", min_value=1, value=2, step=1)
    if members and group_size:
        calculated_groups = max(1, len(members) // group_size)
        remainder = len(members) % group_size
        info = f"→ {calculated_groups} グループ"
        if remainder:
            info += f"（{remainder}人は他のグループに振り分け）"
        st.caption(info)
else:
    num_groups = st.number_input("グループ数", min_value=1, value=2, step=1)
    if members and num_groups:
        base = len(members) // num_groups
        remainder = len(members) % num_groups
        if remainder:
            st.caption(f"→ {base}人のグループ × {num_groups - remainder} + {base + 1}人のグループ × {remainder}")
        else:
            st.caption(f"→ {base}人 × {num_groups} グループ")

# --- 組み分け実行 ---
st.divider()

if st.button("🎲 組み分けを実行", type="primary", use_container_width=True):
    if len(members) < 2:
        st.error("2人以上のメンバーを入力してください")
    elif group_size and group_size >= len(members):
        st.error("グループの人数はメンバー数より少なくしてください")
    elif num_groups and num_groups > len(members):
        st.error("グループ数はメンバー数以下にしてください")
    else:
        history = load_history()
        groups = assign_groups(members, history, group_size=group_size, num_groups=num_groups)

        # 結果保存
        save_result(members, groups, group_size, num_groups)

        # 結果表示
        st.subheader("組み分け結果")
        cols = st.columns(min(len(groups), 3))
        for i, group in enumerate(groups):
            with cols[i % len(cols)]:
                st.markdown(f"### グループ {i + 1}")
                for name in group:
                    st.markdown(f"- {name}")

# --- 履歴表示 ---
st.divider()
st.subheader("📜 過去の組み分け履歴")

history = load_history()
if not history:
    st.info("まだ組み分け履歴がありません")
else:
    for record in reversed(history):
        with st.expander(f"{record['date']}（{len(record['members'])}人 → {len(record['groups'])}グループ）"):
            cols = st.columns(min(len(record["groups"]), 3))
            for i, group in enumerate(record["groups"]):
                with cols[i % len(cols)]:
                    st.markdown(f"**グループ {i + 1}**")
                    for name in group:
                        st.markdown(f"- {name}")
            if st.button("🗑 この履歴を削除", key=f"del_{record['id']}"):
                delete_record(record["id"])
                st.rerun()
