# Importing libraries
import psutil
import speedtest
import csv
import time
from datetime import datetime
import threading


# CSV file location
CSV_FILE = "system_metrics.csv"

stop_event = threading.Event()


# Function to collect system metrics and write to
# a CSV file
def collect_and_store_metrics():
    """
    Stores system metrics in a CSV file.
    """
    start_time = time.time()
    download_speed = 0
    upload_speed = 0
    latency = 0

    while not stop_event.is_set():
        elapsed_time = time.time() - start_time

        # Run speedtest every 10 seconds
        if int(elapsed_time) % 10 == 0:
            try:
                st = speedtest.Speedtest()
                st.download()
                st.upload()
                results_dict = st.results.dict()
                download_speed = round(
                    results_dict["download"] / 1_000_000, 2  # download speed in Mbps
                )
                upload_speed = round(
                    results_dict["upload"] / 1_000_000, 2  # upload speed in Mbps
                )
                latency = round(results_dict["ping"], 2)  # latency in ms
            except speedtest.ConfigRetrievalError as e:
                print(f"Speedtest error: {e}")
                download_speed = 0
                upload_speed = 0
                latency = 0
            except Exception as e:
                print(f"An error occurred: {e}")
                download_speed = 0
                upload_speed = 0
                latency = 0

        # Get the current time
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        # Get the CPU usage
        cpu_percent = round(psutil.cpu_percent(interval=1), 2)
        # Get the memory usage
        memory_percent = round(psutil.virtual_memory().percent, 2)
        # Get the network traffic
        net_io = psutil.net_io_counters()
        bytes_sent = net_io.bytes_sent
        bytes_recv = net_io.bytes_recv
        traffic_volume = bytes_sent + bytes_recv

        # Calculate total bandwidth
        bandwidth_total = round(download_speed + upload_speed, 2)

        # # Calculate bandwidth utilization
        # total_available_bandwidth = 100  # Example: 100 Mbps
        # bandwidth_utilization = (bandwidth_total / total_available_bandwidth) * 100

        # Get network link status
        interfaces = psutil.net_if_stats()
        status = {
            iface: "up" if info.isup else "down" for iface, info in interfaces.items()
        }

        link_status = "down"
        for iface, status in status.items():
            if status == "up":
                link_status = "up"
                break

        # Get network health status
        health_status = "ok" if traffic_volume > 10 * 1024 * 1024 else "not okay"

        # Open the CSV file in append mode
        with open(CSV_FILE, "a", newline="") as file:
            # Create a CSV writer object
            writer = csv.writer(file)
            # Write the header if the file is empty
            if file.tell() == 0:
                writer.writerow(
                    [
                        "timestamp",
                        "cpu_percent",
                        "mem_percent",
                        "download_speed",
                        "upload_speed",
                        "bandwidth_total",
                        "latency",
                        "link_status",
                        "health_status",
                        "bytes_sent",
                        "bytes_recv",
                        "traffic_volume",
                    ]
                )

            # Write the metrics to the CSV file
            writer.writerow(
                [
                    timestamp,
                    cpu_percent,
                    memory_percent,
                    download_speed,
                    upload_speed,
                    bandwidth_total,
                    latency,
                    link_status,
                    health_status,
                    bytes_sent,
                    bytes_recv,
                    traffic_volume,
                ]
            )

        time.sleep(1)


def start_metrics_collections():
    """
    Starts collecting system metrics.
    """
    global stop_event
    stop_event.clear()
    metrics_thread = threading.Thread(target=collect_and_store_metrics)
    metrics_thread.start()

    return metrics_thread


def stop_metrics_collections():
    """
    Stops collecting system metrics.
    """
    global stop_event
    stop_event.set()
