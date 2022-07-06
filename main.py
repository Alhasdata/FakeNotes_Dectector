#Import the required Libraries
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import plotly.express as px
import plotly.graph_objects as go
import seaborn as sns
from PIL import Image

st.set_page_config( layout='wide')

header = st.container()
model = st.container()
functions = st.container()
options =st.container()
body = st.container()
summary = st.container()


with header:

    image = Image.open('data/logo.png')
    st.sidebar.image(image, caption='ONCMF', width=300)
    st.sidebar.markdown("<p style='text-align: center;'>Organisation nationale de lutte contre le faux-monnayage</p>",unsafe_allow_html=True)
    st.sidebar.markdown("")
    st.sidebar.markdown("")
    st.sidebar.markdown("")
    #st.sidebar.title('Navigation') # Sidebar setup
    st.sidebar.title('Navigation') #Sidebar navigation
    options = st.sidebar.radio('Select what you want to display:', ['Home', 'Data Header', 'Results'])
    st.sidebar.markdown("")
    st.sidebar.markdown("")
    st.sidebar.markdown("")
    # Add a title and intro text
    st.markdown("<h1 style='text-align: center; color: grey;'>Bienvenue sur StopFake</h1>", unsafe_allow_html=True)
    st.write("")
    st.markdown("<p style='text-align: center;'>L'app qui vous permet d'identifier les billets de contrefaçons à partir de leurs dimensions géométriques.</p>", unsafe_allow_html=True)
    st.write("")
    

with model:
    # Préparation des fichiers
    data_reg_log = pd.read_csv("data/df_final.csv")
    data_reg_log["is_genuine"].replace([True, False], [1,0], inplace=True)
    X = data_reg_log.iloc[:, 1:]
    y = data_reg_log.iloc[:, 0]
    # Preparation des sets d'entrainement
    from sklearn.model_selection import StratifiedKFold
    cross_validation = StratifiedKFold(n_splits=5, random_state=0, shuffle=True)
    for train_index, test_index in cross_validation.split(X, y):
        # Dataset d'entrainement
        X_train = X.iloc[train_index]
        y_train = y.iloc[train_index]
        # dataset de Test
        X_test = X.iloc[test_index]
        y_test = y.iloc[test_index]
    # Implementation du modèle
    from sklearn.preprocessing import StandardScaler
    from sklearn.linear_model import LogisticRegression
    # Scaler
    scaler = StandardScaler()
    X_train = scaler.fit_transform(X_train)
    X_test = scaler.transform(X_test) 
    # Estimateur
    model_reglog = LogisticRegression(random_state = 0, solver='liblinear')
    model_reglog.fit(X_train, y_train)

     #Récupération du fichier de l'utilisateur
    
    upload_file = st.sidebar.file_uploader('Upload a file containing bank notes dimensions')
    if upload_file is not None:
        df = pd.read_csv(upload_file)

        # Phase de test
        X_upload = df[['diagonal', 'height_left', 'height_right', 'margin_low', 'margin_up','length']]
        x_predict = scaler.transform(X_upload)
        predictions = model_reglog.predict(x_predict)
        X_upload["Predictions"] = predictions
        X_upload["Predictions"] = pd.Categorical(X_upload["Predictions"])
        X_upload["Nature_billet"] =  X_upload["Predictions"].copy()
        X_upload["Nature_billet"].replace([0,1],["Faux billet", "Vrai billet"], inplace=True)



with functions :
# Functions for each of the pages
    def home(uploaded_file):
        if uploaded_file:
            st.markdown("<h4 style='text-align: center; color: grey;'>Utilisez le menu de gauche pour afficher les résultats du test.</h4>", unsafe_allow_html=True)
        else: 
            background = Image.open("data/fake2.jpg")
            col1, col2, col3 = st.columns((1,2,1))
            col2.image(background,use_column_width=True)
            st.write("")
            st.markdown("<h5 style='text-align: center; color: grey;'>Chargez un jeu de données pour démarrer le test...</h5>", unsafe_allow_html=True)
            st.markdown("<p style='text-align: center;'>(Vous pouvez utiliser le menu de gauche pour uploader un fichier csv et afficher les résultats)</p>", unsafe_allow_html=True)
            st.write()
        

    def data_header(uploaded_file):
        col1, col2, col3 = st.columns((1,2,1))
        if uploaded_file:
            col2.markdown("<h5 style='text-align: center; color: grey;'>Un aperçu de vos données...</h5>", unsafe_allow_html=True)
            fig = go.Figure(data=go.Table(header=dict(values=list(df[['diagonal', 'height_left', 'height_right', 'margin_low', 'margin_up','length']].columns), fill_color="#FD8E72", align="center", font=dict( size=18),height=40),
                                          cells=dict(values = [df.diagonal, df.height_left, df.height_right, df.margin_low, df.margin_up,df.length],font=dict( size=16), height=40)))
            fig.update_layout(margin=dict(l=20,r=20,b=40,t=40))
            col2.write(fig)
        else:
            st.markdown("<h4 style='text-align: center; color: grey;'>Chargez un jeu de données SVP.</h4>", unsafe_allow_html=True)


    def results(uploaded_file):
        if uploaded_file:
            st.markdown("<h4 style='text-align: center;'>Résultats du test</h4>", unsafe_allow_html=True)
            st.markdown("")
            st.markdown("")
            st.markdown("")
            col1, col2, col3, col4 = st.columns((1,2,2,1))
            fig = px.pie(X_upload, names = "Nature_billet", hole = 0.2,color_discrete_sequence = ["darkslategrey","bisque"])
            fig.update_layout( margin=dict(l=0,r=25,b=120,t=0,pad=0),legend=dict(yanchor="top",y=0.99,xanchor="left",x=0.01))
            fig2,ax = plt.subplots()
            sns.countplot(x="Nature_billet", palette=["darkslategrey","bisque"], data=X_upload, ax=ax)
            col3.pyplot(fig2, use_container_width=True)
            col2.plotly_chart(fig, use_container_width=True)
            faux =len(X_upload[X_upload["Predictions"]==0])
            vrai = len(X_upload[X_upload["Predictions"]==1])
            st.write('*Nombre de Faux billets détectés :*', faux)
            st.write('*Nombre de billets authentiques détectés :*', vrai)


        else:
            st.markdown("<h4 style='text-align: center; color: grey;'>Chargez un jeu de données SVP.</h4>", unsafe_allow_html=True)



    # Navigation options
if options == 'Home':
    home(upload_file)
elif options == 'Data Header':
    data_header(upload_file)
elif options == 'Results':
    results(upload_file)



footer="""<style>
a:link , a:visited{
color: blue;
background-color: transparent;
text-decoration: underline;
}

a:hover,  a:active {
color: red;
background-color: transparent;
text-decoration: underline;
}

.footer {
position: fixed;
left: 10% ;
bottom: 0;
width: 100%;
background-color: white;
color: black;
text-align: center;
}
</style>
<div class="footer">
<p>Developed with ❤ by Alhassane<a style='display: block; text-align: center;' href="https://github.com/Alhasdata" target="_blank">Github</a></p>
</div>
"""
st.markdown(footer,unsafe_allow_html=True)



