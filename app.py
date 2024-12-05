# Import libraries
import pandas as pd
from flask import Flask
import dash
from dash import dcc
from dash import html
from dash.dependencies import Input, Output
import plotly.graph_objs as go
import os
import signal
import threading

import system_metrics

# CSV file location
CSV_FILE = "system_metrics.csv"

# Create a Flask app
app = Flask(__name__)
dash_app = dash.Dash(__name__, server=app, url_base_pathname="/")


dash_app.layout = html.Div(
    className="container",
    children=[
        dcc.Interval(id="interval-component", interval=5 * 1000, n_intervals=0),
        html.Div(id="cpu-memory-utilization", className="metric"),
        html.Div(id="health-status", className="metric"),
        html.Div(id="network-traffic", className="metric"),
        html.Div(id="speed-test-metric", className="metric"),
    ],
    style={
        "display": "grid",
        "grid-template-columns": "1fr 1fr",
        "grid-template-rows": "1fr 1fr",
        "gap": "10px",
        "height": "100vh",
        "padding": "10px",
    },
)


@dash_app.callback(
    [
        Output("cpu-memory-utilization", "children"),
        Output("health-status", "children"),
        Output("network-traffic", "children"),
        Output("speed-test-metric", "children"),
    ],
    [Input("interval-component", "n_intervals")],
)
def update_metrics(n_intervals):
    df = pd.read_csv(CSV_FILE)
    latest_metrics = df.iloc[-1]

    timestamp = latest_metrics["timestamp"]
    cpu_util = latest_metrics["cpu_percent"]
    memory_util = latest_metrics["mem_percent"]
    download_speed = latest_metrics["download_speed"]
    upload_speed = latest_metrics["upload_speed"]
    # latency = latest_metrics["latency"]
    link_status = latest_metrics["link_status"]
    health_status = latest_metrics["health_status"]
    bytes_sent = latest_metrics["bytes_sent"]
    bytes_recv = latest_metrics["bytes_recv"]
    traffic_volume = latest_metrics["traffic_volume"]
    bandwidth_total = latest_metrics["bandwidth_total"]

    cpu_memory_graph = dcc.Graph(
        figure={
            "data": [
                go.Bar(x=["CPU Utilization"], y=[cpu_util], name="CPU"),
                go.Bar(x=["Memory Utilization"], y=[memory_util], name="Memory"),
            ],
            "layout": go.Layout(title="CPU and Memory Utilization", barmode="group"),
        }
    )

    network_traffic_graph = dcc.Graph(
        figure={
            "data": [
                go.Scatter(
                    x=df["timestamp"],
                    y=df["bytes_sent"],
                    mode="lines",
                    name="Bytes Sent",
                ),
                go.Scatter(
                    x=df["timestamp"],
                    y=df["bytes_recv"],
                    mode="lines",
                    name="Bytes Received",
                ),
                go.Scatter(
                    x=df["timestamp"],
                    y=df["traffic_volume"],
                    mode="lines",
                    name="Traffic Volume",
                ),
            ],
            "layout": go.Layout(
                title="Network Traffic",
                xaxis={"title": "Time"},
                yaxis={"title": "Bytes"},
                barmode="group",
            ),
        }
    )

    speed_graph = dcc.Graph(
        figure={
            "data": [
                go.Scatter(
                    x=df["timestamp"],
                    y=df["download_speed"],
                    mode="lines",
                    name="Download Speed",
                ),
                go.Scatter(
                    x=df["timestamp"],
                    y=df["upload_speed"],
                    mode="lines",
                    name="Upload Speed",
                ),
                go.Scatter(
                    x=df["timestamp"],
                    y=df["bandwidth_total"],
                    mode="lines",
                    name="Total Bandwidth",
                ),
            ],
            "layout": go.Layout(
                title="Speed Test Metrics",
                xaxis={"title": "Time"},
                yaxis={"title": "Speed (Mbps)"},
                barmode="group",
            ),
        }
    )

    health_color = "green" if health_status == "ok" and link_status == "up" else "red"
    health_status_div = html.Div(
        children=[
            html.H2("Health Status"),
            html.P(f"Health Status: {health_status}"),
            html.P(f"Link Status: {link_status}"),
        ],
        style={
            "background-color": health_color,
            "padding": "20px",
            "border-radius": "5px",
        },
    )

    return cpu_memory_graph, health_status_div, network_traffic_graph, speed_graph


def stop_flask_app():
    # Stop the Flask app
    system_metrics.stop_metrics_collections()
    os.kill(os.getpid(), signal.SIGINT)


if __name__ == "__main__":
    # Start the metrics collection thread
    metrics_thread = system_metrics.start_metrics_collections()

    # Set a timer to stop the Flask app
    time_to_stop_in_sec = 300  # time after which the app will stop, in seconds
    timer = threading.Timer(time_to_stop_in_sec, stop_flask_app)
    timer.start()

    try:
        app.run(debug=True)
    finally:
        system_metrics.stop_metrics_collections()
        metrics_thread.join()
