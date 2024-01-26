import streamlit as st
import requests
import networkx as nx
import matplotlib.pyplot as plt
import io
import pathlib
import textwrap
import pandas as pd
import google.generativeai as genai
from pyvis.network import Network
import streamlit.components.v1 as components
import PyPDF2
import time
genai.configure(api_key="AIzaSyBzOp4TIWTPfFSst6Z-gQdbcYsFIvYNloU")
model = genai.GenerativeModel('gemini-pro')
Instruction = "You will now act as an expert annotator for geographic information. Extrapolate all the available relationships from the prompt. Don't leave any possible relationships. Every Entity has to have only one member and every Enitity and Relationship strictly should not be more than one word. The Entities have to be unique and the order should be maintained as the prompt is written. The order of the relationships should follow the order of the prompt.Please make it in a table format.\n Example:\n Text: Sakib studies in RUET in the department of CSE with his friend Atiq, Debashis, Audity. The friends of Sakib are cricketers. the roofs of houses are nice.\n Entity 1 | Relationship | Entity 2 \n Sakib | studies_in | RUET \n Sakib | studies_in | CSE \n Atiq | studies_in | CSE \n Atiq | studies_in | RUET\n Debashis | studies_in | CSE \n Debashis | studies_in | RUET \n Audity | studies_in | CSE \n Audity | studies_in | RUET \n friends | are | cricketers \n the roofs | are | nice \n\n Prompt:"

def extract_text_from_pdf(pdf_content):
    with io.BytesIO(pdf_content) as file:
        reader = PyPDF2.PdfReader(file)
        text = ''
        for page in reader.pages:
            text += page.extract_text()
        return text
    
def generate_and_display_graph(df):
    G = nx.DiGraph()

    # Add nodes and edges from the DataFrame
    for _, row in df.iterrows():
        Entity1 = row['Entity 1']
        Entity2 = row['Entity 2']
        Relationship = row['Relationship']
        G.add_edge(Entity1, Entity2, label=Relationship)

    # Set the figure size (width, height)
    plt.figure(figsize=(25, 22))

    pos = nx.spring_layout(G, k=1)  # Adjust node spacing
    # pos = nx.shell_layout()
    # nodes
    nx.draw_networkx_nodes(G, pos, node_size=3000)

    # edges
    nx.draw_networkx_edges(G, pos, width=2) 
    

    # labels
    nx.draw_networkx_labels(G, pos, font_size=20, font_family='sans-serif')

    # edge labels
    edge_labels = nx.get_edge_attributes(G, 'label')
    # nx.draw_networkx_edge_labels(G, pos, edge_labels=edge_labels)
    nx.draw_networkx_edge_labels(G, pos, edge_labels=edge_labels, font_color='red', font_size=12)


    
    plt.axis('off')  # Turn off the axis

    # Use Streamlit to display the figure
    st.pyplot(plt)
    return G


# def generate_and_display_graph(df):
#     # Create a Pyvis network
#     net = Network(height="500px", width="100%", bgcolor="#ffffff", font_color="black", notebook=True)

#     # Add nodes and edges from the DataFrame
#     for _, row in df.iterrows():
#         Entity1 = row['Entity 1']
#         Entity2 = row['Entity 2']
#         Relationship = row['Relationship']

#         net.add_node(Entity1, Entity1, title=Entity1)
#         net.add_node(Entity2, Entity2, title=Entity2)
#         net.add_edge(Entity1, Entity2, title=Relationship)

#     # Set options for better visualization
#     net.set_options("""
#     var options = {
#       "nodes": {
#         "font": {
#           "size": 12
#         }
#       },
#       "edges": {
#         "color": {
#           "inherit": true
#         },
#         "smooth": false
#       },
#       "interaction": {
#         "dragNodes": true,
#         "tooltipDelay": 200
#       },
#       "physics": {
#         "barnesHut": {
#           "gravitationalConstant": -80000,
#           "centralGravity": 0.1,
#           "springLength": 200
#         },
#         "minVelocity": 0.75
#       }
#     }
#     """)

#     # Generate the network
#     net.show("graph.html")
#     HtmlFile = open("graph.html", 'r', encoding='utf-8')
#     source_code = HtmlFile.read()
#     components.html(source_code, width=800, height=750)



# def creating_dataframe(temp):
#     # Split the data into lines
#     print(temp)
#     lines = temp.strip().split('\n')

