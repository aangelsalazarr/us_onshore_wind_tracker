import pandas as pd
import requests
import json 
import datetime
import matplotlib.pyplot as plt
from fpdf import FPDF
import os
import seaborn as sns


def process_data(dataframe):

    '''
    Purpose of this function is to clean up our data.
    '''
    dataframe['p_name'] = dataframe['p_name'].values.astype(str)
    dataframe.drop(dataframe[dataframe.p_name.str.contains('unknown', case=False)].index)

    return dataframe


###############################################################################


def top_n(df, group_by, filter_by, n=10):
    """
    Filters the top N entities Pandas DataFrame.
    """

    # Group the DataFrame by company sum
    df_temp = df.groupby(group_by)[filter_by].sum()

    # here we are renaming our column to t_cap
    df_temp = df.groupby(group_by)[filter_by].sum().to_frame(name='t_cap')

    # resetting index
    df_temp = df_temp.reset_index()

    # sortinng values in descending order
    df_temp = df_temp.sort_values(filter_by, ascending=False)

    # Get the top 10 entities
    return df_temp[:n]


###############################################################################


def add_data_table(pdf, data, x_start, y_start, w, h):
  """
  Adds a data table to a specific page of an FPDF document.

  Args:
    pdf: An FPDF object.
    data: A Pandas DataFrame or a list of dictionaries.
    page_num: The page number where the table should be added.
    x_start: X-coordinate of the table's top-left corner.
    y_start: Y-coordinate of the table's top-left corner.
    w: Width of the table.
    h: Height of the table.
  """

  # Convert data to DataFrame if needed
  if not isinstance(data, pd.DataFrame):
    data = pd.DataFrame(data)

  # Calculate cell width and height
  cell_w = w / len(data.columns)
  cell_h = h / len(data.index)

  # Draw table header
  pdf.multi_cell(w, cell_h, "Table Header", border=1, align='C', x=x_start, y=y_start)
  pdf.line(x1=x_start, y1=y_start, x2=x_start + w, y2=y_start)  # draw top line

  # Iterate through data and create cells
  for index, row in data.iterrows():
    y_pos = y_start + cell_h * (index + 1)
    for col in data.columns:
      x_pos = x_start + cell_w * data.columns.get_loc(col)
      value = row[col]
      pdf.multi_cell(cell_w, cell_h, value, border=1, align='J', x=x_pos, y=y_pos)
    pdf.line(x1=x_start, y1=y_pos, x2=x_start + w, y2=y_pos)  # draw bottom line


###############################################################################


def grab_data_by_state(state, pls_save=False):
    '''
    Purpose of this function is to grab wind turbing data by statem which is the
    input that the user will provide
    '''
    # purpose is to create a variable that stores todays date
    today = datetime.date.today()

    # formatting date as MM_YYYY
    todays_date = today.strftime('%m_%Y')

    # base path that will be the first part of all url requests
    base_path = 'https://eersc.usgs.gov/api/uswtdb/v1/'

    # url segement that allows us to grab data by state
    by_state = f'turbines?&t_state=eq.{state}'

    # purpose is to walk through how to convert json --> dataframe
    url = base_path + by_state
    response = requests.get(url=url)
    json_data = json.loads(response.content)

    # now we want to convert into a pandas df
    df = pd.DataFrame(data=json_data)

    # if a save == True, then we will create a save path and store the file as xlsx
    if pls_save == True:

        # outputting data as a csv file
        save_path = f'data_files/{state}_data_{todays_date}.xlsx'
        df.to_excel(save_path)

        print('File saved and processed!')

    else:

        print('File saved only.')

    return df


###############################################################################


def histplot_it(gdf, x_value, figw=10, figh=8, hue_by=None):
    '''
    purpose is to apply histplot to data depending on what user wants
    '''
    fig = plt.figure()
    fig.set_figwidth(figw)
    fig.set_figheight(figh)

    # now we will apply depending on x
    sns.histplot(data=gdf, x=x_value, kde=True, hue=hue_by)

    # now giving our plot some pretty visuals
    if x_value == 't_rd':
        plt.title(f'Histogram of USA Wind Turbine Rotor Diameter (m)')
        plt.xlabel('Turbine Rotor Diameter (m)')
    
    elif x_value == 't_cap':
        plt.title(f'Histogram of USA Wind Turbine Rated Capacity (kW)')
        plt.xlabel('Turbine Rated Capacity (kW)')
    
    else:
        print('No pretty stuff for params you provided!')

    return fig


###############################################################################


def kde_plot_it(gdf, state_id, state_map):
  """
  Purpose is to return a kde plot of data for a particular state
  """

  # Create a single seaborn figure
  fig, ax = plt.subplots()

  # Create the kernel density plot
  sns.kdeplot(
      x=gdf.centroid.x,
      y=gdf.centroid.y,
      ax=ax,
      fill=True,
      gridsize=100,
      bw_adjust=0.5,
      cmap="coolwarm"
  )

  # Add the state map
  state_map.plot(ax=ax, facecolor="none", edgecolor="gray", alpha=0.3)

  # Adjust plot settings
  ax.set_axis_off()
  plt.title(f"{state_id} Kernel Density Plot")

  return fig


#### added rotor data function
def rotor_data(gdf, figw=18, figh=12, hue_by=False):
    '''
    purpose is to present rotor data as histplot
    '''
    fig = plt.figure()
    fig.set_figwidth(figw)
    fig.set_figheight(figh)

    # we are storing the name of the state where this data is set
    state = gdf['t_state'][1]
    print(f"we successfully stored the state:{state}")

    if hue_by == '':
        sns.histplot(data=gdf, x='t_rd', kde=True, bins='auto')

    else:
        sns.histplot(data=gdf, x='t_rd', kde=True, bins='auto', 
                     hue=hue_by)
        
    plt.title(f'Histogram of {state} Wind Turbine Rated Capacity (kW)')
    plt.xlabel('Turbine Rated Capacity (kW)')
    return fig



### adding capacity data function
def capacity_data(gdf, figw=18, figh=12, hue_by=False):
    '''
    purpose is to visualize trends in turbine capacity
    '''
    fig = plt.figure()
    fig.set_figwidth(figw)
    fig.set_figheight(figh)

    # we are storing the name of the state where this data is set
    state = gdf['t_state'][1]
    print(f"We successfully stored the state: {state}")

    if hue_by == '':
        sns.histplot(data=gdf, x='t_cap', kde=True, bins='auto')

    else:
        sns.histplot(data=gdf, x='t_cap', kde=True, bins='auto', 
                     hue=hue_by)
        
    plt.title(f'Histogram of {state} Wind Turbine Rated Capacity (kW)')
    plt.xlabel('Turbine Rated Capacity (kW)')
    return fig
