import pandas as pd
import numpy as np

from itertools import combinations,product
from pyvis.network import Network
import streamlit as st
import streamlit.components.v1 as components
from PIL import Image
import base64
import time
import urllib
import re
from streamlit_player import st_player

# 1. Task :  Make Network Graph visible in Streamlit
# 2. Task :  Selection of Lecture Slide (just name) & Show dataframe
# 3. Task :  Selection of Lecture Slide (just name) & Show Network
# 4. Task :  Show images of Lecture Slides in Caroussel
# 5. Task :  Mialoo it button.....


intro_text = "Welcome to mialoo - a learning enhancement tool creating mind maps out of lecture slides using the power of Deep Learning. A mind map functions as a multi-sensory educational tool using visual and spatial information. The goal is to display important concepts and their relation in the form of a network which may facilitate the comprehension, memorization and application of ideas. Concepts and ideas are represented by labelled nodes. Related nodes are connected to each other."




#Define Functions

def multi_line(label):
    """" Display text on multiple lines if longer than 2 words, newline on every second word"""
    counter = 1
    new_string = ""
    words = label.split()
    for i in words:
        if counter % 2 == 1:
            i = i + " "
            new_string += i
        else:
            i = i + "\n"
            new_string += i
        counter+=1

    if new_string[-4:] == "\n":
        new_string = new_string[:-4]
    else:
        new_string = new_string[:-1]
    return(new_string)


def st_display_pdf(pdf_file):
    with open(pdf_file, "rb") as f:
        base64_pdf = base64.b64encode(f.read()).decode('utf-8')
    pdf_display = f'<embed src="data:application/pdf;base64,{base64_pdf}" width="700" height="550" type="application/pdf">'
    st.markdown(pdf_display, unsafe_allow_html = True)


def get_youtube_videos(df):
    top_keywords = list(set(df.sort_values(by = ["cos_sim_wikisum_text + cos_sim_wiki_max_category"], ascending = [False]).loc[:,"display_name"].values[:6]))
    top_category = df.sort_values(by = ["cos_sim_wikisum_text + cos_sim_wiki_max_category"], ascending = [False]).loc[:,"wiki_max_category"].values[0]
    yt_videos = []
    for keyword in top_keywords:
        keyword = keyword + " " + top_category
        keyword = keyword.lower().split()
        keyword = "_".join(keyword)
        html = urllib.request.urlopen("https://www.youtube.com/results?search_query=" + keyword)
        video_ids = re.findall(r"watch\?v=(\S{11})", html.read().decode())
        yt_videos.append("https://www.youtube.com/watch?v=" + video_ids[0])
    return yt_videos



#---------------------------------------------------------------------------------------------------------------------------------------------------------------


#STREAMLIT

#Sidebar
if 'show_lecture' not in st.session_state:
    st.session_state['show_lecture'] = "noshow"

#select lecture to display
lecture = st.sidebar.selectbox(
    "Choose a Lecture",
    ("Classification", "Word2vec", "Basis Norm", "Timeseries-AR-MA","Introduction to Databases","Numerical Analysis","Financial Crises"))

#Load Data
filename = lecture
df_keywords_orig = pd.read_pickle("/Users/kosta/Documents/01_HSLU/05.Master_Thesis/Code/Tasks/T1016_Streamlit/df/"+filename+".pkl")
df_keywords = df_keywords_orig.loc[:,["page", "display_name","in_title", "cos_sim_wikisum_text + cos_sim_wiki_max_category","wiki_url", "title_lower_newline", "text_clean"]]

#Select if title should be shown or not

option = st.sidebar.radio('Would you like to include whole Titles?',
     ('Yes', 'No'))


#Main

st.title('mialoo')

st.write(intro_text)

st.subheader('Lecture')

if st.sidebar.button('Confirm Choices'):
    st.session_state["show_lecture"] = "show"

if st.session_state["show_lecture"] == "show":
    st_display_pdf("pdf/" + lecture + ".pdf")

if st.session_state["show_lecture"] == "noshow":
    st_display_pdf("mialoo_logo.pdf")


st.subheader('Mind Map')

st.write("With a click of a button, mialoo will create a mind map in seconds! Click on the concepts for more informations about them!")

