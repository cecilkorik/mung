builtin_map = {}

# decorator for builtin function with "n" args
def bi(func, n):
	def builtin_varg(vm):
		args = vm.pop(n)
		rv = func(args)
		vm.push(rv)
	return builtin_varg

"""
# manage properties
builtin_map.update({
		'properties': bi_properties,
		'add_property': bi_add_property,
		'delete_property': bi_delete_property,
		'clear_property': bi_clear_property,
		'set_property_opts': bi_set_property_opts,
		'get_property_opts': bi_get_property_opts,
		'set_property_owner': bi_set_property_owner,
		'get_property_owner': bi_get_property_owner,
	})
	
# manage files
builtin_map.update({
		'files': bi_files,
		'add_file': bi_add_file,
		'delete_file': bi_delete_file,
		'set_file_opts': bi_set_file_opts,
		'get_file_opts': bi_get_file_opts,
		'set_file_owner': bi_set_file_owner,
		'get_file_owner': bi_get_file_owner,
	})

# manage functions
builtin_map.update({
		'functions': bi_functions,
		'add_function': bi_add_function,
		'delete_function': bi_delete_function,
		'set_function_code': bi_set_function_code,
		'get_function_code': bi_get_function_code,
		'set_function_opts': bi_set_function_opts,
		'get_function_opts': bi_get_function_opts,
		'set_function_args': bi_set_function_args,
		'get_function_args': bi_get_function_args,
		'set_function_owner': bi_set_function_owner,
		'get_function_owner': bi_get_function_owner,
	})

# server configuration
builtin_map.update({
		'set_server_var': bi_set_server_var,
		'get_server_var': bi_get_server_var,
		'save_database': bi_save_database,
		'shutdown': bi_shutdown,
		'server_info': bi_server_info,
		'time': bi_time,
		'format_time': bi_format_time,
	})

# manage running tasks
builtin_map.update({
		'set_perms': bi_set_perms,
		'get_perms': bi_get_perms,
		'task_id': bi_task_id,
		'kill_task': bi_kill_task,
		'eval': bi_eval,
		'fork': bi_fork,
		'sleep': bi_sleep,
		'resume': bi_resume,
		'raise': bi_raise,
		'stack': bi_stack,
	})

# manage objects
builtin_map.update({
		'create': bi_create,
		'destroy': bi_destroy,
		'set_parent': bi_set_parent,
		'parent': bi_parent,
		'children': bi_children,
		'set_owner': bi_set_owner,
		'owner': bi_owner,
		'max_object': bi_max_object,
		'renumber': bi_renumber,
	})

# manage connections and ports
builtin_map.update({
		'connect': bi_connect,
		'disconnect': bi_disconnect,
		'open_connection': bi_open_connection,
		'close_connection': bi_close_connection,
		'incoming_connections': bi_incoming_connections,
		'outgoing_connections': bi_outgoing_connections,
		'get_connection_info': bi_get_connection_info,
		'set_connection_opts': bi_set_connection_opts,
		'send': bi_send,
		'recv': bi_recv,
		'listen': bi_listen,
		'unlisten': bi_unlisten,
		'setuid': bi_setuid,
	})
"""