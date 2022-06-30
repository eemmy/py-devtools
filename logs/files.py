# -*- coding: utf-8 -*-
from os import path
from datetime import datetime


class Files:
    def __init__(self, config: dict = {}):
        self.__config = config
        self.__messages = []
        self.__outputs = []
        self.output_colors = {
            'red': '\033[1;31m',
            'green': '\033[1;32m',
            'yellow': '\033[1;33m',
            'blue': '\033[1;34m',
            'default': '\033[1;39m',
        }

        self.__validate_configs()
        self.__prepare_file()


    def set_context_color(self, color: str):
        self.__config['context_color'] = color


    def __validate_configs(self):
        default_configs = {
            'output_file': path.dirname(path.realpath(__file__)) + '/output.log',
            'print_outputs': True,
            'rt_write': True,
            'context_color': 'green'
        }

        for option in default_configs:
            if not option in self.__config.keys():
                self.__config[option] = default_configs[option]


    def __prepare_file(self):
        self.__file = open(self.__config['output_file'], 'a+')
        self.__file_open_state = True


    def __get_date(self):
        return f"[{datetime.today().strftime('%Y-%m-%d %H:%M:%S')}]"


    def __print(self, message, date):
        print_message = f"{self.output_colors[self.__config['context_color']]}{date} {self.output_colors['default']}- {message}"

        if self.__config['rt_write'] == True:
            print(print_message)
        else:
            self.__outputs.append(print_message)


    def add(self, message):
        date = self.__get_date()
        output_message = f'{date} - {message}\n'

        if self.__config['rt_write'] == True:
            if self.__file_open_state == False:
                self.__prepare_file()

            self.__file.write(output_message)
            self.__file.close()

            self.__file_open_state = False
            self.__prepare_file()
        else:
            self.__messages.append(output_message)


        self.__print(message, date)


    def write(self):
        if self.__config['rt_write'] == True:
            return None

        if self.__file_open_state == False:
            self.__prepare_file()

        for message in self.__messages:
            self.__file.write(message)

        self.__file.write('\n')

        self.__file.close()
        self.__file_open_state = False
        self.__messages = []

        self.__output_prints()


    def __output_prints(self):
        if self.__config['rt_write'] == True:
            return None

        for output_print in self.__outputs:
            print(output_print)

        print('')

        self.__outputs = []


