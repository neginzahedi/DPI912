import argparse
import os
import socket

def requestTickets(host, port, ticketType, quantity, identifier):
    clientSocket = socket.socket(socket.AF_INET6, socket.SOCK_STREAM)

    try:
        clientSocket.connect((host, port))

        request = f"{ticketType},{quantity}"
        clientSocket.send(request.encode())

        response = clientSocket.recv(1024).decode()
        print(response)

        if identifier:
            with open("GeneratedTickets.txt", "a") as file:
                if not os.path.isfile("GeneratedTickets.txt"):
                    file.write("Generated Tickets:\n")
                file.write(f"Identifier: {identifier}\n")
                file.write(f"Ticket Type: {ticketType}\n")
                file.write(response)
                file.write("\n")

    except ConnectionRefusedError:
        print("Connection refused. Make sure the server is running.")

    finally:
        clientSocket.close()

def generateRequests(host, port, ticketType, quantity, identifier, requests):
    for i in range(requests):
        pid = os.fork()

        if pid == 0:
            # Child process
            requestTickets(host, port, ticketType, quantity, f"{identifier}_{i+1}")
            os._exit(os.EX_OK)  # Terminate child process
            

def main():
    parser = argparse.ArgumentParser(description="Lottery Ticket Generator (Client)")
    parser.add_argument("-H", "--host", type=str, default="::1", help="Server IPv6 address (default is ::1)")
    parser.add_argument("-p", "--port", type=int, default=8888, help="Port number (default is 8888)")
    parser.add_argument("-t", "--ticket", type=str, default="max", help="Ticket type (default is max)")
    parser.add_argument("-q", "--quantity", type=int, default=1, help="Number of tickets per request (default is 1)")
    parser.add_argument("-i", "--identifier", type=str, default="none", help="Unique identifier")
    parser.add_argument("-n", "--requests", type=int, default=1, help="Number of requests (default is 1)")
    args = parser.parse_args()

    generateRequests(args.host, args.port, args.ticket, args.quantity, args.identifier, args.requests)

if __name__ == "__main__":
    main()
