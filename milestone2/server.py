#!/usr/bin/python3

# ==============================================================================
#    Assignment:  Milestone 2

#   Author:  Fatemeh Zahedi
#   Language:  Python3
#   To Compile:  -

#   Class:  Python for Programmers: Sockets and Security - DPI912NSA
#   Professor:  Harvey Kaduri
#   Due Date:  Jun 4, 2023
#   Submitted:  Jun 4, 2023

# -----------------------------------------------------------------------------

#   Description: This script is for a server to generate lottery tickets (Max, 6/49, and Daily Grand) upon client requests.
#                The server listens for incoming connections and generates random tickets based on the requested type and quantity.

#   Collaboration:  -

#   Input: The server waits for client requests in the form of a string with the ticket type and quantity.

#   Output: The server responds with a string containing the generated tickets and sent it back to the client.

#   Algorithm:
#     1. Define LotteryTicket class to store ticket information.
#     2. Define LotteryTicketGenerator class to generate random tickets.
#     3. Extract ticket type and quantity from client request in processClientRequest function.
#     4. Use LotteryTicketGenerator to generate requested tickets.
#     5. Format the generated tickets as a string and Send processed tickets to client using client socket.
#     6. Close the client socket after sending the response.
#     7. The server listens for incoming connections and handles each client request sequentially.
#     8. The main function parses the command-line arguments to get the server's host and port and starts the server.


#   Required Features Not Included:  -

#   Known Bugs:  -

#   Classification: -

# ==============================================================================
import argparse
import random
import socket
import os
import signal
import sys

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

def runServer(host, port, poolSize):
    serverSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    serverSocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    serverSocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1)
    serverSocket.bind((host, port))
    serverSocket.listen(poolSize)
    print(f"Server listening on {host}:{port}...")
    
    def handleChildSignal(signum, frame):
        while True:
            try:
                # Loop through all child processes to prevent zombies
                pid, status = os.waitpid(-1, os.WNOHANG)
                if pid == 0:
                    break
                print(f"Child process {pid} terminated.")
            except OSError:
                break
    
    signal.signal(signal.SIGCHLD, handleChildSignal)
    
    while True:
        try:
            clientSocket, addr = serverSocket.accept()
            print(f"Accepted connection from {addr[0]}:{addr[1]}")
            
            pid = os.fork()
            
            if pid == 0:
                # Child process
                serverSocket.close()  # Close the server socket in the child process
                request = clientSocket.recv(1024).decode().strip()
                ticketType, quantity = request.split(',')
                processClientRequest(clientSocket, addr, ticketType, int(quantity))
                sys.exit(0)  # Terminate the child process
                
            else:
                # Parent process
                clientSocket.close()  # Close the client socket in the parent process
            
        except KeyboardInterrupt:
            print("Server terminated.")
            serverSocket.close()
            sys.exit(0)

def main():
    parser = argparse.ArgumentParser(description="Lottery Ticket Generator (Server)")
    parser.add_argument("-H", "--host", type=str, default="127.0.0.1", help="Server IP address (default is 127.0.0.1)")
    parser.add_argument("-p", "--port", type=int, default=8888, help="Port number (default is 8888)")
    parser.add_argument("-s", "--pool-size", type=int, default=5, help="Size of the listening pool (default is 5)")
    args = parser.parse_args()
    runServer(args.host, args.port, args.pool_size)

if __name__ == "__main__":
    main()
