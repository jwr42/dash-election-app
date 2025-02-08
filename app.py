# Import packages
from dash import Dash, html, dcc, callback, Output, Input
from components import party_colors, result_colors
import dash_bootstrap_components as dbc
import pandas as pd
import plotly.express as px

# Import cleaned data
df = pd.read_csv("data/cleaned_data.csv")

# Instantiate app
app = Dash(external_stylesheets=[dbc.themes.BOOTSTRAP])

# Define layout
app.layout = dbc.Container(
    html.Div(
        [
            # title row
            html.Br(),
            html.H1("2024 Regional UK General Election Results"),
            html.Hr(),
            # filters
            dbc.Row(
                [
                    dbc.Col(
                        dbc.InputGroup(
                            [
                                dbc.InputGroupText("Region"),
                                dbc.Select(
                                    options=[{"label": "All Regions", "value": "All"}]
                                    + [
                                        {"label": region, "value": region}
                                        for region in df["Region"].unique()
                                    ],
                                    value="All",
                                    id="RegionDropdown",
                                ),
                            ]
                        ),
                        width=4,
                    ),
                ],
            ),
            html.Hr(),
            # cards
            dbc.Row(
                [
                    dbc.Col(
                        dbc.Card(
                            dbc.CardBody(
                                [
                                    "Average MP Majority",
                                    html.H2(id="AvgMajorityCard"),
                                ],
                            ),
                        ),
                    ),
                    dbc.Col(
                        dbc.Card(
                            dbc.CardBody(
                                [
                                    "Seats That Changed Party",
                                    html.H2(id="SeatChangeCard"),
                                ],
                            ),
                        ),
                    ),
                    dbc.Col(
                        dbc.Card(
                            dbc.CardBody(
                                [
                                    "Total Votes Cast",
                                    html.H2(id="TotalVotesCastCard"),
                                ]
                            ),
                        ),
                    ),
                    dbc.Col(
                        dbc.Card(
                            dbc.CardBody(
                                [
                                    "Electorate Turnout",
                                    html.H2(id="TurnoutCard"),
                                ]
                            ),
                        ),
                    ),
                ],
            ),
            # visuals
            dbc.Row(
                [
                    dbc.Col(
                        dbc.Card(
                            [
                                dbc.CardHeader("% Seats by Party"),
                                dbc.CardBody(
                                    dcc.Graph(
                                        id="donut_chart",
                                        config={"displayModeBar": False},
                                        className="h-100",
                                    ),
                                ),
                            ]
                        ),
                        width=5,
                    ),
                    dbc.Col(
                        dbc.Card(
                            [
                                dbc.CardHeader("Seat Results Summary"),
                                dbc.CardBody(
                                    dcc.Graph(
                                        id="treemap_chart",
                                        config={"displayModeBar": False},
                                        className="h-100",
                                    ),
                                ),
                            ]
                        ),
                        width=7,
                    ),
                ],
                style={"marginBlock": "10px"},
            ),
        ]
    )
)


# Add controls to build the interaction
@callback(
    [
        Output("SeatChangeCard", "children"),
        Output("AvgMajorityCard", "children"),
        Output("TotalVotesCastCard", "children"),
        Output("TurnoutCard", "children"),
        Output("donut_chart", "figure"),
        Output("treemap_chart", "figure"),
    ],
    Input("RegionDropdown", "value"),
)
def update_values(selected_region):
    # Filter
    filtered_df = df.copy()
    if selected_region != "All":
        filtered_df = filtered_df[filtered_df["Region"] == selected_region]

    # Card Values
    TotalSeatChange = len(
        [result for result in filtered_df["Result"] if "hold" not in result]
    )
    PercentageSeatChange = TotalSeatChange / len(filtered_df["Result"])
    SeatChangeCard = f"{TotalSeatChange} ({PercentageSeatChange:.0%})"
    AvgMajorityCard = [f"{filtered_df['Majority'].mean():,.0f}"]
    TotalVotesCastCard = [f"{filtered_df['Votes Cast'].sum():,.0f}"]
    TurnoutCard = [
        f"{filtered_df['Votes Cast'].sum()/filtered_df['Electorate'].sum():.1%}"
    ]

    # Donut Chart
    df_pie = (
        filtered_df["Winning Party"]
        .value_counts()
        .rename_axis("Party")
        .reset_index(name="Constituencies")
    )
    donut_chart = px.pie(
        df_pie,
        names="Party",
        values="Constituencies",
        color="Party",
        hole=0.5,
        labels={"Constituencies": "Seats"},
        color_discrete_map=party_colors,
    )
    donut_chart.update_traces(
        textposition="inside",
        texttemplate="%{percent:.0%}",
        hovertemplate="%{label} <br>%{value} Seats",
        hoverlabel=dict(bgcolor="white", font_size=18),
    )
    donut_chart.update_layout(
        uniformtext_minsize=20,
        uniformtext_mode="hide",
        showlegend=False,
        annotations=[
            dict(
                text=f"{len(filtered_df)} Seats",
                font=dict(size=20, weight="bold"),
                showarrow=False,
                xanchor="center",
            )
        ],
        margin={"t": 0, "l": 0, "b": 0, "r": 0},
    )

    # Treemap Chart
    df_treemap = (
        filtered_df["Result"]
        .value_counts()
        .rename_axis("Result")
        .reset_index(name="Constituencies")
    )
    treemap_chart = px.treemap(
        df_treemap,
        path=["Result"],
        values="Constituencies",
        color="Result",
        color_discrete_map=result_colors,
    )
    treemap_chart.update_traces(
        marker=dict(cornerradius=2),
        hovertemplate="%{label} <br>%{value} Seats",
        hoverlabel=dict(bgcolor="white", font_size=18),
    )
    treemap_chart.update_layout(
        uniformtext_minsize=20,
        uniformtext_mode="hide",
        margin={"t": 0, "l": 0, "b": 0, "r": 0},
    )

    return (
        SeatChangeCard,
        AvgMajorityCard,
        TotalVotesCastCard,
        TurnoutCard,
        donut_chart,
        treemap_chart,
    )


# Run app
if __name__ == "__main__":
    app.run(debug=True)
