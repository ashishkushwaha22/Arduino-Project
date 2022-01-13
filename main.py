

import time
import board
import busio
import adafruit_ccs811
import subprocess
import Adafruit_DHT
from azure.iot.device import IoTHubDeviceClient, Message

import Adafruit_GPIO.SPI as SPI
import Adafruit_SSD1306

from PIL import Image
from PIL import ImageDraw
from PIL import ImageFont

CONNECTION_STRING = "HostName=xxxxxxxx;DeviceId=xxxxxx;SharedAccessKey=xxxxxxxxxxxxxxxxxxx" 
MSG_SND = '{{"temperature": {temperature},"humidity": {humidity}, "co2": {Co2}}}' 



DHT_SENSOR = Adafruit_DHT.DHT22
DHT_PIN = 4

i2c = board.I2C()  # uses board.SCL and board.SDA
ccs811 = adafruit_ccs811.CCS811(i2c)

# Wait for the sensor to be ready
while not ccs811.data_ready:
    pass

# Raspberry Pi pin configuration:
RST = None     # on the PiOLED this pin isnt used
# Note the following are only used with SPI:
DC = 23
SPI_PORT = 0
SPI_DEVICE = 0

# 128x32 display with hardware I2C:
#disp = Adafruit_SSD1306.SSD1306_128_32(rst=RST)

# 128x64 display with hardware I2C:
disp = Adafruit_SSD1306.SSD1306_128_64(rst=RST)

# Note you can change the I2C address by passing an i2c_address parameter like:
# disp = Adafruit_SSD1306.SSD1306_128_64(rst=RST, i2c_address=0x3C)

# Alternatively you can specify an explicit I2C bus number, for example
# with the 128x32 display you would use:
# disp = Adafruit_SSD1306.SSD1306_128_32(rst=RST, i2c_bus=2)
# Initialize library.
disp.begin()

# Clear display.
disp.clear()
disp.display()

# Create blank image for drawing.
# Make sure to create image with mode '1' for 1-bit color.
width = disp.width
height = disp.height
image = Image.new('1', (width, height))

# Get drawing object to draw on image.
draw = ImageDraw.Draw(image)

# Draw a black filled box to clear the image.
draw.rectangle((0,0,width,height), outline=0, fill=0)

# Draw some shapes.
# First define some constants to allow easy resizing of shapes.
padding = -2
top = padding
bottom = height-padding
# Move left to right keeping track of the current x position for drawing shapes.
x = 0


# Load default font.
#font = ImageFont.load_default()

# Alternatively load a TTF font.  Make sure the .ttf font file is in the same directory as the python$# Some other nice fonts to try: http://www.dafont.com/bitmap.php
font = ImageFont.truetype('Minecraftia-Regular.ttf', 13)

while True:

    humidity, temperature = Adafruit_DHT.read_retry(DHT_SENSOR, DHT_PIN)
    
    try:
        eco2 = ccs811.eco2
    except:
        print("Failed getting CO2 value")
    
    try:
        tvoc = ccs811.tvoc
    except:
        print("Failed getting TVOC value")
    
    if humidity is not None and temperature is not None:
        # Draw a black filled box to clear the image.
        draw.rectangle((0,0,width,height), outline=0, fill=0)

        # Write two lines of text.

        digit = temperature * 10
        digit = int(digit % 10)

        humidity = int(humidity)
        temperature = int(temperature)
        draw.text((x, top+5),     "Environment",  font=font, fill=255)
        draw.text((x, top+20),    "T: " + str(temperature) + "." + str(digit) + "C", font=font, fill=255)
        draw.text((x+64, top+20), "H: " + str(humidity) + "%",  font=font, fill=255)
        draw.text((x, top+35),    "CO2: " + str(eco2) + " PPM", font=font, fill=255)
        draw.text((x, top+50),    "TVOC: "  + str(tvoc) + " PPB", font=font, fill=255)

        # Display image.
        disp.image(image)
        disp.display()
    
    def iothub_client_init():  
        client = IoTHubDeviceClient.create_from_connection_string(CONNECTION_STRING)  
        return client  
    def iothub_client_telemetry_sample_run():  
        try:  
            client = iothub_client_init()  
            print ( "Sending data to IoT Hub, press Ctrl-C to exit" )  
            while True:  
                msg_txt_formatted = MSG_SND.format(temperature=temperature, humidity=humidity, co2 = eco2 )  
                message = Message(msg_txt_formatted)  
                print( "Sending message: {}".format(message) )  
                client.send_message(message)  
                print ( "Message successfully sent" )  
                time.sleep(3)  
        except KeyboardInterrupt:  
            print ( "IoTHubClient stopped" )  
    if __name__ == '__main__':  
        print ( "Press Ctrl-C to exit" )  
        iothub_client_telemetry_sample_run()
    time.sleep(5)