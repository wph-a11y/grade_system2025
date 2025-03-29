# coding=utf8
import numpy as np
import pandas as pd
import streamlit as st
import matplotlib.pyplot as plt
import seaborn as sns
from io import BytesIO

#注意https://docs.streamlit.io/
#pip install streamlit numpy pandas matplotlib seaborn openpyxl xlsxwriter
#终端输入streamlit run "f:/cv/第一章 第一模块：Python快速入门/作业2/基于streamlit的Numpy作业.py"
#streamlit run "...我的路径..."

plt.rcParams['font.sans-serif'] = ['SimHei']  
plt.rcParams['axes.unicode_minus'] = False  

if 'df' not in st.session_state:
    raw_data = np.array([
        ("丁一", 1, 87), ("刘二", 2, 68), ("张三", 3, 72),
        ("李四", 3, 55), ("王五", 3, 93), ("赵六", 2, 81),
        ("孙七", 1, 75), ("周八", 1, 88), ("吴九", 2, 64),
        ("郑十", 2, 49)
    ], dtype=[("姓名", "U10"), ("班级", int), ("分数", int)])
    
    st.session_state.df = pd.DataFrame(raw_data)
    st.session_state.df['状态'] = np.where(
        st.session_state.df['分数'] >= 60, '✅ 及格', '❌ 不及格')

st.set_page_config(
    page_title="智能成绩管理系统",
    page_icon="📊",
    layout="wide"
)

st.markdown("""
<style>
[data-testid="stMetricValue"] {
    font-size: 1.2rem !important;
}
.css-1cpxqw2 {
    border: 1px solid rgba(49, 51, 63, 0.2);
    border-radius: 0.5rem;
    padding: 1rem;
}
</style>
""", unsafe_allow_html=True)

st.title("📚 智能成绩管理系统")
col1, col2, col3 = st.columns([3, 2, 2])

with col1:
    st.subheader("🔍 数据管理")
    search_term = st.text_input("学生姓名搜索", help="支持模糊查询")
    

    with st.expander("➕ 添加新学生", expanded=False):
        with st.form("add_form"):
            new_name = st.text_input("姓名")
            new_class = st.number_input("班级", 1, 5, 1)
            new_score = st.number_input("分数", 0, 100, 60)
            if st.form_submit_button("提交添加"):
                if new_name:
                    new_data = pd.DataFrame([[new_name, new_class, new_score]],
                                          columns=['姓名', '班级', '分数'])
                    new_data['状态'] = np.where(
                        new_data['分数'] >= 60, '✅ 及格', '❌ 不及格')
                    st.session_state.df = pd.concat(
                        [st.session_state.df, new_data], ignore_index=True)
                    st.success("添加成功！")
                else:
                    st.error("姓名不能为空")

filtered_df = st.session_state.df[
    st.session_state.df['姓名'].str.contains(search_term, case=False)
]

with col1:
    
    st.dataframe(
        filtered_df.style.applymap(
            lambda x: 'background-color: #ffcccc' if x == '❌ 不及格' else '',
            subset=['状态']
        ),
        use_container_width=True,
        height=400
    )

with col2:
    st.subheader("📈 分数分析")
  
    avg_score = filtered_df['分数'].mean()
    max_score = filtered_df['分数'].max()
    pass_rate = (filtered_df['状态'] == '✅ 及格').mean()
    
    st.metric("平均分", f"{avg_score:.1f}")
    st.metric("最高分", max_score)
    st.metric("及格率", f"{pass_rate:.1%}")

    fig1, ax1 = plt.subplots(figsize=(8, 4))
    sns.histplot(filtered_df['分数'], bins=10, kde=True, ax=ax1)
    ax1.axvline(60, color='red', linestyle='--', label='及格线')
    ax1.set_title("分数分布直方图")
    ax1.legend()
    st.pyplot(fig1)

with col3:
    st.subheader("🏫 班级对比")
    
 
    selected_class = st.selectbox(
        "选择班级",
        options=sorted(filtered_df['班级'].unique()),
        index=0
    )
    

    class_df = filtered_df[filtered_df['班级'] == selected_class]
    st.dataframe(
        class_df.sort_values('分数', ascending=False),
        use_container_width=True,
        height=200
    )
    

    fig2, ax2 = plt.subplots(figsize=(8, 4))
    sns.boxplot(data=filtered_df, x='班级', y='分数', palette="Set2", ax=ax2)
    ax2.set_title("班级成绩对比")
    st.pyplot(fig2)


with st.sidebar:
    st.header("⚙️ 高级功能")

    if st.button("📥 导出Excel文件"):
        output = BytesIO()
        with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
            st.session_state.df.to_excel(writer, index=False)
        st.download_button(
            label="下载Excel",
            data=output.getvalue(),
            file_name="成绩数据.xlsx",
            mime="application/vnd.ms-excel"
        )
    

    st.subheader("🔎 高级筛选")
    min_score = st.slider("最低分数", 0, 100, 0)  
    st.caption(f"当前显示分数 ≥ {min_score} 的学生")
    filtered_df = filtered_df[filtered_df['分数'] >= min_score]

    with st.expander("🗑️ 批量删除"):
        students_to_delete = st.multiselect(
            "选择要删除的学生",
            options=filtered_df['姓名'].tolist()
        )
        if st.button("确认删除"):
            st.session_state.df = st.session_state.df[
                ~st.session_state.df['姓名'].isin(students_to_delete)
            ]
            st.experimental_rerun()

st.divider()
st.subheader("📝 作业答案")

st.markdown("**第1题：低于及格分数的学生**")
failed = st.session_state.df[st.session_state.df['状态'] == '❌ 不及格'
                          ][['姓名', '班级', '分数']]
st.dataframe(failed, hide_index=True)

st.markdown("**第2题：最高分学生**")
top_score = st.session_state.df.nlargest(1, '分数')[['姓名', '班级', '分数']]
st.dataframe(top_score, hide_index=True)

st.markdown("**第3题：分班成绩排序**")
class_sorted = st.session_state.df.sort_values(
    by=['班级', '分数'], ascending=[True, False])
st.dataframe(class_sorted, hide_index=True)
