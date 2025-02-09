try:
    import distutils.sysconfig  # type: ignore
except ModuleNotFoundError:
    import setuptools._distutils.sysconfig as sysconfig  # type: ignore
    import types
    import sys
    distutils = types.ModuleType("distutils")
    distutils.sysconfig = sysconfig
    sys.modules["distutils"] = distutils
    sys.modules["distutils.sysconfig"] = sysconfig

import iptc  # type: ignore

class Iptables:
    def __init__(self):
        # Utiliza la tabla FILTER y desactiva el autocommit para acumular cambios
        self.table = iptc.Table(iptc.Table.FILTER)
        self.table.autocommit = False

    def append(self, chain_name, *args):
        chain = iptc.Chain(self.table, chain_name)
        rule = iptc.Rule()

        i = 0
        while i < len(args):
            arg = args[i]
            if arg == '-m':
                i += 1
                module = args[i]
                match = rule.create_match(module)
                if module == "mac":
                    i += 1
                    if i < len(args) and args[i] == '--mac-source':
                        i += 1
                        match.mac_source = args[i]
                    else:
                        raise ValueError("Se esperaba '--mac-source' después de '-m mac'")
            elif arg == '-j':
                i += 1
                target_name = args[i]
                rule.target = iptc.Target(rule, target_name)
            i += 1

        chain.append_rule(rule)

    def delete(self, chain_name, *args):
        chain = iptc.Chain(self.table, chain_name)
        rule = iptc.Rule()

        i = 0
        while i < len(args):
            arg = args[i]
            if arg == '-m':
                i += 1
                module = args[i]
                match = rule.create_match(module)
                if module == "mac":
                    i += 1
                    if i < len(args) and args[i] == '--mac-source':
                        i += 1
                        match.mac_source = args[i]
                    else:
                        raise ValueError("Se esperaba '--mac-source' después de '-m mac'")
            elif arg == '-j':
                i += 1
                target_name = args[i]
                rule.target = iptc.Target(rule, target_name)
            i += 1

        rule_to_delete = None
        for r in chain.rules:
            if r.target.name == rule.target.name:
                # Solo se maneja el match 'mac' en este caso
                if rule.matches:
                    expected_mac = rule.matches[0].mac_source
                    for m in r.matches:
                        if m.name == "mac" and getattr(m, "mac_source", None) == expected_mac:
                            rule_to_delete = r
                            break
                else:
                    rule_to_delete = r
            if rule_to_delete:
                break

        if rule_to_delete:
            chain.delete_rule(rule_to_delete)

    def commit(self):
        # Los cambios se aplican al hacer commit en la tabla
        self.table.commit()
