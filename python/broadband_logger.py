#!/usr/bin/python
"""
Telnet into D-Link router, gather broadband usage figures and log them to a
database. This program should be scheduled to run at even intervals,
e.g. each hour.

Herminio Gonzalez, Sep 2013
"""

import socket
import time
import re

class RouterQuery:
    """Encapsulate access to router"""
    def __init__(self):
        self.router_addr = "10.0.0.2"
        self.telnet_port = 23
        self.username = "admin"
        self.password = open('pwd', 'r').read()
        self.router_command = "ifconfig ppp0.1"
        self.raw_data = None

    def retrieve_data(self):
        """Connect to router using telnet and run the 'ifconfig' command,
        capturing the output from that command. Uses the Python socket module
        TODO: consider changing to Python telnetlib
        """

        bufsize = 4096 # large enough to hold any response we are expecting

        socket.setdefaulttimeout(5) # 5 seconds is more than enough on this LAN

        try:
            # open a socket in streaming, blocking mode (the default)
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.connect((self.router_addr, self.telnet_port))

            # perform login
            time.sleep(0.1)
            s.recv(bufsize) # username prompt
            s.send(self.username + "\n")

            time.sleep(0.1)
            s.recv(bufsize) # password prompt
            s.send(self.password + "\n")

            time.sleep(0.1)
            reply = s.recv(bufsize) # should get a '>' prompt if all went ok

            if "Login incorrect" in reply:
                raise Exception("Login incorrect.")

            # execute 'ifconfig' on WAN port, get back results
            s.send(self.router_command + "\n")
            time.sleep(0.2)
            self.raw_data = s.recv(bufsize)

            if not 'bytes' in self.raw_data:
                raise Exception("Did not get byte counts from ifconfig.")

        except socket.error as e:
            print "Error connecting to host. %s" % e
        except Exception as e:
            print e
            raise
        finally:
            # close down telnet connection
            s.send("quit\n")
            s.shutdown(socket.SHUT_RDWR)
            s.close()

        return

    def parse_data(self):
        """Parse the string and extract the number of bytes coming in and out
        Output: tuple with 2 LONGs of the form (rxbytes, txbytes)

        a typical data_str looks like this:
    ifconfig ppp0.1
    ppp0.1  Link encap:Point-Point Protocol
            inet addr:105.228.74.129  P-t-P:105.224.96.1  Mask:255.255.255.255
            UP POINTOPOINT RUNNING NOARP MULTICAST  MTU:1492  Metric:1
            RX packets:29697256 errors:0 dropped:0 overruns:0 frame:0
            TX packets:25851485 errors:0 dropped:0 overruns:0 carrier:0
            collisions:0 txqueuelen:3
            RX bytes:2815336009 (2.6 GiB)  TX bytes:931425720 (888.2 MiB)
        """

        if self.raw_data is None:
            raise Exception("No data to parse.")

        # pull out the RX and TX values
        results = re.findall(r'bytes:(\d+)', self.raw_data)
        if len(results) == 2:
            rxbytes, txbytes = [long(r) for r in results]
        else:
            raise Exception("Could not find the RX/TX values in the data.")

        """ old method, not as succinct as using regexp:
        if "RX bytes:" in data_str:
            tmp = data_str.split("bytes:")[-2:]
            rxbytes = long( tmp[0].split("(")[0] )
            txbytes = long( tmp[1].split("(")[0] )
        else:
            raise Exception("Could not find the RX/TX values.")
        """
        return (rxbytes, txbytes)

    def run_tests(self):
        self.raw_data = 'ifconfig ppp0.1\r\nppp0.1          Link encap:Point-Point Protocol  \r\n                inet addr:105.228.74.129  P-t-P:105.224.96.1  Mask:255.255.255.255\r\n                UP POINTOPOINT RUNNING NOARP MULTICAST  MTU:1492  Metric:1\r\n                RX packets:29697256 errors:0 dropped:0 overruns:0 frame:0\r\n                TX packets:25851485 errors:0 dropped:0 overruns:0 carrier:0\r\n                collisions:0 txqueuelen:3 \r\n                RX bytes:2815336009 (2.6 GiB)  TX bytes:931425720 (888.2 MiB)\r\n\r\n > '
        rx, tx = self.parse_data()
        assert rx == 2815336009L and tx == 931425720L
        try:
            self.raw_data = ''
            rx, tx = self.parse_data()
        except Exception:
            pass
        try:
            rx, tx = self.parse_data('\xff\xfd\x01\xff\xfd!\xff\xfb\x01\xff\xfb\x03BCM96328 Broadband Router\r\nLogin: ')
        except Exception:
            pass
        print "All tests passed."


def log_data(readings, dbfilepath):
    """Do an SQL INSERT on the database table 'traffic'
    readings: tuple of received (rx) and transmitted (tx) bytes on the WAN port
    dbfilepath: path to sqlite database

    the traffic table was created as follows:
    CREATE TABLE IF NOT EXISTS traffic(
    timestamp TEXT PRIMARY KEY,
	rxbytes INTEGER,
	txbytes INTEGER);
    """
    import sqlite3

    rxbytes, txbytes = readings

    conn = sqlite3.connect(dbfilepath)
    c = conn.cursor()

    c.execute("INSERT INTO traffic VALUES(datetime('now'), ?, ?)",
              (rxbytes, txbytes))

    conn.commit()
    conn.close()

def main():
    rq = RouterQuery()
    #rq.run_tests()

    rq.retrieve_data()
    readings = rq.parse_data()
    print "readings = " , readings

    log_data(readings, "router.db")
    print "readings logged"

if __name__ == '__main__':
    main()
