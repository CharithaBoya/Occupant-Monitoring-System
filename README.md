Occupant's Health Monitoring Inside the Autonomous Vehicle

This project monitors the occupant's health inside an autonomous vehicle by:
1. Continuously capturing frames from a camera to detect emotions.
2. Analyzing heart rate data obtained from a smartwatch.
3. Triggering emergency alerts to a designated mobile number if:
     The detected emotion is sad, fear, or angry.
     The heart rate is abnormal (bpm < 70 or bpm > 110).

Prerequisites: 
1. Smartwatch (should support heart rate data export or real-time monitoring)  
2. Heart rate data source: HTML file exported from the smartwatch’s mobile application
3. Twilio API account for sending emergency alerts.
4. Twilio Credentials (replace these in vehicle_dashboard.py):
     TWILIO_SID, TWILIO_AUTH_TOKEN, TWILIO_PHONE_NUMBER, TARGET_PHONE_NUMBER(your phone number)

Setup Instructions

Step 1: Install Visual Studio Code (1.97.2)
Step 2: Install required libraries: pip install bleak twilio
Step 3: Create a folder named Health_Integration.
Step 4: Inside the folder, add the following files:
           vehicle_dashboard.py
           dashboard.html
Step 5: Update your TWILIO CREDENTIALS in vehicle_dashboard.py.
Step 6: Place the Heart Rate file in the same folder.
Step 7: Run vehicle_dashboard.py file in the terminal.

The system will start monitoring and send alerts if an emergency is detected.
