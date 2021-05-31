from sensorclass import Sensor
from machine import Pin
from clock import clock
import time

# bigclock - analog led clock
# using new sensorclass with MQTT built in
# Started 10/1/2019

# motion sensor
motion = Sensor("motion", "IN", 12, onname="motion detected", offname="standby")
brightness = Sensor("brightness", initval=40)
lastmotion = time.time()


statusled = Sensor("led", "OUT", 2)
statusled.setstate(True)


def main():
    thistime = clock()
    lasttime = clock()
    thistime.second = 1
    lasttime.second = 0
    
    Sensor.MQTTSetup("bigclock")
    Sensor.lasthour = -1

    print("Waiting for time sync ...")
    secfade = time.ticks_ms()
    fadetime = 200
    tail = [0,0,0,0,0,0]
    sec = 0
    print("Waiting for time update ...")
    while Sensor.lasthour < 0:
        size = -2
        thistime.draw_hand(thistime.pose[sec], size , thistime.color_second, brightness.value)
        k = 1
        for i in tail:
            thistime.draw_hand(thistime.pose[i], size, thistime.color_second, int(brightness.value/len(tail) * (len(tail) - k ) ))
            k +=1
        tail.pop()
        tail.insert(0,sec)
        sec += 1
        if (sec > 11):
            sec = 0
        thistime.led.write()
        Sensor.Spin()
        time.sleep_ms(100)

    while True:
        if Sensor.lasthour >= 0:
            lasttime.hour = thistime.hour
            lasttime.minute = thistime.minute
            thistime.hour = Sensor.lasthour
            if thistime.hour > 11:
                thistime.hour = thistime.hour - 12
            thistime.minute = int(Sensor.lastminute / 5)
            Sensor.lasthour = -1
        Sensor.Spin()
        secbright = time.ticks_ms() - secfade 

        if secbright < fadetime:
            #thistime.draw_hand(start, len, color
            # Fade out last second hand
            thistime.draw_hand(thistime.pose[lasttime.second], thistime.len_second, thistime.color_second, int(brightness.value / 2 * (fadetime - secbright) / fadetime))
            # int(brightness * (fadetime - secbright) / fadetime))
            thistime.led.write()

        if secbright >= fadetime:
            # Turn off last second hand completely 
            thistime.draw_hand(thistime.pose[lasttime.second], thistime.len_second, thistime.color_second, 0)
            thistime.led.write()

        if secbright < (5 * fadetime): 
            # int(brightness * secbright / 1000)
            #color = [0,0,int(brightness * secbright / 1000)]
            # Brighten current second over 1 second time 
            thistime.draw_hand(thistime.pose[thistime.second], thistime.len_second, thistime.color_second, int(brightness.value * secbright / 1000))
            thistime.led.write()

        if secbright >= (5 * fadetime): 
            thistime.draw_hand(thistime.pose[thistime.second], thistime.len_second, thistime.color_second, brightness.value )
            thistime.led.write()

        if secbright > 5000:
            print("Current brightness: ", brightness)
            lasttime.second = thistime.second
            thistime.second = thistime.second + 1
            if thistime.second == 12:
                thistime.second = 0
            thistime.display(thistime.minute, thistime.hour, -1,brightness.value,brightness.value)
            secfade = time.ticks_ms()

