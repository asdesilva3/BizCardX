# import
import easyocr
import cv2
from PIL import Image
import re
import matplotlib.pyplot as plt
import pandas as pd
import streamlit as st
from streamlit_option_menu import option_menu
import mysql.connector
import os

# INITIALIZING THE EasyOCR READER
reader = easyocr.Reader(['en'])
#_________________________________________________________________________________________________________________________________________

# SETTING PAGE CONFIGURATIONS
icon = Image.open("idcard.ico") #add your icon 
st.set_page_config(page_title= "BizCardX",
                   page_icon= icon,
                   layout= "wide",
                   menu_items={'About': "### This page is created by Desilva!"})

st.markdown("<h1 style='text-align: center; color: purple;'>BizCardX: Extracting Business Card Data with easy OCR</h1>", unsafe_allow_html=True)

# CREATING OPTION MENU
selected = option_menu(None, ["HOME","UPLOAD","VIEW","ALTER", "DELETE"], 
                       icons=["house","cloud-upload","binoculars","pencil-square","trash"],
                       default_index=0,
                       orientation="horizontal",
                       styles={"container": {"padding": "0!important", "background-color": "#fafafa"},
                               "icon": {"color": "orange", "font-size": "20px"},
                               "nav-link": {"font-size": "20px", "text-align": "center", "margin":"0px", "--hover-color": "#eee"},
                               "nav-link-selected": {"background-color": "#6495ED"}})

#________________________________________________________________________________________________________________________________________

# FUNCTION TO DISPLAY THE CARD WITH HIGHLIGHTS
def image_preview(image,res):
    for (bbox, text, prob) in res:
        (tl, tr, br, bl) = bbox # unpack the bounding box 
        tl = (int(tl[0]), int(tl[1]))
        tr = (int(tr[0]), int(tr[1]))
        br = (int(br[0]), int(br[1]))
        bl = (int(bl[0]), int(bl[1]))
        cv2.rectangle(image, tl, br, (0, 255, 0), 2) # (0, 255, 0)-->(green) and 2--> thickness
        #cv2.putText(image, text, (bl[0]-10, bl[1]+10),
        #cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 0, 0), 2) #  scale factor of 0.7, (255, 0, 0)-->(blue) and 2--> thickness
    plt.rcParams['figure.figsize'] = (15,15)
    plt.axis('off')
    plt.imshow(image)

# FUNCTION TO CONVERT IMAGE TO BINARY FORMAT
def img_to_binary(path):
    with open(path, 'rb') as image:
        binary_data = image.read()
    return binary_data

# FUNCTION TO EXTRACT REQUIRED TEXT FROM RESULT  
def extracted_text(result,saved_img):
    details = {
        "Name": [],
        "Designation": [],
        "Company_Name": [],
        "Contact": [],
        "Email": [],
        "Website": [],
        "Address": [],
        "Pincode": [],
        "Image": img_to_binary(saved_img)}

    # Define regular expression pattern to match 6-digit numbers
    pincode_pattern = re.compile(r'\b\d{6,7}\b')

    # Extract name and designation directly
    details["Name"].append(result[0].upper())
    details["Designation"].append(result[1])

    # Initialize lists for storing phone numbers, website URLs, and company names
    phone_numbers = []
    website_urls = []
    company_names = []

    # Iterate over the OCR result starting from index 2
    for item in result[2:]:
        if item.startswith("+") or (item.replace("-", "").isdigit() and '-' in item):
            phone_numbers.append(item)
            
        elif "@" in item and ".com" in item:
            details["Email"].append(item.lower())
            
        elif any(sub in item.lower() for sub in ("www", ".com")):
            website_urls.append(item.lower())
            
        elif pincode_pattern.search(item):
            pincode_match = pincode_pattern.search(item)
            pincode = pincode_match.group()
            details["Pincode"].append(pincode)
            
        elif re.match(r'^[A-Za-z]', item) and item.lower() not in ["email", "website", "pincode"]:
            company_names.append(item.strip())

        else:
            remove_colon = re.sub(r'[;]', '', item)
            details["Address"].append(remove_colon)

    # Join the lists of phone numbers, website URLs, and company name
    details["Contact"].append(", ".join(phone_numbers))
    details["Website"].append(", ".join(website_urls))
    details["Company_Name"].append(' '.join(company_names).strip().title())

    return details
