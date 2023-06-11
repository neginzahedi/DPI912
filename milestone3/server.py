#!/usr/bin/python3

# ==============================================================================
#   Assignment:  Milestone 3
#
#   Author:  Fatemeh Zahedi
#   Language:  Python3
#   To Compile:  -
#
#   Class:  Python for Programmers: Sockets and Security - DPI912NSA
#   Professor:  Harvey Kaduri
#   Due Date:  June 11, 2023
#   Submitted:  June 11, 2023
#
# -----------------------------------------------------------------------------
#
#   Description: This script is for a server to generate lottery tickets (Max, 6/49, and Daily Grand) upon client requests.
#                The server listens for incoming connections and generates random tickets based on the requested type and quantity.
#
#   Collaboration:  -
#
#   Input: python3 server.py -H ::1 -p 8888 (default values)
#
#   Output: 
#           Server listening on [::1]:8888...
#           Accepted connection from [client_address]:client_port
#
#   Algorithm: This algorithm enables the server to handle multiple client connections concurrently 
#              and non-blockingly by forking child processes to handle each client request. 
#              The server listens for connections without blocking and uses signal handling
#              to prevent zombie processes.
#  
#   Required Features Not Included:  -
#   Known Bugs:  -
#   Classification: -
# ==============================================================================


import argparse
import random
import socket
import signal
import os
import errno
import fcntl
import logzero
import time
import atexit
import sys

from logzero import logger

PID_FILE = "server.pid"  # PID file name

class LotteryTicket:
    def __init__(self, ticketType, numbersPerTicket, numbersRange):
        self.ticketType = ticketType
        self.numbersPerTicket = numbersPerTicket
        self.numbersRange = numbersRange

class LotteryTicketGenerator:
    def __init__(self):
        self.lottoTicketTypes = {
            "max": LotteryTicket("LOTTO MAX", [7], 50),
            "6/49": LotteryTicket("LOTTO 6/49", [6], 49),
            "daily": LotteryTicket("DAILY GRAND", [5], 49)
        }
    
    def generateTickets(self, quantityOfTicket, typeOfTicket):
        tickets = []
        for _ in range(quantityOfTicket):
            ticket = []
            for length in typeOfTicket.numbersPerTicket:
                ticketSet = []
                ticketPool = list(range(1, typeOfTicket.numbersRange))
                remainingPool = len(ticketPool) - 1 if ticketPool else None
                for _ in range(length):
                    if ticketPool:
                        randomIndex = random.randint(0, remainingPool)
                        ticketSet.append(ticketPool.pop(randomIndex))
                        remainingPool -= 1
                ticket.append(ticketSet)
            tickets.append(ticket)
        return tickets

def processClientRequest(clientSocket, addr, ticketType, quantity):
    generator = LotteryTicketGenerator()
    
    try:
        tickets = generator.generateTickets(quantity, generator.lottoTicketTypes[ticketType])
        
        processedTickets = ""
        for i, ticket in enumerate(tickets, 1):
            processedTickets += f"{i}. {', '.join(map(str, ticket[0]))}\n"
        
        clientSocket.send(processedTickets.encode())
    
    except (ValueError, KeyError) as e:
        errorMessage = f"Error: {str(e)}"
        clientSocket.send(errorMessage.encode())
    
    clientSocket.close()

def runServer(host, port):
    serverSocket = socket.socket(socket.AF_INET6, socket.SOCK_STREAM)
    serverSocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    serverSocket.bind((host, port))
    serverSocket.listen(5)
    serverSocket.setblocking(False)

    logger.info(f"Server listening on [{host}]:{port}...")

    # Set up the signal handler for SIGCHLD
    signal.signal(signal.SIGCHLD, signalHandler) 

    while True:
        try:
            try:
                clientSocket, addr = serverSocket.accept()
                logger.info(f"Accepted connection from [{addr[0]}]:{addr[1]}")

                pid = os.fork()

                if pid == 0:
                    # Child process
                    serverSocket.close()  # Release socket in child process
                    handleClient(clientSocket, addr)
                    os._exit(os.EX_OK)  # Terminate child process

                else:
                    # Parent process
                    clientSocket.close()  # Release socket in parent process

            except socket.error as e:
                # Handle interrupted system call error
                if e.errno == errno.EINTR:
                    continue
                elif e.errno == errno.EAGAIN or e.errno == errno.EWOULDBLOCK:
                    # No more incoming connections, continue loop
                    continue
                else:
                    raise

        except KeyboardInterrupt:
            # Terminate the server on keyboard interrupt (Ctrl+C)
            logger.info("Server terminated.")
            break

    serverSocket.close()

