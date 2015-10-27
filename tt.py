from virtualmachine import VirtualMachine, static_vm
from parse import Parser
from database import *


db = Database("test")

p = Parser()
vm = static_vm
vm.db = db
bytecode = p.parse("""serverlog("hello"); var2 = "7"; var1 = var2; serverlog(var1);""")
vm.spawn_cmd_task(bytecode, {})
bytecode = p.test()
vm.spawn_cmd_task(bytecode, {})

vm.run()
vm.run()
vm.run()