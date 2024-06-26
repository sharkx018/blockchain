from blockchain import Blockchain
from utility.verfication import Verification
from wallet import Wallet


class Node:

    def __init__(self):
        # self.id = str(uuid4())
        # self.id = 'mukul'
        self.wallet = Wallet()
        self.wallet.create_keys()
        self.blockchain = Blockchain(self.wallet.public_key)

    def get_transaction_value(self):
        tx_recipient = input('Enter the recipient of the transaction: ')
        tx_amount = float(input('Your transaction amount please: '))

        return tx_recipient, tx_amount

    def get_user_choice(self):
        return input('Your choice: ')

    def print_blockchain_elements(self):
        # Output the blockchain list to the console
        for block in self.blockchain.get_chain():
            print('Outputting block')
            print(block)
        else:
            print('-' * 20)

    def listen_for_input(self):
        waiting_for_input = True

        while waiting_for_input:
            print('Please choose')
            print('1: Add a new transaction value')
            print('2: Mine a new block')
            print('3: Output the blockchain block')
            print('4: Check transactions validity')
            print('5: Create wallet')
            print('6: Load wallet')
            print('7: Save wallet Keys')
            # print('v: Verify the chain')
            print('q: Quit')

            user_choice = self.get_user_choice()

            print('-' * 10, 'Choice Registered', '-' * 10)

            if user_choice == '1':
                tx_data = self.get_transaction_value()
                recipient, amount = tx_data

                signature = self.wallet.sign_transaction(self.wallet.public_key, recipient, amount)

                if self.blockchain.add_transaction(recipient, self.wallet.public_key, signature, amount=amount):
                    print('Transaction added.')
                else:
                    print('Invalid transaction')
                print(self.blockchain.get_open_transactions())
            elif user_choice == '2':
                is_ok, msg = self.blockchain.mine_block()
                if not is_ok:
                    print(msg)
            elif user_choice == '3':
                self.print_blockchain_elements()
            elif user_choice == '4':
                if Verification.verify_transactions(self.blockchain.get_open_transactions(), self.blockchain.get_balance):
                    print('All transactions are valid.')
                else:
                    print('There are invalid transactions')
            elif user_choice == '5':
                self.wallet.create_keys()
                self.blockchain = Blockchain(self.wallet.public_key)
            elif user_choice == '6':
                self.wallet.load_keys()
                self.blockchain = Blockchain(self.wallet.public_key)

            elif user_choice == '7':
                self.wallet.save_keys()
            elif user_choice == 'q':
                waiting_for_input = False
            else:
                print('Input was invalid, please check the value from the list!')

            if not Verification.verify_chain(self.blockchain.get_chain()):
                self.print_blockchain_elements()
                break

            print('Balance of {}: {:6.2f}'.format(self.wallet.public_key, self.blockchain.get_balance()))
            # print("get_balance-->>", get_balance(owner))
        else:
            print('User Left!')

        print('Done!')


if __name__ == '__main__':
    node = Node()
    node.listen_for_input()
