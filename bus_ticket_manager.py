import curses
import time
from curses import wrapper
import keyboard
import os
import mysql.connector as mc
import random
import csv
from datetime import datetime, timedelta, date

curses.initscr()
curses.start_color()

selected_color = box_color = unselected_color = success_color = fail_color = None


def initialize_color():
    curses.init_pair(1, curses.COLOR_BLACK, curses.COLOR_WHITE)
    curses.init_pair(2, curses.COLOR_WHITE, curses.COLOR_BLACK)
    curses.init_pair(3, curses.COLOR_BLACK, curses.COLOR_GREEN)
    curses.init_pair(4, curses.COLOR_RED, curses.COLOR_BLACK)

    global selected_color
    global unselected_color
    global success_color
    global fail_color
    global box_color

    selected_color = box_color = curses.color_pair(1)
    unselected_color = curses.color_pair(2)
    success_color = curses.color_pair(3)
    fail_color = curses.color_pair(4)


def clear_full_screen(stdscr):
    stdscr.clear()
    stdscr.attron(selected_color)
    stdscr.border()
    stdscr.attroff(selected_color)
    stdscr.refresh()

def create_center_window(width, height):
    term_size = list(os.get_terminal_size())
    x = int((term_size[0] - width) / 2)
    y = int((term_size[1] - height) / 2)
    win = curses.newwin(height, width, y, x)

    return win

def create_menu_box(stdscr,heading,options, preselect_index=0):
    global unselected_color
    global success_color
    global fail_color
    global box_color
    clear_full_screen(stdscr)
    selected_index = preselect_index
    height = len(options) + 6
    max_str = heading
    for i in options:
        if len(i) > len(max_str):
            max_str = i
            
    width = len(max_str) + 6

    win = create_center_window(width, height)
    win.keypad(True)
    win.nodelay(False)

    while True:
        win.clear()
        win.attron(box_color)
        win.box()
        win.attroff(box_color)
        win.addstr(2,3,heading, curses.A_UNDERLINE | curses.A_BOLD)
        for i in range(len(options)):
            if i == selected_index:
                win.addstr(i + 4, 3, options[i], selected_color)
            else:
                win.addstr(i + 4, 3, options[i], unselected_color)

        win.refresh()
        key = keyboard.read_key()
        if keyboard.is_pressed("up"):
            selected_index -= 1
            if selected_index < 0:
                selected_index = 0

        elif keyboard.is_pressed("down"):
            selected_index += 1
            if selected_index > len(options) - 1:
                selected_index = len(options) - 1

        if keyboard.is_pressed("enter"):
            return selected_index, options[selected_index]
        time.sleep(1/60)

def create_form_window(heading,fields, fail_message,stdscr, login=False):
    global unselected_color
    global success_color
    global fail_color
    global box_color

    #clear_full_screen(stdscr)

    height = len(fields) + 9

    win = create_center_window(80, height)
    win.nodelay(True)
    pressed_up = pressed_down = pressed_enter = False

    alnumspace = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ1234567890. '

    selected_index = 0
    time.sleep(0.2)
    clear_full_screen(stdscr)
    while True:
        win.clear()
        win.attron(selected_color)
        win.box()
        win.attroff(selected_color)

        win.addstr(height - 3, 3, "Press enter after entering info")
        win.addstr(height - 4, 3, fail_message, fail_color)

        row = 0
        for i in fields:
            if row == selected_index :
                if login == True and selected_index==1:
                    win.addstr(row + 4, 3, i + ' : ' + len(str(fields[i]))*'*', selected_color)

                else:
                    win.addstr(row + 4, 3, i + ' : ' + str(fields[i]), selected_color)
            else:
                win.addstr(row + 4, 3, i + ' : ' + str(fields[i]), unselected_color)

            row += 1
        win.addstr(2,3,heading, curses.A_UNDERLINE | curses.A_BOLD)

        win.refresh()
        try:
            key = win.getkey()
        except:
            key = None

        if keyboard.is_pressed("up"):
            if not pressed_up:
                selected_index -= 1
                if selected_index < 0:
                    selected_index = 0
                pressed_up = True
        else:
            pressed_up = False

        if keyboard.is_pressed("down"):
            if not pressed_down:
                selected_index += 1
                if selected_index > len(fields.keys()) - 1:
                    selected_index = len(fields.keys()) - 1
                pressed_down = True

        else:
            pressed_down = False

        if keyboard.is_pressed("enter"):
            return fields

        if key != None and (key in alnumspace or key == ' '):
            fields[list(fields.keys())[selected_index]] += str(key)

        elif key != None and key == '\b':
            fields[list(fields.keys())[selected_index]] = str(fields[list(fields.keys())[selected_index]])[:-1]

        time.sleep(1/60)

