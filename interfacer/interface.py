import json
import pkgutil
import regex
# from interfacer.module import Module as mod
from .utils.tool import Tool, Log


class Interface(Tool):
    def __init__(self, obj=None):
        self.logger = Log(self.__class__.__name__, enable=True, testing=True)
        self.protocols = json.loads(pkgutil.get_data(
            __name__, 'protocols/protocol.json'))
        self.protocol_classification = iter(self.__loadProtocols())
        self.protocol_match = []
        self.protocol_dict = {}
        self.matched_interfaces = []
        # TODO: store matched pairs
        self.pairs = []
        if obj:
            self.logger.logger.info("Is obj.")
            self.verifyInterface(obj)

    def __requirePorts(self, protocol):
        require = set()
        for interface, interface_params in self.protocols['PROTOCOLS'][protocol['standard']][protocol['name']]['INFO']['INTERFACE'].items():
            if interface_params['REQUIRED']:
                require.add(interface)
        return require

    def __loadProtocols(self):
        classification = []
        for family in self.protocols['PROTOCOLS']:
            for name in self.protocols['PROTOCOLS'][family]:
                classification.append({'standard': family, 'name': name})
        return classification

    def loadInterface(self, custom=None):
        if custom:
            self.protocols = json.loads(custom)
        else:
            self.protocols = json.loads(pkgutil.get_data(
                __name__, 'protocols/protocol.json'))
        self.protocol_classification = iter(self.__loadProtocols())

    def pragma(self, interface, family, options=None, modifier=None):
        classification = list(self.__loadProtocols())
        actual = [match[0] for match in self.matched_interfaces]
        official = [match[1] for match in self.matched_interfaces]
        print(official)
        try:
            official[actual.index(interface)]
        except ValueError as v:
            self.logger.logger.warning('{} of ports.'.format(v))
            return None
        else:
            for each in classification:
                # TODO: Add ability to extract substrings, i.e. enable_0 should be valid
                if official[actual.index(interface)] in self.protocols['PROTOCOLS'][each['standard']][each['name']]['INFO']['INTERFACE']:
                    if options:
                        print('a')
                        print(self.protocols['PROTOCOLS'][each['standard']]
                              [each['name']]['PARAMETERS']['PRAGMA'].format(*options))
                        return(self.protocols['PROTOCOLS'][each['standard']][each['name']]['PARAMETERS']['PRAGMA'].format(*options))
                    else:
                        # print("TC:",self.protocols['PROTOCOLS'][each['standard']][each['name']]['INFO']['PRAGMA'].format(interface,official[actual.index(interface)]))
                        if modifier:
                            print('b')
                            print(modifier)
                            print(self.protocols['PROTOCOLS'][each['standard']][each['name']]['INFO']['PRAGMA'].format(
                                f'{family}{modifier}', official[actual.index(interface)]))
                            return(self.protocols['PROTOCOLS'][each['standard']][each['name']]['INFO']['PRAGMA'].format(f'{family}{modifier}', official[actual.index(interface)]))
                        else:
                            print('c')
                            print(self.protocols['PROTOCOLS'][each['standard']][each['name']]['INFO']['PRAGMA'].format(
                                family, official[actual.index(interface)]))
                            return(self.protocols['PROTOCOLS'][each['standard']][each['name']]['INFO']['PRAGMA'].format(family, official[actual.index(interface)]))

                # else:
                    # print("No match for {} in {}".format(interface,each))

    def __keys_exists(self, element, *keys):
        '''
        Check if *keys (nested) exists in `element` (dict).
        '''
        if not isinstance(element, dict):
            raise AttributeError(
                'keys_exists() expects dict as first argument.')
        if len(keys) == 0:
            raise AttributeError(
                'keys_exists() expects at least two arguments, one given.')

        _element = element
        for key in keys:
            try:
                _element = _element[key]
            except KeyError:
                return False
        return True

    def verifyInterface(self, port_list, protocol=None):
        '''
        Check if protocol matches supported protocols.
        '''
        # self.logger.logger.warning(f'INPUT: {port_list}')
        port_list = dict(sorted(port_list.items()))
        self.logger.logger.warning(f'INPUT: {port_list}')
        if not port_list:
            return True
        match_list = []
        if protocol == None:
            self.logger.logger.info('Verifying port list.')
            protocol = next(self.protocol_classification)
        required = self.__requirePorts(protocol)
        for interface, interface_params in self.protocols['PROTOCOLS'][protocol['standard']][protocol['name']]['INFO']['INTERFACE'].items():
            # protocol_direction = self.protocols['PROTOCOLS'][protocol['standard']][protocol['name']]['DIRECTION']
            # print(protocol['name'])
            print(f"INTERFACE: {interface}")
            self.__match([interface, interface_params], port_list, match_list)
        check_req = [match[1] for match in match_list]
        match_req = [match[0] for match in match_list]
        print(f'LOOKING FOR PROTOCOL {protocol}')
        print(f'CHECK REQS: {check_req}')
        print(f'MATCH_LIST: {match_req}')
        print(f'PORT_LIST: {list(port_list.keys())}')

        if self.__verify(required, check_req):
            self.logger.logger.info('Verified {} {} protocol'.format(
                protocol['standard'], protocol['name']))
            print(
                f"VERIFIED {protocol['standard']} {protocol['name']} PORT_LIST: {match_req}")
            # no_interface = sum([len(d[x]) for x in d if isinstance(protocol_dict[protocol['standard']][protocol['name']], list)])) + 1

            if(protocol['standard'] not in self.protocol_dict):
                self.protocol_dict[protocol['standard']] = {}
            if(protocol['name'] not in self.protocol_dict[protocol['standard']]):
                self.protocol_dict[protocol['standard']][protocol['name']] = []
                self.protocol_dict[protocol['standard']
                                   ][protocol['name']].append(match_req)
            else:
                number_interface = sum([len(self.protocol_dict[protocol['standard']][protocol['name']][x]) for x in self.protocol_dict[protocol['standard']]
                                       [protocol['name']] if isinstance(self.protocol_dict[protocol['standard']][protocol['name']][x], list)])
                self.protocol_dict[protocol['standard']
                                   ][protocol['name']][number_interface].append(match_req)

                print(f'NO: {number_interface}')
            # print(f"THINGY: {self.protocol_dict}")
            self.matched_interfaces += match_list
            try:
                self.__keys_exists(port_list, 'direction')
                protocol['direction'] = self.protocols['PROTOCOLS'][protocol['standard']
                                                                    ][protocol['name']]['DIRECTION']
            except:
                pass
            self.protocol_match.append(protocol)
            # print(f'OLD PORTLIST: {port_list}')
            # print(self.matched_interfaces)
            # print(port_list.pop(str(match[0] for match in self.matched_interfaces)))
            # print(f'SET_PORT: {set(port_list)}')
            # print(f'SET_MATCH: {set([match[0] for match in self.matched_interfaces])}')
            # port_list = all(map( port_list.pop, [match[0] for match in self.matched_interfaces]))
            for each in set([match[0] for match in self.matched_interfaces]):
                # print(each)
                try:
                    port_list.pop(each)
                except:
                    pass
            # port_list = dict(
            #     set(port_list)-set([match[0] for match in self.matched_interfaces]))
            # print(f'NEW PORTLIST: {port_list}')

        self.logger.logger.info(self.protocol_dict)
        try:
            next_protocol = next(self.protocol_classification)
        except:
            self.logger.logger.info('Verifying protocols complete.')
            self.logger.logger.info(self.protocol_match)
            self.protocol_classification = iter(self.__loadProtocols())
            return
        self.verifyInterface(port_list, next_protocol)

    def __verify(self, required, match_list):
        required, match_list = set(required), set(match_list)
        # print("VERIFY REQ:",required)
        # print("VERIFY MAT:", match_list)
        return (required.issubset(match_list) and (match_list))

    def __match(self, interface, compare, match_list):
        # compare = dict(sorted(compare.items()))
        self.logger.logger.warning(f'{interface} - {compare}')
        regex_data = [interface[0]]
        match = False
        if 'ALTERNATIVES' in interface[1]:
            for alt in interface[1]['ALTERNATIVES']:
                self.logger.logger.info(
                    f"Found alternative {alt} for {interface[1]}")
                regex_data.append(alt)
        for each in compare:
            print(f"EACH: {each}")
            if match == True:
                print(f'BREAKING: {each}')
                match = False
                break
            for reg in regex_data:
                print(f'REGEX: {regex_data}')
                print(f'REG: {reg} - {each}')
                # print(f'{interface}')
                # print(f'{interface[reg]}')
                # reg = re.compile('.*({}).*'.format(reg))
                search = regex.compile(
                    '(?i)(?<=\s|^|_){}(?=\s|_|$)'.format(reg))
                if regex.search(search, each):
                    if (self.__keys_exists(interface[1], 'DIRECTION')):
                        if regex.search(interface[1]['DIRECTION'], compare[each]['direction']):
                            self.logger.logger.info(
                                "Matched {0} to {1} with direction {2}".format(each, regex_data[0], compare[each]['direction']))
                            match_list.append([each, regex_data[0]])
                            match = True
                            break
                    else:
                        self.logger.logger.info(
                            "Matched {0} to {1} with no direction".format(each, regex_data[0]))
                        match_list.append([each, regex_data[0]])
                        match = True
                        break

                # if re.search(reg, each, re.IGNORECASE):
                #     if (self.__keys_exists(interface[1], 'DIRECTION')):
                #         if re.search(interface[1]['DIRECTION'], compare[each]['direction'], re.IGNORECASE):
                #             self.logger.logger.info(
                #                 "Matched {0} to {1} with direction {2}".format(each, regex[0], compare[each]['direction']))
                #             match_list.append([each, regex[0]])
                #             match = True
                #             break
                #     else:
                #         self.logger.logger.info(
                #             "Matched {0} to {1} with no direction".format(each, regex[0]))
                #         match_list.append([each, regex[0]])
                #         match = True
                #         break

        if not match_list:
            return False
        else:
            return True

    def listInterfaces(self):
        return self.protocol_match


# if __name__ == '__main__':
#     obj = mod.Module(top="blinky_zybo_z7", files=[
#                      "../examples/rtl/top.v", "../examples/rtl/blink.v"], blackboxes=['blinky_zybo_z7'])

#     obj.add_mode('mode_a', ["../examples/rtl/top_0.v",
#                             "../examples/rtl/blink.v"], "../examples/rtl/zybo.xdc")
#     obj.add_mode('mode_b', ["../examples/rtl/top_1.v",
#                             "../examples/rtl/blink.v"], "../examples/rtl/zybo.xdc")

#     obj.list_modes()

#     i = Interface()
#     i.verifyInterface(obj.ports)