#     # Parse each line and store in a list of tuples
#     parsed_data = []
#     for line in lines:
#         entities = line.split('|')
#         if len(entities) == 3:
#             parsed_data.append((entities[0].strip(), entities[1].strip(), entities[2].strip()))

#     # Convert the list of tuples to a DataFrame
#     df = pd.DataFrame(parsed_data, columns=['Entity 1', 'Relationship', 'Entity 2'])

#     # Drop the first row
#     df = df.drop(0)

#     # Reset the index if you want a continuous index starting from 0
#     df = df.reset_index(drop=True)
#     return df

def creating_dataframe(temp):
    # Split the data into lines
    lines = temp.strip().split('\n')

    # Skip the header line and the divider line
    content_lines = lines[2:]

    # Parse each line and store in a list of tuples
    parsed_data = []
    for line in content_lines:
        entities = line.split('|')
        if len(entities) == 5:  # Includes outer borders of the table
            parsed_data.append((entities[1].strip(), entities[2].strip(), entities[3].strip()))

    # Convert the list of tuples to a DataFrame
    df = pd.DataFrame(parsed_data, columns=['Entity 1', 'Relationship', 'Entity 2'])

    print(f"Final DataFrame : {df}")
    return df

# Function to call Gemini API
def call_gemini_api(Instruction,text):
    # Add your API call logic here
    text = text.lower()
    Final_Text = Instruction + text
    print(Final_Text)
    response = model.generate_content(Final_Text)
    return response

# Function to generate graph using NetworkX
def generate_graph(df):
    # Create a graph
    G = nx.Graph()
    # Add nodes and edges from the DataFrame
    for _, row in df.iterrows():
        Entity1 = row['Entity 1']
        Entity2 = row['Entity 2']
        Relationship = row['Relationship']

        # Add nodes with type attributes
        G.add_node(Entity1, type='Entity1')
        G.add_node(Entity2, type='Entity2')

        # Add an edge with a label for the relationship
        G.add_edge(Entity1, Entity2, relationship=Relationship)
    # G = nx.DiGraph()
    # Logic to add nodes and edges based on Gemini response
    return G

# Function to save graph and text
def save_graph_and_text(graph, text, filename):
    # Logic to save graph and text
    pass

def save_results(G,df):
    filename = st.session_state.filename
    if filename:
        print("Save results")
        # Save the DataFrame as an Excel file
        df.to_excel(f'./{filename}.xlsx', index=False)
        print("Dataframe Converted")
        st.success('DataFrame saved as Excel file.')

        # Save the network graph
        plt.figure(figsize=(10, 8))
        nx.draw(G, with_labels=True)
        plt.savefig(f'./{filename}.png', dpi=300)
        st.success('Graph saved as PNG image.')

        # Clear the figure after saving
        plt.clf()
    else:
        st.error('Please enter a filename.')


