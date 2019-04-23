from bi_code import bi

__all__ = ['builtin_map']

builtin_map = {}



"""
# manage properties
builtin_map.update({
		'properties': bi.properties,
		'add_property': bi.add_property,
		'delete_property': bi.delete_property,
		'clear_property': bi.clear_property,
		'set_property_opts': bi.set_property_opts,
		'get_property_opts': bi.get_property_opts,
		'set_property_owner': bi.set_property_owner,
		'get_property_owner': bi.get_property_owner,
	})
	
# manage files
builtin_map.update({
		'files': bi.files,
		'add_file': bi.add_file,
		'delete_file': bi.delete_file,
		'set_file_opts': bi.set_file_opts,
		'get_file_opts': bi.get_file_opts,
		'set_file_owner': bi.set_file_owner,
		'get_file_owner': bi.get_file_owner,
	})

# manage functions
builtin_map.update({
		'functions': bi.functions,
		'add_function': bi.add_function,
		'delete_function': bi.delete_function,
		'set_function_code': bi.set_function_code,
		'get_function_code': bi.get_function_code,
		'set_function_opts': bi.set_function_opts,
		'get_function_opts': bi.get_function_opts,
		'set_function_args': bi.set_function_args,
		'get_function_args': bi.get_function_args,
		'set_function_owner': bi.set_function_owner,
		'get_function_owner': bi.get_function_owner,
	})

# server configuration
builtin_map.update({
		'set_server_var': bi.set_server_var,
		'get_server_var': bi.get_server_var,
		'save_database': bi.save_database,
		'shutdown': bi.shutdown,
		'server_info': bi.server_info,
		'time': bi.time,
		'format_time': bi.format_time,
	})

# manage running tasks
builtin_map.update({
		'set_perms': bi.set_perms,
		'get_perms': bi.get_perms,
		'task_id': bi.task_id,
		'kill_task': bi.kill_task,
		'eval': bi.eval,
		'fork': bi.fork,
		'sleep': bi.sleep,
		'resume': bi.resume,
		'raise': bi.raise,
		'stack': bi.stack,
	})

# manage objects
builtin_map.update({
		'create': bi.create,
		'destroy': bi.destroy,
		'set_parent': bi.set_parent,
		'parent': bi.parent,
		'children': bi.children,
		'set_owner': bi.set_owner,
		'owner': bi.owner,
		'max_object': bi.max_object,
		'renumber': bi.renumber,
	})

# manage connections and ports
builtin_map.update({
		'connect': bi.connect,
		'disconnect': bi.disconnect,
		'open_connection': bi.open_connection,
		'close_connection': bi.close_connection,
		'incoming_connections': bi.incoming_connections,
		'outgoing_connections': bi.outgoing_connections,
		'get_connection_info': bi.get_connection_info,
		'set_connection_opts': bi.set_connection_opts,
		'send': bi.send,
		'recv': bi.recv,
		'listen': bi.listen,
		'unlisten': bi.unlisten,
		'setuid': bi.setuid,
	})
"""

builtin_map.update({
		'serverlog': bi.serverlog,
	})

"""
# builtin functions for list types
listbi_map = {}
listbi_map.update({
		'length': bi.list_len,
		'len': bi.list_len,
		'sort': bi.list_sort,
	})
"""