def login(stdscr):
    global selected_color
    global unselected_color
    global success_color
    global fail_color
    global box_color

    connected = None

    while True:
        f = open("users.csv", 'r', newline='\r\n')
        ro = csv.DictReader(f)
        if connected == False:
            login_info = create_form_window("BUS TICKET MANAGEMENT SYSTEM",
                                            {"User ID" : '', "Password" : ''},
                                            'Invalid Login',
                                            stdscr,
                                            login=True
                                            )
        else:
            login_info = create_form_window("BUS TICKET MANAGEMENT SYSTEM",
                                            {"User ID" : '', "Password" : ''},
                                            '',
                                            stdscr,
                                            login=True
                                            )
        for i in ro:
            if i["User_ID"] == login_info["User ID"] and i["Password"] == login_info["Password"]:
                co = mc.connect(host='localhost', user="root", password="raju")
                if co.is_connected():
                    connected = True
                    cursor_obj = co.cursor()
                    cursor_obj.execute("CREATE DATABASE IF NOT EXISTS passengers")
                    cursor_obj.execute("USE passengers")

                    cursor_obj.execute(
                        "CREATE TABLE IF NOT EXISTS info(Ticket_no VARCHAR(20),Name VARCHAR(40), Age INT, Phone_no CHAR(10), Seat_no INT, Starting_Point VARCHAR(50), Ending_Point VARCHAR(50), Board_Time VARCHAR(7),Booking_Date DATE, Board_Date DATE, Money INT)"
                    )
                    co.close()
                    return login_info
        else:
            connected = False

