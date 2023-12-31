# -*- coding: utf-8 -*-
"""Untitled13.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1_Losb4lUGoUaAQLmoH46ahFrC6Hbz1G9
"""

import tensorflow as tf
import os
import requests
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import datetime
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import MinMaxScaler
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import LSTM, Dense
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import *
from tensorflow.keras.callbacks import ModelCheckpoint
from tensorflow.keras.losses import MeanSquaredError
from tensorflow.keras.metrics import RootMeanSquaredError
from tensorflow.keras.optimizers import Adam

"""## Input data for target city / cities through API"""

'''
def historical():
    cities = pd.read_csv("extracted_data.csv")
    historical_data_by_city = []
    url = "https://archive-api.open-meteo.com/v1/archive"

    for index, row in cities_df.iterrows():
        city_name = row['city']
        latitude = row['lat']
        longitude = row['lng']


        params = {
            "latitude": latitude,
            "longitude": longitude,
            "start_date": "1941-01-01",
            "end_date": "2020-12-31",
            "daily": "temperature_2m_max,temperature_2m_min,temperature_2m_mean,precipitation_sum,rain_sum,snowfall_sum,windspeed_10m_max,shortwave_radiation_sum,et0_fao_evapotranspiration",
            "timezone": "auto"
        }


        response = requests.get(url, params=params)

        # Assuming the response is in JSON format
        historical_data = response.json()

        # Extract relevant data from the response
        daily_data = historical_data['daily']
        elevation = historical_data['elevation']

        # Create a DataFrame from the extracted data
        historical_daily_df = pd.DataFrame(daily_data)
        historical_daily_df.time = pd.to_datetime(historical_daily_df.time)
        historical_daily_df = historical_daily_df.set_index('time')


        # Add city name, elevation, and other info
        historical_daily_df['city'] = city_name
        historical_daily_df['lat'] = latitude
        historical_daily_df['lon'] = longitude
        historical_daily_df['elev'] = elevation

        # Append the DataFrame to the list
        historical_data_by_city.append(historical_daily_df)



    # Concatenate all DataFrames in the list into a single DataFrame
    final_dataframe = pd.concat(historical_data_by_city, ignore_index=False)
    return final_dataframe
final_dataframe_df = historical()
'''

"""# Input data for target cities used for model training from CSV"""

# if want to use the historical data csv (Final_project_data/historical_full.csv)
cities_df = pd.read_csv("/content/drive/MyDrive/Final_pro_upload/For_upload/Final_data_files/cities_data_cls_ele.csv")
data_df = pd.read_csv("/content/drive/MyDrive/Final_pro_upload/For_upload/historical.csv")

import pandas as pd

# We have a DataFrame named 'climate_data' containing data for
# all cities with a 'date' column and a 'city' column

# Determine the length (number of rows) of data for the city with shortest duration (Lima)
lima_length = len(data_df[data_df['city'] == 'Lima'])

# Slice the data for all other cities to match the length of Lima's data
data_df = data_df.groupby('city').apply(lambda x: x.iloc[:lima_length]).reset_index(drop=True)

# Now, 'climate_data' contains data for all cities with the same length as Lima's data

"""## If you have cities data and you want to add climate class and elevation to it

"""

# adding Koeppen-Geiger Climate class information (cls) as a column to city data
'''
def K_Geiger_class(df):
    import pandas as pd
    from scipy.spatial.distance import cdist
    from scipy.spatial import cKDTree

    # Load data from Koeppen-Geiger-ASCII.txt
    koeppen_data = []
    with open("Koeppen-Geiger-ASCII.txt", "r") as file:
        next(file)  # Skip the header line
        for line in file:
            lat, lon, cls = line.strip().split()
            koeppen_data.append((float(lat), float(lon), cls))

    koeppen_df = pd.DataFrame(koeppen_data, columns=["Lat", "Lon", "Cls"])
    kdtree = cKDTree(koeppen_df[["Lat", "Lon"]])

    # Assuming final_dataframe_df is your DataFrame with latitude and longitude columns
    lat_lon_pairs = cities[["lat", "lng"]].values
    distances, indices = kdtree.query(lat_lon_pairs)

    # Assign the Cls values to the "Cls" column in final_dataframe_df
    cities["Cls"] = koeppen_df.loc[indices, "Cls"].values

    # Assuming final_dataframe_df is your DataFrame with latitude column
    cities["Hemi"] = cities["lat"].apply(lambda lat: "N" if lat >= 0 else "S")
    return cities

cities_df = K_Geiger_class(cities)
'''