# Main app function
def main():
    G = nx.Graph()
    df= pd.DataFrame()
    st.title("Text Analysis and Knowledge Graph Generation")
    progress_placeholder = st.empty()
    progress_text_placeholder = st.empty()
    progress_bar = progress_placeholder.progress(0)
    # Instruction input with default value
    st.markdown("### Instructions for the Model")
    st.markdown("This is the instruction you will give to the model. You can change it and play around.")
    instruction_input = st.text_input("Enter your instructions", value=f"{Instruction}")
    # instruction_input = st.text_input("Enter your instructions", value="Extrapolate all the available relationships from the prompt. Don't leave any possible relationships. Every Entity has to have only one member and every Enitity and Relationship should not be more than one word. The Entities have to be unique and the order should be maintained as the prompt is written. The order of the relationships should follow the order of the prompt.Please make it in a table format.\n Example:\n Text: Sakib studies in RUET in the department of CSE with his friend Atiq, Debashis, Audity. The friends of Sakib are cricketers. the roofs of houses are nice.\n Entity 1 | Relationship | Entity 2 \n Sakib | studies_in | RUET \n Sakib | studies_in | CSE \n Atiq | studies_in | CSE \n Atiq | studies_in | RUET\n Debashis | studies_in | CSE \n Debashis | studies_in | RUET \n Audity | studies_in | CSE \n Audity | studies_in | RUET \n friends | are | cricketers \n the roofs | are | nice \n\n Prompt:")

    # Text input
    # text_input = st.text_area("Enter your text here. If you found any Keyerror then please try again")
    pdf_file = st.file_uploader("Upload a PDF file",type=["pdf"])
    #Process button
    if st.button("Process"):
        progress_bar.progress(0) 
        progress_text_placeholder.text("Start Processing")
        if pdf_file:
            pdf_content = pdf_file.getvalue()
            extracted_text = extract_text_from_pdf(pdf_content)
            print(f"Pdf content \n:{extracted_text[:150]}")
            # time.sleep(1)
            progress_placeholder.empty()
            progress_text_placeholder.text("Progress: 20%")
            progress_bar.progress(20) 
            # Call Gemini API
            response = call_gemini_api(instruction_input,extracted_text)
            progress_placeholder.empty()
            progress_bar.progress(40) 
            progress_text_placeholder.text("Progress: 40%")
            temp = response.text
            print(f"########### OUTPUT #########")
            print(temp)
            print(f"########### End of Output #########")
            # Creating DataFrame
            df = creating_dataframe(temp)
            progress_placeholder.empty()
            progress_bar.progress(60) 
            progress_text_placeholder.text("Progress: 60%")
            st.dataframe(df, width=800, height=600)
            time.sleep(1)
            progress_bar = st.progress(80)
            progress_text_placeholder.text("Progress: 80%")
            # Generate graph
            G = generate_and_display_graph(df)
            progress_placeholder.empty()
            progress_bar.progress(100) 
            progress_text_placeholder.text("Completed")
            # G = generate_graph(df)
            
            # # Drawing the graph
            # fig, ax = plt.subplots()
            # # plt.figure(figsize=(14, 10))  # Increased figure size
            # # Use the spring layout for a better structural layout
            # pos = nx.spring_layout(G, k=0.30, iterations=20)

            # # Draw nodes with increased size for better visibility
            # nx.draw_networkx_nodes(G, pos, node_size=5000, node_color="skyblue", alpha=0.9)

            # # Draw edges with increased width for better visibility
            # nx.draw_networkx_edges(G, pos, width=2, alpha=0.5, edge_color="gray")

            # # Draw labels for nodes with increased font size
            # nx.draw_networkx_labels(G, pos, font_size=9, font_family="sans-serif")

            # # Draw edge labels (relationships) with better visibility
            # edge_labels = nx.get_edge_attributes(G, 'relationship')
            # nx.draw_networkx_edge_labels(G, pos, edge_labels=edge_labels, font_color='red', font_size=8)

            # # # Draw graph
            # # fig, ax = plt.subplots()
            # # nx.draw(G, with_labels=True, ax=ax)
            # st.pyplot(fig)

            # # Save option
            # if st.button("Save Graph"):
            #     filename = st.text_input("Enter filename to save")
            #     if filename:
            #         save_graph_and_text(G, text_input, filename)
            #         st.success("Saved successfully!")
    # Asking the user for the decision
    # st.write("Please Hit the Button if you want to save the result.")
    # # Initialize session state variables
    # if 'filename' not in st.session_state:
    #     st.session_state.filename = ''

    # if st.button('Save Results'):
    #     # Input for filename
    #     st.session_state.filename = st.text_input('Enter a filename (without extension)', key='filename_input')

    #     # Save button with a callback function
    #     st.button('Save', on_click=save_results(G,df))
    # if st.button('Save Results'):
    #     filename = st.text_input('Enter a filename (without extension)')

    #     if st.button('Save'):
    #         if filename:
    #             # Save the DataFrame as an Excel file
    #             df.to_excel(f'./{filename}.xlsx', index=False)
    #             st.success('DataFrame saved as Excel file.')

    #             # Save the network graph
    #             plt.figure(figsize=(10, 8))
    #             nx.draw(G, with_labels=True)
    #             plt.savefig(f'./{filename}.png',dpi=300)
    #             st.success('Graph saved as PNG image.')

    #             # You might want to clear the figure after saving
    #             plt.clf()
    #         else:
    #             st.error('Please enter a filename.')
    # Reset button
    if st.button("Reset"):
        st.experimental_rerun()
    
    # Add the disclaimer
    st.markdown("---")  # This adds a horizontal line for visual separation
    st.markdown("**Disclaimer:** This application uses the Gemini Pro model, which might produce results that are not always accurate. Users are advised to use their discretion.")

    # Add the creator information
    st.markdown("<div style='text-align: center;'> Created by Debashis and Aditi  </div>", unsafe_allow_html=True)

    # Add the copyright notice
    # We use <div> tags for center alignment in HTML
    st.markdown("<div style='text-align: center;'> &copy; Copyright belongs to IRSC Lab, Wake Forest University </div>", unsafe_allow_html=True)


if __name__ == "__main__":
    main()