def select_seat(stdscr, pas_info):
    coloumn = 4
    height = 5

    term_size = list(os.get_terminal_size())
    start_x = int((term_size[0] - 30) / 2)
    start_y = int((term_size[1] - 20) / 2)
    box_side = 5
    seats = []

    global selected_color
    global success_color
    selected_seat = [0, 0]

    curses.curs_set(False)
    selected_number = 0
    main_win = curses.newwin(height + 28, coloumn + 27, start_y - 4, start_x - 3)
    main_win.attron(selected_color)
    main_win.box()
    main_win.attroff(selected_color)
    main_win.addstr(2,3,"Available seats", curses.A_UNDERLINE)

    clear_full_screen(stdscr)
    conn_obj = mc.connect(host='localhost', user="root", password="raju")
    cursor_obj = conn_obj.cursor(dictionary=True)
    cursor_obj.execute("USE passengers")
    cursor_obj.execute("SELECT * FROM info")
    l = cursor_obj.fetchall()

    print_message = None
    while True:
        counter = 0
        if print_message == True:
            main_win.addstr(30, 2 ,"This seat has been selected",fail_color)
        main_win.refresh()

        for y in range(height):
            for x in range(coloumn):
                if x <= 1:
                    win = curses.newwin(box_side, box_side, (y * box_side + start_y), (x * box_side + start_x))
                else:
                    win = curses.newwin(box_side, box_side, (y * box_side + start_y), (x * box_side + 5 + start_x))

                for i in l:
                    if (
                            i["Seat_no"] == counter
                            and i["Board_Time"] == pas_info["Board_Time"]
                            and i["Starting_Point"] == pas_info["Starting_Point"]
                            and i["Ending_Point"] == pas_info["Ending_Point"]
                            and str(i["Board_Date"]) == pas_info["Board_Date"]
                    ):
                        win.attron(success_color)
                print()
                if [y, x] == selected_seat:
                    selected_number = counter
                    win.attron(selected_color)

                win.box()
                stdscr.addstr(start_y - 2, start_x, "Select seat to book :", curses.A_UNDERLINE)

                win.addstr(2, 2, str(counter))

                win.refresh()

                counter += 1
                win.attroff(success_color)
                win.attroff(selected_color)

        keyboard.read_key()

        if keyboard.is_pressed("up"):
            selected_seat[0] -= 1
            if selected_seat[0] < 0:
                selected_seat[0] = 0

        if keyboard.is_pressed("down"):
            selected_seat[0] += 1
            if selected_seat[0] > height - 1:
                selected_seat[0] = height - 1

        if keyboard.is_pressed("left"):
            selected_seat[1] -= 1
            if selected_seat[1] < 0:
                selected_seat[1] = 0

        if keyboard.is_pressed("right"):
            selected_seat[1] += 1
            if selected_seat[1] > coloumn - 1:
                selected_seat[1] = coloumn - 1

        if keyboard.is_pressed("enter"):
            for i in l:
                if (
                        selected_number == i["Seat_no"]
                        and i["Board_Time"] == pas_info["Board_Time"]
                        and i["Starting_Point"] == pas_info["Starting_Point"]
                        and i["Ending_Point"] == pas_info["Ending_Point"]
                        and str(i["Board_Date"]) == pas_info["Board_Date"]):

                    print_message = True
                    break
            else:
                return selected_number
            time.sleep(0.2)

        time.sleep(1 / 60)