# adding elevation information (elevation) as a column to city data
'''
def elevation(df):
    import pandas as pd
    import requests


    # Initialize an empty list to store elevation data
    elevations = []

    # Loop through cities and fetch elevation data
    for index, row in cities_df.iterrows():
        lat = row['lat']
        lon = row['lng']

        # Construct the OpenTopoData API URL
        api_url = f"https://api.opentopodata.org/v1/srtm90m?locations={lat},{lon}"

        try:
            # Send a request to the API and retrieve elevation data
            response = requests.get(api_url)
            elevation_data = response.json()
            elevation = elevation_data['results'][0]['elevation']
        except Exception as e:
            print(f"Error fetching elevation for {row['city']}: {str(e)}")
            elevation = None

        # Append elevation information to the 'elevations' list
        elevations.append(elevation)

    # Add the 'elevation' column to the 'cities_df' DataFrame
    cities_df['elevation'] = elevations
    return cities_df

cities_df = elevation(cities_df)
'''

# Filter out rows with NaN values in both 'city' and 'population' columns
cities_df_clean = cities_df.copy()
cities_df_clean = cities_df.dropna(subset=['city', 'population'])

# For each unique key, select the row with the highest population
cities_data = cities_df_clean.loc[cities_df_clean.groupby('city')['population'].idxmax()]

# Display the modified right DataFrame
print("Modified Right DataFrame (with highest population rows only):")
cities_data

# clean word cities data for processing
cities = cities_data.drop(columns=['city_ascii', 'country', 'iso2', 'iso3', 'admin_name', 'capital', 'population', 'id'])

cities

# Check for and display duplicate keys in the right DataFrame
duplicate_keys = cities[cities.duplicated(subset=['city'], keep=False)]
print(duplicate_keys)

"""## merge cities and historical climate dfs"""

# We have DataFrames 'data' and 'cities_df_clean'

# Merge the two DataFrames based on the 'city' column
combined_data = pd.merge(data_df, cities, on='city', how='left')

combined_data

# Check for NaN values in each column and count them
nan_count = combined_data.isna().sum()

# You can also check if there are any NaN values in any column
has_nan = nan_count.any()

# Print the count of NaN values in each column
print("NaN Count in Each Column:")
print(nan_count)

# Check if there are any NaN values in any column
if has_nan:
    print("There are NaN values in one or more columns.")
else:
    print("There are no NaN values in any column.")

# Replace NaN values in each column with the median of the last 30 days data in that column
# for climate variables and length of a city data for others
combined_data = combined_data.fillna(combined_data.rolling(window=300000, min_periods=1).median())
#combined_data['elevation'] = combined_data['elevation'].fillna(combined_data['elevation'].median())
data = combined_data.copy()

"""## Save historical data withe all required variables"""

'''
from pathlib import Path
#filepath = Path('fill your file path and name here')
filepath = Path("/content/drive/MyDrive/Final_pro_upload/For_upload/Final_data_files/data_allveriables.csv")
filepath.parent.mkdir(parents=True, exist_ok=True)
data.to_csv(filepath, index=False)

'''

"""## Load historical data (if want to use the given data "hist.csv")"""

'''
data = pd.read_csv("your file path")
'''



"""## Data preprocessing (Historical / Reference) (Historical / Reference) - One hot encoding and scaling

### One hot encoding for climate class (Cls) and hemisphare (Hemi)
"""

# Apply one-hot encoding to the "Cls" column
cls_encoded = pd.get_dummies(data["Cls"], prefix="Cls")

# Apply one-hot encoding to the "Hemisphere" column
hemisphere_encoded = pd.get_dummies(data["Hemi"], prefix="Hemi")

# Concatenate the encoded columns back to the original DataFrame
data_encoded = pd.concat([data, cls_encoded, hemisphere_encoded], axis=1)

# Drop the original "Cls" and "Hemisphere" columns
data_encoded = data_encoded.drop(["Cls", "Hemi", "lat"], axis=1)

"""### Scaling selcted data"""

from sklearn.preprocessing import MinMaxScaler

# Columns to be scaled
columns_to_scale = ['lng', 'elevation']

# Initialize the MinMaxScaler
scaler = MinMaxScaler(feature_range=(0, 2))

# Apply the MinMaxScaler to the absolute values of the selected columns
data_encoded[columns_to_scale] = scaler.fit_transform(data_encoded[columns_to_scale].abs())

"""### Encoding time variables"""

#-----------------------------------------
df_time = data_encoded.copy()


# Assuming you have a DataFrame named 'df_time' and a column 'date' containing dates and times
df_time['date'] = pd.to_datetime(df_time['date'])  # Convert 'date' column to Timestamp objects

#------------------------------------------
# date and time variable scaling
df_time['Seconds'] = df_time['date'].map(pd.Timestamp.timestamp)

day = 60*60*24
year = 365.2425*day

df_time['Day_sin'] = np.sin(df_time['Seconds'] * (2 * np.pi / day))
df_time['Day_cos'] = np.cos(df_time['Seconds'] * (2 * np.pi / day))
df_time['Year_sin'] = np.sin(df_time['Seconds'] * (2 * np.pi / year))
df_time['Year_cos'] = np.cos(df_time['Seconds'] * (2 * np.pi / year))

# Drop the specified columns
df_time = df_time.drop(columns=['Seconds', 'Day_cos'])

