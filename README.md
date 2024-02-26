# BizCardX: Business Card Data Extraction with OCR

## Table of Contents

1. [Project Overview](#project-overview)
2. [Technologies Used](#technologies-used)
3. [Features](#features)
4. [Workflow](#workflow)
5. [Approach](#approach)
6. [Testing](#testing)
7. [Results](#results)
8. [Acknowledgments](#acknowledgments)


## Project Overview

BizCardX is a Streamlit application designed to extract relevant information from business cards uploaded by users. The application utilizes optical character recognition (OCR) technology to parse the uploaded images and extract details such as company name, cardholder name, designation, contact information, and address.


## Technologies Used

- Python
- Streamlit
- EasyOCR
- MySQL


## Features

- User-friendly interface for uploading business card images.
- Extraction of information using EasyOCR.
- Display of extracted data in a clean and organized manner.
- Integration with a database to store extracted information.
- CRUD (Create, Read, Update, Delete) functionality for managing stored data.
- Continuous improvement through bug fixes and feature enhancements.

## Workflow

![BizCardX_Workflow](https://github.com/asdesilva3/BizCardX/assets/148002331/f46270aa-3561-4509-aab6-d82da39ae000)


## Approach

1. **Install Required Packages**: Install Streamlit, easyOCR, and a database management system like SQLite or MySQL.

   ```bash
   pip install streamlit 
   pip install easyocr 
   pip install mysql-connector-python

2. **Design User Interface**: Create an intuitive UI using Streamlit with widgets like file uploader, buttons, and text boxes.

3. **Implement Image Processing and OCR**: Using easyOCR to extract information from the uploaded business card image.

   ```bash
   import easyocr
      
   reader = easyocr.Reader(['en'])
   result = reader.readtext(uploaded_file)

4. **Display Extracted Information**: Present the extracted data in a clean and organized manner in the Streamlit GUI using tables, text boxes, and labels.

5. **Database Integration**: Store the extracted information and uploaded images in a database using SQL queries for table creation, data insertion, retrieval, update, and deletion.

   ```bash
   import mysql.connector

   # Establish MySQL connection
   connection = mysql.connector.connect(
                           user='username',
                           password='password',
                           host='localhost',
                           database='bizcard_db')

6. **Test the Application**: Thoroughly test the application locally using

   ```bash
   streamlit run app.py


## Results

The result is a Streamlit application that allows users to upload business card images, extract relevant information, and store it in a database. The extracted data includes company name, cardholder name, designation, contact details, and address. The application provides a simple and intuitive user interface for efficient data management. It is scalable, maintainable, and extensible, meeting the needs of businesses and individuals for managing business card information effectively.


## Acknowledgments

- Special thanks to the creators of Streamlit and easyOCR for providing the tools necessary for this project.
