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
        
        # No need for column renaming since DatabaseManager already returns
        # properly named columns in get_all_products()
        
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

        app.layout = dbc.Container(
            [
                # Store components should be at the top level of the layout
                dcc.Store(id='last-update-store', data=initial_time),
                
                dbc.Row([
                    dbc.Col(
                        html.H1(
                            "Product Data",
                            className="text-center text-light my-4"
                        ),
                        width=9
                    ),
                    dbc.Col(
                        dbc.Button(
                            [
                                "Refresh Data ",
                                html.I(className="fas fa-sync-alt")
                            ],
                            id="refresh-button",
                            color="primary",
                            className="mt-4"
                        ),
                        width=3
                    )
                ]),
                dbc.Row([
                    dbc.Col(
                        html.Div(
                            id="last-update-time",
                            className="text-light mb-3"
                        )
                    )
                ]),
                dbc.Row(
                    dbc.Col(
                        dash_table.DataTable(
                            id='table',
                            columns=[
                                {"name": i, "id": i, "presentation": "markdown"} if i == "URL"
                                else {"name": i, "id": i} 
                                for i in df.columns
                            ],
                            data=[
                                {
                                    **record,
                                    'URL': f'[Link]({record["URL"]})'
                                }
                                for record in df.to_dict('records')
                            ],
                            markdown_options={"html": True},
                            page_size=10,
                            style_table={'overflowX': 'auto'},
                            style_cell={
                                'textAlign': 'left',
                                'backgroundColor': 'rgb(50, 50, 50)',
                                'color': 'white',
                                'minWidth': '180px', 
                                'width': '180px', 
                                'maxWidth': '180px',
                                'whiteSpace': 'normal'
                            },
                            style_cell_conditional=[
                                {
                                    'if': {'column_id': 'URL'},
                                    'cursor': 'pointer',
                                    'textDecoration': 'underline',
                                    'color': '#7FDBFF'
                                }
                            ],
                            style_header={
                                'backgroundColor': 'rgb(30, 30, 30)',
                                'color': 'white',
                                'fontWeight': 'bold'
                            },
                        ),
                        width=12
                    )
                ),
                dcc.Loading(
                    id="loading",
                    type="default",
                    children=html.Div(id="loading-output")
                ),
            ],
            fluid=True,
            className="bg-dark text-light"
        )

        @app.callback(
            [Output('table', 'data'),
             Output('last-update-store', 'data'),
             Output('loading-output', 'children')],
            [Input('refresh-button', 'n_clicks')],
            prevent_initial_call=True
        )
        def refresh_data(n_clicks):
            """
            Callback to refresh the data when the refresh button is clicked
            """
            if n_clicks is None:
                raise dash.exceptions.PreventUpdate
                
            try:
                df = fetch_data(db_manager)
                if df.empty:
                    logging.warning("No data found in database")
                    return [], datetime.now().strftime("%Y-%m-%d %H:%M:%S"), "No data available"
                     
                current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                # Transform the URL into markdown links
                data = [
                    {
                        **record,
                        'URL': f'[Link]({record["URL"]})'
                    }
                    for record in df.to_dict('records')
                ]
                return data, current_time, ""
            except Exception as e:
                logging.error(f"Error refreshing data: {e}")
                return dash.no_update, dash.no_update, f"Error refreshing data: {str(e)}"

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

        app.run(host='0.0.0.0', port='8080', debug=True)
        logging.info("Dash application started.")
    except Exception as e:
        logging.error(f"Error starting the application: {e}")
        raise