# Copy the modified DataFrame to 'df'
df = df_time.copy()
df = df.set_index(['city', 'date'])
df = df.drop(["w_code"], axis=1)

df

"""## x, y data split and scaling/preprocessing remaining variables"""

# X, y data prep

def df_to_X_y(df, window_size=7):
  df_as_np = df.to_numpy()
  X = []
  y = []
  for i in range(len(df_as_np)-window_size):
    row = [r for r in df_as_np[i:i+window_size]]
    X.append(row)
    label = [df_as_np[i+window_size][0], df_as_np[i+window_size][3]]
    y.append(label)
  return np.array(X), np.array(y)
X, y = df_to_X_y(df)

#---------------------------------
# train, test and validation data split

X_train, y_train = X[:600000], y[:600000]
X_val, y_val = X[800000:1000000], y[600000:1000000]
X_test, y_test = X[1000000:], y[1000000:]
X_train.shape, y_train.shape, X_val.shape, y_val.shape, X_test.shape, y_test.shape


#---------------------------------------------
# normalization and capturing noise, seasonality and extreams

temp_training_mean = np.mean(X_train[:, :, 0])
temp_training_std = np.std(X_train[:, :, 0])
p_training_mean = np.mean(X_train[:, :, 3])
p_training_std = np.std(X_train[:, :, 3])

wind_training_mean = np.mean(X_train[:, :, 1])
wind_training_std = np.std(X_train[:, :, 1])
red_training_mean = np.mean(X_train[:, :, 2])
red_training_std = np.std(X_train[:, :, 2])


def preprocess(X):
    X[:, :, 0] = (X[:, :, 0] - temp_training_mean) / temp_training_std
    X[:, :, 1] = (X[:, :, 3] - p_training_mean) / p_training_std
    X[:, :, 2] = (X[:, :, 1] - wind_training_mean) / wind_training_std
    X[:, :, 3] = (X[:, :, 2] - red_training_mean) / red_training_std


def preprocess_output(y):
    y[:, 0] = (y[:, 0] - temp_training_mean) / temp_training_std
    y[:, 1] = (y[:, 1] - p_training_mean) / p_training_std

#------------------------------
preprocess(X_train)
preprocess(X_val)
preprocess(X_test)



#--------------------------------
preprocess_output(y_train)
preprocess_output(y_val)
preprocess_output(y_test)

"""##  Model"""

import tensorflow as tf
from tensorflow.keras.layers import Input, LSTM, Dense
from tensorflow.keras.models import Model
from tensorflow.keras.callbacks import ModelCheckpoint
from tensorflow.keras.optimizers import Adam
from tensorflow.keras.losses import MeanSquaredError
from tensorflow.keras.metrics import RootMeanSquaredError

# Define the model
inputs = Input(shape=(7, 24))
x = LSTM(32, return_sequences=True)(inputs)
x = LSTM(64)(x)
x = Dense(32, activation=tf.nn.relu)(x)  # Use tf.nn.relu for ReLU activation
outputs = Dense(2, activation='linear')(x)  # Linear activation is fine as it is

model = Model(inputs=inputs, outputs=outputs)

# Compile the model
optimizer = Adam(learning_rate=0.001)
model.compile(loss=MeanSquaredError(), optimizer=optimizer, metrics=[RootMeanSquaredError()])

# Print model summary
model.summary()

"""## Model training"""

from tensorflow.keras.callbacks import EarlyStopping
# Define the ModelCheckpoint callback
cp = ModelCheckpoint('best_model.h5', save_best_only=True, monitor='val_loss', mode='min', verbose=1)

# Define the EarlyStopping callback
early_stop = EarlyStopping(monitor='val_loss', mode='min', patience=8, verbose=1)

# Train the model
history = model.fit(X_train, y_train, validation_data=(X_val, y_val), epochs=7, callbacks=[cp])

# Load the best model
best_model = tf.keras.models.load_model('best_model.h5')

# Evaluate the best model
test_loss = best_model.evaluate(X_test, y_test)
print(f'Test Loss: {test_loss[0]}, Test RMSE: {test_loss[1]}')

# Specify the desired file path and name
model_filename = 'my_trained_model.h5'

# Save the model to the specified file
best_model.save(f'/content/drive/MyDrive/Final_pro_upload/For_upload/best_model/{model_filename}')

print(f"Model saved to {model_filename}")

from tensorflow.keras.models import load_model
# Define the path to the saved model directory
# Define the filename of the saved model
#model_filename = 'my_trained_model.h5'

# Load the saved model
best_model = load_model(f'/content/drive/MyDrive/Final_pro_upload/For_upload/Final_data_files/best_model.h5')

# Make predictions on the validation set
predicted_values = best_model.predict(X)

def postprocess_temp(arr):
  arr = (arr*temp_training_std) + temp_training_mean
  return arr

def postprocess_p(arr):
  arr = (arr*p_training_std) + p_training_mean
  return arr

# Extract temperature and precipitation predictions

predicted_precipitation, predicted_temperature = postprocess_p(predicted_values[:, 1]), postprocess_temp(predicted_values[:, 0])

