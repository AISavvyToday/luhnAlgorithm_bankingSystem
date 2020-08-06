import random
import math
import sqlite3



def createCard():
    card_num = '400000'
    for i in range(9):
        n = str(random.sample(range(0,9), 1))
        card_num += n.strip(']').strip('[')
        i += 1
    pin = ''
    for i in range(4):
        n = str(random.sample(range(0,9), 1))
        pin += n.strip(']').strip('[')
        i += 1
    card_nums_list = [num for num in card_num]
    for i in range(0,15):
        if i % 2:
            continue
        else:
            card_nums_list[i] = str(int(card_num[i]) * 2)
    for i in range(len(card_nums_list)):
        num = int(card_nums_list[i])
        if num > 9:
            num -= 9
            card_nums_list[i] = str(num)
        else:
            card_nums_list[i] = str(num)
    ctr_num = 0
    for digit in card_nums_list:
        ctr_num += int(digit)
    check_sum = str(math.ceil(ctr_num / 10) * 10 - ctr_num)
    card_num += check_sum

    return card_num, pin


while True:
    conn = sqlite3.connect('card.s3db')
    cur = conn.cursor()
    cur.execute('CREATE TABLE IF NOT EXISTS card (id Integer PRIMARY KEY, number Text, pin Text, balance Integer Default 0);')
    conn.commit()
    action = input('''
1. Create an account
2. Log into account
0. Exit: ''')
    if action == '1':
        card_deets = createCard()
        insert_query = 'INSERT INTO card (number, pin) VALUES (?,?)'
        cur.execute(insert_query, card_deets)
        conn.commit()
        print('''
Your card has been created
Your card number:
{}
Your card PIN:
{}
'''.format(card_deets[0], card_deets[1]))

    elif action == '2':
        while True:
            print('\n')
            entered_card_num = input("Enter your card number: ")
            entered_pin = input("Enter your PIN: ")

            whole_table_query = 'SELECT * FROM card'
            cur.execute(whole_table_query)
            records = cur.fetchall()
            customer_pin = ''
            for row in records:
                if row[1] == entered_card_num:
                    customer_pin += row[2]

            if customer_pin == entered_pin:
                print('\n')
                print("You have successfully logged in!")
                while True:
                    do = input(
'''
1. Balance
2. Add income
3. Do transfer
4. Close account
5. Log out
0. Exit: ''')
                    if do == '1':
                        print('\n')
                        balance = list(cur.execute('SELECT balance FROM card WHERE number = ?', (entered_card_num,)))[0][0]
                        print("Balance: {}".format(balance))
                    elif do == '2':
                        amt_to_add = int(input('\nEnter income: '))
                        cur.execute('UPDATE card SET balance = balance + ? WHERE number = ?', (amt_to_add, entered_card_num))
                        conn.commit()
                        print('\nIncome was added!')

                    elif do == '3':
                        print('Transfer')

                        receiver_account_num = input('\nEnter card number: ')
                        check_sum_num = receiver_account_num[-1]
                        trans_acc = receiver_account_num[0:-1]
                        trans_acc_nums_list = [num for num in trans_acc]

                        for i in range(0,15):
                            if i % 2:
                                continue
                            else:
                                trans_acc_nums_list[i] = str(int(trans_acc_nums_list[i]) * 2)

                        for i in range(len(trans_acc_nums_list)):
                            num = int(trans_acc_nums_list[i])
                            if num > 9:
                                num -= 9
                                trans_acc_nums_list[i] = str(num)
                            else:
                                trans_acc_nums_list[i] = str(num)

                        acc_luhn_total = 0
                        for digit in trans_acc_nums_list:
                            acc_luhn_total += int(digit)

                        acc_luhn_total += int(check_sum_num)
                        if acc_luhn_total % 10 == 0:
                            all_account_numbers = list(cur.execute('SELECT number FROM card'))
                            bank_account_numbers = []
                            for num in all_account_numbers:
                                bank_account_numbers.append(num[0])

                            if receiver_account_num in bank_account_numbers:
                                if receiver_account_num == entered_card_num:
                                    print("You can't transfer money to the same account!")
                                else:
                                    transfer_amt = int(input('Enter how much money you want to transfer: '))
                                    acc_bal = list(cur.execute('SELECT balance FROM card WHERE number = ?', (entered_card_num,)))[0][0]
                                    if transfer_amt > acc_bal:
                                        print('Not enough money!')
                                    else:
                                        cur.execute('UPDATE card SET balance = balance + ? WHERE number = ?',(transfer_amt, receiver_account_num))
                                        cur.execute('UPDATE card SET balance = balance - ? WHERE number = ?',(transfer_amt, entered_card_num))
                                        conn.commit()
                                        print('Success!')


                            else:
                                print('Such a card does not exist.')

                        else:
                            print('Probably you made mistake in the card number. Please try again!')

                    elif do == '4':
                        cur.execute('DELETE FROM card WHERE number = ?',(entered_card_num,))
                        conn.commit()
                        print('The account has been closed!')
                        break

                    elif do == '5':
                        print('\n')
                        print("You have successfully logged out!")
                        break
                    elif do == '0':
                        print('Bye!')
                        exit()

            else:
                print('\n')
                print('Wrong card number or PIN!')
            break
    if action == '0':
        print('\n')
        print("Bye!")
        conn.close()
        break
