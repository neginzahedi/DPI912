import argparse
import socket
import signal
import os
from lottery import LotteryTicketGenerator

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
    print(f"Server listening on [{host}]:{port}...")

    while True:
        clientSocket, addr = serverSocket.accept()
        print(f"Accepted connection from [{addr[0]}]:{addr[1]}")

        pid = os.fork()

        if pid == 0:
            # Child process
            serverSocket.close()  # Release socket in child process

            request = clientSocket.recv(1024).decode().strip()
            ticketType, quantity = request.split(',')
            processClientRequest(clientSocket, addr, ticketType, int(quantity))
            
            clientSocket.close()  # Release socket in child process
            os._exit(os.EX_OK)  # Terminate child process

        else:
            # Parent process
            clientSocket.close()  # Release socket in parent process
            signal.signal(signal.SIGCHLD, signal.SIG_IGN)  # Prevent zombies

            
def main():
    parser = argparse.ArgumentParser(description="Lottery Ticket Generator (Server)")
    parser.add_argument("-H", "--host", type=str, default="::1", help="Server IPv6 address (default is ::1)")
    parser.add_argument("-p", "--port", type=int, default=8888, help="Port number (default is 8888)")
    args = parser.parse_args()
    runServer(args.host, args.port)

if __name__ == "__main__":
    main()