"""## Reference data copies oreperation for trend and variability corrections"""

reference = df.copy()
reference = reference.rename(columns={"date": "ref_time", "tmp": "ref_tmp", "pcp": "ref_pcp"})
# Set "ref_time" and "city" as the index
#reference.set_index(['city', 'ref_time'], inplace=True)

reference

# Keep only "ref_tmp" and "ref_pcp" columns
ref_data = reference[['ref_tmp', 'ref_pcp']]

# Drop the first 7 rows from the multi-index DataFrame
ref_data = ref_data.iloc[7:]

#Reset the index to maintain 'ref_time' and 'city' as columns
#ref_data.reset_index(inplace=True)

#ref_data.head(10)
#ref_data['month'] = pd.to_datetime(ref_data.index['date']).month
ref_data['month'] = pd.to_datetime(ref_data.index.get_level_values('date')).month

ref_data

# create "ref_tmp_pcp" numpy array for adjustments
ref_hist_temp = np.array(ref_data.iloc[0:, 0]).copy()
ref_hist_pcp = np.array(ref_data.iloc[0:, 1]).copy()
ref_tmp_pcp = np.column_stack((ref_hist_temp, ref_hist_pcp))

import numpy as np
import pandas as pd
from sklearn.metrics import mean_squared_error, mean_absolute_error

def adjust_temperature(predicted_temperature, ref_data, extreme_weight_t=0.01, trend_weight_t=0, monthly_weight_t=0.01):
    adjusted_temperature = []

    # Group the reference data by city
    grouped = ref_data.groupby('city')

    for city, city_data in grouped:
        # Calculate historical variability and extreme thresholds for this city
        city_temperature_std = np.std(city_data['ref_tmp'])
        temperature_threshold = np.mean(city_data['ref_tmp']) + 2.5 * city_temperature_std

        # Generate binary extreme indicators based on thresholds
        temperature_extreme_indicator = np.where(city_data['ref_tmp'] > temperature_threshold, 1, 0)

        # Generate extreme components based on the binary indicators
        temperature_extreme_component = temperature_extreme_indicator * np.random.uniform(1.5, 2.5, len(city_data))

        # Calculate the linear trend component for temperature based on historical data
        start_temperature = city_data['ref_tmp'].iloc[0]
        end_temperature = city_data['ref_tmp'].iloc[-1]
        trend_temperature = np.linspace(start_temperature, end_temperature, len(city_data))
        temperature_trend_component = trend_temperature - city_data['ref_tmp']

        # Calculate the monthly variation component for temperature based on historical data
        monthly_mean_temperature = city_data.groupby(['city', 'month'])['ref_tmp'].transform('mean')
        temperature_monthly_component = monthly_mean_temperature - city_data['ref_tmp']



        # Extract the predicted temperature for this city
        predicted_temperature_city = predicted_temperature[:len(city_data)]

        # Calculate the combined temperature components
        combined_temperature_components = (
            (extreme_weight_t * temperature_extreme_component) +
            (trend_weight_t * temperature_trend_component) +
            (monthly_weight_t * temperature_monthly_component)
        )

        # Add combined components to predicted values for this city
        adjusted_city_temperature = predicted_temperature_city + combined_temperature_components

        # Append the adjusted temperatures to the result
        adjusted_temperature.extend(adjusted_city_temperature.tolist())

        # Remove used elements from predicted_temperature
        predicted_temperature = predicted_temperature[len(city_data):]

    return np.array(adjusted_temperature)

# temp adjustment usage
adjusted_predicted_temperature = adjust_temperature(predicted_temperature, ref_data)

"""### adjusted_predicted_pcp"""

# precipitation correction
import numpy as np
import pandas as pd
from sklearn.metrics import mean_squared_error, mean_absolute_error
# Reset the index of ref_data


def adjust_precipitation(predicted_precipitation,
                         ref_data, extreme_weight_p1=8,
                         extreme_weight_p2=3,
                         extreme_weight_p3=0.6,
                         seasonal_weight_p=0.01):
    # Calculate historical variability and thresholds from reference data
    precipitation_std = np.std(ref_data['ref_pcp'])
    precipitation_threshold1 = np.mean(ref_data['ref_pcp']) + 8 * precipitation_std
    precipitation_threshold2 = np.mean(ref_data['ref_pcp']) + 4 * precipitation_std
    precipitation_threshold3 = np.mean(ref_data['ref_pcp']) + 1.5 * precipitation_std

    # Generate binary extreme indicators based on thresholds
    precipitation_extreme_indicator1 = np.where(ref_data['ref_pcp'] > precipitation_threshold1, 1, 0)
    precipitation_extreme_indicator2 = np.where(ref_data['ref_pcp'] > precipitation_threshold2, 1, 0)
    precipitation_extreme_indicator3 = np.where(ref_data['ref_pcp'] > precipitation_threshold3, 1, 0)

    # Generate extreme components based on the binary indicators
    precipitation_extreme_component1 = precipitation_extreme_indicator1 * np.random.uniform(2, 12, len(ref_data))
    precipitation_extreme_component2 = precipitation_extreme_indicator2 * np.random.uniform(2, 12, len(ref_data))
    precipitation_extreme_component3 = precipitation_extreme_indicator3 * np.random.uniform(2, 12, len(ref_data))

    # Calculate seasonal component for precipitation based on historical data

    monthly_mean_precipitation = ref_data.groupby(['city', 'month'])['ref_pcp'].transform('mean')
    precipitation_seasonal_component = monthly_mean_precipitation - ref_data['ref_pcp']

    # Calculate adjusted precipitation
    adjusted_precipitation = predicted_precipitation + (extreme_weight_p1 * precipitation_extreme_component1) + (extreme_weight_p2 * precipitation_extreme_component2) + (extreme_weight_p3 * precipitation_extreme_component3) + (seasonal_weight_p * precipitation_seasonal_component.values)

    return adjusted_precipitation