#__________________________________________________________________________________________________________________________________

# HOME MENU
if selected == "HOME":
        st.markdown("### :orange[**Overview:**]")
        st.markdown("### BizCardX extracts business card data via OCR, storing it in a database, with Streamlit GUI enabling easy data management, including read, update, and delete functionalities.")
        st.write("")
        st.markdown("### :orange[**Technologies Used:**]")
        st.markdown("### Python, EasyOCR, Matplotlib, Streamlit, MySQL and Pandas")           

# UPLOAD AND EXTRACT MENU
if selected == "UPLOAD":
    st.markdown("### Here the Business Card with be extracted using OCR")
    st.markdown("### Upload a Business Card :open_file_folder:")
    uploaded_cards = st.file_uploader("Upload here", label_visibility="hidden", type=["png", "jpeg", "jpg"],accept_multiple_files=True)
    
    all_dfs = []
    if uploaded_cards is not None:
        all_dfs.clear()  # Reset the list before processing new images

        for index, uploaded_card in enumerate(uploaded_cards):
            # save card in the folder called "Cards"
            with open(os.path.join("cards", uploaded_card.name), "wb") as f:
                f.write(uploaded_card.getbuffer())

            # store the path as saved_img
            saved_img = os.path.join("cards", uploaded_card.name)

            # DISPLAYING THE UPLOADED CARD
            col1, col2 = st.columns(2,gap="medium")
            with col1:
                st.markdown(f"### Uploaded Card - {uploaded_card.name}")
                st.image(uploaded_card)
                
            # DISPLAYING THE CARD WITH HIGHLIGHTS
            with col2:
                with st.spinner("Please wait ... Image processing ..."):
                    st.set_option('deprecation.showPyplotGlobalUse', False)

                    # easy OCR
                    image = cv2.imread(saved_img)
                    res = reader.readtext(saved_img)

                    st.markdown(f"### Image Processed Card - {uploaded_card.name}")
                    st.pyplot(image_preview(image,res)) 
                
            result = reader.readtext(saved_img, detail=0, paragraph=False)            
            card_details = extracted_text(result,saved_img)
            
            df = pd.DataFrame(card_details)
            all_dfs.append(df)

        if all_dfs:  # Check if there are any processed details
            combined_df = pd.concat(all_dfs, ignore_index=True)
            st.success("### Data Extracted Successfully for all images!")
            st.write(combined_df, width=1000)

            #MySQL CONNECTION
            connection  = mysql.connector.connect(user='root', 
                                                password='YOUR_PASSWORD', #change to your password
                                                host='localhost', 
                                                database="bizcardx") #change to your database name
            cursor = connection.cursor(buffered=True)

            # TRANSFERRING DATA TO SQL
            if st.button("Upload to Database"):
                # Define the table creation query
                create_table_query = '''CREATE TABLE IF NOT EXISTS card_details
                                        (ID INT AUTO_INCREMENT PRIMARY KEY,
                                        Name varchar(225),
                                        Designation varchar(225),
                                        Company_Name varchar(225),
                                        Contact varchar(100),
                                        Email text,
                                        Website text,
                                        Address text,
                                        Pincode varchar(10),
                                        Image LONGBLOB)'''   # large binary objects

                cursor.execute(create_table_query)
                connection.commit()

                insert_query = """INSERT INTO card_details(Name,
                                                            Designation,
                                                            Company_Name,
                                                            Contact,
                                                            Email,
                                                            Website,
                                                            Address,
                                                            Pincode,
                                                            Image)
                            VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s)""" #here %S means string values
                
                # Iterate over each row in the DataFrame
                for index, row in combined_df.iterrows():
                    cursor.execute(insert_query, row.tolist())

                connection.commit()
                st.success("#### Uploaded to Database Successfully!")
            connection.close()
    else:
        st.warning("No business cards were processed.")    

