import argparse
import random

class LotteryTicketGenerator:
    def __init__(self):
        self.lotto_ticket_types = {
            'max': {'name': 'Lotto Max', 'numbers_range': list(range(1, 50)), 'numbers_per_ticket': 7},
            '649': {'name': 'Lotto 649', 'numbers_range': list(range(1, 50)), 'numbers_per_ticket': 6},
            'daily': {'name': 'Daily Grand', 'numbers_range': list(range(1, 50)), 'numbers_per_ticket': 5}
        }

    def tickets_generator(self, ticket_type_key, quantity):
        if ticket_type_key not in self.lotto_ticket_types:
            raise ValueError(f"Invalid ticket type '{ticket_type_key}'")

        ticket_type = self.lotto_ticket_types[ticket_type_key]
        numbers_range = ticket_type['numbers_range']
        numbers_per_ticket = ticket_type['numbers_per_ticket']

        tickets = []
        for _ in range(quantity):
            ticket = random.sample(numbers_range, numbers_per_ticket)
            ticket.sort()
            tickets.append(ticket)

        return tickets

def display_tickets(tickets):
    for ticket in tickets:
        print(', '.join(map(str, ticket)))

def main():
    parser = argparse.ArgumentParser(description='Lottery Ticket Generator')
    parser.add_argument('-t', '--ticket_type', type=str, choices=['max', '649', 'daily'],
                        help='Ticket type: max (Lotto Max), 649 (Lotto 649), daily (Daily Grand)')
    parser.add_argument('-q', '--quantity', type=int, default=1,
                        help='Number of tickets to generate (default: 1)')

    args = parser.parse_args()

    if args.ticket_type is None:
        parser.print_help()
        return

    generator = LotteryTicketGenerator()

    ticket_type_key = args.ticket_type
    quantity = args.quantity

    try:
        tickets = generator.tickets_generator(ticket_type_key, quantity)
        display_tickets(tickets)
    except ValueError as e:
        print(f"Error: {str(e)}")

if __name__ == '__main__':
    main()
