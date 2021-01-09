# importing all relevant libraries

import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import math
from datetime import datetime
from matplotlib.dates import date2num

from Project import trip_data_readin

# set seaborn styles
sns.set()
sns.set_style("whitegrid")
sns.set_palette("pastel")

# set pandas display styles
pd.set_option('display.max_columns', 20)
pd.set_option('display.width', 2000)

#
# TASK: CALCULATE REVENUE PER BIKE FOR BOTH CITIES BREMEN AND DÜSSELDORF
#       CALCULATE KPI HOURLY, VISUALIZE OVER TIME (DAY, WEEK, MONTH)
#

def generate_plot_revenue_per_hour_for_city(city, start_date, end_date, time_interval):
    '''
    Generates plots of revenue per hour, summed, and revenue per hour, on average,
    for a given city and time frame. For each city 4 plots are generated, 2 of those scatter plots
    and 2 line plots, plotting both KPI's, respectively.

    :param city: a city in string format, e.g. "Bremen" or "Duesseldorf"
    :param start_date: an iso format time string, e.g. "2019-03-28 12:00:00"
    :param end_date: an iso format time string, e.g. "2019-03-31 12:00:00"
    :param time_interval: a string defining the length of time interval (used for plot titles)
    '''

    # sorting and key stats of data
    trip_data_br = trip_data_readin(city)
    trip_data_br_sorted = trip_data_br.sort_values(by=['day'], axis=0)

    # count trip duration intervals for each trip, i.e. how much revenue each trip generated,
    # by setting the revenue to 1 plus the number of 30-minute durations fitting into the trip duration
    trip_data_br_sorted["revenue_per_trip"] = trip_data_br_sorted["trip_duration"].apply(
        lambda x: float((math.floor(x / pd.Timedelta(minutes=30))) + 1))
    print("Added Revenue per trip: \n\n", trip_data_br_sorted.head(10))

    # SET TIME WINDOW FOR HOURLY GROUPING OF VALUES
    startDate = datetime.fromisoformat(start_date)
    endDate = datetime.fromisoformat(end_date)

    # select rows in the given time window
    mask = (trip_data_br_sorted["datetime_start"] > startDate) & (trip_data_br_sorted["datetime_start"] <= endDate)
    trip_data_br_sorted_time_framed = trip_data_br_sorted.loc[mask]

    # Group data in the given time window by hours and aggregate the revenue per trip:
    # as sum over all rented bikes in a specific hour, and as average over all rented bikes in a specific hour
    times = pd.DatetimeIndex(trip_data_br_sorted_time_framed.datetime_start)
    groupedByHours = trip_data_br_sorted_time_framed.groupby([times.month, times.day, times.hour])[
        "revenue_per_trip"].agg(num_of_trips_per_hour="count", revenue_per_hour_sum="sum", revenue_per_hour_avg="mean")

    # reset index to get time labels as column labels
    groupedByHours.index.rename(["month", "day", "hour"], inplace=True)
    groupedByHours.reset_index(inplace=True)

    # generate date column for plot labelling
    groupedByHours["date"] = "2019-" + groupedByHours["month"].astype(str) + "-" +  groupedByHours["day"].astype(str) + " " + \
                             groupedByHours["hour"].astype(str) + ":00:00"

    # generate datetime column for checking of weekdays
    groupedByHours["datetime"] = [pd.to_datetime(d) for d in groupedByHours.date]

    # check, if date is weekday (.weekday() returns 0 for a monday, and 6 for a sunday)
    groupedByHours["is_weekday"] = [dt.weekday() <= 4 for dt in groupedByHours.datetime]

    # GROUPING AND VISUALIZATION
    print("Grouped by hours: \n\n", groupedByHours.head(20))
    print(groupedByHours.info())

    # create figure and axes
    fig1, (ax1, ax2) = plt.subplots(nrows=1, ncols=2, figsize=(20, 10))
    plt.rcParams["font.size"] = 2

    # generate scatter plots
    plot1 = sns.scatterplot(ax=ax1, data=groupedByHours, x="date", y="revenue_per_hour_sum", hue="is_weekday", ci=None)
    plot2 = sns.scatterplot(ax=ax2, data=groupedByHours, x="date", y="revenue_per_hour_avg", hue="is_weekday", ci=None)

    # set tick and label options
    ax1.tick_params(labelrotation=90)
    ax2.tick_params(labelrotation=90)
    plt.setp(plot1.axes.get_xticklabels()[::2], visible=False)
    plt.setp(plot2.axes.get_xticklabels()[::2], visible=False)
    ax1.set_title(f"Revenue/hour from {startDate} to {endDate} ({time_interval})")
    ax2.set_title(f"Revenue/hour from {startDate} to {endDate} ({time_interval})")

    fig1.subplots_adjust(left=0.05, right=0.98, top=0.98, bottom=0.25)

    # create figure and axes
    fig2, (ax3, ax4) = plt.subplots(nrows=1, ncols=2, figsize=(20, 10))

    # generate line plots
    plot3 = sns.lineplot(ax=ax3, data=groupedByHours, x="date", y="revenue_per_hour_sum", hue="is_weekday", ci=None)
    plot4 = sns.lineplot(ax=ax4, data=groupedByHours, x="date", y="revenue_per_hour_avg", hue="is_weekday", ci=None)

    # set tick and label options
    ax3.tick_params(labelrotation=90)
    ax4.tick_params(labelrotation=90)
    plt.setp(plot3.axes.get_xticklabels()[::2], visible=False)
    plt.setp(plot4.axes.get_xticklabels()[::2], visible=False)
    ax3.set_title(f"Revenue/hour from {startDate} to {endDate} ({time_interval})")
    ax4.set_title(f"Revenue/hour from {startDate} to {endDate} ({time_interval})")

    fig2.subplots_adjust(left=0.05, right=0.98, top=0.98, bottom=0.25)

# generate plots for both cities
cities = ["Bremen", "Duesseldorf"]
for city in cities:
    generate_plot_revenue_per_hour_for_city(city, "2019-02-01 00:00:00", "2019-02-02 23:59:00", "day")
    generate_plot_revenue_per_hour_for_city(city, "2019-02-01 00:00:00", "2019-02-08 23:59:00", "week")
    generate_plot_revenue_per_hour_for_city(city, "2019-02-01 00:00:00", "2019-02-28 23:59:00", "month")

plt.legend()
plt.show()