if st.button('Create Mind Map'):
    #Youtube Videos
    # Get youtube links for top candidates 
    videos = get_youtube_videos(df_keywords_orig)
    my_bar = st.progress(0)
    progress = 0
    for percent_complete in range(10):
        time.sleep(0.1)
        progress += 10
        my_bar.progress(progress)
    if option == "No":
        HtmlFile = open("mind_map.html", 'r', encoding='utf-8')
        source_code = HtmlFile.read() 
        components.html(source_code, height = 800 ,width=900)
        st.subheader("Related Videos")
        for i in videos:
            st_player(i)

    else:
        HtmlFile = open("mind_map_full_titles.html", 'r', encoding='utf-8')
        source_code = HtmlFile.read() 
        components.html(source_code, height = 800 ,width=900)
        st.subheader("Related Videos")
        for i in videos:
            st_player(i)


    




































    











#Create Visualization





#Get edges between filename and title concept
edges_filename_title = []
df_keywords_titles = df_keywords[df_keywords["in_title"]==1].loc[:,["page","display_name"]]



#Catch Title keywords in a list
keywords_in_titles = list(df_keywords_titles["display_name"].values)


for keyword in set(keywords_in_titles):
    edges_filename_title.append((filename, keyword))



#Get connections between concepts in same title
edges_title_title = []
grouped_title = df_keywords_titles.groupby("page")
group_keys = []
for key, group in grouped_title:
    if group[group.columns[0]].count()>1:
        group_keys.append(key)

#Group in order to see which keywords in the titles are connected together

for key in group_keys:
    multi_group_df = grouped_title.get_group(key)
    concepts_in_titles = multi_group_df["display_name"].values
    if len(concepts_in_titles) == 2:
            edges_title_title.append((concepts_in_titles[0],concepts_in_titles[1]))
    #get all possible tuple for titles with more than 2 concepts   
    else:
        combis = list(combinations(concepts_in_titles, 2))
        for combi in combis:
            edges_title_title.append(combi)


edges_title_title = list(set(edges_title_title))



#Get connections between concepts not in title and concepts in title, now I want all possible combinations of two lists
#Get list of title concepts and get list of non-title concepts per list
edges_title_text = []
df_keywords_title_text = df_keywords.loc[:,["page","display_name","in_title"]]
grouped_title_text = df_keywords_title_text.groupby("page")
group_keys = []
title_keywords_no_relation = []
text_keywords_no_relation = []
for key, group in grouped_title_text:
    if 0 in set(group["in_title"].values) and 1 in set(group["in_title"].values):
        group_keys.append(key)

    elif 1 in set(group["in_title"].values):
        for keyword in group["display_name"].values:
            title_keywords_no_relation.append(keyword)

    else:
        for keyword in group["display_name"].values:
            text_keywords_no_relation.append((key,keyword))

for key in group_keys:
    title_keywords = []
    text_keywords =  []
    for row in grouped_title_text.get_group(key).itertuples(index=False):
        row = tuple(row)
        if row[2] == 1:
            title_keywords.append(row[1])
        else:
            text_keywords.append(row[1])
    title_text_combinations = list(product(title_keywords, text_keywords))
    for combi in title_text_combinations:
        edges_title_text.append(combi)


text_keywords_no_relation = list(set(text_keywords_no_relation))


#Get all concepts that are part of text (not in title) and connect them to their original title (that does not contain any concepts)
all_edges = edges_filename_title + edges_title_title + edges_title_text
nodes_1 = [edge[0] for edge in all_edges]
nodes_2 = [edge[1] for edge in all_edges]
all_nodes_temp = list(set(nodes_1 + nodes_2))
homeless_nodes = [i for i in text_keywords_no_relation if i[1] not in all_nodes_temp]



edges_filename_origina_title = []
edges_filename_text_wo_concept_in_title = []
#homeless node = (page, keyword)
for page,keyword in homeless_nodes:
        # try:
        #         #title = df_keywords[(df_keywords["page"]==page)&(df_keywords["display_name"]==keyword)].loc[:,"title_lower_newline"].values[0].capitalize()
        #         edges_filename_origina_title.append((filename,title))
        #         edges_original_title_text.append((title,keyword))
        # except KeyError:
        #         #In case there is no title on the page just connect to the filename in the center
        #         print(keyword)
        edges_filename_text_wo_concept_in_title.append((filename,keyword))

