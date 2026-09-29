#import necessary libraries
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import time
import os
from contextlib import contextmanager
from functools import wraps
import calendar

#this function calculates the analysis and processing time
def timer(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        start=time.time()
        rv=func(*args, **kwargs)
        end=time.time()
        duration=end-start
        print(f"Time of Execution: {duration:.4f}")
        return rv
    return wrapper

#this function is a context manager that opens the file and checks if it exists and if it's empty
@contextmanager
def AnalysisFile(file):
    try:
        with open(file) as analysis:
            if os.path.getsize(file)!=0:
                df=pd.read_csv(analysis)
                yield df
            else:
                print(f"The file {file} is empty")
                yield None
    except FileNotFoundError:
        print(f"The file {file} doesn't exist")
        yield None
    except PermissionError:
        print(f"You are not allowed to do this action")
        yield None

@timer
def analyse_sales_data(file):
    with AnalysisFile(file) as df:
        # If df is none we stop the program return none else we continue
        if df is None:
            return None
        else:
            print(f"    ======== Analyse du ficher << {file} >> ========\n")
            # Number of sales and columns name
            print(f"Number of sales: {df.shape[0]} \nColumns name: {df.columns.to_list()}\n")

            missing_values = df.isnull().sum()
            print(f"Columns with missing values:\n{missing_values[missing_values >0].to_string()}")
            
            all_null=df[df.isnull().any(axis=1)]
            print(f"Rows with missing values:\n{all_null}\n")

            #Delete rows whose quantity column is empty
            new_df = df.dropna(subset=['Quantity'], inplace=False)

            #Assigned the most popular Region from the category
            grouped= new_df.groupby(['Category','Region']).size().sort_values(ascending=False)
            new_df.loc[new_df[new_df['Region'].isnull()].index[0],'Region'] = grouped.loc['Furniture'].index[0]
            print(f"Number of sales after processing: {new_df.shape[0]}")

            print(f"The Type of Data: \n{new_df.dtypes}\n")
            print(f"General statistics: \n{new_df.describe()}\n")

            #creation of a new column Revenue
            new_df["Revenue"] = new_df["Quantity"] * new_df["Unit_Price"]

            #changed the date format from string to datetime 
            new_df['Date']= pd.to_datetime(new_df['Date'])

            #calculate the revenue group by
            revenue_mois= new_df.groupby(new_df['Date'].dt.month)['Revenue'].sum()
            revenue_produit=new_df.groupby('Product')['Revenue'].sum()
            revenue_region=new_df.groupby('Region')['Revenue'].sum()

            print(f"Total revenue: {new_df['Revenue'].sum()}")
            print(f"Average order revenue: {new_df['Revenue'].mean()}")
            print(f"Highest revenue order: \n{new_df.loc[new_df['Revenue'].idxmax(),['Order_ID','Product','Revenue']].to_string()}")
            print(f"\nBest selling product: {new_df.groupby('Product')['Quantity'].sum().idxmax()}")
            print(f"Best region: {revenue_region.idxmax()}")
            print(f"Best month: {calendar.month_name[revenue_mois.idxmax()]}\n")

            #Initialization of subplots
            figure,axes=plt.subplots(2,2, figsize=(12,10))
            figure.suptitle("Sales analysis chart")

            #First chart: Distribution of order amounts
            axes[0,0].hist(new_df['Revenue'], bins=15,color='skyblue',edgecolor='black')
            axes[0,0].set_xticks(np.arange(50, 550,50))
            axes[0,0].set_xlabel("Revenue")
            axes[0,0].set_ylabel("Order")
            axes[0,0].set_title("Distribution of order amounts")

            #Second chart: Monthly revenue
            axes[0,1].bar(revenue_mois.index, revenue_mois.values,color='lightgreen',edgecolor='black')
            axes[0,1].set_xticks(revenue_mois.index)
            axes[0,1].set_xticklabels(calendar.month_name[m] for m in revenue_mois.index)
            axes[0,1].set_xlabel("Date")
            axes[0,1].set_ylabel("Revenue")
            axes[0,1].set_title("Monthly revenue")

            #Third chart: Products revenue
            axes[1,0].bar(revenue_produit.index,revenue_produit.values,color='lightcoral',edgecolor='black')
            axes[1,0].tick_params(axis="x", labelrotation=20)
            axes[1,0].set_xlabel("Product")
            axes[1,0].set_ylabel("Revenue")
            axes[1,0].set_title("Products revenue")

            #fourth chart: Region revenue
            axes[1,1].bar(revenue_region.index,revenue_region.values,color='lightyellow',edgecolor='black')
            axes[1,1].set_xlabel("Region")
            axes[1,1].set_ylabel("Revenue")
            axes[1,1].set_title("Region revenue")

            plt.tight_layout(pad=3.0)
            plt.show()


print(analyse_sales_data("Sales_Data_Analysis/data/sales.csv"))