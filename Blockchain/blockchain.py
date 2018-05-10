from functools import reduce
import hashlib as hl
import json
from hash_util import hash_block, hash_string_256
from collections import OrderedDict
import pickle


# Initializing the blockchain list
MINING_REWARD = 10

genesis_block = {'previous_hash': ' ',
                 'index': 0,
                 'transactions': [],
                 'proof': 100
                 }
blockchain = [genesis_block]
open_transactions = []
# Owner of this particular blockchain node
owner = 'John'
# Registered participants: Myself + other people that are sending/receiving
participant = {'John'}


def load_data():
    with open('blockchain.txt', mode='r') as f:
        # file_content = pickle.loads(f.read())
        
        file_content = f.readlines()
        global blockchain
        global open_transactions
        
        # blockchain = file_content['chain']
        # open_transactions = file_content['ot']

        blockchain = json.loads(file_content[0][:-1])

        updated_blockchain = []
        for block in blockchain:
            updated_block = {
                'previous_hash': block['previous_hash'],
                'index': block['index'],
                'proof': block['proof'],
                'transactions': [OrderedDict(
                    [('sender', tx['sender']), ('recipient', tx['recipient']), ('amount', tx['amount'])]) for tx in block['transactions']]
            }
            updated_blockchain.append(updated_block)
        blockchain = updated_blockchain

        open_transactions = json.loads(file_content[1])

        updated_transactions = []
        for tx in open_transactions:
            updated_transaction = OrderedDict(
                [('sender', tx['sender']), ('recipient',
                                            tx['recipient']), ('amount', tx['amount'])]
            )
            updated_transactions.append(updated_transaction)
        open_transactions = updated_transactions


load_data()


def save_data():
    with open('blockchain.txt', mode='w') as f:
        f.write(json.dumps(blockchain))
        f.write('\n')
        f.write(json.dumps(open_transactions))
        # save_data = {
        #     'chain': blockchain,
        #     'ot': open_transactions
        # }
        # f.write(pickle.dumps(save_data))


def valid_proof(transactions, last_hash, proof):
    guess = (str(transactions) + str(last_hash) + str(proof)).encode()
    guess_hash = hash_string_256(guess)
    print(guess_hash)
    return guess_hash[0:2] == '00'


def proof_of_work():
    last_block = blockchain[-1]
    last_hash = hash_block(last_block)
    proof = 0
    while not valid_proof(open_transactions, last_hash, proof):
        proof += 1
    return proof


def get_balance(participant):

    tx_sender = [[tx['amount'] for tx in block['transactions']
                  if tx['sender'] == participant] for block in blockchain]

    # Fetch a list of all sent coin amounts for the given person (empty lists are returned if the person was NOT the sender)
    # This fetchs sent amounts of open transactions (to avoid double spending)
    open_tx_sender = [tx['amount']
                      for tx in open_transactions if tx['sender'] == participant]
    tx_sender.append(open_tx_sender)
    amount_sent = reduce(
        lambda tx_sum, tx_amt: tx_sum + sum(tx_amt) if len(tx_amt) > 0 else tx_sum + 0, tx_sender, 0)

    # This fetches received coin amounts of transactions that were already included in the blocks
    # Ignoring open transactions here because you shouldn't be able to spend coins before the transaction was confirmed
    tx_recipient = [[tx['amount'] for tx in block['transactions']
                     if tx['recipient'] == participant] for block in blockchain]

    amount_received = reduce(
        lambda tx_sum, tx_amt: tx_sum + sum(tx_amt) if len(tx_amt) > 0 else tx_sum + 0, tx_recipient, 0)

    # Return the total balance
    return amount_received - amount_sent


def get_last_blockchain_value():
    """ Returns the last value of the current block. """

    # Creating a check to see if there's a starting transaction
    if len(blockchain) < 1:
        return None
    return blockchain[-1]


def verify_transaction(transaction):

    sender_balance = get_balance(transaction['sender'])
    return sender_balance >= transaction['amount']


