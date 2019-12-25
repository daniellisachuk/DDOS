import pingparsing
import time
import sys

file = open('ping_p.txt', 'a+')
try:

    for _ in range(100):
        transmitter = pingparsing.PingTransmitter()
        transmitter.destination_host = sys.argv[1]
        transmitter.count = 1
        result = transmitter.ping()

        parser = pingparsing.PingParsing()
        parser.parse(result)

        file.write('{}, '.format(parser.rtt_max))
        time.sleep(5)
except KeyboardInterrupt:
    file.close()
