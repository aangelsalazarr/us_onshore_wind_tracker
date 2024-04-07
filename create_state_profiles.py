# importing necessary modules
import geopandas as gpd
import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns
import numpy as np
import pointpats
from fpdf import FPDF
import functions as fns
import os
import datetime


# setting up todays date to label our files
today = datetime.date.today()

# formatting date as MM_YYYY
todays_date = today.strftime('%m_%Y')


def gimme_profile(state_id):

    '''
    purpose of this function is to grab data from US Wind Turbine Database
    and save it as an excel file and then create a pdf of different analysis
    done.
    '''
    # grabbing data from web
    data = fns.grab_data_by_state(state=state_id, pls_save=True)

    # now let's create a geopandas dataframe while converting the 
    # x y coordinates
    df = pd.read_excel(f'data_files/{state_id}_data_{todays_date}.xlsx')
    points = gpd.points_from_xy(df['xlong'], df['ylat'])

    # converting df into a geopandas dataframe
    gdf = gpd.GeoDataFrame(df, geometry=points, crs='EPSG:4326')

    # setting up some params
    plt.rcParams['figure.dpi'] = 100

    # loading our map outline
    states = gpd.read_file('2015-2019-acs-states.geojson')

    # removing non main land states
    states = states[~states['ST'].isin(['AK', 'HI', 'PR'])]
    states = states.to_crs(gdf.crs)

    # grabbing only polygon for specific state
    state_store = states[states['ST'].isin([f'{state_id}'])]


    # second plot will be a historgram tracking the trend of rotor diameter
    # 5Y and 10Y; this uses seaborn plots so will warrant a different pdf
    gdf_5y = gdf[gdf['p_year'] >= 2018]
    gdf_3y = gdf[gdf['p_year'] >= 2020]

    # initialzing a pdf page
    pdf = FPDF()

    # maps each turbine by year
    ch=8
    pdf.add_page()
    pdf.set_font('Arial', 'B', 24)
    pdf.cell(w=0, h=20, txt=f'{state_id} Report', ln=1)
    pdf.set_font('Arial', '', 16)
    pdf.cell(w=30, h=ch, txt="Date: ", ln=0)
    pdf.cell(w=30, h=ch, txt="12/9/2023", ln=1)
    pdf.cell(w=30, h=ch, txt="Author: ", ln=0)
    pdf.cell(w=30, h=ch, txt="Angel Salazar", ln=1)


    # grabbing top 10 manufacturers by capacity
    top_manus = fns.top_n(df=gdf, group_by='t_manu', filter_by='t_cap')

    # Table Header
    pdf.set_font('Arial', 'B', 16)
    pdf.cell(w=95, h=ch, txt='Manufacturer', 
             border=1, ln=0, align='C')
    pdf.cell(w=95, h=ch, txt='Aggregated Turbine Capacity', 
             border=1, ln=1, align='C') # Table contents
    pdf.set_font('Arial', '', 16)
    for i in range(0, len(top_manus)):
        pdf.cell(w=95, h=ch, 
                txt=top_manus['t_manu'].iloc[i], 
                border=1, ln=0, align='C')
        pdf.cell(w=95, h=ch, 
                txt=top_manus['t_cap'].iloc[i].astype(str), 
                border=1, ln=1, align='C')


    pdf.add_page()
    ax = gdf.plot('p_year', markersize=3, legend=True)
    dots = state_store.plot(facecolor='none', edgecolor='black', ax=ax)
    ax.set_axis_off()
    plt.title(f'{state_id} Turbine Count by Year')
    plt.savefig('dots.png', bbox_inches='tight')
    pdf.image('dots.png', 10, 10, 180)
    os.remove('dots.png')


    # kernel density plot of turbine locations
    pdf.add_page()
    kde_plot = fns.kde_plot_it(gdf=gdf, state_id=state_id, 
                               state_map=state_store)
    plt.savefig('kde_plot.png', bbox_inches='tight')
    pdf.image('kde_plot.png', 10, 10, 180)
    os.remove('kde_plot.png')


    # rotor data density histplot
    pdf.add_page()
    rotors = fns.rotor_data(gdf=gdf)
    plt.savefig('rd.png', bbox_inches='tight')
    pdf.image('rd.png', 10, 10, 180)
    os.remove('rd.png')


    # adding rotor data from past 5 years
    pdf.add_page()
    years5 = fns.rotor_data(gdf=gdf_5y, 
                            hue_by='p_year')
    plt.savefig('years5_rd.png', bbox_inches='tight')
    pdf.image('years5_rd.png', 10, 10, 180)
    os.remove('years5_rd.png')


    # adding rotor data for past 3 years
    pdf.add_page()
    years3 = fns.rotor_data(gdf=gdf_3y,
                            hue_by='p_year')
    plt.savefig('years3_rd.png', bbox_inches='tight')
    pdf.image('years3_rd.png', 10, 10, 180)
    os.remove('years3_rd.png')

     # adding capacity data for past 5 years
    pdf.add_page()
    caps = fns.capacity_data(gdf)
    plt.savefig('cap.png', bbox_inches='tight')
    pdf.image('cap.png', 10, 10, 180)
    os.remove('cap.png')

    # adding capacity data for past 5 years
    pdf.add_page()
    years5 = fns.capacity_data(gdf=gdf_5y, 
                               hue_by='p_year')
    plt.savefig('years5_cap.png', bbox_inches='tight')
    pdf.image('years5_cap.png', 10, 10, 180)
    os.remove('years5_cap.png')

    # adding capacity data for past 3 years
    pdf.add_page()
    years3 = fns.capacity_data(gdf=gdf_3y, 
                               hue_by='p_year')
    plt.savefig('years3_cap.png', bbox_inches='tight')
    pdf.image('years3_cap.png', 10, 10, 180)
    os.remove('years3_cap.png')

    pdf.output(f'state_profiles/{state_id}_Report_{todays_date}.pdf')

    '''
    # storing all our dataframes in a list to iterate through 
    gdfs = [gdf_3y, gdf_5y]

    # iterate through each and save histplot figure
    for gdf in gdfs:
        fig = fns.rotor_data(gdf=gdf, hue_by='p_year')
        plt.savefig(f'histplot{gdfs.index(gdf)}.png')
    '''


estados = [#'TX', 
           'IA', 'MN', 'KS', 'OK', 'CO', 'CA', 'IL', 'ND']

for estado in estados:

    gimme_profile(estado)