# Example usage
adjusted_predicted_precipitation = adjust_precipitation(predicted_precipitation, ref_data)

#  Series for predictions and actuals
p_preds, temp_preds = adjusted_predicted_precipitation.flatten(), adjusted_predicted_temperature.flatten()
p_actuals, temp_actuals = ref_hist_pcp.flatten(), ref_hist_temp.flatten()

# Create the DataFrame
final_df = pd.DataFrame(data={'Temperature Predictions': temp_preds,
                               'Temperature Actuals': temp_actuals,
                               'Precipitation Predictions': p_preds,
                               'Precipitation Actuals': p_actuals
                              })

# Adjust the 'Precipitation Predictions' and 'Precipitation Actuals' columns as needed
final_df['Precipitation Predictions'] = np.where(final_df['Precipitation Predictions'] < 0.6, 0, final_df['Precipitation Predictions'])
final_df['Precipitation Actuals'] = np.where(final_df['Precipitation Actuals'] < 0, 0, final_df['Precipitation Actuals'])
final_df

import matplotlib.pyplot as plt
import numpy as np
from sklearn.metrics import mean_absolute_error, r2_score, mean_squared_error

# Plot actual vs. predicted temperatures
start, end = 0, 1200000

plt.plot(final_df['Temperature Actuals'][start:end], label='Temperature_Reference')
plt.plot(final_df['Temperature Predictions'][start:end], label='Temperature_future_Predictions')

plt.xlabel('Time')
plt.ylabel('Temperature')
plt.title('Temperature_Reference vs. Temperature_future_Predictions')
plt.legend()

plt.show()

# Calculate accuracy indices for temperature predictions
actual_temps = final_df['Temperature Actuals'][start:end]
predicted_temps = final_df['Temperature Predictions'][start:end]

mae_temp = mean_absolute_error(actual_temps, predicted_temps)
r2_temp = r2_score(actual_temps, predicted_temps)
rmse_temp = np.sqrt(mean_squared_error(actual_temps, predicted_temps))
mean_percent_error_temp = np.mean(np.where(actual_temps != 0, (actual_temps - predicted_temps) / actual_temps, 0)) * 100




print(f"MAE for Temperature: {mae_temp:.2f}")
print(f"R2 Score for Temperature: {r2_temp:.2f}")
print(f"RMSE for Temperature: {rmse_temp:.2f}")
print(f"Mean Percent Error for Temperature: {mean_percent_error_temp:.2f}%")

# Plot actual vs. predicted precipitations
plt.plot(final_df['Precipitation Actuals'][start:end], label='Precipitation_Reference')
plt.plot(final_df['Precipitation Predictions'][start:end], label='Precipitation_future_Predictions')

plt.xlabel('Time')
plt.ylabel('Precipitation')
plt.title('Precipitation_Reference vs. Precipitation_future_Predictions')
plt.legend()

plt.show()

# Calculate accuracy indices for precipitation predictions
actual_precip = final_df['Precipitation Actuals'][start:end]
predicted_precip = final_df['Precipitation Predictions'][start:end]

mae_precip = mean_absolute_error(actual_precip, predicted_precip)
r2_precip = r2_score(actual_precip, predicted_precip)
rmse_precip = np.sqrt(mean_squared_error(actual_precip, predicted_precip))
nse_precip = 1 - (np.sum((actual_precip - predicted_precip)**2) / np.sum((actual_precip - np.mean(actual_precip))**2))


print(f"MAE for Precipitation: {mae_precip:.2f}")
print(f"R2 Score for Precipitation: {r2_precip:.2f}")
print(f"RMSE for Precipitation: {rmse_precip:.2f}")
print(f"Nash-Sutcliffe Efficiency for Precipitation: {nse_precip:.2f}")

"""##  Future data copies prep for trend and variability corrections"""

f_data = data.copy()
f_data = f_data.rename(columns={"time": "f_date", "tmp": "f_tmp", "pcp": "f_pcp"})

