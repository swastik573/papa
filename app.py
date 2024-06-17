from flask import Flask, request, render_template, redirect, url_for
import pandas as pd
import os
import numpy as np

UPLOAD_FOLDER = 'uploads'
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'
if(app.config['UPLOAD_FOLDER']):
 print(app.config['UPLOAD_FOLDER'])
else : 
 print("none")
app = Flask(__name__, static_folder='templates/static')

def extract_column_below_header(df, header_name):
    # Find the header location
 try :
      header_location = df.apply(lambda row: row.astype(str).str.contains(header_name, case=False, na=False).any(), axis=1)
      header_row_index = header_location[header_location].index[0]
        
        # Find the column index of the header
      header_col_index = df.iloc[header_row_index][df.iloc[header_row_index].astype(str).str.contains(header_name, case=False, na=False)].index[0]
        
        # Extract values below the header
      column_values = df[header_col_index][header_row_index + 1:].reset_index(drop=True)
        
    
      return column_values
 except IndexError:
        print(f"Header '{header_name}' not found in the DataFrame.")
        return pd.Series([])

def process_files(portal_path, books_path):
    portal_ext = os.path.splitext(portal_path)[1]
    books_ext = os.path.splitext(books_path)[1]

    if portal_ext == '.xls':
        portal_df = pd.read_excel(portal_path, sheet_name="B2B", skiprows=4, header=[0, 1], engine='xlrd')
    else:  # assuming .xlsx or other compatible formats
        portal_df = pd.read_excel(portal_path, sheet_name="B2B", skiprows=4, header=[0, 1])

    # Read books data
    if books_ext == '.xls':
        books_df = pd.read_excel(books_path, sheet_name="GSTR", skiprows=4, header=1, engine='xlrd')
    else:  # assuming .xlsx or other compatible formats
        books_df = pd.read_excel(books_path, sheet_name="GSTR", skiprows=4, header=1)
    
    # Combine the multi-level headers into single level by joining with '_'
    portal_df.columns = ['_'.join(col).strip() for col in portal_df.columns.values]
    
    
    # Clean up column names by removing 'Unnamed' and 'level' parts including numbers
    portal_df.columns = [col.split('_')[0] if 'Unnamed' in col else col for col in portal_df.columns]
    
    
    
    
    		
			

    portal_df['Tax Amount'] = portal_df['Tax Amount_Integrated Tax(₹)'] + portal_df['Tax Amount_Central Tax(₹)'] + portal_df['Tax Amount_State/UT Tax(₹)']
    
    
    
    portal_relevant = portal_df[['Trade/Legal name','GSTIN of supplier',  'Tax Amount']]
    books_relevant = books_df[['Name of Party','GSTIN', 'Tax Amount']]

# Rename columns to match
    portal_relevant.columns = ['Company Name','GST Number',  'Tax Amount']
    books_relevant.columns = ['Company Name', 'GST Number', 'Tax Amount']
# Select relevant columns
       # Select relevant columns
    

# Group by GST Number and sum the Tax Amount
    portal_summed = portal_relevant.groupby('GST Number', as_index=False).agg({'Company Name': 'first', 'Tax Amount': 'sum'})
    books_summed = books_relevant.groupby('GST Number', as_index=False).agg({'Company Name': 'first', 'Tax Amount': 'sum'})

# Merge based on 'GST Number' using outer join
    merged_df = pd.merge(portal_summed, books_summed, on='GST Number', how='outer', suffixes=('_Portal', '_Books'))
    merged_df['Tax Amount_Portal'].fillna(0, inplace=True)
    merged_df['Tax Amount_Books'].fillna(0, inplace=True)

# Calculate differences and handle NaN values
    merged_df['Difference_Tax'] = merged_df['Tax Amount_Portal'] - merged_df['Tax Amount_Books']

# Ensure differences are NaN where either of the original values is NaN
    merged_df['Difference_Tax'] = merged_df['Difference_Tax'].where(~merged_df[['Tax Amount_Portal', 'Tax Amount_Books']].isnull().any(axis=1), np.nan)

# Calculate 'Company Name' based on presence in portal or books
    merged_df['Company Name'] = np.where(merged_df['Tax Amount_Portal']!=0, merged_df['Company Name_Portal'], merged_df['Company Name_Books'])

# Select the required columns
    merged_df = merged_df[['GST Number', 'Company Name', 'Tax Amount_Portal', 'Tax Amount_Books', 'Difference_Tax']]
    merged_df.sort_values(by='Company Name', inplace=True)

# Filter differences that are outside the range of -10 to 10 and not NaN
    differences = merged_df[((merged_df['Difference_Tax'] < -100) | (merged_df['Difference_Tax'] > 100))]

# Format the differences for better readability
    differences['Difference_Tax'] = differences['Difference_Tax'].apply(lambda x: '{:.2f}'.format(x) if pd.notna(x) else x)

# Return or display the differences


    
    return differences

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/uploads', methods=['POST'])
def upload_files():
    portal_file = request.files['portal_file']
    books_file = request.files['books_file']

    if portal_file and books_file:
        portal_path = os.path.join('uploads', 'PORTAL.xlsx')
        books_path = os.path.join('uploads', 'BOOKS.xlsx')

        portal_filename = portal_file.filename.split()[0]

        portal_file.save(portal_path)
        books_file.save(books_path)

        differences = process_files(portal_path, books_path)
        # Render the DataFrame to HTML with Pandas
       
        html_table = differences.to_html(classes='data', header=True)

# Remove leading and trailing whitespace from the HTML table
        html_table = html_table.strip()
        
# Pass the cleaned HTML table to the template
        return render_template('result.html', tables=[html_table]  , portal_filename = portal_filename )

    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug="true" , port=80)
   
