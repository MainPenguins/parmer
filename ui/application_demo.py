import sys

from ui.application import ParmerApplication


app = ParmerApplication()

print("Starting Parmer...")
status = app.run(sys.argv)
print(f"Parmer exited: {status}")
