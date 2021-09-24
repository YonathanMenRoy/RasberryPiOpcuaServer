TEMPERATURE_READER_PIN =17
RED_LED_REDEMPTION_PIN = 27
GREEN_LED_OUTPUT_LED = 22
BLUE_LED_OUTPUT_LED = 5

import asyncio
import RPi.GPIO as GPIO
import dht11
import time
from asyncua import Server, ua


async def main():
    server = Server()
    await server.init()
    server.set_server_name("OPC UA YONATHAN")

    GPIO.setmode(GPIO.BCM)
    instance = dht11.DHT11(TEMPERATURE_READER_PIN)
    GPIO.setup(RED_LED_REDEMPTION_PIN, GPIO.OUT)
    GPIO.setup(GREEN_LED_OUTPUT_LED, GPIO.OUT)
    GPIO.setup(BLUE_LED_OUTPUT_LED, GPIO.OUT)
    GPIO.output(RED_LED_REDEMPTION_PIN, GPIO.HIGH)
    GPIO.output(GREEN_LED_OUTPUT_LED, GPIO.HIGH)
    GPIO.output(BLUE_LED_OUTPUT_LED, GPIO.HIGH)

    url = "opc.tcp://10.4.1.135:4840"
    server.set_endpoint(url)
    server.set_security_policy([ua.SecurityPolicyType.NoSecurity,
                                ua.SecurityPolicyType.Basic256Sha256_SignAndEncrypt,
                                ua.SecurityPolicyType.Basic256Sha256_Sign])

    namespace = "OPCUA_SERVER"
    address_namespace = await server.register_namespace(namespace)
    motor1 = await server.nodes.objects.add_object(address_namespace, "Motor1")
    temperature_variable_node = await motor1.add_variable(address_namespace, "Temperature", 0, varianttype=ua.VariantType.Double)
    motor_is_on_variable_node = await motor1.add_variable(address_namespace, "isOn", False)
    led1 = await  server.nodes.objects.add_object(address_namespace, "Led1")
    red_variable_node = await led1.add_variable(address_namespace, "Red", False)
    green_variable_node = await led1.add_variable(address_namespace, "Green", False)
    blue_variable_node = await led1.add_variable(address_namespace, "Blue", False)
    await red_variable_node.set_writable(True)
    await green_variable_node.set_writable(True)
    await blue_variable_node.set_writable(True)


    async def deactivate_led(parent):
        print("Led is now off")
        GPIO.output(RED_LED_REDEMPTION_PIN, GPIO.HIGH)
        GPIO.output(GREEN_LED_OUTPUT_LED, GPIO.HIGH)
        GPIO.output(BLUE_LED_OUTPUT_LED, GPIO.HIGH)
        await red_variable_node.set_value(False)
        await green_variable_node.set_value(False)
        await blue_variable_node.set_value(False)

    async def activate_motor(parent):
        print("Motor is now on")
        await motor_is_on_variable_node.set_value(True)

    activate_motor_method_node = await motor1.add_method(address_namespace, "TurnOn", activate_motor, [], [ua.VariantType.Boolean])
    deactivate_led_method_node = await led1.add_method(address_namespace, "TurnOff", deactivate_led, [], [ua.VariantType.Boolean])

    async with server:
        while True:
            result = instance.read()
            if result.is_valid():
                await temperature_variable_node.set_value(result.temperature)
                await asyncio.sleep(5)
            else:
                print("Error: %d" % result.error_code)
            if await red_variable_node.read_value():
                print("Red")
                GPIO.output(RED_LED_REDEMPTION_PIN, GPIO.LOW)
            if await green_variable_node.read_value():
                print("Green")
                GPIO.output(GREEN_LED_OUTPUT_LED, GPIO.LOW)
            if await blue_variable_node.read_value():
                print("Blue")
                GPIO.output(BLUE_LED_OUTPUT_LED, GPIO.LOW)
            time.sleep(3)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        GPIO.cleanup()
        print("End")
# See PyCharm help at https://www.jetbrains.com/help/pycharm/
