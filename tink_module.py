import pandas as pd
import uuid
import random as rd
import hashlib
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from df2gspread import df2gspread as d2g


def update_category_from_google_sheet_data(df,key_name,key,cat1,cat2):
    #print(len(df[df[key_name].str.contains(key)]))
    for i in df[df[key_name].str.contains(key)].index:
        df.loc[i,'level_2_category'] = cat2
        df.loc[i,'level_1_category'] = cat1

def find_month(date_in, salary_df):
    date_out = salary_df[(salary_df['from_date'] <= date_in) & (salary_df['to_date'] > date_in)]['budget_month']
    if date_out is not None: 
        return pd.to_datetime(str(date_out.values[0])).strftime('%Y-%m-%d') if len(date_out) > 0 else None
    else:
        return None

def get_id(my_string):
    return str(int(hashlib.md5(my_string.encode('utf-8')).hexdigest(),16))

def get_sheet_from_book(book,sheet_name):
    scope = ['https://spreadsheets.google.com/feeds']
    # Give the path to the Service Account Credential json file 
    credentials = ServiceAccountCredentials.from_json_keyfile_name('./service_account_GS.json',scope)
    # Authorise your Notebook
    gc = gspread.authorize(credentials)
    # The sprad sheet ID, which can be taken from the link to the sheet
    spreadsheet_key = '1RlAbGix-Z6xGfvTrGJz7FzZbIn5aNgQKj7DxvEgc0oc'
    workbook = gc.open_by_key(spreadsheet_key)
    sheet = workbook.worksheet(sheet_name)
    return sheet
    

def clean_data(transactions_raw, categories_raw,accounts_raw):

    ## Transactions
    transactions = pd.DataFrame(transactions_raw)
    #remove reservations
    transactions = transactions[transactions['pending']==False]
    transactions['transaction_date'] = pd.to_datetime(transactions['originalDate'], unit='ms')
    transactions = transactions[transactions['transaction_date']>'2019-09-01']
    transactions['transaction_date_str'] =pd.to_datetime(transactions['date'], unit='ms').dt.strftime('%Y-%m-%d')
    transactions['transaction_modified_date_str']=pd.to_datetime(transactions['lastModified'], unit='ms').dt.strftime('%Y-%m-%d')
    #transactions['transaction_date'] = transactions['transaction_date'].dt.strftime('%Y-%m-%d')
    transactions['transaction_amount'] = transactions['originalAmount']
    transactions['category_id'] = transactions['categoryId']
    transactions['transaction_description'] = transactions['originalDescription']
    transactions['transaction_formated_description'] = transactions['formattedDescription']
    transactions['account_id'] = transactions['accountId']
    transactions = transactions[['transaction_date','transaction_date_str','transaction_modified_date_str','transaction_amount','transaction_description','transaction_formated_description','category_id','account_id']]
    
    ## Accounts
    accounts = pd.DataFrame(accounts_raw)
    accounts['account_type'] = accounts['name']
    accounts['account_id'] = accounts['id']
    accounts['account_number'] = accounts['accountNumber']
    
    account_names = pd.DataFrame([
            {'account_number':'33009107283104','account_name':'Julia Personkonto'},
            {'account_number':'33008712091415','account_name':'Filip Personkonto'},
            {'account_number':'18492079010','account_name':'Gemensamt Transaktionskonto'},
            {'account_number':'30392163284','account_name':'Filip Sparkonto'},
            {'account_number':'18492872179','account_name':'Gemensamt Sparkonto'}]
    )
    accounts = accounts.merge(account_names,left_on='account_number',right_on='account_number')
    accounts = accounts[['account_id','account_number','account_type','account_name']]
    
    ## Categories
    categories = pd.DataFrame(categories_raw)
    categories['category_id'] = categories['id']
    categories['category_level'] = categories['code'].str.replace('.',':').str.split(':').apply(lambda x: len(x))
    categories['transaction_type'] = categories['typeName']
    categories['level_1_category'] = categories.apply(lambda x: x['primaryName'] if x['category_level']>1 else None,axis=1)
    categories['level_2_category'] = categories['secondaryName']
    categories = categories[['transaction_type','level_1_category','level_2_category','category_level','category_id']]
    
    ## Merge Dataframes
    transactions = transactions.merge(accounts,left_on='account_id', right_on='account_id')
    transactions = transactions.merge(categories,left_on='category_id', right_on='category_id')
    
    ## Set salary cutoff dates
    lon = transactions[transactions['transaction_description'] == 'Lön'].copy()
    lon = lon.sort_values(by='transaction_date',ascending=False)
    lon['salary_month'] = lon['transaction_date'].apply(lambda x: x.replace(day=1,hour=0))
    lon = lon.groupby('salary_month').min().reset_index()[['salary_month','transaction_date']]
    lon['previous_salary_date'] = lon[['transaction_date']].shift(periods=-1)
    lon = lon.fillna(pd.Timestamp(2099, 1, 1))
    lon['budget_month'] = (lon['salary_month'] + pd.DateOffset(months=1))
    lon = lon.drop('salary_month',axis=1)
    lon.columns=['from_date','to_date','budget_month']
   
    transactions['budget_month'] = transactions['transaction_date'].apply(lambda x: find_month(x,lon))
    transactions['transaction_id'] = transactions.apply(lambda x: get_id(x['transaction_date_str']+str(x['transaction_amount'])+x['transaction_description']+x['account_name']),axis=1)
    transactions = transactions[transactions['budget_month']>='2019-10-01']
    duplicates = transactions.groupby('transaction_id').count()
    print("--- Duplicates ---")
    for i in duplicates[duplicates['transaction_date_str'] > 1].index.values:
        print(transactions[transactions['transaction_id']==i]['transaction_description'].values[0]+': ' + str(transactions[transactions['transaction_id']==i]['transaction_amount'].values[0]))
    
    ## download manual transaction categories and update dataframe
    sheet = get_sheet_from_book('1RlAbGix-Z6xGfvTrGJz7FzZbIn5aNgQKj7DxvEgc0oc','manual categories')
    values = sheet.get_all_values()
    manual_categories_data = pd.DataFrame(values[1:],columns=values[0])
    
    manual_categories_data.apply(lambda x: update_category_from_google_sheet_data(transactions,x['key_name'],x['key_value'],x['level_1_category'],x['level_2_category']),axis=1)
    transactions = transactions[transactions['level_1_category']!='Exclude']
    return transactions
