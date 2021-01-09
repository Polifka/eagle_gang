import pandas as pd
from haversine import haversine, Unit

# define readin functions
def trip_data_readin(city):
    trip_data = pd.read_csv("../Project_Data/Trip_Data/" + city + ".csv", encoding="ISO-8859-1")
    trip_data = trip_data_data_prep(trip_data)
    trip_data = merge_trip_data_with_weather_data(trip_data, city)
    return trip_data


def trip_data_data_prep(trip_data):
    trip_data["datetime_start"] = pd.to_datetime(trip_data['day'] + ' ' + trip_data['time'])
    trip_data["trip_duration"] = pd.to_timedelta(trip_data["trip_duration"])
    trip_data["datetime_end"] = trip_data["datetime_start"] + trip_data["trip_duration"]
    trip_data["weekday"] = pd.to_datetime(trip_data["datetime_start"]).dt.weekday
    trip_data["month"] = trip_data["datetime_start"].dt.month
    trip_data["hour"] = trip_data["datetime_start"].dt.hour

    trip_data = distance_between_coordinates(trip_data)
    return trip_data


def distance_between_coordinates(trip_data):
    trip_data["distance"] = trip_data.apply(
        lambda row: haversine((row["orig_lat"], row["orig_lng"]), (row["dest_lat"], row["dest_lng"]), Unit.KILOMETERS),
        axis=1)
    return trip_data


def merge_trip_data_with_weather_data(trip_data, city):
    trip_data.set_index(pd.DatetimeIndex(trip_data["datetime_start"]), inplace=True)
    weather = read_DWD_data(city)
    trip_data["rounded_time_hourly"] = trip_data["datetime_start"].dt.round("H")
    combined = pd.merge(trip_data, weather, on="rounded_time_hourly", how='left')
    combined["wind"] = combined['wind'].fillna(method="ffill")
    combined["rain"] = combined['rain'].fillna(method="ffill")
    combined["temp"] = combined['temp'].fillna(method="ffill")
    return combined


def read_DWD_data(city):
    temp_data = pd.read_csv("../Project_Data/Weather_Data/" + city + "/" + "data_TT_TU_MN009.csv", encoding="ISO-8859-1")
    temp_data = temp_data.rename(columns={"Zeitstempel": "rounded_time_hourly"})
    temp_data.set_index((pd.to_datetime(temp_data['rounded_time_hourly'].astype(str), format='%Y%m%d%H%M')),
                        inplace=True)
    temp_data = temp_data.drop(
        ['Produkt_Code', 'SDO_ID', 'SDO_ID', 'Qualitaet_Niveau', 'Qualitaet_Byte', 'rounded_time_hourly'], axis=1)
    temp_data.columns = ['temp']

    wind_data = pd.read_csv("../Project_Data/Weather_Data/" + city + "/" + "data_F_MN003.csv", encoding="ISO-8859-1")
    wind_data = wind_data.rename(columns={"Zeitstempel": "rounded_time_hourly"})
    wind_data.set_index((pd.to_datetime(wind_data['rounded_time_hourly'].astype(str), format='%Y%m%d%H%M')),
                        inplace=True)
    wind_data = wind_data.drop(
        ['Produkt_Code', 'SDO_ID', 'SDO_ID', 'Qualitaet_Niveau', 'Qualitaet_Byte', 'rounded_time_hourly'], axis=1)
    wind_data.columns = ['wind']

    rain_data = pd.read_csv("../Project_Data/Weather_Data/" + city + "/" + "data_R1_MN008.csv", encoding="ISO-8859-1")
    rain_data = rain_data.rename(columns={"Zeitstempel": "rounded_time_hourly"})
    rain_data.set_index((pd.to_datetime(rain_data['rounded_time_hourly'].astype(str), format='%Y%m%d%H%M')),
                        inplace=True)
    rain_data = rain_data.drop(
        ['Produkt_Code', 'SDO_ID', 'SDO_ID', 'Qualitaet_Niveau', 'Qualitaet_Byte', 'rounded_time_hourly'], axis=1)
    rain_data.columns = ['rain']

    weather = pd.merge(temp_data, wind_data, on="rounded_time_hourly", how='left')
    weather = pd.merge(weather, rain_data, on="rounded_time_hourly", how='left')
    return weather


# create combined dataSet
def export(city_name):
    data_set = trip_data_readin(city_name)
    data_set.to_csv("../Project_Data/Combined_Data/" + city_name + ".csv")

def round_to_nearest(x, base=5):
    '''
    Rounds a value to the nearest base step, per default base=5
    :param x: the value to round
    :param base: the number, to which is rounded (e.g. 12 is rounded down to 10, 13 is rounded up to 15)
    :return: an integer whose value is the rounded value of the param value
    '''
    return int(base * round(float(x)/base))