def add_transaction(recipient, sender=owner, amount=1.0):
    """ Append a new value as well as the last block value to the blockchain 

    Arguments:
        :sender: The sender of the coins.
        :recipient: The recipient of the coins.
        :amount: The amount of coins sent with the transaction (default = 1.0)   
    """
    # transaction = {'sender': sender,
    #                'recipient': recipient,
    #                'amount': amount
    #                }

    transaction = OrderedDict(
        [('sender', sender), ('recipient', recipient), ('amount', amount)])

    if verify_transaction(transaction):
        open_transactions.append(transaction)
        participant.add(sender)
        participant.add(recipient)
        save_data()
        return True

    return False


def mine_block():
    """Create a new block and add open transactions to it."""

    # Fetch the last block of the blockchain
    last_block = blockchain[-1]

    # Hash the last block (=> to be able to compare it to the stored has value)
    hashed_block = hash_block(last_block)
    proof = proof_of_work()

    # Providing a reward for miners
    # reward_transaction = {
    #     'sender': 'MINING',
    #     'recipient': owner,
    #     'amount': MINING_REWARD
    # }
    reward_transaction = OrderedDict(
        [('sender', 'MINING'), ('recipient', owner), ('amount', MINING_REWARD)]
    )

    # Copy transaction instead of manipulating the original open_transactions
    copied_transactions = open_transactions[:]
    copied_transactions.append(reward_transaction)
    block = {'previous_hash': hashed_block,
             'index': len(blockchain),
             'transactions': copied_transactions,
             'proof': proof
             }
    blockchain.append(block)

    return True


def get_transaction_value():
    """ Returns the input of the user (a new transaction amount) as a float. """

    tx_recipient = input('Enter the recipientof the transaction: ')
    tx_amount = float(input('Your transaction amount please: '))

    return tx_recipient, tx_amount


def get_user_choice():

    user_input = input('Your choice: ')
    return user_input


def print_blockchain_elements():

    # Output the current blockchain list
    for block in blockchain:
        print('Outputting Block')
        print(block)

    else:
        print('-' * 20)


def verify_chain():

    for (index, block) in enumerate(blockchain):
        if index == 0:
            continue

        if block['previous_hash'] != hash_block(blockchain[index - 1]):
            return False

        if not valid_proof(block['transactions'][:-1], block['previous_hash'], block['proof']):
            print('PoW is invalid')
            return False
    return True


def verify_transactions():

    return all([verify_transaction(tx) for tx in open_transactions])


waiting_for_input = True


while waiting_for_input:

    print('Please choose')
    print('1: Add a new transaction value')
    print('2: Mine a new block')
    print('3: Output the blockchain blocks')
    print('4: Output participants')
    print('5: Check transaction validity')
    print('h: Manipulate the blockchain')
    print('q: Quit')

    user_choice = get_user_choice()

    if user_choice == '1':
        tx_data = get_transaction_value()
        recipient, amount = tx_data
        if add_transaction(recipient, amount=amount):
            print('Added Transactoin.')
        else:
            print('Transaction failed.')
        print(open_transactions)

    elif user_choice == '2':
        if mine_block():
            open_transactions = []
            save_data()

    elif user_choice == '3':
        print_blockchain_elements()

    elif user_choice == '4':
        print(participant)

    elif user_choice == '5':
        if verify_transactions:
            print('All transactions are valid.')
        else:
            print('There are invalid transactions.')

    elif user_choice == 'h':
        if len(blockchain) >= 1:
            blockchain[0] = {'previous_hash': ' ',
                             'index': 0,
                             'transactions': [{'sender': 'Chris', 'recipient': 'Max', 'amount': 100}]
                             }

    elif user_choice == 'q':
        waiting_for_input = False

    else:
        print('Input was invalid, please pick a value from the list!')

    if not verify_chain():
        print_blockchain_elements()
        print('Blockchain no longer valid')
        break
    print('Balace of {}: {:6.2f}'.format('John', get_balance('John')))
else:
    print('User left!')


print('Done!')
