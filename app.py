import streamlit as st 
import igraph as ig
import plotly.express as px
import numpy as np
import pandas as pd
from datetime import datetime
import plotly.graph_objs as go


st.set_page_config(page_title='Tablero Días Singulares',
                           page_icon=None,
                           layout='wide')

def build_json(df):
    df = df[['Producto Bala', 'Producto Asociado']]

    df = df.groupby('Producto Bala')['Producto Asociado'].apply(set).apply(list).reset_index()

    nodes = []
    links = []
    group = 0
    sum_index1 = 0
    sum_index2 = 0
    for index, values in enumerate(df.values):
        nodes.append({'name': values[0], 'group': group})
        for index2, value in enumerate(values[1]):
            sum_index2 += 1
            links.append({'source': sum_index1, 'target': sum_index2})
            nodes.append({'name': value, 'group': group})
        sum_index2 += 1
        sum_index1 += 2

        group += 1
    return {'nodes': nodes, 'links': links}

if __name__ == '__main__':

    with st.container(border=True):
        
        st.markdown(
            """
            <style>
                .st-emotion-cache-z5fcl4  {
                    padding: 3rem 5rem 10rem;
                }
            </style>
            """,
            unsafe_allow_html=True
        )

        image_path = 'images/Sofka logo.png'

        col1, _, col2 = st.columns([1, 1, 3], gap='small')

        with col1:
            st.image(image_path, width=200)

        with col2:
            st.markdown('<h2>Ventas Días Singulares</h2>', unsafe_allow_html=True)
            # st.title('Tablero Control de Inventario')

        st.markdown(
            """
            <div style="border-bottom: 2px solid orange; margin-bottom: 20px;"></div>
            """,
            unsafe_allow_html=True
        )

        # with st.form('test'):

            # st.selectbox('Producto', options=['Producto 1', 'Producto 2', 'Producto 3'])

            # st.selectbox('Sede', options=['Éxito Laureles', 'Éxito Gran Vía', 'Éxito La Central', 'Éxito Aventura', 'Éxito Unicentro Medellín', 
            #                               'Éxito San Antonio', 'Éxito Belen', 'Éxito la 70'])

            # st.number_input('Supply Time', min_value=1)

            # if st.form_submit_button('Realizar proyección', use_container_width=True):
            #     pass

        df_date = pd.read_csv('data/dimDate.csv')
        df_products = pd.read_csv('data/dimProd.csv')
        df_sale = pd.read_csv('data/dimSale.csv')
        df_event_singular = pd.read_csv('data/dimEventsSingular.csv')
        df_event_normal = pd.read_csv('data/dimEvents.csv')

        df_event_singular['Tipo de día'] = 'SINGULAR'
        df_event_normal['Tipo de día'] = 'NORMAL'

        df2_list = [df_event_singular, df_event_normal]
        df2 = pd.concat(df2_list)

        df = df_event_singular.join(df_sale, 
                                    lsuffix='idSale', 
                                    rsuffix='id', 
                                    how='inner', 
                                    on='idSale').join(df_date.set_index('id'), 
                                                    on='idDate')
        
        df['dates'] = pd.to_datetime(df['dates'])
        df['añoMes'] = df['dates'].dt.strftime('%Y-%m')

        df.rename(columns={'diaSingular': 'Fecha', 
                'productSource': 'Producto Bala', 
                'productAssociate': 'Producto Asociado', 
                'quantity': 'Cantidad Vendida',
                'distance': 'Distancia'}, inplace=True)
        
        with st.sidebar:
            shoot_prod = st.multiselect('Productos Balas', options=df['Producto Bala'].unique(), default=df['Producto Bala'].unique())
            df = df[df['Producto Bala'].isin(shoot_prod)]
    
        fig = px.scatter_3d(df, x='Producto Bala', 
                            y='Producto Asociado', 
                            z='Fecha', 
                            size='Cantidad Vendida', 
                            color='Producto Asociado',
                            labels=None,
                            hover_data=['Distancia'])
        
        
        fig.update_layout(
            height=600, 
        )

        fig.update_traces(marker=dict(line=dict(width=2, color='DarkSlateGray')), selector=dict(mode='markers'))
        fig.update_layout(scene=dict(bgcolor='white'))

        fig.update_layout(
            scene=dict(
                xaxis_title='Producto Bala',
                yaxis_title='Producto Asociado',
                zaxis_title='Fecha',
                xaxis=dict(tickangle=-3),
                yaxis=dict(tickangle=3),
                ),
            title='Proyección de ventas en días singulares',
        )

        fig.update_yaxes(automargin=False)

        # fig.update_layout()
        col1, col2 = st.columns((1, 1))
        fig.update_layout(xaxis=dict(visible=False),
                         yaxis=dict(visible=False),)
        # fig.update_xaxes(visible=False)
        # fig.update_yaxes(visible=False)
        tab1, tab2, tab3, tab4 = st.tabs(['Ventas asociativas', 'Relación asociativas', 'Ventas totales', 'Proyección de ventas'])

        tab1.plotly_chart(fig, theme=None, use_container_width=True, config=dict(displaylogo=False, displayModeBar=True))

        data = build_json(df)
        try:
            N=len(data['nodes'])

            L=len(data['links'])
            Edges=[(data['links'][k]['source'], data['links'][k]['target']) for k in range(L)]

        
            G=ig.Graph(n=N, edges=Edges, directed=True)

            labels=[]
            group=[]
            for node in data['nodes']:
                labels.append(node['name'])
                group.append(node['group'])

            layt=G.layout('kk', dim=3)
            Xn=[layt[k][0] for k in range(N)]# x-coordinates of nodes
            Yn=[layt[k][1] for k in range(N)]# y-coordinates
            Zn=[layt[k][2] for k in range(N)]# z-coordinates
            Xe=[]
            Ye=[]
            Ze=[]
            for e in Edges:
                Xe+=[layt[e[0]][0],layt[e[1]][0], None]# x-coordinates of edge ends
                Ye+=[layt[e[0]][1],layt[e[1]][1], None]
                Ze+=[layt[e[0]][2],layt[e[1]][2], None]

            trace1=go.Scatter3d(x=Xe,
                        y=Ye,
                        z=Ze,
                        mode='lines',
                        line=dict(color='rgb(125,125,125)', width=1),
                        hoverinfo='none'
                        )

            trace2=go.Scatter3d(x=Xn,
                        y=Yn,
                        z=Zn,
                        mode='markers',
                        name='actors',
                        marker=dict(symbol='circle',
                                        color=group,
                                        colorscale='Viridis',
                                        line=dict(color='rgb(50,50,50)', width=0.5)
                                        ),
                        text=labels,
                        hoverinfo='text'
                        )

            axis=dict(showbackground=False,
                    showline=False,
                    zeroline=False,
                    showgrid=False,
                    showticklabels=False,
                    visible=False)

            layout = go.Layout(
                    title='Relación entre productos',
                    showlegend=False,
                margin=dict(
                    t=25,
                    b=0,
                    l=0,
                    r=0
                ),
                hovermode='closest')
            
            data=[trace1, trace2]
            fig=go.Figure(data=data)
            fig.update_layout(
                height=600, 
                scene = dict(xaxis = dict(showgrid = False,showticklabels = False),
                                   yaxis = dict(showgrid = False,showticklabels = False),
                                   zaxis = dict(showgrid = False,showticklabels = False)
             )
            )
            # fig.update_layout(scene = dict(xaxis = dict(showgrid = False,showticklabels = False),
            #                        yaxis = dict(showgrid = False,showticklabels = False),
            #                        zaxis = dict(showgrid = False,showticklabels = False)
            #  ))
            with tab2:
                st.plotly_chart(fig, use_container_width=True, theme=None, config=dict(displaylogo=False, displayModeBar=False))
        except:
            pass


        fig = px.histogram(df, x='Fecha', y='Cantidad Vendida', color='Producto Bala',
                    hover_data=df.columns, height=600, title='Ventas por días singulares')
        
        fig.update_yaxes(dict(title="Ventas"))

        tab3.plotly_chart(fig, use_container_width=True, config=dict(displaylogo=False, displayModeBar=True))
        

        df1 = df[['Fecha', 'Producto Bala', 'Cantidad Vendida']]
        df2 = df[['Fecha', 'Producto Bala', 'Cantidad Vendida']]
        df1['Proyección de ventas'] = 'Proyección de ventas'
        df1['Ventas'] = df['Cantidad Vendida'].apply(lambda x: x*1.5)

        df2['Proyección de ventas'] = 'Ventas reales'
        df2['Ventas'] = df2['Cantidad Vendida']
        df = pd.concat([df1, df2])


        df_grouped = df.groupby(['Fecha', 'Producto Bala', 'Proyección de ventas']).sum().reset_index()
                
        fig = px.histogram(df_grouped, x='Fecha', y='Ventas', color='Proyección de ventas',barmode='group', height=600, 
                           title='Proyección de ventas días singulares')
        fig.update_yaxes(dict(title="Proyección de ventas vs Ventas reales"))
        # fig = px.histogram(df_grouped, x='Fecha', y='Ventas', color='Proyección de ventas',barmode='group', height=600, 
        #                    title='Proyección de ventas días singulares',  yaxis_title="Proyección de ventas")

        tab4.plotly_chart(fig, use_container_width=True, config=dict(displaylogo=False, displayModeBar=True))
        
                # dashboard.build_top_logo(image_path)