def book_ticket(stdscr, log_info):
    co = mc.connect(host='localhost', user="root", password="raju", database='passengers')
    cur_obj = co.cursor()

    if cur_obj.rowcount == 20:
        conformation_window(stdscr, "All seats have been filled")
        return
    info = {}
    start_places = [
                    "Lal Bagh Stop - Bangalore",
                    "VGP Snow Kingdom Stop - Chennai",
                    "Salar Jung Museum - Hyderabad"
    ]
    info['Starting_Point'] = create_menu_box(stdscr, "CHOOSE START POINT :", start_places)[1]
    end_places = []
    for i in start_places:
        if i not in info['Starting_Point']:
            end_places.append(i)

    info['Ending_Point'] = create_menu_box(stdscr, "CHOOSE END POINT :", end_places)[1]
    info['Board_Time'] = create_menu_box(stdscr, "CHOOSE BOARDING TIME :",["6:00 am", "4:00 pm"])[1]

    dates = []
    for i in range(11):
        dates.append(str(date.today() + timedelta(i)))

    info['Board_Date'] = create_menu_box(stdscr, "CHOOSE BOARDING DATE",dates)[1]
    validity = True
    passenger = {"Name":'', "Age": '',"Phone_no":''}

    def is_valid_name(name):
        check_dot = 0
        if name == '':
            return False
        for i in name:
            if i == '.':
                check_dot += 1
            if i.isdigit() or not (i.isalnum() or i.isspace()) or check_dot > 1 :
                break
        else:
            return True

    def is_valid_age(age):
        age = str(age)
        if len(age) > 2 or len(age) == 0 or not age.isdigit():
            return False
        else:
            return True

    def is_valid_phone_no(no):
        no = str(no)
        if no == '':
            return False
        for i in no:
            if len(no) != 10 or not no.isdigit():
                return False

        else:
            return True

    def is_valid_name2(name):
        if name == '':
            return False

        elif name.count('.') > 1:
            return False


        for k in name:
            if k in '1234567890':
                return False
        else:
            return True



    def generate_ticket_no():
        ticket_no = 'RDR'
        for i in range(random.randint(2, 4)):
            ticket_no += str(random.randint(1,9))
        return ticket_no

    val_string = ''
    while validity:
        passenger = create_form_window("Passenger Details :",
                                       passenger,
                                       val_string,
                                       stdscr
                                       )
        validity = False
        val_string = ''
        if not is_valid_age(passenger["Age"]):
            val_string += "Age ,"
            passenger["Age"] = ''
            validity = True

        if not is_valid_name2(passenger["Name"]):
            val_string += "Name ,"
            passenger["Name"] = ''
            validity = True

        if not is_valid_phone_no(passenger["Phone_no"]):
            val_string += "Phone no ,"
            passenger["Phone_no"] = ''
            validity = True

        val_string += "is not valid"

    info.update(passenger)
    print(info)

    ### after getting the information about the passenger
    seat_no = select_seat(stdscr, info)
    info["Seat_no"] = seat_no
    print('\t', info["Seat_no"])
    info["Ticket_no"] = generate_ticket_no()
    info['Booking_Date'] = str(date.today())

    if info["Starting_Point"] == "Lal Bagh Stop - Bangalore":
        if info["Ending_Point"] == "VGP Snow Kingdom Stop - Chennai":
            info["Money"] = 740
        if info["Ending_Point"] == "Salar Jung Museum - Hyderabad":
            info["Money"] = 800

    if info["Starting_Point"] == "VGP Snow Kingdom Stop - Chennai":
        if info["Ending_Point"] == "Lal Bagh Stop - Bangalore":
            info["Money"] = 740
        if info["Ending_Point"] == "Salar Jung Museum - Hyderabad":
            info["Money"] = 1200

    if info["Starting_Point"] == "Salar Jung Museum - Hyderabad":
        if info["Ending_Point"] == "VGP Snow Kingdom Stop - Chennai":
            info["Money"] = 1200
        if info["Ending_Point"] == "Lal Bagh Stop - Bangalore":
            info["Money"] = 800

    height = len(info)
    clear_full_screen(stdscr)
    win = create_center_window(80,height + 9)
    win.attron(selected_color)
    win.box()
    win.attroff(selected_color)

    win.addstr(2,3,"TICKET", curses.A_UNDERLINE | curses.A_REVERSE)
    counter = 0
    for i in info:
        win.addstr(counter + 4, 3, i + " : " + str(info[i]))
        counter += 1
    win.addstr(counter + 6, 3, "Press enter key to continue", curses.A_UNDERLINE | curses.A_REVERSE)
    win.refresh()
    time.sleep(0.2)
    while True:
        key = keyboard.read_key()
        if key == 'enter':
            break
    co = mc.connect(host='localhost', user="root", password="raju", database='passengers')
    cursor_obj = co.cursor(dictionary=True)
    cursor_obj.execute("INSERT INTO info VALUES(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)", (
        info["Ticket_no"], info["Name"], info["Age"], info["Phone_no"], info["Seat_no"], info["Starting_Point"],
        info["Ending_Point"], info["Board_Time"], info["Booking_Date"], info["Board_Date"], info["Money"]))
    co.commit()
    co.close()

def cancel_ticket(stdscr, log_info):
    print_message = False
    running = True

    while running:
        co = mc.connect(host='localhost', user="root", password="raju", database='passengers')
        cursor_obj = co.cursor(dictionary=True)

        if print_message == False:
            ticket_no = create_form_window("Enter ticket no to cancel", {"Ticket_no":''},'',stdscr)
        else:
            ticket_no = create_form_window("Enter ticket no to cancel", {"Ticket_no":''},'No such ticket no exists',stdscr)

        cursor_obj.execute("SELECT * FROM info")
        l = cursor_obj.fetchall()

        for i in l:
            if i["Ticket_no"] == ticket_no["Ticket_no"]:
                cursor_obj.execute('DELETE FROM info WHERE Ticket_no="' + ticket_no["Ticket_no"] + '"')
                co.commit()
                running = False
                break
        else:
            print_message = True

        co.close()
