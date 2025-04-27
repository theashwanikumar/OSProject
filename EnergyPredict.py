import tkinter as tk
from tkinter import messagebox, ttk

class EnergyEfficientCPUScheduler:
    def __init__(self, root):
        self.root = root
        self.root.title("Energy-Efficient CPU Scheduling")

        tk.Label(root, text="Number of Processes:").pack()
        self.process_count_entry = tk.Entry(root)
        self.process_count_entry.pack()
        tk.Button(root, text="Set Processes", command=self.create_process_entries).pack()

        self.process_frame = tk.Frame(root)
        self.process_frame.pack()

        tk.Button(root, text="Run Energy-Efficient Scheduling", command=self.run_scheduling).pack()
        self.result_label = tk.Label(root, text="")
        self.result_label.pack()

        self.table_frame = tk.Frame(root)
        self.table_frame.pack()

    def create_process_entries(self):
        for widget in self.process_frame.winfo_children():
            widget.destroy()

        try:
            self.num_processes = int(self.process_count_entry.get())
            if self.num_processes <= 0:
                raise ValueError("Number of processes must be positive.")

            tk.Label(self.process_frame, text="Arrival Time").grid(row=0, column=1)
            tk.Label(self.process_frame, text="Burst Time").grid(row=0, column=2)
            tk.Label(self.process_frame, text="Process Type").grid(row=0, column=3)

            self.arrival_entries = []
            self.burst_entries = []
            self.process_types = []

            for i in range(self.num_processes):
                tk.Label(self.process_frame, text=f"P{i+1}").grid(row=i+1, column=0)
                at_entry = tk.Entry(self.process_frame, width=5)
                bt_entry = tk.Entry(self.process_frame, width=5)
                pt_type = ttk.Combobox(self.process_frame, values=["CPU-bound", "IO-bound", "Mixed"], width=10)
                pt_type.set("CPU-bound")

                at_entry.grid(row=i+1, column=1)
                bt_entry.grid(row=i+1, column=2)
                pt_type.grid(row=i+1, column=3)

                self.arrival_entries.append(at_entry)
                self.burst_entries.append(bt_entry)
                self.process_types.append(pt_type)
        except ValueError:
            messagebox.showerror("Error", "Enter a valid number of processes.")

    def predict_real_energy(self, burst_time, process_type):
        # Model for consistency
        cpu_freq = 3000 # MHz
        cpu_usage = 70 # %
        base_power = 65 # Watts at full

        multiplier = {
            "CPU-bound": 1.0,
            "IO-bound": 0.5,
            "Mixed": 0.75
        }

        usage_multiplier = multiplier.get(process_type, 1.0)

        estimated_power = (cpu_usage / 100) * (cpu_freq / 1000) * base_power * usage_multiplier
        energy = estimated_power * burst_time  # Joules = Watts * seconds
        return energy

    def run_scheduling(self):
        try:
            arrival_times = [int(at.get()) for at in self.arrival_entries]
            burst_times = [int(bt.get()) for bt in self.burst_entries]
            process_types = [ptype.get() for ptype in self.process_types]

            energy_consumption = [
                self.predict_real_energy(bt, ptype)
                for bt, ptype in zip(burst_times, process_types)
            ]

            process_ids = [f"P{i+1}" for i in range(self.num_processes)]

            # Sort ing by efficiency
            processes = sorted(
                zip(process_ids, energy_consumption, arrival_times, burst_times),
                key=lambda x: x[1] / x[3]
            )

            sorted_ids, sorted_energy, sorted_at, sorted_bt = zip(*processes)

            waiting_time = [0] * self.num_processes
            turnaround_time = [0] * self.num_processes
            completion_time = [0] * self.num_processes

            completion_time[0] = sorted_at[0] + sorted_bt[0]
            for i in range(1, self.num_processes):
                completion_time[i] = max(completion_time[i-1], sorted_at[i]) + sorted_bt[i]
                waiting_time[i] = completion_time[i-1] - sorted_at[i]
                turnaround_time[i] = waiting_time[i] + sorted_bt[i]

            avg_wt = sum(waiting_time) / self.num_processes
            avg_tat = sum(turnaround_time) / self.num_processes
            avg_energy = sum(sorted_energy) / self.num_processes

            execution_order = " → ".join(sorted_ids)
            self.result_label.config(
                text=f"Execution Order: {execution_order}\n"
                     f"Avg Waiting Time: {avg_wt:.2f}\n"
                     f"Avg Turnaround Time: {avg_tat:.2f}\n"
                     f"Avg Energy Consumption: {avg_energy:.2f} J"
            )

            self.display_table(sorted_at, sorted_bt, sorted_energy, waiting_time, turnaround_time, sorted_ids)

        except ValueError:
            messagebox.showerror("Error", "Enter valid integer values.")

    def display_table(self, arrival_times, burst_times, energy_consumption, waiting_times, turnaround_times, process_ids):
        for widget in self.table_frame.winfo_children():
            widget.destroy()

        columns = ("Process", "Arrival Time", "Burst Time", "Energy (J)", "Waiting Time", "Turnaround Time")
        table = ttk.Treeview(self.table_frame, columns=columns, show="headings")

        for col in columns:
            table.heading(col, text=col)
            table.column(col, width=110, anchor="center")

        for i in range(len(arrival_times)):
            table.insert("", "end", values=(
                process_ids[i], arrival_times[i], burst_times[i],
                f"{energy_consumption[i]:.2f}", waiting_times[i], turnaround_times[i]
            ))

        table.pack()

if __name__ == "__main__":
    root = tk.Tk()
    app = EnergyEfficientCPUScheduler(root)
    root.mainloop()
