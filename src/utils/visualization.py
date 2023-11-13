import numpy as np
import pandas as pd
import plotly.express as px

from models.f1_simulation import F1Simulation

class F1SimVisualization:
    def __init__(self,f1_simulation:F1Simulation):
        self.f1_simulation=f1_simulation

    def plot_tyre_sequence(self, filepath:str):
        list_dict_sequences=list()
        latest_tyre=self.f1_simulation.list_tyre_setting_all_laps[0]
        latest_tyre_start=0
        for i in range(len(self.f1_simulation.list_car_status_will_be_pit)):
            if self.f1_simulation.list_car_status_will_be_pit[i]==True:
                list_dict_sequences.append(dict(Driver='Sim',Start=latest_tyre_start+1,Finish=i+1,Resource=latest_tyre))
                latest_tyre=self.f1_simulation.list_tyre_setting_all_laps[i+1]
                latest_tyre_start=i
        list_dict_sequences.append(dict(Driver='Sim',Start=latest_tyre_start+1,Finish=self.f1_simulation.number_of_laps,Resource=latest_tyre))

        df_sequences=pd.DataFrame(list_dict_sequences)
        df_sequences['Laps']=df_sequences['Finish']-df_sequences['Start']

        cm={
            'Soft':'#ED1C24',
            'Medium':'#FEC706',
            'Hard':'White'
        }

        fig=px.bar(data_frame=df_sequences,x='Laps',y='Driver',color='Resource',color_discrete_map=cm, labels={'Resource':'Tyre Compound'})
        fig.update_traces(marker=dict(
            line=dict(
                color='black'
            )
        ))
        fig.update_layout(
            plot_bgcolor='#DDDDDD',
            legend=dict(
                orientation="h",
            )
        )
        fig.write_image(filepath,width=1600, height=900)

    def plot_car_speed(self,filepath:str):
        fig=px.line(self.f1_simulation.list_car_speed_all_stopwatches)
        fig.write_image(filepath)