def handleClient(clientSocket, addr):
    try:
        request = clientSocket.recv(1024).decode().strip()
        ticketType, quantity = request.split(',')
        processClientRequest(clientSocket, addr, ticketType, int(quantity))
    except (ValueError, KeyError) as e:
        errorMessage = f"Error: {str(e)}"
        clientSocket.send(errorMessage.encode())
    except socket.error as e:
        logger.error(f"Socket error occurred: {str(e)}")
    finally:
        clientSocket.close()

def signalHandler(signum, frame):
    # Collect exit status of terminated child processes
    while True:
        try:
            pid, status = os.waitpid(-1, os.WNOHANG)
            if pid == 0:
                # No more terminated child processes
                break
        except OSError:
            # No child processes
            break

def configure_logging():
    log_directory = "."  # Set the log directory to the current directory
    os.chdir(log_directory)  # Change directory to the log folder
    
    log_file = "server.log"
    logzero.logfile(log_file, maxBytes=1e6, backupCount=3)
    formatter = logzero.LogFormatter(fmt="%(asctime)s - %(levelname)s: %(message)s")
    logzero.formatter(formatter)
    logger.info("Server started.")

def write_pid_file():
    with open(PID_FILE, "w") as pid_file:
        pid_file.write(str(os.getpid()))

def remove_pid_file():
    os.remove(PID_FILE)

def is_server_running():
    if os.path.exists(PID_FILE):
        with open(PID_FILE, "r") as pid_file:
            pid = pid_file.read().strip()
            if pid:
                try:
                    os.kill(int(pid), 0)
                    return True
                except OSError:
                    pass
    return False

def start_server(args):
    if is_server_running():
        logger.error("Server is already running.")
        sys.exit(1)

    # Daemonize the process
    if os.fork():
        sys.exit(0)
    os.setsid()
    if os.fork():
        sys.exit(0)
    os.umask(0)

    # Redirect standard I/O to /dev/null
    null_file = "/dev/null"
    sys.stdin.close()
    sys.stdout = open(null_file, "a")
    sys.stderr = open(null_file, "a")

    # Write PID file
    write_pid_file()

    # Configure logging and register cleanup function
    configure_logging()
    atexit.register(stop_server)

    # Run the server
    runServer(args.host, args.port)

import time

def stop_server():
    if not is_server_running():
        logger.error("Server is not running.")
        sys.exit(1)

    # Read the PID from the file
    with open(PID_FILE, "r") as pid_file:
        pid = pid_file.read().strip()

    # Remove the PID file
    remove_pid_file()

    # Terminate the server process
    os.kill(int(pid), signal.SIGTERM)

    # Get the current timestamp
    timestamp = time.strftime("%y%m%d %H:%M:%S")

    # Log server stop event
    logger.info(f"{timestamp} - INFO: Server stopped.")

    # Append the log message to the log file
    with open("server.log", "a") as log_file:
        log_file.write(f"{timestamp} - INFO: Server stopped.\n")



def main():
    parser = argparse.ArgumentParser(description="Lottery Ticket Generator (Server)")
    parser.add_argument("-H", "--host", type=str, default="::1", help="Server IPv6 address (default is ::1)")
    parser.add_argument("-p", "--port", type=int, default=8888, help="Port number (default is 8888)")
    parser.add_argument("command", choices=["start", "stop"], help="Command to start or stop the server")
    args = parser.parse_args()

    if args.command == "start":
        start_server(args)
    elif args.command == "stop":
        stop_server()

if __name__ == "__main__":
    main()