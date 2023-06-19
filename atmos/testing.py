from datetime import datetime
import pytz

# # Create a UTC datetime object
# utc_datetime = datetime.utcnow()

# # Define the UTC+8 timezone
# malaysia = pytz.timezone('Asia/Kuala_Lumpur')

# # Convert the UTC datetime to UTC+8
# utc_plus_8_datetime = utc_datetime.replace(tzinfo=pytz.utc).astimezone(utc_plus_8)

# # Print the converted datetime
# print(utc_plus_8_datetime)





malaysia_tz = pytz.timezone('Asia/Kuala_Lumpur')
malaysia_datetime = datetime.utcnow().replace(tzinfo=pytz.utc).astimezone(malaysia_tz)

print(malaysia_datetime)