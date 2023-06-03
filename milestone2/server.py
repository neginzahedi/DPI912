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

def runServer(host, port, pool_size):
    serverSocket = socket.socket(socket.AF_INET6, socket.SOCK_STREAM)
    serverSocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    serverSocket.bind((host, port))
    serverSocket.listen(5)
    print(f"Server listening on [{host}]:{port}...")

    while True:
        clientSocket, addr = serverSocket.accept()
        print(f"Accepted connection from [{addr[0]}]:{addr[1]}")

        pid = os.fork()
        if pid == 0:  # Child process
            serverSocket.close()
            request = clientSocket.recv(1024).decode().strip()
            ticketType, quantity = request.split(',')
            processClientRequest(clientSocket, addr, ticketType, int(quantity))
            os._exit(0)
        else:  # Parent process
            clientSocket.close()

def main():
    parser = argparse.ArgumentParser(description="Lottery Ticket Generator (Server)")
    parser.add_argument("-H", "--host", type=str, default="::1", help="Server IPv6 address (default is ::1)")
    parser.add_argument("-p", "--port", type=int, default=8888, help="Port number (default is 8888)")
    parser.add_argument("-s", "--pool-size", type=int, default=5, help="Listening pool size (default is 5)")
    args = parser.parse_args()
    runServer(args.host, args.port, args.pool_size)

if __name__ == "__main__":
    main()