def generate_ticket(stdscr, log_info):
    print_message = False
    info = {}
    running = True
    while running:
        co = mc.connect(host='localhost', user="root", password="raju", database='passengers')
        cursor_obj = co.cursor(dictionary=True)
        if print_message == False:
            ticket_no = create_form_window("Enter ticket no",{"Ticket_no" : ''},'', stdscr)

        else:
            ticket_no = create_form_window("Enter ticket no", {"Ticket_no" : ""}, 'No such ticket no found', stdscr)

        cursor_obj.execute("SELECT * FROM info")
        l = cursor_obj.fetchall()

        for i in l:
            if i["Ticket_no"] == ticket_no["Ticket_no"]:
                info = i
                running = False
                break
        else:
            print_message = True
        co.close()

    height = len(info)
    time.sleep(0.2)
    clear_full_screen(stdscr)
    win = create_center_window(80,height + 9)
    win.attron(selected_color)
    win.box()
    win.attroff(selected_color)

    win.addstr(2,3,"TICKET", curses.A_UNDERLINE | curses.A_REVERSE)
    counter = 0
    for i in info:
        win.addstr(counter + 4, 3, i + " : " + str(info[i]))
        counter += 1
    win.addstr(counter + 6, 3, "Press enter key to continue", curses.A_UNDERLINE | curses.A_REVERSE)
    win.refresh()

    while True:
        key = keyboard.read_key()
        if key == 'enter':
            break

def display_all_passengers(stdscr, log_info):
    co = mc.connect(host='localhost', user="root", password="raju", database='passengers')
    cursor_obj = co.cursor()

    cursor_obj.execute("SELECT * FROM info")
    l = cursor_obj.fetchall()

    time.sleep(0.2)

    headings = ('TICKET NO', 'NAME', 'AGE', 'PHONE NO', 'SEAT NO', 'STARTING POINT', 'ENDING POINT', 'BOARD TIME', 'BOOKING DATE', 'BOARDING DATE', 'MONEY')

    l = [headings] + [('','','','','','','','','','','')] + l

    max_strings = []
    for i in range(len(l[0])):
        max_strings.append('')
        for j in range(len(l)):
            if len(str(l[j][i])) > len(max_strings[i]):
                max_strings[i] = str(l[j][i])

    width = 0
    for i in max_strings:
        width += len(i)
    width += 17
    clear_full_screen(stdscr)
    win = create_center_window(width, cursor_obj.rowcount + 8)
    win.move(2,2)
    counter = 3


    for i in l:
        for j in range(len(i)):
            if counter == 3:
                win.attron(selected_color)
            win.addstr('|' + str(i[j]) + (' ' * (len(max_strings[j]) - len(str(i[j])))))
            win.attroff(selected_color)

        win.move(counter, 2)
        counter += 1

    win.addstr(counter, 3, "Press enter key to continue")
    win.attron(selected_color)
    win.box()
    win.attroff(selected_color)
    win.refresh()

    while True:
        key = keyboard.read_key()
        if key == "enter":
            break

