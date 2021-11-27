class Stats:
    def __init__(self):
        # Initialize variables
        self.received = None
        self.values = {
            'pitch': 9999,
            'roll': 9999,
            'yaw': 9999,
            'vgx': 9999,
            'vgy': 9999,
            'vgz': 9999,
            'templ': 9999,
            'temph': 9999,
            'tof': 9999,
            'h': 9999,
            'bat': 9999,
            'baro': 9999,
            'time': 9999,
            'agx': 9999,
            'agy': 9999,
            'agz': 9999,
        }

    def parse(self, stats_string: bytes):
        stats_string = stats_string.decode('utf-8')
        stats_string = stats_string.replace(';\r\n', '')
        keys_and_values = stats_string.split(';')
        for combi in keys_and_values:
            if not combi == '':
                temp = combi.split(':')
                self.values[temp[0]] = float(temp[1])

    def get_temp(self):
        return (self.values['templ'] + self.values['temph'])/2

    def get_baro(self):
        return self.values['baro']

    def get_tof(self):
        return self.values['tof']

    def get_time(self):
        return self.values['time']

    def get_bat(self):
        return self.values['bat']

    def get_height(self):
        return self.values['h']
