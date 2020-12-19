import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
import dash_table
import plotly.express as px
import pandas as pd
import numpy as np 


external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

df = pd.read_csv('https://raw.githubusercontent.com/wadefagen/datasets/master/gpa/uiuc-gpa-dataset.csv')

grades = ['A+', 'A', 'A-', 'B+', 'B', 'B-','C+', 'C', 'C-', 'D+', 'D', 'D-', 'F', 'W']

df['n_students'] = df[grades].sum(axis = 1) 

def gpa(row):
    gpa_points = 0
    gpa_points += (row['A+'] + row['A']) * 4
    gpa_points += row['A-'] * 3.66
    gpa_points += row['B+'] * 3.33
    gpa_points += row['B'] * 3
    gpa_points += row['B-'] * 2.66
    gpa_points += row['C+'] * 2.33
    gpa_points += row['C'] * 2
    gpa_points += row['C-'] * 1.66
    gpa_points += row['D+'] * 1.33
    gpa_points += row['D'] * 1
    gpa_points += row['D-'] * .66
    return gpa_points

df['gpa_points'] = df.apply(lambda x: gpa(x), axis = 1)

marks_array = [0 , 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1 , 1.1, 1.2,
       1.3, 1.4, 1.5, 1.6, 1.7, 1.8, 1.9, 2 , 2.1, 2.2, 2.3, 2.4, 2.5,
       2.6, 2.7, 2.8, 2.9, 3 , 3.1, 3.2, 3.3, 3.4, 3.5, 3.6, 3.7, 3.8,
       3.9, 4]

def name(row):
    return (row['Subject'] + ' ' + str(row['Number']) + ": " + row['Course Title'])

gpa_df = df.groupby(by = ['Subject', 'Number', 'Course Title'])[['gpa_points', 'n_students']].sum().reset_index()
gpa_df['Average GPA'] = round(gpa_df['gpa_points'] / gpa_df['n_students'], 2)
gpa_df['n_classes'] = df.groupby(by = ['Subject', 'Number', 'Course Title']).count().reset_index()['n_students']
gpa_df['n_4s'] = df.groupby(by = ['Subject', 'Number', 'Course Title'])[['A+', 'A']].sum().reset_index()[['A+', 'A']].sum(axis = 1)
gpa_df['% A+/A'] = round((gpa_df['n_4s'] / gpa_df['n_students']) * 100, 2)
gpa_df['Average Students Per Class'] = round(gpa_df['n_students'] / gpa_df['n_classes'], 2)

gpa_df['Course'] = gpa_df.apply(lambda x: name(x), axis = 1) 


def generate_table(dataframe, max_rows=1000):
    return html.Table([
        html.Thead(
            html.Tr([html.Th(col) for col in dataframe.columns])
        ),
        html.Tbody([
            html.Tr([
                html.Td(dataframe.iloc[i][col]) for col in dataframe.columns
            ]) for i in range(min(len(dataframe), max_rows))
        ])
    ], style={'marginLeft': 'auto', 'marginRight': 'auto'})


app.layout = html.Div([
    dcc.Markdown('''
    # UIUC Course Minimum GPA
    ### Select a Subject

    '''),

    dcc.Dropdown(
        id = 'class-subject',
        options = [{'label': i, 'value': i } for i in df['Subject'].unique()],
        value = 'AAS'
    ),

    dcc.Markdown('''
    ### Select Course Level

    '''),

    html.Div([
    dcc.Dropdown(
        id = 'student-type',
        options = [{'label': i, 'value': i} for i in ['Undergraduate', 'Graduate']],
        value = 'Undergraduate'
    )]),

    dcc.Markdown('''
    ### Select Minimum GPA 

    ''', style={ 'text-align': 'center' }),

    dcc.Slider(
    id='gpa-slider',
    min = 0,
    max = 4,
    value = 3,
    step = None, 
    marks = {str(i): str(round(i, 2)) for i in marks_array}
    ),
    dcc.Graph(id = 'graph'),

    html.Div(id = 'table')
])


@app.callback(
   Output('graph', 'figure'),
   Output('table', 'children'),
   Input('class-subject', 'value'),
   Input('student-type', 'value'),
   Input('gpa-slider', 'value')
)

def update_figure(selected_subject, selected_student, selected_gpa):
    if selected_student == 'Undergraduate':
        filtered_courses = gpa_df[(gpa_df['Subject'] == selected_subject) & (gpa_df['Average GPA'] > selected_gpa) & (gpa_df['Number'] <= 500)]

    else:
        filtered_courses = gpa_df[(gpa_df['Subject'] == selected_subject) & (gpa_df['Average GPA'] > selected_gpa) & (gpa_df['Number'] >= 400)]
    
    filtered_df_show = filtered_courses[['Course', 'Average GPA', '% A+/A']]

    fig = px.scatter(filtered_courses,
            x = '% A+/A',
            y = 'Average GPA', 
            size = 'Average Students Per Class',
            color = 'Average GPA',
            size_max = 50,
            template = "plotly",
            title = "GPA",
            hover_name = 'Course',
            hover_data = ['Average Students Per Class'])

    fig.update_layout(transition_duration = 500)

    return fig, generate_table(filtered_df_show, max_rows = len(filtered_df_show))



### After getting that to work, then add two graphs, one for undergrad and grad
### After that, maybe post the data frame with classes and average gpas 

if __name__ == '__main__':
    app.run_server(debug=True)