def modify_ticket(stdscr ,log_info):
    print_message = False
    running = True
    while running:
        co = mc.connect(host='localhost', user="root", password="raju", database='passengers')
        cursor_obj = co.cursor(dictionary=True)

        if print_message == False:
            ticket_no = create_form_window("Enter ticket no to modify", {"Ticket_no":''},'',stdscr)
        else:
            ticket_no = create_form_window("Enter ticket no to modify", {"Ticket_no":''},'No such ticket no exists',stdscr)

        cursor_obj.execute("SELECT * FROM info")
        l = cursor_obj.fetchall()

        co.close()
        for i in l:
            if i["Ticket_no"] == ticket_no["Ticket_no"]:
                print(i)
                co = mc.connect(host='localhost', user="root", password="raju",
                                database='passengers')
                cursor_obj = co.cursor(dictionary=True)
                cursor_obj.execute("DELETE FROM info WHERE Ticket_no=%s", (i["Ticket_no"],))
                co.commit()
                # write code to modify ticket
                info = {}
                start_places = [
                    "Lal Bagh Stop - Bangalore",
                    "VGP Snow Kingdom Stop - Chennai",
                    "Salar Jung Museum - Hyderabad"
                ]
                info['Starting_Point'] = create_menu_box(stdscr, "CHOOSE START POINT :", start_places, start_places.index(i["Starting_Point"]))[1]
                end_places = []
                for j in start_places:
                    if j not in info['Starting_Point']:
                        end_places.append(j)

                try:
                    info['Ending_Point'] = create_menu_box(stdscr, "CHOOSE END POINT :", end_places, end_places.index(i["Ending_Point"]))[1]
                except:
                    info['Ending_Point'] = create_menu_box(stdscr, "CHOOSE END POINT :", end_places)[1]


                info['Board_Time'] = create_menu_box(stdscr, "CHOOSE BOARDING TIME :", ["6:00 am", "4:00 pm"])[1]

                dates = []
                for x in range(11):
                    dates.append(str(date.today() + timedelta(x)))

                try:
                    info['Board_Date'] = create_menu_box(stdscr, "CHOOSE BOARDING DATE", dates, dates.index(str(i["Board_Time"])))[1]
                except:
                    info['Board_Date'] = create_menu_box(stdscr, "CHOOSE BOARDING DATE", dates)[1]

                validity = True
                passenger = {"Name": i["Name"], "Age": i["Age"], "Phone_no": i["Phone_no"]}

                def is_valid_name2(name):
                    if name == '':
                        print("not valid")
                        return False

                    elif name.count('.') > 1:
                        print(name.find('.'))
                        print("dot dot")
                        print(name)
                        return False

                    for k in name:
                        if k in '1234567890':
                            return False
                    else:
                        return True



                def is_valid_name(name):
                    if name == '':
                        print("not valid")
                    else:
                        check_dot = 0
                        for i in name:
                            if i == '.':
                                check_dot += 1
                            if (i.isalpha() or i == '.' or i.isspace()) and check_dot <= 1:
                                pass
                            else:
                                return False

                        else:
                            return True

                def is_valid_age(age):
                    age = str(age)
                    if len(age) > 2 or len(age) == 0 or not age.isdigit():
                        return False
                    else:
                        return True

                def is_valid_phone_no(no):
                    no = str(no)
                    if no == '':
                        return False

                    for i in no:
                        if len(no) != 10 or not no.isdigit():
                            return False

                    else:
                        return True

                val_string = ''
                while validity:
                    passenger = create_form_window("Passenger Details :",
                                                   passenger,
                                                   val_string,
                                                   stdscr
                                                   )
                    validity = False
                    val_string = ''
                    if not is_valid_age(passenger["Age"]):
                        val_string += "Age ,"
                        passenger["Age"] = ''
                        validity = True

                    if not is_valid_name2(passenger["Name"]):
                        val_string += "Name ,"
                        passenger["Name"] = ''
                        validity = True

                    if not is_valid_phone_no(passenger["Phone_no"]):
                        val_string += "Phone no ,"
                        passenger["Phone_no"] = ''
                        validity = True

                    val_string += "is not valid"

                info.update(passenger)
                print(info)

                ### after getting the information about the passenger
                seat_no = select_seat(stdscr, info)
                info["Seat_no"] = seat_no

                info["Ticket_no"] = i["Ticket_no"]

                info['Booking_Date'] = str(date.today())

                if info["Starting_Point"] == "Lal Bagh Stop - Bangalore":
                    if info["Ending_Point"] == "VGP Snow Kingdom Stop - Chennai":
                        info["Money"] = 740
                    if info["Ending_Point"] == "Salar Jung Museum - Hyderabad":
                        info["Money"] = 800

                if info["Starting_Point"] == "VGP Snow Kingdom Stop - Chennai":
                    if info["Ending_Point"] == "Lal Bagh Stop - Bangalore":
                        info["Money"] = 740
                    if info["Ending_Point"] == "Salar Jung Museum - Hyderabad":
                        info["Money"] = 1200

                if info["Starting_Point"] == "Salar Jung Museum - Hyderabad":
                    if info["Ending_Point"] == "VGP Snow Kingdom Stop - Chennai":
                        info["Money"] = 1200
                    if info["Ending_Point"] == "Lal Bagh Stop - Bangalore":
                        info["Money"] = 800
                co = mc.connect(host='localhost', user="root", password="raju",
                                database='passengers')
                cursor_obj = co.cursor(dictionary=True)
                cursor_obj.execute("INSERT INTO info VALUES(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)", (
                    info["Ticket_no"], info["Name"], info["Age"], info["Phone_no"], info["Seat_no"],
                    info["Starting_Point"],
                    info["Ending_Point"], info["Board_Time"], info["Booking_Date"], info["Board_Date"], info["Money"]))
                co.commit()
                co.close()
                #-----------------------------

                running = False
                break
        else:
            print_message = True

        co.close()
    pass