# Extract same temperature and precipitation data to be use for future
f_temp = np.array(f_data.iloc[7:, 0]).copy()
f_pcp = np.array(f_data.iloc[7:, 3]).copy()
f_tmp_pcp = np.column_stack((f_temp, f_pcp))

f_time = data.index[7:].values.copy()
# Create a dictionary to hold the arrays
data_dict_f = {
    'time': f_time,
    'Predicted_temp': f_temp,
    'Predicted_pcp': f_pcp
}

# Create a DataFrame from the dictionary
f_data_df = pd.DataFrame(data_dict_f)

"""## Model use for future data

## Preparing Future data
"""

df.head(-5)

data_for_fprep = df.copy()
data_for_fprep.reset_index(level='city', inplace=True)

data_for_fprep

import pandas as pd

# Create a date range from 2024-01-01 to 2099-12-05 with a 80-year frequency
date_range = pd.date_range(start='2024-01-01', end='2099-12-05', freq='D')

# Calculate the total number of rows in your DataFrame
num_rows = len(data_for_fprep)

# Calculate the index for each row based on modulo operation
index_mod = [i % len(date_range) for i in range(num_rows)]

# Add the "time" column to the DataFrame using the index_mod
data_for_fprep['date'] = date_range[index_mod]
# make city regular column
#data_for_fprep.reset_index(drop=True, inplace=True)

# Reset the index for the DataFrame
data_for_fprep.reset_index(drop=True, inplace=True)
data_for_fprep.set_index(['date', 'city'], inplace=True)
data_for_fprep

f_df = data_for_fprep.copy()
#data_for_fprep['Seconds'] = data_for_fprep.index.get_level_values('time').map(pd.Timestamp.timestamp)

def f_df_to_X_y(f_df, window_size=7):
  f_df_as_np = f_df.to_numpy()
  X_f = []
  y_f = []
  for i in range(len(f_df_as_np)-window_size):
    row = [r for r in f_df_as_np[i:i+window_size]]
    X_f.append(row)
    label = [f_df_as_np[i+window_size][0], f_df_as_np[i+window_size][1]]
    y_f.append(label)
  return np.array(X_f), np.array(y_f)

X_f, y_f = f_df_to_X_y(f_df)
#---------------------------------
# future data for trend and seasonality correction


#---------------------------------
# train, test and validation data split

X_f_train, y_f_train = X_f[:600000], y_f[:600000]
X_f_val, y_f_val = X_f[800000:1000000], y_f[600000:1000000]
X_f_test, y_f_test = X_f[1000000:], y_f[1000000:]

X_f_train.shape, y_f_train.shape, X_f_val.shape, y_f_val.shape, X_f_test.shape, y_f_test.shape

#---------------------------------------------
# normalization and capturing noise, seasonality and extreams

f_temp_training_mean = np.mean(X_f_train[:, :, 0])
f_temp_training_std = np.std(X_f_train[:, :, 0])
f_p_training_mean = np.mean(X_f_train[:, :, 3])
f_p_training_std = np.std(X_f_train[:, :, 3])

f_wind_training_mean = np.mean(X_f_train[:, :, 1])
f_wind_training_std = np.std(X_f_train[:, :, 1])
f_red_training_mean = np.mean(X_f_train[:, :, 2])
f_red_training_std = np.std(X_f_train[:, :, 2])


def f_preprocess(X_f):
    X_f[:, :, 0] = (X_f[:, :, 0] - f_temp_training_mean) / f_temp_training_std
    X_f[:, :, 1] = (X_f[:, :, 3] - f_p_training_mean) / f_p_training_std
    X_f[:, :, 2] = (X_f[:, :, 1] - f_wind_training_mean) / f_wind_training_std
    X_f[:, :, 3] = (X_f[:, :, 2] - f_red_training_mean) / f_red_training_std

def f_preprocess_output(y_f):
    y_f[:, 0] = (y_f[:, 0] - f_temp_training_mean) / f_temp_training_std
    y_f[:, 1] = (y_f[:, 1] - f_p_training_mean) / f_p_training_std

#------------------------------
f_preprocess(X_f_train)
f_preprocess(X_f_val)
f_preprocess(X_f_test)

#--------------------------------
f_preprocess_output(y_f_train)
f_preprocess_output(y_f_val)
f_preprocess_output(y_f_test)

# Make predictions using the loaded model
future_predicted_values = best_model.predict(X_f)

future_predicted_values

def f_postprocess_temp(arr):
  arr = (arr*temp_training_std) + temp_training_mean
  return arr

def f_postprocess_p(arr):
  arr = (arr*p_training_std) + p_training_mean
  return arr

# Extract temperature and precipitation predictions

#predicted_precipitation, predicted_temperature = postprocess_p(predicted_values[:, 1]), postprocess_temp(predicted_values[:, 0])
future_predicted_precipitation = f_postprocess_p(future_predicted_values[:, 1])
future_predicted_temperature =  f_postprocess_temp(future_predicted_values[:, 0])

