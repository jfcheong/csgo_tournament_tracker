import streamlit as st
import pandas as pd
# Import classes using precise module indications. For example:
from highcharts_core.chart import Chart
from highcharts_core.global_options.shared_options import SharedOptions
from highcharts_core.options import HighchartsOptions
from highcharts_core.options.plot_options.bar import BarOptions
from highcharts_core.options.series.bar import BarSeries
import streamlit as st
import streamlit_highcharts as hct

st.title("Home Page")


chart_def={
   "title":{
      "text":"Sales of petroleum products March, Norway",
      "align":"left"
   },
   "xAxis":{
      "categories":["Jet fuel","Duty-free diesel"]
   },
   "yAxis":{
      "title":{"text":"Million liter"}
   },
   "series":[
        {"type":"column",
            "name":"2020",
            "data":[59,83]},
        {"type":"column",
            "name":"2021",
            "data":[24,79]
        },
        {"type":"column",
            "name":"2022",
            "data":[58,88]
        },
        {"type":"spline",
            "name":"Average",
            "data":[47,83.33],
            "marker":{
                "lineWidth":2,
                "fillColor":"black",
            }
        }
    ]
}

hct.streamlit_highcharts(chart_def,640)