def conformation_window(stdscr, message):
    create_menu_box(stdscr,"CONFORMATION MESSAGE" ,[message])


def check_availability(stdscr):

    co = mc.connect(host='localhost', user="root", password="raju", database='passengers')
    cur = co.cursor()

    if cur.rowcount == 20:
        conformation_window(stdscr, "All seats have been filled")
        return
    info = {}
    start_places = [
        "Lal Bagh Stop - Bangalore",
        "VGP Snow Kingdom Stop - Chennai",
        "Salar Jung Museum - Hyderabad"
    ]
    info['Starting_Point'] = create_menu_box(stdscr, "CHOOSE START POINT :", start_places)[1]
    end_places = []
    for i in start_places:
        if i not in info['Starting_Point']:
            end_places.append(i)

    info['Ending_Point'] = create_menu_box(stdscr, "CHOOSE END POINT :", end_places)[1]
    info['Board_Time'] = create_menu_box(stdscr, "CHOOSE BOARDING TIME :",["6:00 am", "4:00 pm"])[1]

    dates = []
    for i in range(11):
        dates.append(str(date.today() + timedelta(i)))

    info['Board_Date'] = create_menu_box(stdscr, "CHOOSE BOARDING DATE",dates)[1]

 ###########################################
    coloumn = 4
    height = 5

    term_size = list(os.get_terminal_size())
    start_x = int((term_size[0] - 30) / 2)
    start_y = int((term_size[1] - 20) / 2)
    box_side = 5
    seats = []

    global selected_color
    global success_color
    selected_seat = [0, 0]

    curses.curs_set(False)
    selected_number = 0
    main_win = curses.newwin(height + 28, coloumn + 27, start_y - 4, start_x - 3)
    main_win.attron(selected_color)
    main_win.box()
    main_win.attroff(selected_color)
    main_win.addstr(2,3,"Select seat", curses.A_UNDERLINE)

    clear_full_screen(stdscr)
    conn_obj = mc.connect(host='localhost', user="root", password="raju")
    cursor_obj = conn_obj.cursor(dictionary=True)
    cursor_obj.execute("USE passengers")
    cursor_obj.execute("SELECT * FROM info")
    l = cursor_obj.fetchall()

    print_message = None
    while True:
        counter = 0
        selected_seats = 0
        main_win.refresh()

        for y in range(height):
            for x in range(coloumn):
                if x <= 1:
                    win = curses.newwin(box_side, box_side, (y * box_side + start_y), (x * box_side + start_x))
                else:
                    win = curses.newwin(box_side, box_side, (y * box_side + start_y), (x * box_side + 5 + start_x))

                for i in l:
                    if (
                            i["Seat_no"] == counter
                            and i["Board_Time"] == info["Board_Time"]
                            and i["Starting_Point"] == info["Starting_Point"]
                            and i["Ending_Point"] == info["Ending_Point"]
                            and str(i["Board_Date"]) == info["Board_Date"]
                    ):
                        win.attron(success_color)
                        selected_seats += 1

                win.box()
                win.addstr(2, 2, str(counter))
                win.attroff(success_color)
                win.refresh()

                counter += 1

        print(selected_seats)
        main_win.addstr(30, 2, "Available seats : " + str(20 - selected_seats))
        main_win.refresh()
        keyboard.read_key()

        if keyboard.is_pressed("enter"):
            time.sleep(0.2)
            break