reference_f = f_df.copy()
reference_f = reference_f.rename(columns={"date": "ref_time", "tmp": "ref_tmp", "pcp": "ref_pcp"})
# Set "ref_time" and "city" as the index
#reference.set_index(['city', 'ref_time'], inplace=True)

reference_f

# Keep only "ref_tmp" and "ref_pcp" columns
ref_data_f = reference_f[['ref_tmp', 'ref_pcp']]

# Drop the first 7 rows from the multi-index DataFrame
ref_data_f = ref_data_f.iloc[7:]

#Reset the index to maintain 'ref_time' and 'city' as columns
#ref_data.reset_index(inplace=True)
ref_data_f

#ref_data.head(10)
#ref_data['month'] = pd.to_datetime(ref_data.index['date']).month
ref_data_f['month'] = pd.to_datetime(ref_data_f.index.get_level_values('date')).month

ref_data_f

# create "ref_tmp_pcp" numpy array for adjustments
ref_hist_temp_f = np.array(ref_data_f.iloc[0:, 0]).copy()
ref_hist_pcp_f = np.array(ref_data_f.iloc[0:, 1]).copy()
ref_tmp_pcp_f = np.column_stack((ref_hist_temp_f, ref_hist_pcp_f))

"""# Temperation adjustments"""

import numpy as np
import pandas as pd
from sklearn.metrics import mean_squared_error, mean_absolute_error

def adjust_temperature(future_predicted_temperature, ref_data_f, extreme_weight_t=1, trend_weight_t=0.1, monthly_weight_t=1):
    adjusted_temperature = []

    # Group the reference data by city
    grouped = ref_data_f.groupby('city')

    for city, city_data in grouped:
        # Calculate historical variability and extreme thresholds for this city
        city_temperature_std = np.std(city_data['ref_tmp'])
        temperature_threshold = np.mean(city_data['ref_tmp']) + 2.5 * city_temperature_std

        # Generate binary extreme indicators based on thresholds
        temperature_extreme_indicator = np.where(city_data['ref_tmp'] > temperature_threshold, 1, 0)

        # Generate extreme components based on the binary indicators
        temperature_extreme_component = temperature_extreme_indicator * np.random.uniform(1.5, 2.5, len(city_data))

        # Calculate the linear trend component for temperature based on historical data
        start_temperature = city_data['ref_tmp'].iloc[0]
        end_temperature = city_data['ref_tmp'].iloc[-1]
        trend_temperature = np.linspace(start_temperature, end_temperature, len(city_data))
        temperature_trend_component = trend_temperature - city_data['ref_tmp']

        # Calculate the monthly variation component for temperature based on historical data
        monthly_mean_temperature = city_data.groupby(['city', 'month'])['ref_tmp'].transform('mean')
        temperature_monthly_component = monthly_mean_temperature - city_data['ref_tmp']



        # Extract the predicted temperature for this city
        predicted_temperature_city = future_predicted_temperature[:len(city_data)]

        # Calculate the combined temperature components
        combined_temperature_components = (
            (extreme_weight_t * temperature_extreme_component) +
            (trend_weight_t * temperature_trend_component) +
            (monthly_weight_t * temperature_monthly_component)
        )

        # Add combined components to predicted values for this city
        adjusted_city_temperature = predicted_temperature_city + combined_temperature_components

        # Append the adjusted temperatures to the result
        adjusted_temperature.extend(adjusted_city_temperature.tolist())

        # Remove used elements from predicted_temperature
        future_predicted_temperature = future_predicted_temperature[len(city_data):]

    return np.array(adjusted_temperature)

# temp adjustment usage
final_future_pred_tmp = adjust_temperature(future_predicted_temperature, ref_data_f)

final_future_pred_tmp

"""### adjusted_predicted_pcp"""

# precipitation correction
import numpy as np
import pandas as pd
from sklearn.metrics import mean_squared_error, mean_absolute_error
# Reset the index of ref_data


def adjust_future_predictions(future_predicted_precipitation,
                         ref_data, extreme_weight_p1=8,
                         extreme_weight_p2=3,
                         extreme_weight_p3=0.6,
                         seasonal_weight_p=0.01):
    # Calculate historical variability and thresholds from reference data
    precipitation_std = np.std(ref_data_f['ref_pcp'])
    precipitation_threshold1 = np.mean(ref_data_f['ref_pcp']) + 8 * precipitation_std
    precipitation_threshold2 = np.mean(ref_data_f['ref_pcp']) + 4 * precipitation_std
    precipitation_threshold3 = np.mean(ref_data_f['ref_pcp']) + 1.5 * precipitation_std

    # Generate binary extreme indicators based on thresholds
    precipitation_extreme_indicator1 = np.where(ref_data_f['ref_pcp'] > precipitation_threshold1, 1, 0)
    precipitation_extreme_indicator2 = np.where(ref_data_f['ref_pcp'] > precipitation_threshold2, 1, 0)
    precipitation_extreme_indicator3 = np.where(ref_data_f['ref_pcp'] > precipitation_threshold3, 1, 0)

    # Generate extreme components based on the binary indicators
    precipitation_extreme_component1 = precipitation_extreme_indicator1 * np.random.uniform(2, 12, len(ref_data))
    precipitation_extreme_component2 = precipitation_extreme_indicator2 * np.random.uniform(2, 12, len(ref_data))
    precipitation_extreme_component3 = precipitation_extreme_indicator3 * np.random.uniform(2, 12, len(ref_data))

    # Calculate seasonal component for precipitation based on historical data

    monthly_mean_precipitation = ref_data_f.groupby(['city', 'month'])['ref_pcp'].transform('mean')
    precipitation_seasonal_component = monthly_mean_precipitation - ref_data_f['ref_pcp']

    # Calculate adjusted precipitation
    adjusted_precipitation = future_predicted_precipitation + (extreme_weight_p1 * precipitation_extreme_component1) + (extreme_weight_p2 * precipitation_extreme_component2) + (extreme_weight_p3 * precipitation_extreme_component3) + (seasonal_weight_p * precipitation_seasonal_component.values)

    return adjusted_precipitation



