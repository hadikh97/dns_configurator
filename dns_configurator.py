import tkinter as tk
from tkinter import messagebox
import subprocess
import re
import os
import sys
import ctypes


def validate_ip(address):
    pattern = re.compile(r"^(?:[0-9]{1,3}\.){3}[0-9]{1,3}$")
    if pattern.match(address):
        return all(0 <= int(num) < 256 for num in address.split('.'))
    return False


def is_admin():
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False


def run_as_admin():
    if sys.version_info[0] == 3 and sys.version_info[1] >= 5:
        os.startfile(sys.argv[0], 'runas')
    else:
        messagebox.showerror("Error", "Please run this script as an administrator.")
    sys.exit()


def set_dns(preferred, alternate):
    if not validate_ip(preferred) or not validate_ip(alternate):
        messagebox.showerror("Error",
                             "Invalid IP address format. Please use the format x.x.x.x, where x is between 0 and 255.")
        return

    script = f"""
    $interface = Get-NetAdapter | Where-Object {{ $_.Status -eq "Up" }}
    Set-DnsClientServerAddress -InterfaceIndex $interface.InterfaceIndex -ServerAddresses "{preferred}","{alternate}"
    """
    ps_command = ["powershell", "-Command", script]
    result = subprocess.run(ps_command, capture_output=True, text=True)
    if result.returncode == 0:
        messagebox.showinfo("Success", "DNS settings updated successfully.")
    else:
        messagebox.showerror("Error", f"Failed to update DNS settings:\n{result.stderr}")


def reset_dns():
    script = """
    $interface = Get-NetAdapter | Where-Object { $_.Status -eq "Up" }
    Set-DnsClientServerAddress -InterfaceIndex $interface.InterfaceIndex -ResetServerAddresses
    """
    ps_command = ["powershell", "-Command", script]
    result = subprocess.run(ps_command, capture_output=True, text=True)
    if result.returncode == 0:
        messagebox.showinfo("Success", "DNS settings removed successfully.")
    else:
        messagebox.showerror("Error", f"Failed to remove DNS settings:\n{result.stderr}")


def on_set_dns():
    preferred = preferred_entry.get()
    alternate = alternate_entry.get()
    set_dns(preferred, alternate)


def on_reset_dns():
    reset_dns()


if not is_admin():
    run_as_admin()

app = tk.Tk()
app.title("DNS Configurator")

tk.Label(app, text="Preferred DNS:").grid(row=0, column=0, padx=10, pady=10)
preferred_entry = tk.Entry(app)
preferred_entry.grid(row=0, column=1, padx=10, pady=10)

tk.Label(app, text="Alternate DNS:").grid(row=1, column=0, padx=10, pady=10)
alternate_entry = tk.Entry(app)
alternate_entry.grid(row=1, column=1, padx=10, pady=10)

set_button = tk.Button(app, text="Set DNS", command=on_set_dns)
set_button.grid(row=2, column=0, padx=10, pady=10)

reset_button = tk.Button(app, text="Reset DNS", command=on_reset_dns)
reset_button.grid(row=2, column=1, padx=10, pady=10)

app.mainloop()
