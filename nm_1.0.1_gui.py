import os
import time
import psutil
import tkinter as tk
from tkinter import messagebox
from prettytable import PrettyTable
from prettytable import DOUBLE_BORDER

# Units of memory sizes
size = ['bytes', 'KB', 'MB', 'GB', 'TB']

# Function that returns bytes in a readable format
def getSize(bytes):
    for unit in size:
        if bytes < 1024:
            return f"{bytes:.1f}{unit}"
        bytes /= 1024

# Function to update the data in the GUI
def updateData():
    global dataSent, dataRecv, netStats2

    # Getting the network i/o stats again to 
    # count the sending and receiving speed
    netStats2 = psutil.net_io_counters()

    # Upload/Sending speed
    uploadStat = netStats2.bytes_sent - dataSent
    # Receiving/Download Speed
    downloadStat = netStats2.bytes_recv - dataRecv

    # Updating the labels with the new data
    label_received.config(text=f"Received: {getSize(netStats2.bytes_recv)}")
    label_receiving.config(text=f"Receiving: {getSize(downloadStat)}/s")
    label_sent.config(text=f"Sent: {getSize(netStats2.bytes_sent)}")
    label_sending.config(text=f"Sending: {getSize(uploadStat)}/s")

    # Check if the download or upload speed exceeds 1 MBps (1 MBps = 1 * 1024 * 1024 bytes per second)
    if downloadStat > 1 * 1024 * 1024 or uploadStat > 1 * 1024 * 1024:
        messagebox.showwarning("Warning", "Network traffic speed exceeds 1 MBps!")

    # Again getting the data of total bytes sent and received
    dataSent = netStats2.bytes_sent
    dataRecv = netStats2.bytes_recv

    # Call the function again after 1 second
    root.after(1000, updateData)

# Creating the main window
root = tk.Tk()
root.title("Network Traffic Monitor")

# Creating labels to display the data
label_received = tk.Label(root, text="Received: 0 bytes")
label_received.pack()

label_receiving = tk.Label(root, text="Receiving: 0.0 bytes/s")
label_receiving.pack()

label_sent = tk.Label(root, text="Sent: 0 bytes")
label_sent.pack()

label_sending = tk.Label(root, text="Sending: 0.0 bytes/s")
label_sending.pack()

# psutil.net_io_counters() returns network I/O statistics as a namedtuple
netStats1 = psutil.net_io_counters()

# Getting the data of total bytes sent and received
dataSent = netStats1.bytes_sent
dataRecv = netStats1.bytes_recv

# Start updating the data
updateData()

# Start the main event loop
root.mainloop()
