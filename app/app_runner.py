import pandas as pd
import dash
from dash import dash_table, dcc, html, Input, Output
import dash_bootstrap_components as dbc
import logging
from datetime import datetime
from typing import List, Dict
from scraper.db_manager import DatabaseManager

def fetch_data(db_manager: DatabaseManager) -> pd.DataFrame:
    """
    Fetches and processes data from the database.
    Returns processed DataFrame.
    """
    try:
        # Get data from database manager 
        data = db_manager.get_all_products()
        
        # Convert to DataFrame
        df = pd.DataFrame(data)
        
        return df
    except Exception as e:
        logging.error(f"Error fetching data: {e}")
        raise

def run_application(db_manager: DatabaseManager) -> None:
    """
    Runs the Dash web application with dynamic data refresh capability.
    """
    try:
        app = dash.Dash(__name__, 
                       external_stylesheets=[dbc.themes.SLATE],
                       suppress_callback_exceptions=True)

        # Initial data load
        df = fetch_data(db_manager)
        initial_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        app.layout = dbc.Container([
            # Store components
            dcc.Store(id='last-update-store', data=initial_time),
            dcc.Interval(id='interval-component', interval=300000), # 5 minute refresh
            
            dbc.Row([
                dbc.Col(
                    html.H1("Product Data", className="text-center text-light my-4"),
                    width=9
                ),
                dbc.Col(
                    dbc.Button(
                        ["Refresh Data ", html.I(className="fas fa-sync-alt")],
                        id="refresh-button",
                        color="danger", 
                        className="mt-4"
                    ),
                    width=3
                )
            ]),

            dbc.Row([
                dbc.Col(
                    html.Div(id="last-update-time", className="text-light mb-3")
                )
            ]),

            dbc.Row([
                dbc.Col(
                    id='table-container',
                    width=12
                )
            ]),

            dcc.Loading(
                id="loading",
                type="default",
                children=html.Div(id="loading-output")
            ),

            html.Div(id="error-message", className="text-danger")
        ],
        fluid=True,
        className="bg-dark text-light")

        @app.callback(
            [Output('table-container', 'children'),
             Output('last-update-store', 'data'),
             Output('loading-output', 'children'),
             Output('error-message', 'children')],
            [Input('refresh-button', 'n_clicks'),
             Input('interval-component', 'n_intervals')],
            prevent_initial_call=True
        )
        def refresh_data(n_clicks, n_intervals):
            """
            Callback to refresh the data when the refresh button is clicked or interval triggers
            """
            try:
                df = fetch_data(db_manager)
                if df.empty:
                    logging.warning("No data found in database")
                    return None, datetime.now().strftime("%Y-%m-%d %H:%M:%S"), None, "No data available"
                
                current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                
                # Create table
                table = dbc.Table(
                    # Create header
                    [html.Thead(html.Tr([html.Th(col) for col in df.columns]))]+
                    # Create body with URL links
                    [html.Tbody([
                        html.Tr([
                            html.Td(
                                html.A(
                                    "Link",
                                    href=row["URL"],
                                    className="text-info text-decoration-underline"
                                ) if col == "URL"
                                else row[col]
                            )
                            for col in df.columns
                        ])
                        for row in df.to_dict('records')
                    ])],
                    dark=True,
                    bordered=True,
                    hover=True,
                    responsive=True,
                    striped=True,
                    className="text-light",
                    style={
                        'backgroundColor': 'rgb(50, 50, 50)',
                        'minWidth': '180px'
                    }
                )
                
                return table, current_time, None, None
                
            except Exception as e:
                logging.error(f"Error refreshing data: {e}")
                return dash.no_update, dash.no_update, None, f"Error refreshing data: {str(e)}"

        @app.callback(
            Output('last-update-time', 'children'),
            [Input('last-update-store', 'data')]
        )
        def update_timestamp(timestamp):
            """
            Callback to update the last refresh timestamp display
            """
            if timestamp:
                return f"Last updated: {timestamp}"
            return "Last updated: Never"

        app.run(host='0.0.0.0', port='8080')
        logging.info("Dash application started.")
        
    except Exception as e:
        logging.error(f"Error starting the application: {e}")
        raise