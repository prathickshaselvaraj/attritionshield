from flask import Flask, render_template
import pandas as pd
import plotly.express as px
import pickle
import json

app = Flask(__name__)

corporate_colors = {
    'primary': '#1A73E8',
    'accent': '#0F9D58', 
    'warning': '#EA4335',
    'text': '#202124',
    'background': '#F5F7FA'
}

# LOAD FROM PICKLE FILE
with open('results/hr_insights.pkl', 'rb') as f:
    insights = pickle.load(f)

@app.route('/')
def dashboard():
    key_metrics = insights['key_metrics']
    dept_data = insights['department_analysis']
    high_risk_roles = insights['high_risk_roles']
    overtime_impact = insights['overtime_impact']

    # Create SIMPLE charts without complex serialization
    dept_chart = create_simple_dept_chart(dept_data)
    overtime_chart = create_simple_overtime_chart(overtime_impact)
    income_chart = create_simple_income_chart()

    return render_template('dashboard.html',
                         total_employees=key_metrics['total_employees'],
                         attrition_rate=key_metrics['attrition_rate'],
                         avg_income=key_metrics['avg_income'],
                         overtime_rate=key_metrics['overtime_rate'],
                         salary_gap=key_metrics['salary_gap'],
                         dept_chart=dept_chart,
                         overtime_chart=overtime_chart,
                         income_chart=income_chart,
                
                         role_attrition=high_risk_roles,
                         dept_data=dept_data,  
                         overtime_impact=overtime_impact,
                         colors=corporate_colors)

def create_simple_dept_chart(dept_data):
    df_dept = pd.DataFrame(dept_data)
    
    # Create manual data structure
    data = [{
        'type': 'bar',
        'x': df_dept['Department'].tolist(),
        'y': df_dept['AttritionRate%'].tolist(),
        'marker': {
            'color': df_dept['AttritionRate%'].tolist(),
            'colorscale': [[0, '#0F9D58'], [1, '#EA4335']]
        }
    }]
    
    layout = {
        'title': 'Attrition Rate by Department',
        'plot_bgcolor': '#F5F7FA',
        'paper_bgcolor': '#F5F7FA',
        'font': {'color': '#202124'},
        'showlegend': False,
        'height': 400
    }
    
    return json.dumps({'data': data, 'layout': layout})

def create_simple_overtime_chart(overtime_data):
    data = [{
        'type': 'bar',
        'x': ['No', 'Yes'],
        'y': [overtime_data['overtime_no'], overtime_data['overtime_yes']],
        'marker': {
            'color': ['#0F9D58', '#EA4335']
        }
    }]
    
    layout = {
        'title': 'Overtime Impact on Attrition',
        'plot_bgcolor': '#F5F7FA',
        'paper_bgcolor': '#F5F7FA',
        'font': {'color': '#202124'},
        'showlegend': False,
        'height': 400
    }
    
    return json.dumps({'data': data, 'layout': layout})

def create_simple_income_chart():
    df = pd.read_csv('data/employee_attrition.csv')
    income_comparison = df.groupby('Attrition')['MonthlyIncome'].mean().round().reset_index()
    
    data = [{
        'type': 'bar',
        'x': ['Stayed', 'Left'],
        'y': [
            income_comparison[income_comparison['Attrition'] == 'No']['MonthlyIncome'].iloc[0],
            income_comparison[income_comparison['Attrition'] == 'Yes']['MonthlyIncome'].iloc[0]
        ],
        'marker': {
            'color': ['#0F9D58', '#EA4335']
        }
    }]
    
    layout = {
        'title': 'Income Comparison: Leavers vs Stayers',
        'plot_bgcolor': '#F5F7FA',
        'paper_bgcolor': '#F5F7FA',
        'font': {'color': '#202124'},
        'showlegend': False,
        'height': 400
    }
    
    return json.dumps({'data': data, 'layout': layout})

def create_satisfaction_chart():
    df = pd.read_csv('data/employee_attrition.csv')
    
    # Calculate attrition rate by job satisfaction level
    satisfaction_attrition = df.groupby('JobSatisfaction')['Attrition'].apply(
        lambda x: (x == 'Yes').mean() * 100
    ).round(1).reset_index()
    satisfaction_attrition.columns = ['JobSatisfaction', 'AttritionRate']
    
    data = [{
        'type': 'bar',
        'x': satisfaction_attrition['JobSatisfaction'].tolist(),
        'y': satisfaction_attrition['AttritionRate'].tolist(),
        'marker': {
            'color': satisfaction_attrition['AttritionRate'].tolist(),
            'colorscale': [[0, '#0F9D58'], [1, '#EA4335']]
        }
    }]
    
    layout = {
        'title': '',
        'xaxis': {
            'title': 'Job Satisfaction Level',
            'tickvals': [1, 2, 3, 4],
            'ticktext': ['Very Low', 'Low', 'High', 'Very High']
        },
        'yaxis': {
            'title': 'Attrition Rate (%)'
        },
        'plot_bgcolor': '#F5F7FA',
        'paper_bgcolor': '#FFFFFF',
        'font': {'color': '#202124'},
        'showlegend': False,
        'height': 300
    }
    
    return json.dumps({'data': data, 'layout': layout})

if __name__ == '__main__':
    app.run(debug=True)