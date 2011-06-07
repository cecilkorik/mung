from virtualmachine import VirtualMachine
from parse import Parser

p = Parser()
vm = VirtualMachine(None)
bytecode = p.parse("""serverlog("hello"); var1 = var2;""")
vm.spawn_cmd_task(bytecode, {})

vm.run()