#Combine Everything to get all edges and all nodes
all_edges = edges_filename_title + edges_title_title + edges_title_text + edges_filename_origina_title + edges_filename_text_wo_concept_in_title
all_edges = [edge for edge in all_edges if edge[0] != edge[1]]

nodes_1 = [edge[0] for edge in all_edges]
nodes_2 = [edge[1] for edge in all_edges]
all_nodes = list(set(nodes_1 + nodes_2))


#Visualization of Network without title

g = Network(height='700px', width = "800px",
bgcolor = "#FFFFFF", font_color = "black")

for node in all_nodes:
    if len(df_keywords[df_keywords["display_name"]==node].loc[:,"wiki_url"].values) > 0:
        link = df_keywords[df_keywords["display_name"]==node].loc[:,"wiki_url"].values[0]
        l1 = '"<a href=\\\''
        l2 = "\\'>"
        l3 = '</a>"'
        title = l1+link+l2+'wiki'+l3
    else:
        title = node
    if node in keywords_in_titles:
        g.add_node(n_id = node, label=multi_line(node), shape="box", labelHighlightBold = True, color = "#B3C8ED", title = title)
    elif node == filename:
        g.add_node(n_id = node, abel=multi_line(node), color = "#CCCCCC",shape="box", font = "50px", labelHighlightBold = True)

    else:
        g.add_node(n_id = node, label=multi_line(node),shape="box", labelHighlightBold = True, title = title)
for edge in all_edges:
    if edge[0] != edge[1] and edge[0]!="" and edge[1]!="":
        g.add_edge(edge[0],edge[1])


g.force_atlas_2based(overlap=1, central_gravity=0.001, spring_length=200)
g.toggle_physics(True)



g.show("mind_map.html")



##Visualization of Network with title


#Find all title where there is a keyword on page --> filename ------ whole_title ----- all keywords
edges_filename_title = []
df_keywords_titles = np.unique(df_keywords.loc[:,"title_lower_newline"].values)

for title in df_keywords_titles:
    edges_filename_title.append((filename, title.capitalize()))


#Get connection between title and all concepts on the page
edges_original_title_all = []
grouped_title = df_keywords.groupby("title_lower_newline")

titles_original  =  [i.capitalize() for i in list(df_keywords_titles)]

#Group in order to see which keywords in the titles are connected together

for title in titles_original:
    multi_group_df = grouped_title.get_group(title.lower())
    concepts_in_under_title = multi_group_df["display_name"].values
    for concept in concepts_in_under_title:
        if title != "":
            edges_original_title_all.append((title.capitalize(),concept))
        else:
            edges_original_title_all.append((filename, concept))


all_edges = edges_original_title_all+edges_filename_title
nodes_1 = [edge[0] for edge in all_edges]
nodes_2 = [edge[1] for edge in all_edges]
all_nodes = [node for node in  list(set(nodes_1 + nodes_2)) if node != ""]

g = Network(height='700px', width = "800px",
bgcolor = "#FFFFFF", font_color = "black")

for node in all_nodes:
    if len(df_keywords[df_keywords["display_name"]==node].loc[:,"wiki_url"].values) > 0:
        link = df_keywords[df_keywords["display_name"]==node].loc[:,"wiki_url"].values[0]
        l1 = '"<a href=\\\''
        l2 = "\\'>"
        l3 = '</a>"'
        title = l1+link+l2+'wiki'+l3
    else:
        title = node
    if node in titles_original:
        g.add_node(n_id = node, label=multi_line(node), shape="text", labelHighlightBold = True, color = "#B3C8ED", title = title)
        
    elif node == filename:
        g.add_node(n_id = node, label=multi_line(node), color = "#CCCCCC",shape="box", labelHighlightBold = True)

    else:
        g.add_node(n_id = node, label=multi_line(node),shape="ellipse", labelHighlightBold = True, title = title)
for edge in all_edges:
    if edge[0] != edge[1] and edge[0]!="" and edge[1]!="":
        g.add_edge(edge[0],edge[1])


g.force_atlas_2based(overlap=1, central_gravity=0.001, spring_length=200)
g.toggle_physics(True)
g.show("mind_map_full_titles.html")