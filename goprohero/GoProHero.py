#!/usr/bin/python

# GoProHero.py
# Josh Villbrandt <josh@javconcepts.com>, Blair Gagnon <blairgagnon@gmail.com>
# August 2013 - November 2014

import logging
import socket
import unicodedata
from colorama import Fore

# urllib support for Python 2 and Python 3
try:
    from urllib.request import urlopen, HTTPError, URLError
except ImportError:
    from urllib2 import urlopen, HTTPError, URLError

# attempt imports for image() function
try:
    import cv2
    from PIL import Image
    import StringIO
    import base64
except ImportError:
    pass


class GoProHero:
    @classmethod
    def config(self):
        return {
            'status': GoProHero.statusMatrix,
            'command': GoProHero.commandMaxtrix
        }

    @classmethod
    def _hexToDec(self, val):
        returnVal = int.from_bytes(val,byteorder='big')
        return returnVal

    @classmethod
    def _splitByControlCharacters(self, val):
        # extract non-control characters
        output = []
        s = ''
        for c in val:
            if unicodedata.category(c)[0] == 'C':
                if len(s) > 0:
                    # start a new string if we found a control character
                    output.append(str(s))
                    s = ''
            else:
                s += c

        # clean up any left over string
        if len(s) > 0:
            output.append(str(s))

        # return extracts strings
        return output

    @classmethod
    def _extractModel(self, val):
        parts = self._splitByControlCharacters(val.decode('UTF-8'))
        if len(parts) > 0:
            # the first two chunks of 'HD4.02.01.02.00'
            return '.'.join(parts[0].split('.')[0:2])
        else:
            return None

    @classmethod
    def _extractFirmware(self, val):
        parts = self._splitByControlCharacters(val.decode('UTF-8'))
        if len(parts) > 0:
            # everything except the first two chunks of 'HD4.02.01.02.00'
            return '.'.join(parts[0].split('.')[2:])
        else:
            return None

    @classmethod
    def _extractName(self, val):
        parts = self._splitByControlCharacters(val.decode('UTF-8'))
        if len(parts) > 1:
            return parts[1]
        else:
            return None

    def _statusURL(self, command):
        return 'http://{}/{}?t={}'.format(self._ip, command, self._password)

    def _commandURL(self, command, value):
        if value is not None:
            return 'http://{}/{}?t={}&p=%{}'.format(
                self._ip, command, self._password, value)
        else:
            return 'http://{}/{}?t={}'.format(
                self._ip, command, self._password)

    def _previewURL(self):
        return 'http://{}:8080/live/amba.m3u8'.format(self._ip)

    timeout = 2.0
    statusMatrix = {
        'bacpac/se': {
            'power': {
                'a': 18,
                'b': 20,
                'translate': {
                    '00': 'sleeping',
                    '01': 'on'
                }
            }
        },
        'camera/se': {
            'preview': {
                'a': 18,
                'b': 19,
                'translate': {
                    '0': 'off',
                    '1': 'on'
                }
            },
            'batt1': {
                'a': 19,
                'b': 20,
                'translate': '_hexToDec'
            }
        },
        'camera/sx': {  # the first 62 bytes of sx are almost the same as se
            'mode': {
                'a': 1,
                'b': 2,
                'translate': {
                    b'\x00': 'video',
                    b'\x01': 'still',
                    b'\x02': 'burst',
                    b'\x03': 'timelapse',
                    b'\x07': 'settings'
                }
            },
            'defaultmode': {    #Not in API3
                'a': 6,
                'b': 8,
                'translate': {
                    '00': 'video',
                    '01': 'still',
                    '02': 'burst',
                    '03': 'timelapse'
                }
            },
            'spotmeter': {
                'a': 4,
                'b': 5,
                'translate': {
                    b'\x00': 'off',
                    b'\x01': 'on'
                }
            },
            'timelapseinterval': {
                'a': 5,
                'b': 6,
                'translate': '_hexToDec'
            },
            'autooff': {    #not in API3
                'a': 12,
                'b': 14,
                'translate': {
                    '00': 'never',
                    '01': '1 minute',
                    '02': '2 minutes',
                    '03': '5 minutes'
                }
            },
            'fov': {
                'a': 7,
                'b': 8,
                'translate': {
                    b'\x00': '170',
                    b'\x01': '127',
                    b'\x02': '90'
                }
            },
            'photores': {
                'a': 8,
                'b': 9,
                'translate': {
                    b'\x00': '11MP wide',
                    b'\x01': '8MP med',
                    b'\x02': '5MP wide',
                    b'\x03': '5MP med',
                    b'\x04': '7MP wide',
                    b'\x05': '12MP wide',
                    b'\x06': '7MP med'
                }
            },
            'minselapsed': {    #Not in API3
                'a': 27,
                'b': 29,
                'translate': '_hexToDec'
            },
            'secselapsed': {    #Not in API3
                'a': 28,
                'b': 30,
                'translate': '_hexToDec'
            },
            'orientation': {
                'a': 18,
                'b': 19,
                'translate': {         #Bitwise
                    # looks like this really should just be the third bit
                    b'\x00': 'up',
                    b'\x04': 'down'
                }
            },
            'charging': {       #Not in API3
                'a': 39,
                'b': 40,
                'translate': {
                    '2': 'no',  # 2 only shows up temporarily
                    '3': 'no',
                    '4': 'yes'
                }
            },
            'picsremaining': {
                'a': 21,
                'b': 23,
                'translate': '_hexToDec'
            },
            'npics': {
                'a': 23,
                'b': 25,
                'translate': '_hexToDec'
            },
            'minsremaining': {
                'a': 25,
                'b': 27,
                'translate': '_hexToDec'
            },
            'nvids': {
                'a': 27,
                'b': 29,
                'translate': '_hexToDec'
            },
            'record': {
                'a': 29,
                'b': 30,
                'translate': {
                    b'\x00': 'off',
                    b'\x01': 'on'
                }
            },
            'lowlight': {       #Not in API3
                'a': 60,
                'b': 61,
                'translate': {
                    '0': 'off',
                    '4': 'on'
                }
            },
            'protune': {        #Bitwise stuff
                'a': 61,
                'b': 62,
                'translate': {
                    '0': 'off',  # seems to be only while in the menu
                    '2': 'on',  # seems to be only while in the menu
                    '4': 'off',
                    '6': 'on'
                }
            },
            'whitebalance': {
                'a': 34,
                'b': 35,
                'translate': {
                    b'\x00': 'auto',
                    b'\x01': '3000K',
                    b'\x02': '5500K',
                    b'\x03': '6500K',
                    b'\x04': 'raw'
                }
            },
            'looping': {
                'a': 37,
                'b': 38,
                'translate': {
                    b'\x00': 'off',
                    b'\x01': '5 minutes',
                    b'\x02': '20 minutes',
                    b'\x03': '60 minutes',
                    b'\x04': '120 minutes',
                    b'\x05': 'max'
                }
            },
            'batt2': {
                'a': 57,
                'b': 58,
                'translate': '_hexToDec'
            },
            'overheated': {  # experimental #Not in API3
                'a': 92,
                'b': 93,
                'translate': {
                    '0': 'false',
                    '4': 'true'
                }
            },
            'attachment': { #Not in API3
                'a': 93,
                'b': 94,
                'translate': {
                    '0': 'none',
                    '4': 'LCD',
                    '8': 'battery'
                }
            },
            'vidres': {
                'a': 50,
                'b': 51,
                'translate': {
                    b'\x00': 'WVGA',
                    b'\x01': '720p',
                    b'\x02': '960p',
                    b'\x03': '1080p',
                    b'\x04': '1440p',
                    b'\x05': '2.7K',
                    b'\x06': '2.7K 17:9 Cinema',
                    b'\x07': '4K',
                    b'\x08': '4K 17:9 Cinema',
                    b'\x09': '1080p SuperView',
                    b'\x0a': '720p SuperView'
                }
            },
            'fps': {
                'a': 51,
                'b': 52,
                'translate': {
                    b'\x00': '12',
                    b'\x01': '15',
                    b'\x02': '24',
                    b'\x03': '25',
                    b'\x04': '30',
                    b'\x05': '48',
                    b'\x06': '50',
                    b'\x07': '60',
                    b'\x08': '100',
                    b'\x09': '120',
                    b'\x0a': '240'
                }
            }
        },
        'camera/cv': {
            'name': {
                'translate': '_extractName'
            },
            'model': {
                'translate': '_extractModel'
            },
            'firmware': {
                'translate': '_extractFirmware'
            }
        }
    }
    commandMaxtrix = {
        'power': {
            'cmd': 'bacpac/PW',
            'translate': {
                'sleep': '00',
                'on': '01'
            }
        },
        'record': {
            'cmd': 'camera/SH',
            'translate': {
                'off': '00',
                'on': '01'
            }
        },
        'preview': {
            'cmd': 'camera/PV',
            'translate': {
                'off': '00',
                'on': '02'
            }
        },
        'orientation': {
            'cmd': 'camera/UP',
            'translate': {
                'up': '00',
                'down': '01'
            }
        },
        'mode': {
            'cmd': 'camera/CM',
            'translate': {
                'video': '00',
                'still': '01',
                'burst': '02',
                'timelapse': '03',
                'timer': '04',
                'hdmiout': '05'
            }
        },
        'volume': {
            'cmd': 'camera/BS',
            'translate': {
                '0': '00',
                '70': '01',
                '100': '02'
            }
        },
        'locate': {
            'cmd': 'camera/LL',
            'translate': {
                'off': '00',
                'on': '01'
            }
        },
        'picres': {
            'cmd': 'camera/PR',
            'translate': {
                '11MP wide': '00',
                '8MP med': '01',
                '5MP wide': '02',
                '5MP med': '03',
                '7MP wide': '04',
                '12MP wide': '05',
                '7MP med': '06'
            }
        },
        'vidres': {
            'cmd': 'camera/VV',
            'translate': {
                'WVGA': '00',
                '720p': '01',
                '960p': '02',
                '1080p': '03',
                '1440p': '04',
                '2.7K': '05',
                '2.7K 17:9 Cinema': '06',
                '4K': '07',
                '4K 17:9 Cinema': '08',
                '1080p SuperView': '09',
                '720p SuperView': '0a'
            }
        },
        'fov': {
            'cmd': 'camera/FV',
            'translate': {
                '170': '00',
                '127': '01',
                '90': '02'
            }
        },
        'fps': {
            'cmd': 'camera/FS',
            'translate': {
                '12': '00',
                '12.5': '0b',
                '15': '01',
                '24': '02',
                '25': '03',
                '30': '04',
                '48': '05',
                '50': '06',
                '60': '07',
                '100': '08',
                '120': '09',
                '240': '0a'
            }
        },
        'looping': {
            'cmd': 'camera/LO',
            'translate': {
                'off': '00',
                '5 minutes': '01',
                '20 minutes': '02',
                '60 minutes': '03',
                '120 minutes': '04',
                'max': '05'
            }
        },
        'protune': {
            'cmd': 'camera/PT',
            'translate': {
                'off': '00',
                'on': '01'
            }
        },
        'delete_last': {
            'cmd': 'camera/DL'
        },
        'delete_all': {
            'cmd': 'camera/DA'
        }
    }

    def __init__(
            self, ip='10.5.5.9', password='password', log_level=logging.INFO):
        self._ip = ip
        self._password = password

        # setup log
        log_format = '%(asctime)s   %(message)s'
        logging.basicConfig(format=log_format, level=log_level)

    def password(self, password=None):
        if password is None:
            return self._password
        else:
            self._password = password

    def status(self):
        status = {
            # summary = 'notfound', 'sleeping', 'on', or 'recording'
            'summary': 'notfound',
            'raw': {}
        }
        camActive = True

        # loop through different status URLs
        for cmd in self.statusMatrix:

            # stop sending requests if a previous request failed
            if camActive:
                url = self._statusURL(cmd)

                # attempt to contact the camera
                try:
                    response = urlopen(
                        url, timeout=self.timeout).read()
                    status['raw'][cmd] = response  # save raw response
                    print("Response:{}".format(response))

                    # loop through different parts we know how to translate
                    for item in self.statusMatrix[cmd]:
                        args = self.statusMatrix[cmd][item]
                        print("Args:{}".format(args))
                        if 'a' in args and 'b' in args:
                            part = response[args['a']:args['b']]
                        else:
                            part = response
                        # translate the response value if we know how
                        if 'translate' in args:
                            status[item] = self._translate(
                                args['translate'], part)
                        else:
                            status[item] = part
                        print("Part: {}".format(part))
                except (HTTPError, URLError, ConnectionError) as e:
                    logging.warning('{}{} - error opening {}: {}{}'.format(
                        Fore.YELLOW, 'GoProHero.status()', url, e, Fore.RESET))
                    camActive = False

        # build summary
        if 'record' in status and status['record'] == 'on':
            status['summary'] = 'recording'
        elif 'power' in status and status['power'] == 'on':
            status['summary'] = 'on'
        elif 'power' in status and status['power'] == 'sleeping':
            status['summary'] = 'sleeping'

        logging.info('GoProHero.status() - result {}'.format(status))
        return status

    def image(self):
        try:
            # use OpenCV to capture a frame and store it in a numpy array
            stream = cv2.VideoCapture(self._previewURL())
            success, numpyImage = stream.read()

            if success:
                # use Image to save the image to a file, but actually save it
                # to a string
                image = Image.fromarray(numpyImage)
                output = StringIO.StringIO()
                image.save(output, format='PNG')
                str = output.getvalue()
                output.close()

                logging.info('GoProHero.image() - success!')
                return 'data:image/png;base64,'+base64.b64encode(str)
        except NameError:
            logging.warning('{}{} - OpenCV not installed{}'.format(
                Fore.YELLOW, 'GoProHero.image()', Fore.RESET))
        except IOError as e:
            logging.warning('{}{} - Pillow prereqs not installed: {}{}'.format(
                Fore.YELLOW, 'GoProHero.image()', e, Fore.RESET))

        # catchall return statement
        return False

    def command(self, command, value=None):
        func_str = 'GoProHero.command({}, {})'.format(command, value)

        if command in self.commandMaxtrix:
            args = self.commandMaxtrix[command]
            # accept both None and '' for commands without a value
            if value == '':
                value = None
            # for commands with values, translate the value
            if value is not None and value in args['translate']:
                value = args['translate'][value]
            # build the final url
            url = self._commandURL(args['cmd'], value)

            # attempt to contact the camera
            try:
                urlopen(url, timeout=self.timeout).read()
                logging.info('{} - http success!'.format(func_str))
                return True
            except (HTTPError, URLError, socket.timeout) as e:
                logging.warning('{}{} - error opening {}: {}{}'.format(
                    Fore.YELLOW, func_str, url, e, Fore.RESET))

        # catchall return statement
        return False

    def test(self, url, toHex=True):
        try:
            url = 'http://{}/{}'.format(self._ip, url)

            print(url)
            response = urlopen(
                url, timeout=self.timeout).read()

            if toHex:
                response = response.encode('UTF-8')

            print(response)
        except (HTTPError, URLError, socket.timeout) as e:
            print(e)

    def _translate(self, config, value):
        if isinstance(config, dict):
            # use a lookup dictionary
            if value in config:
                return config[value]
            else:
                return 'translate error: {} not found'.format(value)
        else:
            # use an internal function
            if hasattr(self, config):
                return getattr(self, config)(value)
            else:
                return 'translate error: {} not a function'.format(value)
