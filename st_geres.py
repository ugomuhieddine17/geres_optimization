#####################################################
################## PACKAGES #########################
#####################################################
import streamlit as st
import streamlit.components.v1 as components
import pandas as pd
import numpy as np
import altair as alt
from altair import expr, datum



st.set_page_config(page_title='My garment factory optimization', 
page_icon = './geres_logo.jpg',
menu_items={
        'Get Help': 'https://www.geres.eu',
        'Report a bug': "mailto:ugo.muhieddine@student-cs.fr",
        'About': "# GERES tools for garment factory optimization. This is a *draft* app!"
    }
    )
with st.columns(5)[1]:
    st.image('geres_logo.jpg', width=400)

st.title('Optimize your garment factory')
# Define list of selection options and sort alphabetical
## DATA construction
data_df = pd.read_csv('fake_data.csv', index_col=0)
equipment_df = pd.DataFrame(list(data_df['Equipment associated'].unique()), columns=['Equipment'])

equipment_df['Quantity'] = 0

tab_factory, tab_improv, tab_dash = st.tabs(['My factory information', 'My potential improvements', 'My dashboard'])



with tab_factory:
    col1, col2 = st.columns(2)

    with col1:
        start_color, end_color = st.select_slider(
            'Select your range of investment',
            options=['NO COST', 'LOW', 'MEDIUM', 'HIGH'],
            value=('MEDIUM', 'HIGH'))
        
        interest_saving = st.radio(
        "What saving to focus on?",
        ('CO2', 'Costs', 'Electricity', 'Water', 'Diesel', 'LPG', 'Wood'))

    with col2:
        st.write('Fill your factory equipment')
        

        st.data_editor(equipment_df, height=200, width=500, disabled=['Equipment'], hide_index=True, key='equipment_had')

        #equipment and their quantities
        equipment_qtties = dict()
        for key, val in st.session_state.equipment_had['edited_rows'].items():
            equipment_qtties[equipment_df.iloc[key].Equipment] = val["Quantity"]
        
        for equip in equipment_df.Equipment.unique():
            if equip not in equipment_qtties.keys():
                equipment_qtties[equip] = 0

        if 'equipment_df' not in st.session_state:
            st.session_state['equipment_df'] = equipment_df
            

        st.session_state.equipment_df.Quantity = st.session_state.equipment_df.Equipment.apply(lambda x: equipment_qtties[x])

        
# TAB OF SELECTION OF THE IMPROVEMENT
with tab_improv:
    #apply the quantity too
    data_improv = pd.merge(data_df, st.session_state['equipment_df'], left_on='Equipment associated', right_on='Equipment', how='left')

    if 'data_improv' not in st.session_state:
            st.session_state['data_improv'] = pd.merge(data_df, st.session_state['equipment_df'], left_on='Equipment associated', right_on='Equipment', how='left')
    st.session_state['data_improv'] = pd.merge(data_df, st.session_state['equipment_df'], left_on='Equipment associated', right_on='Equipment', how='left')

    st.write(st.session_state['data_improv'])

    dico_of_group_by_savings = {'Electricity savings (kWh/yr)': np.mean,
        'LPG savings (tonnes/yr)': lambda x: round(np.mean(x),3),
        'Wood savings (tonnes/yr)': lambda x: round(np.mean(x),3),
        'Diesel savings (kL/yr)': lambda x: round(np.mean(x),3),
       'Water savings (m3/yr)': lambda x: round(np.mean(x),3),
        'CO2 savings (tCO2/yr)': lambda x: round(np.mean(x),3),
        'Costs savings (USD/yr)': lambda x: round(np.mean(x),3),
        'Quantity':'first'
        }

    #the df for the widget
    if 'to_widget_data' not in st.session_state:
            st.session_state['to_widget_data'] = st.session_state['data_improv'].groupby(['Equipment', 'Category of energy saving']).agg(
                    dico_of_group_by_savings
                ).reset_index()
    st.session_state['to_widget_data'] = st.session_state['data_improv'].groupby(['Equipment', 'Category of energy saving']).agg(
        dico_of_group_by_savings
    ).reset_index()
    for col in dico_of_group_by_savings.keys():
        st.session_state['to_widget_data'][col] = st.session_state['to_widget_data'][col] * st.session_state['to_widget_data'].Quantity
    col_of_interest = [col for col in st.session_state['to_widget_data']  if interest_saving in col][0]
    st.session_state['to_widget_data']['selected'] = False
    columns_to_plot = ['Equipment',
    'Category of energy saving'] + [col_of_interest] + ['selected']
    st.session_state.to_widget_data = st.session_state.to_widget_data.sort_values(by=col_of_interest, ascending=False)
    

    # Display the data editor
    st.data_editor(
        st.session_state.to_widget_data[columns_to_plot].sort_values(by=col_of_interest, ascending=False),
        column_config={
            "selected": st.column_config.CheckboxColumn(
                "Action you want to take?",
                help="Select your **favorite** widgets",
                default=False,
            )
        },
        hide_index=True,
        key='improv_data_editor',
        width=700
    )


with tab_dash:

    if 'df_selected_improv' not in st.session_state:
        st.session_state.df_selected_improv = st.session_state['to_widget_data'].iloc[list(st.session_state.improv_data_editor['edited_rows'].keys())]
    
    st.session_state.df_selected_improv = st.session_state['to_widget_data'].iloc[list(st.session_state.improv_data_editor['edited_rows'].keys())]
    st.write(st.session_state.df_selected_improv)

    # Chart plot
    if 'col_inte_chart' not in st.session_state:
        st.session_state.col_inte_chart = alt.Chart(st.session_state.df_selected_improv).mark_bar().encode(
            x='Equipment',
            y=alt.Y(f'{col_of_interest}:Q',
            # tooltip=[
            #     alt.Tooltip('Category of energy saving', title='Category of energy saving')
            # ]
            )
            ).properties(
                    width=700,
                    height=300
                    )
    st.session_state.col_inte_chart = alt.Chart(st.session_state.df_selected_improv).mark_bar().encode(
            x='Equipment',
            y=alt.Y(f'{col_of_interest}:Q',
            # tooltip=[
            #     alt.Tooltip('Category of energy saving', title='Category of energy saving')
            # ]
            )
            ).properties(
                    width=700,
                    height=300
                    )
    st.altair_chart(st.session_state.col_inte_chart, use_container_width=True)

    if 'pie_chart_dash' not in st.session_state:
        st.session_state.pie_chart_dash = alt.Chart(st.session_state.df_selected_improv).encode(
        theta=alt.Theta(f"{col_of_interest}:Q", stack=True), color=alt.Color("Equipment:N")
    ).mark_arc(outerRadius=120)

    st.session_state.pie_chart_dash = alt.Chart(st.session_state.df_selected_improv).encode(
        theta=alt.Theta(f"{col_of_interest}:Q", stack=True), color=alt.Color("Equipment:N")
    ).mark_arc(outerRadius=120)

    st.altair_chart(st.session_state.pie_chart_dash, use_container_width=True)