def serach_name(stdscr):
    co = mc.connect(host='localhost', user='root', password='raju', database='passengers')
    cur = co.cursor()
    name = create_form_window("Enter name",{"Name" : ''},"",stdscr)
    print(name["Name"])
    query = "SELECT * FROM info WHERE Name = '%s'" % (name["Name"],)
    print(query)
    cur.execute(query)
    l = cur.fetchall()

    if l == []:
        conformation_window(stdscr,"no such name found")
        return

    time.sleep(0.2)

    headings = ('TICKET NO', 'NAME', 'AGE', 'PHONE NO', 'SEAT NO', 'STARTING POINT', 'ENDING POINT', 'BOARD TIME', 'BOOKING DATE', 'BOARDING DATE', 'MONEY')

    l = [headings] + [('','','','','','','','','','','')] + l

    max_strings = []
    for i in range(len(l[0])):
        max_strings.append('')
        for j in range(len(l)):
            if len(str(l[j][i])) > len(max_strings[i]):
                max_strings[i] = str(l[j][i])

    width = 0
    for i in max_strings:
        width += len(i)
    width += 17
    clear_full_screen(stdscr)
    win = create_center_window(width, cur.rowcount + 8)
    win.move(2,2)
    counter = 3


    for i in l:
        for j in range(len(i)):
            if counter == 3:
                win.attron(selected_color)
            win.addstr('|' + str(i[j]) + (' ' * (len(max_strings[j]) - len(str(i[j])))))
            win.attroff(selected_color)

        win.move(counter, 2)
        counter += 1

    win.addstr(counter, 3, "Press enter key to continue")
    win.attron(selected_color)
    win.box()
    win.attroff(selected_color)
    win.refresh()

    while True:
        key = keyboard.read_key()
        if key == "enter":
            break


def menu_handle(stdscr, log_info):
    clear_full_screen(stdscr)

    while True:
        ch = create_menu_box(stdscr,"CHOOSE OPTION :",["book a ticket", "cancel ticket", "generate ticket", "modify ticket","display all passengers","check availability of seats","search based on name","quit"])

        if ch[0] == 0:
            book_ticket(stdscr, log_info)
            conformation_window(stdscr, "Your ticket has been booked successfully")

        if ch[0] == 1:
            cancel_ticket(stdscr, log_info)
            conformation_window(stdscr, "Your ticket has been cancelled successfully")

        if ch[0] == 2:
            generate_ticket(stdscr,log_info)

        if ch[0] == 3:
            modify_ticket(stdscr, log_info)
            conformation_window(stdscr, "Your ticket has been modified successfully")

        if ch[0] == 4:
            display_all_passengers(stdscr, log_info)

        if ch[0] == 5:
            check_availability(stdscr)

        if ch[0] == 6:
            serach_name(stdscr)

        if ch[0] == 7:
            break

def main(stdscr):
    curses.curs_set(0)
    initialize_color()
    clear_full_screen(stdscr)
    login_info = login(stdscr)
    menu_handle(stdscr, login_info)

wrapper(main)