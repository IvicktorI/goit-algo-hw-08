from collections import UserDict
import datetime as dt
from datetime import datetime as dtdt
from prettytable import PrettyTable
import pickle
import random


class Field:
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return str(self.value)

class Name(Field):
    def __init__(self, value : str):
           super().__init__(value)
           
    def __eq__(self, other):
        return isinstance(other, Name) and self.value == other.value

    def __hash__(self):
        return hash(self.value)
    
    def __str__(self):
        return f'{self.value}'

class Phone(Field):
    def __init__(self, value: str):
        if self.is_valid_number(value):
            super().__init__(value)
        else:
            raise ValueError("Incorrect phone number")
    @staticmethod
    def is_valid_number(number: str):
        return str(number).isdigit() and len(str(number)) == 10
    
    def __str__(self):
        return f'{self.value}'
    
class Birthday(Field):
    def __init__(self, value):
        try:
            self.value=dtdt.strptime(value, "%d.%m.%Y").date()
        except ValueError:
            raise ValueError("Invalid date format. Use DD.MM.YYYY")
    
    def __str__(self):
        return self.value.strftime('%d.%m.%Y')
    
class Record:
    def __init__(self, name: str,phone=None, birthday=None):
        self.name = Name(name)
        if phone==None:
            self.phones = []
        else:
            _phone=Phone(phone)
            self.phones = [_phone]
        self.birthday=birthday
    
    def add_phone(self,phone: str):
        for ph in self.phones:
            if ph.value==phone:
                return 0
        self.phones.append(Phone(phone))
        return 1
        
    def remove_phone(self, phone: str):
        for ph in self.phones:
            if ph.value==phone:
                self.phones.remove(ph)
                break
    
    def edit_phone(self,old_phone: str, new_phone: str):
        for ph in self.phones:
            if ph.value==old_phone:
                ph = Phone(new_phone)
                return 1
        return 0
        
    def find_phone(self, phone: str) ->Phone:
        for ph in self.phones:
            if ph.value==phone:
                return ph
    
    def add_birthday(self,birthday: str):
        self.birthday=Birthday(birthday)
            
    def __str__(self):
        return f"Contact name: {self.name.value}, phones: {'; '.join(p.value for p in self.phones)}"
    
class AddressBook(UserDict):      
    def add_record(self, record: Record):
        self.data[record.name.value] = record

    def find(self,name: str):
        return self.data.get(name,None)
         
    def delete(self,name):
        del self.data[name] 
                
    def show_all(self):
        table = PrettyTable()
        table.field_names = ['Name','Phones']

        for contact in self.data.values():
            ph = '\n'.join(p.value for p in contact.phones)
            table.add_row([contact.name,ph])
        return table
    
    def birthdays(self):
        # congratulation list
        clist=[]
        # congratulation week
        # today = begin
        # today + 7 days = end
        begin= dtdt.today().date()
        end=dtdt.fromordinal(7+dtdt.toordinal(begin)).date()
        for i in self.data.values():
            # temp - birthday in current year
            temp=dtdt.strptime(i.birthday, "%d.%m.%Y").date().replace(year=begin.year)
            if temp>=begin and temp<=end:
                if temp.weekday()==5:
                    c=temp.replace(day=temp.day+2)
                    temp=c
                if temp.weekday()==6:
                    c=temp.replace(day=temp.day+1)
                    temp=c
                clist.append({'name':i.name, 'congratulation_date':dtdt.strftime(temp, "%d.%m.%Y")})

        table = PrettyTable()
        table.field_names = ['Name','Congratulation date']

        for contact in clist:
            table.add_row([contact['name'],contact['congratulation_date']])
        return table
    
def input_error(func):
    def inner(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except ValueError as e:
            return f'{e}'
        except KeyError:
            return 'No such name found'
        except IndexError:
            return 'Not found'
        except Exception as e:
            return f'Error: {e}'

    return inner

@input_error
def parse_input(user_input):
    cmd, *args = user_input.split()
    cmd = cmd.strip().lower()
    return cmd, *args

@input_error
def add_record(args, book: AddressBook):
    name, phone = args
    record = book.find(name)
    if record is None:
        record = Record(name,phone)
        book.add_record(record)
        return "Contact added."
    if record.add_phone(phone):
        return "Contact updated."
    else:
        return 'Phone already recorded.'

@input_error
def edit_phone(args, contacts):
    if len(args)==3:
        name, old_phone, new_phone = args
    else :
        raise ValueError ('Insufficient parameters')
    if name in contacts:
        if contacts[name].edit_phone(old_phone,new_phone):
            return "Record change."
    return 'Record not found'

@input_error
def delete_phone(args, contacts):
    if len(args)==2:
        name, phone = args
    else :
        raise ValueError ('Insufficient parameters')
    if name in contacts:
        contacts[name].remove_phone(phone)
        return "Phone delete."
    else:
        return 'Record not found'

@input_error
def find_record(args, contacts: AddressBook):
    name = args[0]
    rec=contacts.find(name)
    if rec is not None:
        return rec
    else : 
        return 'Record not found'
   
@input_error 
def delete_record(args, contacts: AddressBook):
    name = args[0]
    contacts.delete(name)
    return f'Record delete'

@input_error
def show_all(contacts: AddressBook):
    return contacts.show_all()
    
@input_error
def add_birthday(args, book: AddressBook):
    name,bd=args
    record = book.find(name)
    if record is not None:
        record.add_birthday(bd)
        return 'Birthday added'
    else:
        return 'Record not found'

@input_error
def show_birthday(args, book):
    name=args[0]
    record = book.find(name)
    if record is not None:
        return f"Contact name: {record.name}, birthday: {record.birthday}"
    else:
        return 'Record not found'

@input_error
def birthdays(book: AddressBook):
    return book.birthdays()

def save_data(book: AddressBook, filename="addressbook.pkl"):
    with open(filename, "wb") as f:
        pickle.dump(book, f)

def load_data(filename="addressbook.pkl"):
    try:
        with open(filename, "rb") as f:
            return pickle.load(f)
    except FileNotFoundError:
        return AddressBook()

def main():
    book = load_data()
    print("Welcome to the assistant bot!")
    while True:
        user_input = input("Enter a command: ")
        command, *args = parse_input(user_input)

        match command:
            case 'hello':
                print('How can I help you?')
            case 'add':
                print(add_record(args,book))
            case 'add_birthday':
                print(add_birthday(args,book))
            case 'show_birthday':
                print(show_birthday(args,book))
            case 'birthdays':
                print(birthdays(book))
            case 'change':
                print(edit_phone(args,book))
            case 'phone':
                print(find_record(args,book))
            case 'delete':
                print(delete_record(args,book))
            case 'delete_phone':
                print(delete_phone(args, book))
            case 'all':
                print(show_all(book))
            case 'close':
                print('Good bye!')
                save_data(book)
                break
            case 'exit':
                print('Good bye!')
                save_data(book)
                break
            case _:
                print('Invalid command.')


if __name__ == "__main__":
    main()