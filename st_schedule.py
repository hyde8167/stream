import streamlit as st
import pandas as pd
import pulp
from matplotlib import pyplot as plt
import seaborn as sns

plt.rcParams['font.family'] = 'TakaoGothic'

from ShiftScheduler import ShiftScheduler

##########
file_path='./4_ShiftScheduler.py'



####################
# タイトル
st.title("シフトスケジューリングアプリ")

# サイドバー
st.sidebar.header("データのアップロード")

Input_day=st.sidebar.file_uploader('カレンダー',type='csv')
Input_staff=st.sidebar.file_uploader('スタッフシフト',type='csv')




# タブ
tab1, tab2, tab3 = st.tabs(["カレンダー情報", "スタッフ情報", "シフト表作成"])

with tab1:
    st.markdown("## カレンダー情報")
    if Input_day is not None:
        df_day=pd.read_csv(Input_day)
        st.write(df_day)

with tab2:
    st.markdown("## スタッフ情報")
    if Input_staff is not None:
        df_sche=pd.read_csv(Input_staff)
        st.write(df_sche)

with tab3:
    chk1=0
    chk2=0
    if Input_day is None:
        st.write('カレンダー情報をアップロードしてください')
    else:
        chk1=1
    #
    if Input_staff is None:
        st.write('スタッフ情報をアップロードしてください')
    else:
        chk2=1
    ###########
    if (chk1 + chk2)==2:

        staff_penalty={}
        staff_ids=df_sche['スタッフID'].unique()
        for i,row in df_sche.iterrows():
            staff_penalty[row["スタッフID"]] = st.slider(
                f"{row['スタッフID']}の希望違反ペナルティ",
                0,  # 最小値
                100,  # 最大値
                50,  # デフォルト値は50
                key=row["スタッフID"],
            )
        
        
        
        
        
        
        if st.button('モデルを実行'):
            ss=ShiftScheduler()
            ss.set_data(df_sche,df_day)
            ss.build_model()
            ss.solve()
            df=ss.sch_df

            
            #
            st.markdown("## 最適化結果")
           # 最適化結果の出力
            st.write("実行ステータス:", pulp.LpStatus[ss.status])
            st.write("目的関数値:", pulp.value(ss.model.objective))
           
            # #shift graph
            st.markdown("## シフト表")
            st.write(df)

            # 各スタッフの合計シフト数をstreamlitのbar chartで表示
            st.markdown("## シフト数の充足確認")
            shift_sum = ss.sch_df.sum(axis=1)
            # st.bar_chart(shift_sum)
            fig, ax = plt.subplots()
            shift_sum.plot(kind='bar', ax=ax)
            st.pyplot(fig)


            
            st.markdown("## スタッフの希望の確認")
            shift_sum2 = ss.sch_df.sum(axis=0)
            # st.bar_chart(shift_sum)
            fig, ax = plt.subplots()
            shift_sum2.plot(kind='bar', ax=ax)
            st.pyplot(fig) 
            
            
            
            st.markdown("## 責任者の合計シフト数の充足確認")
            # shift_scheduleに対してstaff_dataをマージして責任者の合計シフト数を計算
            shift_schedule_with_staff_data =pd.merge(df,df_sche,left_index=True,right_on="スタッフID")
            shift_chief_only = shift_schedule_with_staff_data.query("責任者フラグ == 1")
            shift_chief_only = shift_chief_only.drop(
                columns=[
                    "スタッフID",
                    "責任者フラグ",
                    "希望最小出勤日数",
                    "希望最大出勤日数",
                ]
            )
            shift_chief_sum = shift_chief_only.sum(axis=0)
            st.bar_chart(shift_chief_sum)

            # シフト表のダウンロード
            st.download_button(
                label="シフト表ダウンロード",
                data=ss.sch_df.to_csv().encode("utf-8"),
                file_name="output.csv",
                mime="text/csv",
            )