if selected == "VIEW":
    #MySQL CONNECTION
    connection  = mysql.connector.connect(user='root', 
                                        password='YOUR_PASSWORD', #change to your password
                                        host='localhost', 
                                        database="bizcardx") #change to your database name

    cursor = connection.cursor(buffered=True)       
    
    cursor.execute("select Name, Designation, Company_Name, Contact, Email, Website, Address, Pincode from card_details")
    updated_df = pd.DataFrame(cursor.fetchall(), columns=["Name", "Designation", "Company_Name", 
                                                        "Contact", "Email", "Website", "Address", "Pincode"])
    st.write(updated_df)
    connection.close()

if selected == "ALTER":
    #MySQL CONNECTION
    connection  = mysql.connector.connect(user='root', 
                                        password='YOUR_PASSWORD', #change to your password
                                        host='localhost', 
                                        database="bizcardx") #change to your database name

    cursor = connection.cursor(buffered=True)

    try:
        # Execute the SQL query to retrieve card details from the "bizcardx" table
        cursor.execute("SELECT Name FROM card_details")
        result = cursor.fetchall()

        # Extract card details from the result and create a dictionary
        business_cards = {}
        for row in result: business_cards[row[0]] = row[0]

        # Create options for the selectbox
        options = ["None"] + list(business_cards.keys())

        # Present the options to the user using a selectbox
        selected_card = st.selectbox("**Select a card**", options)
                    
        if selected_card == "None":
            st.write("No card selected.")

        else:
            st.markdown("#### Update the Data")

            cursor.execute("SELECT Name, Designation, Company_Name, Contact, Email, Website, Address, Pincode from card_details WHERE Name=%s",
            (selected_card,))
            result = cursor.fetchone()

            # DISPLAYING ALL THE INFORMATIONS
            Name = st.text_input("NAME", result[0])
            Designation = st.text_input("DESIGNATION", result[1])
            Company_Name = st.text_input("COMPANY_NAME", result[2])
            Contact = st.text_input("CONTACT", result[3])
            Email = st.text_input("EMAIL", result[4])
            Website = st.text_input("WEBSITE", result[5])
            Address = st.text_input("ADDRESS", result[6])
            Pincode = st.text_input("PINCODE", result[7])

            if st.button(":red[Commit Changes to DB]"):

                # Update the information for the selected business card in the database
                cursor.execute("""UPDATE card_details SET Name=%s,
                                        Designation=%s,
                                        Company_Name=%s,
                                        Contact=%s,
                                        Email=%s,
                                        Website=%s,
                                        Address=%s,
                                        Pincode=%s
                        WHERE Name=%s""", (Name, Designation, Company_Name, Contact, Email, Website, Address, Pincode, selected_card))

                connection.commit()
                st.success("Information Updated in Database Successfully.")
                connection.close()
    except:
        st.warning("There is no data available in the database")

if selected == "DELETE":
    #MySQL CONNECTION
    connection  = mysql.connector.connect(user='root', 
                                        password='YOUR_PASSWORD', #change to your password
                                        host='localhost', 
                                        database="bizcardx") #change to your database name
    cursor = connection.cursor(buffered=True)

    try:
        cursor.execute("SELECT Name FROM card_details")
        result = cursor.fetchall()

        business_cards = {}
        for row in result: business_cards[row[0]] = row[0]

        options = ["None"] + list(business_cards.keys())
        selected_card = st.selectbox("**Select a Card**", options)

        if selected_card == "None":
            st.write("No card selected.")
        else:
            st.write(f"### You have selected :red[**{selected_card}'s**] card to delete")
            st.write("#### To delete this card. Press the DELETE button")

            if st.button(f' :red[DELETE]'):
                cursor.execute(f"DELETE FROM card_details WHERE Name='{selected_card}'")
                connection.commit()
                st.success(f'''{selected_card}'s information deleted from database''')
                connection.close()

    except:
        st.warning("There is no data available in the database")
 
#_____________________________________END________________________________________________