# usage
final_future_pred_pcp = adjust_future_predictions(future_predicted_precipitation, ref_data_f)

final_future_df = ref_data_f.copy()

# Assign temp_preds to the 'Predicted_temp' column
final_future_df['future_tmp'] = final_future_pred_tmp.round(1)

# Assign p_preds to the 'Predicted_pcp' column
final_future_df['future_pcp'] = final_future_pred_pcp.round(1)

final_future_df = final_future_df.drop(['month'], axis=1)
final_future_df

# Replace precipitation values less than 0.5 with 0
final_future_df['future_pcp'] = np.where(final_future_df['future_pcp'] < 0.8, 0, final_future_df['future_pcp'])
final_future_df['ref_pcp'] = np.where(final_future_df['ref_pcp'] < 0.1, 0, final_future_df['ref_pcp'])

'''
# Specify the path where you want to save the CSV file
csv_file_path = 'your future file path and name.csv'

# Save the DataFrame to a CSV file
final_future_df.to_csv(csv_file_path, index=False)  # Set index=False if you don't want to save the index column
'''

import matplotlib.pyplot as plt
import numpy as np
from sklearn.metrics import mean_absolute_error, r2_score, mean_squared_error

# Reset the index of your DataFrame
final_future_df.reset_index(drop=True, inplace=True)

# Plot actual vs. predicted temperatures
start, end = 0, 120000

plt.plot(final_future_df.index[start:end], final_future_df['ref_tmp'][start:end], label='Temperature_Reference')
plt.plot(final_future_df.index[start:end], final_future_df['future_tmp'][start:end], label='Temperature_future_Predictions')


plt.xlabel('Time')
plt.ylabel('Temperature')
plt.title('Temperature_Reference vs. Temperature_future_Predictions')
plt.legend()

plt.show()

# Calculate accuracy indices for temperature predictions
actual_temps = final_future_df['ref_tmp'][start:end]
predicted_temps = final_future_df['future_tmp'][start:end]

mae_temp = mean_absolute_error(actual_temps, predicted_temps)
r2_temp = r2_score(actual_temps, predicted_temps)
rmse_temp = np.sqrt(mean_squared_error(actual_temps, predicted_temps))
mean_percent_error_temp = np.mean(np.where(actual_temps != 0, (actual_temps - predicted_temps) / actual_temps, 0)) * 100


print(f"MAE for Temperature: {mae_temp:.2f}")
print(f"R2 Score for Temperature: {r2_temp:.2f}")
print(f"RMSE for Temperature: {rmse_temp:.2f}")
print(f"Mean Percent Error for Temperature: {mean_percent_error_temp:.2f}%")

# Plot actual vs. predicted precipitations
plt.plot(final_future_df['ref_pcp'][start:end], label='Precipitation_Reference')
plt.plot(final_future_df['future_pcp'][start:end], label='Precipitation_future_Predictions')

plt.xlabel('Time')
plt.ylabel('Precipitation')
plt.title('Precipitation_Reference vs. Precipitation_future_Predictions')
plt.legend()

plt.show()

# Calculate accuracy indices for precipitation predictions
actual_precip = final_future_df['ref_pcp'][start:end]
predicted_precip = final_future_df['future_pcp'][start:end]

mae_precip = mean_absolute_error(actual_precip, predicted_precip)
r2_precip = r2_score(actual_precip, predicted_precip)
rmse_precip = np.sqrt(mean_squared_error(actual_precip, predicted_precip))
nse_precip = 1 - (np.sum((actual_precip - predicted_precip)**2) / np.sum((actual_precip - np.mean(actual_precip))**2))


print(f"MAE for Precipitation: {mae_precip:.2f}")
print(f"R2 Score for Precipitation: {r2_precip:.2f}")
print(f"RMSE for Precipitation: {rmse_precip:.2f}")
print(f"Nash-Sutcliffe Efficiency for Precipitation: {nse_precip:.2f}")