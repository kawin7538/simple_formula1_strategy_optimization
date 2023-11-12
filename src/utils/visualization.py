import numpy as np
import pandas as pd
import plotly.express as px

from models.f1_simulation import F1Simulation

class F1SimVisualization:
    def __init__(self,f1_simulation:F1Simulation):
        self.f1_simulation=f1_simulation

    def plot_tyre_sequence(self):
        list_dict_sequences=list()
        latest_tyre=self.f1_simulation.list_tyre_setting_all_laps[0]
        latest_tyre_start=0
        for i in range(len(self.f1_simulation.list_car_status_will_be_pit)):
            if self.f1_simulation.list_car_status_will_be_pit[i]==True:
                list_dict_sequences.append(dict(Task='tyre sequence',Start=latest_tyre_start+1,Finish=i+1,Resource=latest_tyre))
                latest_tyre=self.f1_simulation.list_tyre_setting_all_laps[i+1]
                latest_tyre_start=i
        list_dict_sequences.append(dict(Task='tyre sequence',Start=latest_tyre_start+1,Finish=self.f1_simulation.number_of_laps,Resource=latest_tyre))

        df_sequences=pd.DataFrame(list_dict_sequences)
        df_sequences['Delta']=df_sequences['Finish']-df_sequences['Start']

        cm={
            'Soft':'#ED1C24',
            'Medium':'#ffcc29',
            'Hard':'White'
        }
        
        fig=px.timeline(df_sequences,x_start='Start',x_end='Finish',y='Task',color='Resource',color_discrete_map=cm)
        # Update the layout
        fig.layout.xaxis.type = 'linear'
        fig.update_layout(
            plot_bgcolor='#AAAAAA'
        )
        for i in np.arange(len(df_sequences)):
            fig.data[i].x = (df_sequences['Delta'][i],)
        fig.write_image("output/temp.png")

    def plot_car_speed(self):
        fig=px.line(self.f1_simulation.list_car_speed_all_stopwatches)
        fig.write_image("output/temp.png")