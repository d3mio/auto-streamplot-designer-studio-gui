import tkinter as tk
from tkinter import ttk
import random
from threading import Thread
import time
import json
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
import pandas as pd

class StreamPlotDesigner:
    def __init__(self, root):
        self.root = root
        self.root.title("StreamPlot Designer Studio")
        self.root.geometry("1200x800")
        self.root.configure(bg='#1e1e1e')
        
        # Dark mode color scheme
        self.bg_color = '#1e1e1e'
        self.fg_color = '#ffffff'
        self.accent_color = '#4285f4'
        self.card_bg = '#2d2d2d'
        
        # Initialize variables
        self.streaming = False
        self.connection_status = {"Kafka": False, "MQTT": False, "WebSocket": False}
        
        # Create main layout
        self.create_widgets()
        
        # Start data simulation thread
        self.simulator_thread = Thread(target=self.simulate_data_stream, daemon=True)
        self.simulator_thread.start()
    
    def create_widgets(self):
        # Configure style
        style = ttk.Style()
        style.theme_use('clam')
        style.configure('TFrame', background=self.bg_color)
        style.configure('TLabel', background=self.bg_color, foreground=self.fg_color)
        style.configure('TButton', background=self.accent_color, foreground=self.fg_color)
        style.configure('TNotebook', background=self.bg_color, padding=5)
        style.configure('TNotebook.Tab', background=self.card_bg, foreground=self.fg_color, padding=[10, 5])
        
        # Main container
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Left sidebar
        sidebar_frame = ttk.Frame(main_frame, width=250)
        sidebar_frame.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 10))
        
        # Right content area
        content_frame = ttk.Frame(main_frame)
        content_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        
        # Sidebar widgets
        self.create_sidebar(sidebar_frame)
        
        # Content area
        self.create_content_area(content_frame)
    
    def create_sidebar(self, parent):
        # Title
        title_label = ttk.Label(parent, text="StreamPlot Studio", font=('Helvetica', 16, 'bold'))
        title_label.pack(pady=(0, 20))
        
        # Data Sources section
        sources_frame = ttk.LabelFrame(parent, text="Data Sources", padding=(10, 5))
        sources_frame.pack(fill=tk.X, pady=(0, 15))
        
        ttk.Button(sources_frame, text="Kafka Connector", command=lambda: self.connect_source('Kafka')).pack(fill=tk.X, pady=2)
        ttk.Button(sources_frame, text="MQTT Broker", command=lambda: self.connect_source('MQTT')).pack(fill=tk.X, pady=2)
        ttk.Button(sources_frame, text="WebSocket", command=lambda: self.connect_source('WebSocket')).pack(fill=tk.X, pady=2)
        
        # Widgets panel
        widgets_frame = ttk.LabelFrame(parent, text="Visualization Widgets", padding=(10, 5))
        widgets_frame.pack(fill=tk.X, pady=(0, 15))
        
        widget_types = ["Line Chart", "Bar Chart", "Scatter Plot", "Gauge", "Status Light"]
        for widget in widget_types:
            btn = ttk.Button(widgets_frame, text=widget, command=lambda w=widget: self.add_widget_to_canvas(w))
            btn.pack(fill=tk.X, pady=2)
        
        # Settings
        settings_frame = ttk.LabelFrame(parent, text="Settings", padding=(10, 5))
        settings_frame.pack(fill=tk.X)
        
        # Theme toggle
        self.theme_var = tk.StringVar(value='dark')
        ttk.Label(settings_frame, text="Theme:").pack(anchor=tk.W)
        ttk.Radiobutton(settings_frame, text="Dark", variable=self.theme_var, value='dark').pack(anchor=tk.W)
        ttk.Radiobutton(settings_frame, text="Light", variable=self.theme_var, value='light').pack(anchor=tk.W)
        
        # Connection status indicators
        status_frame = ttk.Frame(parent)
        status_frame.pack(fill=tk.X, pady=(15, 0))
        
        tk.Label(status_frame, text="Connections:", bg=self.bg_color, fg=self.fg_color).pack(anchor=tk.W)
        
        self.kafka_status = tk.Label(status_frame, text="Kafka: ●", fg='red', bg=self.bg_color)
        self.kafka_status.pack(anchor=tk.W)
        
        self.mqtt_status = tk.Label(status_frame, text="MQTT: ●", fg='red', bg=self.bg_color)
        self.mqtt_status.pack(anchor=tk.W)
        
        self.ws_status = tk.Label(status_frame, text="WebSocket: ●", fg='red', bg=self.bg_color)
        self.ws_status.pack(anchor=tk.W)
        
        # Start/Stop button
        self.stream_btn = ttk.Button(parent, text="Start Streaming", command=self.toggle_streaming)
        self.stream_btn.pack(fill=tk.X, pady=(15, 0))
    
    def create_content_area(self, parent):
        # Notebook for dashboard tabs
        self.notebook = ttk.Notebook(parent)
        self.notebook.pack(fill=tk.BOTH, expand=True)
        
        # Create default dashboard tab
        self.create_default_dashboard()
        
        # Add new tab button
        add_tab_btn = ttk.Button(parent, text="+ New Dashboard", command=self.add_new_dashboard)
        add_tab_btn.pack(fill=tk.X, pady=(10, 0))
    
    def create_default_dashboard(self):
        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text="Dashboard 1")
        
        # Canvas for widgets
        canvas_frame = ttk.Frame(tab)
        canvas_frame.pack(fill=tk.BOTH, expand=True)
        
        # Initialize with sample widgets
        self.create_sample_widgets(canvas_frame)
    
    def create_sample_widgets(self, parent):
        # Sample line chart
        chart_frame = ttk.LabelFrame(parent, text="Live Data Stream", padding=10)
        chart_frame.grid(row=0, column=0, padx=10, pady=10, sticky='nsew')
        
        fig = Figure(figsize=(6, 3), dpi=100)
        self.chart_ax = fig.add_subplot(111)
        self.line, = self.chart_ax.plot([], [], '-', linewidth=2)
        self.chart_ax.set_facecolor('#2d2d2d')
        fig.patch.set_facecolor(self.card_bg)
        self.chart_ax.tick_params(colors=self.fg_color)
        
        for spine in self.chart_ax.spines.values():
            spine.set_color(self.fg_color)
        
        chart_canvas = FigureCanvasTkAgg(fig, master=chart_frame)
        chart_canvas.draw()
        chart_canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        
        # Sample gauge
        gauge_frame = ttk.LabelFrame(parent, text="Current Value", padding=10)
        gauge_frame.grid(row=0, column=1, padx=10, pady=10, sticky='nsew')
        
        self.gauge_value = tk.Label(gauge_frame, text="0.0", font=('Helvetica', 48), bg=self.card_bg, fg=self.accent_color)
        self.gauge_value.pack(expand=True)
        
        # Status indicators
        status_frame = ttk.LabelFrame(parent, text="System Status", padding=10)
        status_frame.grid(row=1, column=0, columnspan=2, padx=10, pady=10, sticky='nsew')
        
        tk.Label(status_frame, text="CPU Usage:", fg=self.fg_color, bg=self.card_bg).pack(anchor=tk.W)
        self.cpu_usage = ttk.Progressbar(status_frame, orient='horizontal', length=200, mode='determinate')
        self.cpu_usage.pack(fill=tk.X, pady=5)
        
        tk.Label(status_frame, text="Memory Usage:", fg=self.fg_color, bg=self.card_bg).pack(anchor=tk.W)
        self.mem_usage = ttk.Progressbar(status_frame, orient='horizontal', length=200, mode='determinate')
        self.mem_usage.pack(fill=tk.X, pady=5)
        
        parent.grid_columnconfigure(0, weight=1)
        parent.grid_columnconfigure(1, weight=1)
        parent.grid_rowconfigure(0, weight=1)
        parent.grid_rowconfigure(1, weight=0)
    
    def add_new_dashboard(self):
        tab_count = self.notebook.index('end')
        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text=f"Dashboard {tab_count + 1}")
        self.notebook.select(tab)
        
        # Canvas for widgets
        canvas_frame = ttk.Frame(tab)
        canvas_frame.pack(fill=tk.BOTH, expand=True)
        
        # Instructions label
        ttk.Label(canvas_frame, text="Drag and drop widgets from the left panel", 
                 font=('Helvetica', 12, 'italic'), foreground='gray').pack(expand=True)
    
    def connect_source(self, source_type):
        # Simulate connection
        self.connection_status[source_type] = not self.connection_status[source_type]
        
        # Update UI
        if source_type == "Kafka":
            self.kafka_status.config(text=f"Kafka: ●", fg='green' if self.connection_status[source_type] else 'red')
        elif source_type == "MQTT":
            self.mqtt_status.config(text=f"MQTT: ●", fg='green' if self.connection_status[source_type] else 'red')
        elif source_type == "WebSocket":
            self.ws_status.config(text=f"WebSocket: ●", fg='green' if self.connection_status[source_type] else 'red')
    
    def toggle_streaming(self):
        self.streaming = not self.streaming
        if self.streaming:
            self.stream_btn.config(text="Stop Streaming")
        else:
            self.stream_btn.config(text="Start Streaming")
    
    def add_widget_to_canvas(self, widget_type):
        current_tab = self.notebook.nametowidget(self.notebook.select())
        for child in current_tab.winfo_children():
            if isinstance(child, ttk.Frame) and len(child.winfo_children()) < 3:  # Simple check for empty canvas
                self.create_widget_on_canvas(child, widget_type)
                break
    
    def create_widget_on_canvas(self, canvas, widget_type):
        if widget_type == "Line Chart":
            # Create line chart widget
            pass
        elif widget_type == "Gauge":
            # Create gauge widget
            pass
        # Implement other widget types
    
    def simulate_data_stream(self):
        data_points = 50
        x_data = list(range(data_points))
        y_data = [0] * data_points
        
        while True:
            if self.streaming:
                # Update chart data
                new_value = random.uniform(-10, 10)
                y_data.pop(0)
                y_data.append(new_value)
                
                # Update widgets
                self.update_chart(x_data, y_data)
                self.gauge_value.config(text=f"{new_value:.2f}")
                
                # Update system metrics
                self.cpu_usage['value'] = random.randint(10, 90)
                self.mem_usage['value'] = random.randint(20, 80)
                
                # Simulate message processing
                if self.connection_status["Kafka"]:
                    pass  # Simulate Kafka messages
                
                if self.connection_status["MQTT"]:
                    pass  # Simulate MQTT messages
                
                if self.connection_status["WebSocket"]:
                    pass  # Simulate WebSocket messages
                
            time.sleep(0.5)
    
    def update_chart(self, x_data, y_data):
        self.line.set_data(x_data, y_data)
        self.chart_ax.relim()
        self.chart_ax.autoscale_view()
        
        # Get the figure to update
        fig = self.chart_ax.get_figure()
        fig.canvas.draw_idle()

if __name__ == "__main__":
    root = tk.Tk()
    app = StreamPlotDesigner(root)
    root.mainloop()