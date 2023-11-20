from datetime import timedelta
import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

from models.f1_simulation import F1Simulation
from f1_env.f1_env import F1Env

class F1SimVisualization:
    def __init__(self,f1_simulation:F1Simulation|F1Env):
        self.f1_simulation=f1_simulation

    def plot_tyre_sequence(self, filepath:str):
        list_dict_sequences=list()
        latest_tyre=self.f1_simulation.list_tyre_setting_all_laps[0]
        latest_tyre_start=0

        cm={
            'Soft':'#ED1C24',
            'Medium':'#FEC706',
            'Hard':'White'
        }

        for i in range(len(self.f1_simulation.list_car_status_will_be_pit)):
            if self.f1_simulation.list_car_status_will_be_pit[i]==True:
                list_dict_sequences.append(dict(Driver='Sim',Start=latest_tyre_start,Finish=i+1,Resource=latest_tyre,tyre_color=cm[latest_tyre],Laps=i+1-latest_tyre_start))
                latest_tyre=self.f1_simulation.list_tyre_setting_all_laps[i+1]
                latest_tyre_start=i+1
        list_dict_sequences.append(dict(Driver='Sim',Start=latest_tyre_start,Finish=self.f1_simulation.number_of_laps,Resource=latest_tyre,tyre_color=cm[latest_tyre], Laps=self.f1_simulation.number_of_laps-latest_tyre_start))

        # df_sequences=pd.DataFrame(list_dict_sequences)
        # df_sequences['Laps']=df_sequences['Finish']-df_sequences['Start']

        # fig=px.bar(data_frame=df_sequences,x='Laps',y='Driver',color='Resource',color_discrete_map=cm, labels={'Resource':'Tyre Compound'}, title='Tyre Sequence for this race', orientation='h')
        # fig.update_traces(marker=dict(
        #     line=dict(
        #         color='black'
        #     )
        # ))
        # fig.update_layout(
        #     plot_bgcolor='#DDDDDD',
        #     legend=dict(
        #         orientation="h",
        #     )
        # )
        # fig=go.Figure()
        bar_traces=[
            go.Bar(
                name=dict_sequence['Resource'],
                x=[dict_sequence['Laps']],y=[dict_sequence['Driver']],orientation='h',base=dict_sequence['Start'],marker_color=dict_sequence['tyre_color'],marker_line_color='black',marker_line_width=2, showlegend=True
            )
            for dict_sequence in list_dict_sequences
        ]
        layout = go.Layout(showlegend=True,barmode='stack')
        fig = go.Figure(data=bar_traces, layout=layout)
        fig.update_layout(
            plot_bgcolor='#DDDDDD',
            xaxis_title='Laps'
        )
        names = set()
        fig.for_each_trace(
            lambda trace:
                trace.update(showlegend=False)
                if (trace.name in names) else names.add(trace.name)
        )
        # fig.add_trace(
        #     go.Bar(x=df_sequences['Laps'],y=df_sequences['Driver'],orientation='h',base=df_sequences['Start'],meta=df_sequences['Resource'],marker_color=df_sequences['tyre_color'],marker_line_color='black',showlegend=True)
        # )
        fig.write_image(filepath,width=1600, height=900)

    def plot_car_speed(self,filepath:str):
        fig=px.line(self.f1_simulation.list_car_speed_all_stopwatches,title='Car Speed for all stopwatch in this race')
        fig.update_layout(
            xaxis_title='number of stopwatch for all laps',
            yaxis_title='Speed (km/hr)',
            showlegend=False
        )
        temp_max_speed=max(self.f1_simulation.list_car_speed_all_stopwatches)
        temp_max_speed_idx=self.f1_simulation.list_car_speed_all_stopwatches.index(temp_max_speed)
        fig.add_annotation(text=f"Max Speed: lap {temp_max_speed_idx//self.f1_simulation.racetrack.num_stopwatch+1} at {temp_max_speed:.2f} km/hr",xref="paper", yref="paper",x=1, y=-0.075, showarrow=False, font=dict(color='red'))
        fig.write_image(filepath,width=1600, height=900)

    def plot_laptime_all_stopwatch(self,filepath:str):
        fig=px.line(self.f1_simulation.list_time_usage_all_stopwatches,title='Laptime for all stopwatch in this race')
        fig.update_layout(
            xaxis_title='number of stopwatch for all laps',
            yaxis_title='Duration at stopwatch (seconds)',
            showlegend=False
        )
        # calculate elapsed seconds for each lap
        temp_list_time_elapsed_lap=[0]*self.f1_simulation.number_of_laps
        for i in range(self.f1_simulation.number_of_laps):
            for j in range(self.f1_simulation.racetrack.num_stopwatch):
                temp_list_time_elapsed_lap[i]+=self.f1_simulation.list_time_usage_all_stopwatches[self.f1_simulation.racetrack.num_stopwatch*i+j]
        temp_min_laptime=min(temp_list_time_elapsed_lap)
        temp_min_laptime_idx=temp_list_time_elapsed_lap.index(temp_min_laptime)
        fig.add_annotation(text=f"Fastest Lap: lap {temp_min_laptime_idx+1} at {timedelta(seconds=temp_min_laptime)}",xref="paper", yref="paper",x=1, y=-0.06, showarrow=False, font=dict(color='red'))
        fig.add_annotation(text=f"Time Elapesed: {timedelta(seconds=sum(self.f1_simulation.list_time_usage_all_stopwatches))}",xref="paper", yref="paper",x=1, y=-0.08, showarrow=False, font=dict(color='red'))
        fig.write_image(filepath,width=1600, height=900)

    def plot_engine_horsepower_all_stopwatch(self,filepath:str):
        fig=px.line(self.f1_simulation.list_engine_horsepower_all_stopwatches,title='Engine Horsepower for all stopwatch in this race')
        fig.update_layout(
            xaxis_title='number of stopwatch for all laps',
            yaxis_title='Engine Horsepower (HP)',
            showlegend=False
        )
        temp_max_engine_horsepower=max(self.f1_simulation.list_engine_horsepower_all_stopwatches)
        temp_max_engine_horsepower_idx=self.f1_simulation.list_engine_horsepower_all_stopwatches.index(temp_max_engine_horsepower)
        fig.add_annotation(text=f"Most Horsepower: lap {temp_max_engine_horsepower_idx//self.f1_simulation.racetrack.num_stopwatch+1} at {temp_max_engine_horsepower}",xref="paper", yref="paper",x=1, y=-0.075, showarrow=False, font=dict(color='red'))
        fig.write_image(filepath,width=1600, height=900)

    def plot_engine_reliability_all_stopwatch(self,filepath:str):
        fig=px.line(self.f1_simulation.list_engine_reliability_all_stopwatches,title='Engine Reliability for all stopwatch in this race')
        fig.update_layout(
            xaxis_title='number of stopwatch for all laps',
            yaxis_title='Engine Reliability (Percent)',
            showlegend=False
        )
        fig.write_image(filepath,width=1600, height=900)

    def plot_fuel_level_all_stopwatch(self,filepath:str):
        fig=px.line(self.f1_simulation.list_engine_fuel_level_all_stopwatches,title='Engine Fuel Level for all stopwatch in this race')
        fig.update_layout(
            xaxis_title='number of stopwatch for all laps',
            yaxis_title='Engine Fuel Level (kg)',
            showlegend=False
        )
        fig.write_image(filepath,width=1600, height=900)

    def plot_engine_temperature_all_stopwatch(self,filepath:str):
        fig=px.line(self.f1_simulation.list_engine_temperature_all_stopwatches,title='Engine Temperature for all stopwatch in this race')
        fig.update_layout(
            xaxis_title='number of stopwatch for all laps',
            yaxis_title='Engine Temperature (Celcius)',
            showlegend=False
        )
        fig.write_image(filepath,width=1600, height=900)

    def plot_brake_pressure_all_stopwatch(self,filepath:str):
        fig=px.line(self.f1_simulation.list_brake_pressure_all_stopwatches,title='Brake Pressure for all stopwatch in this race')
        fig.update_layout(
            xaxis_title='number of stopwatch for all laps',
            yaxis_title='Brake Pressure (psi)',
            showlegend=False
        )
        fig.write_image(filepath,width=1600, height=900)

    def plot_brake_reliability_all_stopwatch(self,filepath:str):
        fig=px.line(self.f1_simulation.list_brake_reliability_all_stopwatches,title='Brake Reliability for all stopwatch in this race')
        fig.update_layout(
            xaxis_title='number of stopwatch for all laps',
            yaxis_title='Brake Reliability (Percent)',
            showlegend=False
        )
        fig.write_image(filepath,width=1600, height=900)

    def plot_brake_temperature_all_stopwatch(self,filepath:str):
        fig=px.line(self.f1_simulation.list_brake_temperature_all_stopwatches,title='Brake Temperature for all stopwatch in this race')
        fig.update_layout(
            xaxis_title='number of stopwatch for all laps',
            yaxis_title='Brake Temperature (Celcius)',
            showlegend=False
        )
        fig.write_image(filepath,width=1600, height=900)

    def plot_tyre_reliability_all_stopwatch(self,filepath:str):
        fig=px.line(self.f1_simulation.list_tyre_reliability_all_stopwatches,title='Tyre Reliability for all stopwatch in this race')
        fig.update_layout(
            xaxis_title='number of stopwatch for all laps',
            yaxis_title='Tyre Reliability (Percent)',
            showlegend=False
        )
        fig.write_image(filepath,width=1600, height=900)

    def plot_tyre_temperature_all_stopwatch(self,filepath:str):
        fig=px.line(self.f1_simulation.list_tyre_temperature_all_stopwatches,title='Tyre Temperature for all stopwatch in this race')
        fig.update_layout(
            xaxis_title='number of stopwatch for all laps',
            yaxis_title='Tyre Temperature (Celcius)',
            showlegend=False
        )
        fig.write_image(filepath,width=1600, height=900)

    def plot_engine_setting_all_stopwatch(self, filepath:str):
        list_lap_idx=list()
        for i in range(self.f1_simulation.number_of_laps):
            list_lap_idx+=[i]*self.f1_simulation.racetrack.num_stopwatch
        dict_data={
            'lap_idx':list_lap_idx,
            'stopwatch_idx':list(range(self.f1_simulation.racetrack.num_stopwatch))*self.f1_simulation.number_of_laps,
            'engine_setting':self.f1_simulation.list_engine_setting_all_stopwatches
        }
        df=pd.DataFrame.from_dict(dict_data)
        list_lap_engine_idx=list()
        for i in range(self.f1_simulation.number_of_laps):
            list_lap_engine_idx+=[i]*len(self.f1_simulation.car.engine.list_engine_mode_name)
        template_df=pd.DataFrame.from_dict({'lap_idx':list_lap_engine_idx,'engine_setting':self.f1_simulation.car.engine.list_engine_mode_name*self.f1_simulation.number_of_laps})
        merged_df=df.groupby(['lap_idx','engine_setting']).agg({'engine_setting':'count'}).rename(columns={'engine_setting':'count_engine_setting'}).reset_index()
        template_merged_df=template_df.merge(merged_df,how='left').fillna(0)
        final_df=template_merged_df.pivot_table(index='engine_setting',columns='lap_idx',values='count_engine_setting').reindex(self.f1_simulation.car.engine.list_engine_mode_name[::-1])/self.f1_simulation.racetrack.num_stopwatch
        fig=go.Figure(data=go.Heatmap(
            z=final_df,x=list(range(self.f1_simulation.number_of_laps)),y=self.f1_simulation.car.engine.list_engine_mode_name[::-1],colorscale='Oranges',zmin=0,zmax=1,xgap=1,ygap=1,colorbar={"title": '% Utilization'}
        ))
        fig.update_xaxes(type='category',gridcolor='black',tickson='boundaries',linewidth=2)
        fig.update_yaxes(type='category',gridcolor='black',tickson='boundaries',linewidth=2)
        fig.update_traces(colorbar_orientation='h')
        fig.update_layout(
            xaxis_title='laps',
            yaxis_title='Engine Mode',
            title='Engine mode utilization ratio'
        )
        fig.write_image(filepath,width=1600, height=900, scale=3)

    def plot_brake_setting_all_stopwatch(self, filepath:str):
        list_lap_idx=list()
        for i in range(self.f1_simulation.number_of_laps):
            list_lap_idx+=[i]*self.f1_simulation.racetrack.num_stopwatch
        dict_data={
            'lap_idx':list_lap_idx,
            'stopwatch_idx':list(range(self.f1_simulation.racetrack.num_stopwatch))*self.f1_simulation.number_of_laps,
            'brake_setting':self.f1_simulation.list_brake_setting_all_stopwatches
        }
        df=pd.DataFrame.from_dict(dict_data)
        list_lap_brake_idx=list()
        for i in range(self.f1_simulation.number_of_laps):
            list_lap_brake_idx+=[i]*len(self.f1_simulation.car.brakes.list_brake_mode_name)
        template_df=pd.DataFrame.from_dict({'lap_idx':list_lap_brake_idx,'brake_setting':self.f1_simulation.car.brakes.list_brake_mode_name*self.f1_simulation.number_of_laps})
        merged_df=df.groupby(['lap_idx','brake_setting']).agg({'brake_setting':'count'}).rename(columns={'brake_setting':'count_brake_setting'}).reset_index()
        template_merged_df=template_df.merge(merged_df,how='left').fillna(0)
        final_df=template_merged_df.pivot_table(index='brake_setting',columns='lap_idx',values='count_brake_setting').reindex(self.f1_simulation.car.brakes.list_brake_mode_name[::-1])/self.f1_simulation.racetrack.num_stopwatch
        fig=go.Figure(data=go.Heatmap(
            z=final_df,x=list(range(self.f1_simulation.number_of_laps)),y=self.f1_simulation.car.brakes.list_brake_mode_name[::-1],colorscale='Oranges',zmin=0,zmax=1,xgap=1,ygap=1,colorbar={"title": '% Utilization'}
        ))
        fig.update_xaxes(type='category',gridcolor='black',tickson='boundaries',linewidth=2)
        fig.update_yaxes(type='category',gridcolor='black',tickson='boundaries',linewidth=2)
        fig.update_traces(colorbar_orientation='h')
        fig.update_layout(
            xaxis_title='laps',
            yaxis_title='Brake Mode',
            title='Brake mode utilization ratio'
        )
        fig.write_image(filepath,width=1600, height=900, scale=3)

    def plot_package(self,folderpath:str):
        self.plot_tyre_sequence(folderpath+'/tyre_sequence.png')
        self.plot_car_speed(folderpath+'/car_speed.png')
        self.plot_laptime_all_stopwatch(folderpath+'/laptime_all_stopwatch.png')
        self.plot_engine_horsepower_all_stopwatch(folderpath+"/engine_horsepower_all_stopwatch.png")
        self.plot_engine_reliability_all_stopwatch(folderpath+"/engine_reliability_all_stopwatch.png")
        self.plot_fuel_level_all_stopwatch(folderpath+"/engine_fuel_level_all_stopwatch.png")
        self.plot_engine_temperature_all_stopwatch(folderpath+"/engine_temperature_all_stopwatch.png")
        self.plot_brake_pressure_all_stopwatch(folderpath+"/brake_pressure_all_stopwatch.png")
        self.plot_brake_reliability_all_stopwatch(folderpath+"/brake_reliability_all_stopwatch.png")
        self.plot_brake_temperature_all_stopwatch(folderpath+"/brake_temperature_all_stopwatch.png")
        self.plot_tyre_reliability_all_stopwatch(folderpath+"/tyre_reliability_all_stopwatch.png")
        self.plot_tyre_temperature_all_stopwatch(folderpath+"/tyre_temperature_all_stopwatch.png")
        self.plot_engine_setting_all_stopwatch(folderpath+"/engine_setting_all_stopwatch.png")
        self.plot_brake_setting_all_stopwatch(folderpath+"/brake_setting_all_stopwatch.png")