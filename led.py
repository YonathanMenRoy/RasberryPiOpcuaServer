RED_LED_REDEMPTION_PIN = 27
GREEN_LED_OUTPUT_LED = 22
BLUE_LED_OUTPUT_LED = 5

import asyncio
import RPi.GPIO as GPIO
import time
from asyncua import Server, ua

async def main():
    server = Server()
    await server.init()
    server.set_server_name("OPC UA YONATHAN")

    GPIO.setmode(GPIO.BCM)
    GPIO.setup(RED_LED_REDEMPTION_PIN, GPIO.OUT)
    GPIO.setup(RED_LED_REDEMPTION_PIN, GPIO.OUT)
    GPIO.setup(RED_LED_REDEMPTION_PIN, GPIO.OUT)

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

    async def activate_motor(parent):
        print("Motor is now on")
        await motor_is_on_variable_node.set_value(True)

    activate_motor_method_node = await motor1.add_method(address_namespace, "TurnOn", activate_motor, [], [ua.VariantType.Boolean])

    async with server:
        while True:
            result = instance.read()
            if result.is_valid():
                await temperature_variable_node.set_value(result.temperature)
                await asyncio.sleep(5)
            else:
                print("Error: %d" % result.error_code)
            time.sleep(3)

    print("Hello World!")

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        GPIO.cleanup()
        print("End")
# See PyCharm help at https://www.jetbrains.com/help/pycharm/
